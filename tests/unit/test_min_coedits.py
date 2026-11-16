"""
--min-coedits N: keep only developer pairs with at least N time-stamped
co-edits (their weight), counted after --coedit-window. Pairs below the
minimum are removed with all their co-edits; kept pairs are unchanged.
Default 1: every pair, as before.

Replaces the skipped test of the planned 'min_interactions' feature
(docs/planned-network-definitions.md).

Run with:
    pytest tests/unit/test_min_coedits.py -v
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import networkx as nx
import networkx_temporal as tx
import pytest

from scraplog.networks.temporal import keep_pairs_by_coedit_count

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def coauthorship(*edges):
    network = tx.TemporalMultiGraph()
    for u, v, time in edges:
        network.add_edge(u, v, time=time)
    return network


# a-b: 3 co-edits, b-c: 1, a-c: 2 (written both ways round)
NETWORK = coauthorship(("a", "b", "2024-01-01T00:00:00+00:00"), ("b", "c", "2024-01-02T00:00:00+00:00"),
                       ("b", "a", "2024-01-03T00:00:00+00:00"), ("a", "c", "2024-01-04T00:00:00+00:00"),
                       ("c", "a", "2024-01-05T00:00:00+00:00"), ("a", "b", "2024-01-06T00:00:00+00:00"))


def pairs(network):
    return sorted((min(u, v), max(u, v), d["time"]) for u, v, d in network.temporal_edges(data=True))


def test_pairs_below_the_minimum_are_dropped_with_all_their_co_edits():
    assert pairs(keep_pairs_by_coedit_count(NETWORK, 2)) == [
        ("a", "b", "2024-01-01T00:00:00+00:00"), ("a", "b", "2024-01-03T00:00:00+00:00"),
        ("a", "b", "2024-01-06T00:00:00+00:00"),
        ("a", "c", "2024-01-04T00:00:00+00:00"), ("a", "c", "2024-01-05T00:00:00+00:00")]


def test_developers_left_without_co_edits_are_not_nodes():
    kept = keep_pairs_by_coedit_count(NETWORK, 3)
    assert {n for u, v, _ in kept.temporal_edges(data=True) for n in (u, v)} == {"a", "b"}
    assert all("c" not in snapshot.nodes() for snapshot in kept)


def test_minimum_one_keeps_everything():
    assert pairs(keep_pairs_by_coedit_count(NETWORK, 1)) == pairs(NETWORK)


# --- scrapLog ---------------------------------------------------------------------------------

LOG = PROJECT_ROOT / "test-data" / "TensorFlow" / "tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN"


def run(tmp_path, *args):
    shutil.copy(LOG, tmp_path / "t.IN")
    return subprocess.run([sys.executable, str(PROJECT_ROOT / "scrapLog.py"), "-r", "t.IN",
                           "-t", "inter_individual_graph_temporal", *args],
                          cwd=tmp_path, capture_output=True, text=True, env=ENV, timeout=300)


def csv_rows(tmp_path):
    lines = (tmp_path / "t.temporal.edges.csv").read_text().splitlines()
    return [line.split(",")[:3] for line in lines if not line.startswith("#")][1:]


# The one pair (akuegel, jreiffers) has 2 co-edits: on 6 Jan (52h after akuegel's change)
# and on 8 Jan (4 days later).
@pytest.mark.parametrize("args, rows", [
    ([], [["akuegel@google.com", "jreiffers@google.com", "2"]]),
    (["--min-coedits", "2"], [["akuegel@google.com", "jreiffers@google.com", "2"]]),
    (["--min-coedits", "3"], []),
    (["--coedit-window", "3d", "--min-coedits", "2"], []),  # counted after the window: 1 co-edit
    (["--coedit-window", "5d", "--min-coedits", "2"], [["akuegel@google.com", "jreiffers@google.com", "2"]]),
])
def test_scraplog_min_coedits(tmp_path, args, rows):
    result = run(tmp_path, *args)

    assert result.returncode == 0, result.stdout + result.stderr
    assert csv_rows(tmp_path) == rows


def test_min_coedits_is_recorded(tmp_path):
    run(tmp_path, "--min-coedits", "2")
    header = (tmp_path / "t.temporal.edges.csv").read_text().splitlines()[2]
    assert json.loads(header.split(": ", 1)[1])["min_coedits"] == 2


@pytest.mark.parametrize("value", ["0", "-1", "two"])
def test_invalid_min_coedits_stops(tmp_path, value):
    result = run(tmp_path, "--min-coedits", value)

    assert result.returncode != 0
    assert not (tmp_path / "t.temporal.graphml.zip").exists()
