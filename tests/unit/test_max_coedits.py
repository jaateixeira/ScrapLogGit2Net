"""
--max-coedits N: the upper bound to --min-coedits. Developer pairs with more
than N time-stamped co-edits (their weight), counted after --coedit-window,
are removed with all their co-edits; kept pairs are unchanged. Default: no
upper limit, as before. A maximum below --min-coedits stops with exit code 1.

Run with:
    pytest tests/unit/test_max_coedits.py -v
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import networkx_temporal as tx
import pytest

from scraplog.networks.temporal import keep_pairs_by_coedit_count

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}

# a-b: 3 co-edits, b-c: 1, a-c: 2
NETWORK = tx.TemporalMultiGraph()
for u, v, day in [("a", "b", 1), ("b", "c", 2), ("b", "a", 3), ("a", "c", 4), ("c", "a", 5), ("a", "b", 6)]:
    NETWORK.add_edge(u, v, time=f"2024-01-0{day}T00:00:00+00:00")


def counts(network):
    result = {}
    for u, v, _ in network.temporal_edges(data=True):
        pair = (min(u, v), max(u, v))
        result[pair] = result.get(pair, 0) + 1
    return result


def test_pairs_above_the_maximum_are_dropped_with_all_their_co_edits():
    assert counts(keep_pairs_by_coedit_count(NETWORK, max_coedits=2)) == {("b", "c"): 1, ("a", "c"): 2}


def test_minimum_and_maximum_together():
    assert counts(keep_pairs_by_coedit_count(NETWORK, min_coedits=2, max_coedits=2)) == {("a", "c"): 2}


def test_no_maximum_keeps_everything():
    assert counts(keep_pairs_by_coedit_count(NETWORK)) == {("a", "b"): 3, ("b", "c"): 1, ("a", "c"): 2}


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


# The one pair (akuegel, jreiffers) has 2 co-edits, 1 of them within 3 days.
@pytest.mark.parametrize("args, rows", [
    (["--max-coedits", "2"], [["akuegel@google.com", "jreiffers@google.com", "2"]]),
    (["--max-coedits", "1"], []),
    (["--coedit-window", "3d", "--max-coedits", "1"], [["akuegel@google.com", "jreiffers@google.com", "1"]]),
])
def test_scraplog_max_coedits(tmp_path, args, rows):
    result = run(tmp_path, *args)

    assert result.returncode == 0, result.stdout + result.stderr
    assert csv_rows(tmp_path) == rows


def test_max_coedits_is_recorded(tmp_path):
    run(tmp_path, "--max-coedits", "5")
    header = (tmp_path / "t.temporal.edges.csv").read_text().splitlines()[2]
    assert json.loads(header.split(": ", 1)[1])["max_coedits"] == 5


@pytest.mark.parametrize("args", [["--max-coedits", "0"], ["--min-coedits", "3", "--max-coedits", "2"]])
def test_maximum_below_the_minimum_stops(tmp_path, args):
    result = run(tmp_path, *args)

    assert result.returncode == 1
    assert "Invalid --max-coedits" in result.stdout + result.stderr
    assert not (tmp_path / "t.temporal.graphml.zip").exists()
