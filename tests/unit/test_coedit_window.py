"""
--coedit-window: an optional time window in the edge definition.

When developer B commits a file, B is linked to each developer A who changed
that file before. With a window w, only if A's latest change to the file is at
most w before B's commit (boundary included). Without a window, nothing
changes. Developers with no co-edit inside a window are not nodes (as always).

Replaces two skipped tests of the planned 'relationship_window' feature
(docs/planned-network-definitions.md).

Run with:
    pytest tests/unit/test_coedit_window.py -v
"""

import json
import shutil
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import networkx as nx
import pytest

from scraplog.core.models import ProcessingState
from scraplog.networks.temporal import extract_temporal_network_from_parsed_change_log_entries, parse_duration

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def co_edits(entries, window=None):
    """(developer, developer, time) of every co-edit, sorted."""
    state = ProcessingState()
    state.parsed_change_log_entries = entries
    graph = extract_temporal_network_from_parsed_change_log_entries(state, coedit_window=window)
    return sorted((min(u, v), max(u, v), data["time"]) for u, v, data in graph.temporal_edges(data=True))


def commit(email, files, when):
    return ((email, email.split("@")[1].split(".")[0]), files, when)


ALICE_THEN_BOB_30_MIN = [
    commit("alice@example.com", ["src/main.py"], "Mon Jan 1 12:00:00 2024 +0000"),
    commit("bob@example.com", ["src/main.py"], "Mon Jan 1 12:30:00 2024 +0000"),
]


def test_within_the_window_gives_an_edge():
    assert co_edits(ALICE_THEN_BOB_30_MIN, timedelta(hours=1)) == [
        ("alice@example.com", "bob@example.com", "2024-01-01T12:30:00+00:00")]


def test_outside_the_window_gives_no_edge_and_no_nodes():
    entries = [commit("alice@example.com", ["src/main.py"], "Mon Jan 1 12:00:00 2024 +0000"),
               commit("bob@example.com", ["src/main.py"], "Mon Jan 1 14:00:00 2024 +0000")]

    state = ProcessingState()
    state.parsed_change_log_entries = entries
    graph = extract_temporal_network_from_parsed_change_log_entries(state, coedit_window=timedelta(hours=1))

    assert list(graph.temporal_edges()) == []
    assert all(len(snapshot.nodes()) == 0 for snapshot in graph)  # no nodes without edges (README, Q7)


def test_the_boundary_is_included():
    assert co_edits(ALICE_THEN_BOB_30_MIN, timedelta(minutes=30)) != []
    assert co_edits(ALICE_THEN_BOB_30_MIN, timedelta(minutes=29)) == []


def test_offsets_are_compared_as_instants():
    # 13:00 at UTC+1 is 12:00 UTC: 30 minutes before Bob, not 30 minutes after
    entries = [commit("alice@example.com", ["f"], "Mon Jan 1 13:00:00 2024 +0100"),
               commit("bob@example.com", ["f"], "Mon Jan 1 12:30:00 2024 +0000")]
    assert len(co_edits(entries, timedelta(minutes=30))) == 1


def test_window_counts_from_the_latest_change_of_the_earlier_developer():
    # Alice changes f at 0:00 and 9:00; Bob at 10:00. Her latest change is 1 hour before.
    entries = [commit("alice@example.com", ["f"], "Mon Jan 1 00:00:00 2024 +0000"),
               commit("alice@example.com", ["f"], "Mon Jan 1 09:00:00 2024 +0000"),
               commit("bob@example.com", ["f"], "Mon Jan 1 10:00:00 2024 +0000")]
    assert len(co_edits(entries, timedelta(hours=1))) == 1


def test_without_a_window_nothing_changes():
    entries = [commit("alice@example.com", ["f"], "Mon Jan 1 00:00:00 2024 +0000"),
               commit("bob@example.com", ["f"], "Mon Jun 3 00:00:00 2024 +0000")]
    assert co_edits(entries) == co_edits(entries, timedelta(days=10_000)) != []
    assert co_edits(entries, timedelta(days=30)) == []


@pytest.mark.parametrize("text, expected", [
    ("30d", timedelta(days=30)), ("12h", timedelta(hours=12)), ("90m", timedelta(minutes=90)),
    ("3600s", timedelta(seconds=3600)), ("3600", timedelta(seconds=3600)),
])
def test_parse_duration(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["0", "0d", "-1d", "1w", "1.5h", "abc", ""])
def test_invalid_durations_are_rejected(text):
    with pytest.raises(ValueError):
        parse_duration(text)


# --- scrapLog ---------------------------------------------------------------------------------

LOG = PROJECT_ROOT / "test-data" / "TensorFlow" / "tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN"


def run(tmp_path, *args):
    return subprocess.run([sys.executable, str(PROJECT_ROOT / "scrapLog.py"), "-r", "t.IN",
                           "-t", "inter_individual_graph_weighted", *args],
                          cwd=tmp_path, capture_output=True, text=True, env=ENV, timeout=300)


@pytest.mark.parametrize("window, weight", [("5d", 2), ("53h", 1)])
def test_scraplog_coedit_window(tmp_path, window, weight):
    # akuegel last changed the shared files on 3 Jan 23:44; jreiffers changed them
    # 52h 4m 34s later (6 Jan) and 4d 6h 46m later (8 Jan), all at UTC-8.
    shutil.copy(LOG, tmp_path / "t.IN")

    result = run(tmp_path, "--coedit-window", window)

    assert result.returncode == 0, result.stdout + result.stderr
    g = nx.read_graphml(tmp_path / "t.WeightedNetwork.graphML")
    assert [w for _, _, w in g.edges(data="weight")] == [weight]
    assert json.loads(g.graph["scraplog_parameters"])["coedit_window"] == window


def test_scraplog_rejects_an_invalid_window(tmp_path):
    shutil.copy(LOG, tmp_path / "t.IN")

    result = run(tmp_path, "--coedit-window", "1w")

    assert result.returncode == 1
    assert "Invalid --coedit-window" in result.stdout + result.stderr
    assert not (tmp_path / "t.WeightedNetwork.graphML").exists()
