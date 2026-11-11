"""
deanonymize_github_users.py
- created its HTTP cache, github_cache.sqlite, on import, in the current
  directory (even for --help). It is now created when processing starts,
  next to the output file by default (--cache-file, --no-cache);
- on a rate limit, slept exactly one hour and retried without limit
  (recursively). It now waits until the reset time GitHub sends, at most
  MAX_RATE_LIMIT_WAITS times, and --no-wait stops at once.

The rate-limit tests run the real PyGithub client against a local HTTP
server that answers like GitHub; the wait is replaced, so nothing waits.

Run with:
    pytest tests/unit/test_deanonymizer_cache_and_rate_limit.py -v
"""

import functools
import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import networkx as nx
import pytest
from github import Github

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}
NOREPLY = "123+dev@users.noreply.github.com"


def files_in(directory):
    return sorted(str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file())


# --- cache file -----------------------------------------------------------------------------

def test_help_creates_no_cache_file(tmp_path):
    result = subprocess.run([sys.executable, "-m", "scraplog.tools.deanonymize_github_users", "--help"],
                            cwd=tmp_path, capture_output=True, text=True, env=ENV)

    assert result.returncode == 0, result.stdout + result.stderr
    assert files_in(tmp_path) == []


RUN_MAIN = """
import sys
import scraplog.tools.deanonymize_github_users as d
d.validate_configuration_and_api_access = lambda path: {{"token": "no-token"}}
sys.argv = ["deanonymize_github_users.py", *{args!r}]
d.main()
"""


@pytest.mark.parametrize("extra_args, cache_file", [
    ([], "data/out.github_cache.sqlite"),
    (["--cache-file", "data/my.sqlite"], "data/my.sqlite"),
    (["--no-cache"], None),
])
def test_cache_file_location(tmp_path, extra_args, cache_file):
    (tmp_path / "data").mkdir()
    g = nx.Graph()
    g.add_node("1", **{"e-mail": "alice@google.com", "affiliation": "google"})  # no lookup needed
    nx.write_graphml(g, tmp_path / "data/in.graphml")

    args = ["data/in.graphml", "data/out.graphml", *extra_args]
    result = subprocess.run([sys.executable, "-c", RUN_MAIN.format(args=args)],
                            cwd=tmp_path, capture_output=True, text=True, env=ENV)

    assert result.returncode == 0, result.stdout + result.stderr
    expected = {"data/in.graphml", "data/out.graphml"} | ({cache_file} if cache_file else set())
    assert set(files_in(tmp_path)) == expected


def test_default_cache_file_is_next_to_the_output():
    from scraplog.tools.deanonymize_github_users import default_cache_file
    assert default_cache_file("results/net.out.graphml") == "results/net.out.github_cache.sqlite"


# --- rate limit -----------------------------------------------------------------------------

class FakeGitHub(BaseHTTPRequestHandler):
    """Answers /users/dev with a rate-limit 403 the first `limited` times, then with a profile."""
    limited = 0
    reset = 0

    def do_GET(self):
        cls = type(self)
        if self.path.startswith("/users/dev/orgs"):
            self._send(200, [{"login": "nvidia"}])
        elif self.path.startswith("/users/dev"):
            if cls.limited > 0:
                cls.limited -= 1
                self._send(403, {"message": "API rate limit exceeded for user ID 1."},
                           {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(cls.reset)})
            else:
                self._send(200, {"login": "dev", "email": "dev@nvidia.com", "company": "NVIDIA"})
        else:
            self._send(404, {"message": "Not Found"})

    def _send(self, status, body, headers=None):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture
def github(monkeypatch):
    """The module under test, talking to a local fake GitHub; returns (module, recorded sleeps)."""
    import scraplog.tools.deanonymize_github_users as d

    server = HTTPServer(("127.0.0.1", 0), FakeGitHub)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    real_github = Github
    monkeypatch.setattr(d, "Github", lambda token, **kw: real_github(token, base_url=base_url, **kw))
    sleeps = []
    monkeypatch.setattr(d, "_wait", sleeps.append)
    FakeGitHub.reset = int(time.time()) + 120
    yield d, sleeps
    server.shutdown()


def test_waits_until_the_reset_time_then_resolves(github):
    d, sleeps = github
    FakeGitHub.limited = 1

    result = d.deanonymize_github_user_with_cache_and_pygithub(NOREPLY, "no-token", {})

    assert result == ("dev@nvidia.com", "nvidia")
    assert len(sleeps) == 1
    assert 120 <= sleeps[0] <= 126  # until X-RateLimit-Reset, plus a 5 s margin; not a fixed hour


def test_gives_up_after_max_waits(github):
    d, sleeps = github
    FakeGitHub.limited = 100

    with pytest.raises(d.RateLimitStop):
        d.deanonymize_github_user_with_cache_and_pygithub(NOREPLY, "no-token", {})
    assert len(sleeps) == d.MAX_RATE_LIMIT_WAITS


def test_no_wait_stops_at_once(github):
    d, sleeps = github
    FakeGitHub.limited = 1

    with pytest.raises(d.RateLimitStop):
        d.deanonymize_github_user_with_cache_and_pygithub(NOREPLY, "no-token", {}, wait_on_rate_limit=False)
    assert sleeps == []


def test_wait_seconds_from_headers():
    from scraplog.tools.deanonymize_github_users import rate_limit_wait_seconds
    assert rate_limit_wait_seconds({"Retry-After": "60"}) == 65
    assert rate_limit_wait_seconds({"X-RateLimit-Reset": "1000"}, now=900) == 105
    assert rate_limit_wait_seconds({"X-RateLimit-Reset": "1000"}, now=2000) == 5  # reset already passed
    assert rate_limit_wait_seconds({}) == 3600


def test_cached_responses_never_expire(tmp_path):
    # They expired after one hour, so a rerun after a rate-limit stop (at least an hour later)
    # fetched everything again.
    import requests
    import requests_cache
    from scraplog.tools.deanonymize_github_users import install_http_cache

    install_http_cache(str(tmp_path / "cache.sqlite"))
    try:
        # install_cache makes every requests.Session (PyGithub's too) a cached session
        assert requests.Session().settings.expire_after == requests_cache.NEVER_EXPIRE
    finally:
        requests_cache.uninstall_cache()
