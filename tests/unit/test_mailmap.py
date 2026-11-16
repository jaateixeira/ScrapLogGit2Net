"""
Identity merging with --mailmap (Git's .mailmap format, scraplog/mailmap.py) and
the identities report <output>.identities.csv (scraplog/identities_report.py).

Run with:
    pytest tests/unit/test_mailmap.py -v
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scraplog.identities_report import possible_duplicates
from scraplog.mailmap import load_mailmap

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}

MAILMAP = """# comment line
Proper One <one@proper.org> <ONE@commit.org>
<two@proper.org> <two@commit.org>
Name Only <three@commit.org>
Specific Four <four@proper.org> Old Four <four@commit.org>
Generic Four <four-generic@proper.org> <four@commit.org>
Five <five@proper.org> <five@commit.org> trailing text
"""

QUERIES = [("X", "one@commit.org"), ("X", "two@COMMIT.org"), ("Someone", "three@commit.org"),
           ("old four", "four@commit.org"), ("Other", "four@commit.org"), ("X", "five@commit.org"),
           ("Nobody", "nobody@x.org")]


def test_same_answers_as_git_check_mailmap(tmp_path):
    git = shutil.which("git")
    assert git, "git is needed (it is needed to make the input logs anyway)"
    (tmp_path / "mailmap").write_text(MAILMAP)
    subprocess.run([git, "init", "-q", str(tmp_path / "repo")], check=True)
    mailmap = load_mailmap(tmp_path / "mailmap")

    for name, email in QUERIES:
        expected = subprocess.run([git, "-c", f"mailmap.file={tmp_path / 'mailmap'}", "check-mailmap",
                                   f"{name} <{email}>"], cwd=tmp_path / "repo", capture_output=True,
                                  text=True, check=True).stdout.strip()
        mapped_name, mapped_email = mailmap.map(name, email)
        assert f"{mapped_name} <{mapped_email}>" == expected


def test_malformed_line_is_reported_with_its_number(tmp_path):
    (tmp_path / "mailmap").write_text("Good <a@b.org>\nno e-mail here\n")
    with pytest.raises(ValueError, match="line 2"):
        load_mailmap(tmp_path / "mailmap")


def test_possible_duplicates():
    identities = [("Alice", "alice@home.org", "Alice", "alice@home.org"),
                  ("alice ", "alice@work.com", "alice ", "alice@work.com"),   # same name, other case/spaces
                  ("Bob", "Bob@b.org", "Bob", "Bob@b.org"), ("Robert", "bob@b.org", "Robert", "bob@b.org"),
                  ("Carol", "carol@c.org", "Carol", "carol@c.org")]
    assert possible_duplicates(identities) == {
        "alice@home.org": "same_name", "alice@work.com": "same_name",
        "Bob@b.org": "email_case", "bob@b.org": "email_case"}


# --- scrapLog ---------------------------------------------------------------------------------

# Alice commits f from home (10:00), Bob commits f (11:00), Alice commits f from work (12:00).
LOG = """==Alice;alice@home.org;Mon Jan 1 10:00:00 2024 +0000==
f.py

==Bob;bob@b.org;Mon Jan 1 11:00:00 2024 +0000==
f.py

==Alice;alice@work.com;Mon Jan 1 12:00:00 2024 +0000==
f.py
"""


def run(tmp_path, *args):
    (tmp_path / "t.IN").write_text(LOG)
    return subprocess.run([sys.executable, str(PROJECT_ROOT / "scrapLog.py"), "-r", "t.IN",
                           "-t", "inter_individual_graph_weighted", *args],
                          cwd=tmp_path, capture_output=True, text=True, env=ENV, timeout=300)


def data_lines(path):
    return [line for line in path.read_text().splitlines() if not line.startswith("#")]


def test_without_mailmap_the_two_addresses_are_two_people(tmp_path):
    assert run(tmp_path).returncode == 0
    # Bob-alice@home (11:00); alice@work-alice@home and alice@work-bob (12:00)
    assert [row.split(",")[:3] for row in data_lines(tmp_path / "t.WeightedNetwork.edges.csv")[1:]] == [
        ["alice@home.org", "alice@work.com", "1"], ["alice@home.org", "bob@b.org", "1"],
        ["alice@work.com", "bob@b.org", "1"]]
    assert data_lines(tmp_path / "t.WeightedNetwork.identities.csv") == [
        "original_name,original_email,name,email,commits,possible_duplicate",
        "Alice,alice@home.org,Alice,alice@home.org,1,same_name",
        "Alice,alice@work.com,Alice,alice@work.com,1,same_name",
        "Bob,bob@b.org,Bob,bob@b.org,1,"]


def test_mailmap_merges_them_into_one_node(tmp_path):
    (tmp_path / "mailmap").write_text("Alice <alice@work.com> <alice@home.org>\n")

    result = run(tmp_path, "--mailmap", "mailmap")

    assert result.returncode == 0, result.stdout + result.stderr
    # Bob after Alice (11:00), Alice after Bob (12:00): one pair, two co-edits, no self-loop
    assert [row.split(",")[:3] for row in data_lines(tmp_path / "t.WeightedNetwork.edges.csv")[1:]] == [
        ["alice@work.com", "bob@b.org", "2"]]
    assert data_lines(tmp_path / "t.WeightedNetwork.identities.csv")[1:] == [
        "Alice,alice@home.org,Alice,alice@work.com,1,", "Alice,alice@work.com,Alice,alice@work.com,1,",
        "Bob,bob@b.org,Bob,bob@b.org,1,"]
    graphml = (tmp_path / "t.WeightedNetwork.graphML").read_text()
    assert "alice@home.org" not in graphml and '"mailmap": {"path": "mailmap"' in graphml.replace("&quot;", '"')


def run_temporal(tmp_path, *args):
    return run(tmp_path, "-t", "inter_individual_graph_temporal", *args)  # the later -t wins


def test_filtering_the_mapped_address_removes_every_alias(tmp_path):
    (tmp_path / "mailmap").write_text("Alice <alice@work.com> <alice@home.org>\n")
    (tmp_path / "filter.txt").write_text("alice@work.com\n")

    result = run_temporal(tmp_path, "--mailmap", "mailmap", "-fe", "filter.txt")

    assert result.returncode == 0, result.stdout + result.stderr
    assert data_lines(tmp_path / "t.temporal.edges.csv")[1:] == []  # only Bob is left
    assert [row.split(",")[3] for row in data_lines(tmp_path / "t.temporal.identities.csv")[1:]] == ["bob@b.org"]


def test_filtering_an_alias_removes_only_its_commits(tmp_path):
    (tmp_path / "mailmap").write_text("Alice <alice@work.com> <alice@home.org>\n")
    (tmp_path / "filter.txt").write_text("alice@home.org\n")

    result = run_temporal(tmp_path, "--mailmap", "mailmap", "-fe", "filter.txt")

    assert result.returncode == 0, result.stdout + result.stderr
    # Bob (11:00) has no earlier editor left; Alice at work (12:00) follows Bob
    assert [row.split(",")[:3] for row in data_lines(tmp_path / "t.temporal.edges.csv")[1:]] == [
        ["alice@work.com", "bob@b.org", "1"]]


def test_invalid_mailmap_stops(tmp_path):
    (tmp_path / "mailmap").write_text("not a mailmap line\n")

    result = run(tmp_path, "--mailmap", "mailmap")

    assert result.returncode == 1
    assert "Cannot read --mailmap" in result.stdout + result.stderr
    assert not (tmp_path / "t.WeightedNetwork.graphML").exists()
