"""
-a / --aggregate-email-prefixes: map the organization part of email domains to
an organization name.

It used to have no effect: a matching key returned the organization part
unchanged instead of the configured name. Keys now match exactly
(case-insensitive) and the configured name is used, in lower case.

Run with:
    pytest tests/unit/test_email_aggregation.py -v
"""

import json
import subprocess
import sys
from pathlib import Path

import networkx as nx
import pytest

from scraplog.core.models import ProcessingState
from scraplog.identity import extract_affiliation_from_email

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def state():
    state = ProcessingState()
    state.email_aggregation_config = {"gmail": "Google", "GoogleMail": "google", "goog": "alphabet"}
    return state


@pytest.mark.parametrize("email,expected", [
    ("alice@gmail.com", "google"),           # configured name, in lower case
    ("bob@googlemail.com", "google"),        # key matched case-insensitively
    ("carol@us.gmail.com", "google"),        # subdomain removed first, then matched
    ("dave@google.com", "google"),           # 'goog' is not a prefix match any more
    ("erin@ibm.com", "ibm"),                 # no key: unchanged
])
def test_aggregation_uses_configured_name_on_exact_match(state, email, expected):
    assert extract_affiliation_from_email(email, state) == expected


def test_no_config_leaves_affiliations_unchanged():
    assert extract_affiliation_from_email("alice@gmail.com", ProcessingState()) == "gmail"


GIT_LOG = """==Alice;alice@gmail.com;Mon Jan 1 10:00:00 2024 +0000==
shared.py

==Bob;bob@googlemail.com;Tue Jan 2 10:00:00 2024 +0000==
shared.py

==Carol;carol@ibm.com;Wed Jan 3 10:00:00 2024 +0000==
shared.py

"""


def affiliations_in_output(tmp_path, *extra_args):
    log = tmp_path / "project.IN"
    log.write_text(GIT_LOG)
    out = tmp_path / "out.graphml"
    subprocess.run(
        [sys.executable, "-m", "scraplog.scraplog", "-r", str(log), "-o", str(out), *extra_args],
        cwd=tmp_path, capture_output=True, text=True, check=True,
        env={"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": ""},
    )
    graph = nx.read_graphml(out)
    return {graph.nodes[n]["e-mail"]: graph.nodes[n]["affiliation"] for n in graph}


def test_scraplog_without_a(tmp_path):
    assert affiliations_in_output(tmp_path) == {
        "alice@gmail.com": "gmail", "bob@googlemail.com": "googlemail", "carol@ibm.com": "ibm"}


def test_scraplog_with_a_merges_into_one_organization(tmp_path):
    config = tmp_path / "aggregate.json"
    config.write_text(json.dumps({"gmail": "Google", "googlemail": "google"}))

    assert affiliations_in_output(tmp_path, "-a", str(config)) == {
        "alice@gmail.com": "google", "bob@googlemail.com": "google", "carol@ibm.com": "ibm"}
