"""
deanonymize_github_users.py used to print the GitHub token in full: a debug
line `github_token=<token>` on every run, and `config={'token': '<token>'}`
when checking the configuration. Only a short masked prefix may be shown.

Runs in a subprocess in tmp_path, so nothing the tool writes lands in the
repository. No network call is made: the
API check and the rate-limit table are replaced by stubs.

Run with:
    pytest tests/unit/test_deanonymizer_token.py -v
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FAKE_TOKEN = "ghp_FAKEtoken0123456789abcdefSECRETPART"

SCRIPT = """
import scraplog.tools.deanonymize_github_users as d
d.test_github_api_access = lambda token: True
d.display_rate_limit_info = lambda token: None
config = d.validate_configuration_and_api_access()
assert config["token"] == {token!r}
"""


def run_check(tmp_path, env_token=None, config_file=False):
    env = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}
    if env_token:
        env["GITHUB_TOKEN"] = env_token
    if config_file:
        (tmp_path / "config.ini").write_text(f"[github]\ntoken = {FAKE_TOKEN}\n")
    return subprocess.run(
        [sys.executable, "-c", SCRIPT.format(token=FAKE_TOKEN)],
        cwd=tmp_path, capture_output=True, text=True, env=env,
    )


def test_token_from_environment_is_not_printed(tmp_path):
    result = run_check(tmp_path, env_token=FAKE_TOKEN)

    assert result.returncode == 0, result.stderr
    output = result.stdout + result.stderr
    assert "SECRETPART" not in output
    assert "ghp_FAKE..." in output  # the masked prefix is still shown


def test_token_from_config_file_is_not_printed(tmp_path):
    result = run_check(tmp_path, config_file=True)

    assert result.returncode == 0, result.stderr
    assert "SECRETPART" not in result.stdout + result.stderr
