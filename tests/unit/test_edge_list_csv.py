"""
scrapLog had no edge-list export. Every run now also writes <output>.edges.csv:
source, target (e-mails, source < target), weight (number of time-stamped
co-edits, the weight of the weighted network), first_ts, last_ts (as in the
log) and first_ts_utc, last_ts_utc (converted to UTC).

Run with:
    pytest tests/unit/test_edge_list_csv.py -v
"""

import csv
import shutil
import subprocess
import sys
from pathlib import Path

import networkx as nx
import pytest

from scraplog.export.edge_list import edge_list_path, edge_list_rows

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DATA = PROJECT_ROOT / "test-data"
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}

HEADER = "source,target,weight,first_ts,last_ts,first_ts_utc,last_ts_utc\n"


def scraplog(cwd, *args):
    result = subprocess.run([sys.executable, str(PROJECT_ROOT / "scrapLog.py"), *args], cwd=cwd,
                            capture_output=True, text=True, env=ENV, timeout=300)
    assert result.returncode == 0, result.stdout + result.stderr


# --- the rows -------------------------------------------------------------------------------

def test_first_and_last_are_chosen_by_instant_not_by_text():
    rows = edge_list_rows([
        ("b@x.org", "a@x.org", "2024-01-01T05:00:00+00:00"),  # 05:00 UTC
        ("a@x.org", "b@x.org", "2024-01-01T09:00:00+05:00"),  # 04:00 UTC: earlier, though its text sorts later
        ("a@x.org", "b@x.org", "2024-01-01T09:00:00+05:00"),  # the same co-edit again: counted once
    ])

    assert rows == [("a@x.org", "b@x.org", 2,
                     "2024-01-01T09:00:00+05:00", "2024-01-01T05:00:00+00:00",
                     "2024-01-01T04:00:00+00:00", "2024-01-01T05:00:00+00:00")]


def test_only_the_edges_of_the_network_are_listed():
    coedits = [("a", "b", "2024-01-01T00:00:00+00:00"), ("b", "c", "2024-01-02T00:00:00+00:00")]

    assert [row[:2] for row in edge_list_rows(coedits, nx.Graph([("b", "a")]))] == [("a", "b")]
    with pytest.raises(ValueError, match="no time-stamped co-edit"):
        edge_list_rows(coedits, nx.Graph([("a", "c")]))


@pytest.mark.parametrize("network_file, csv_file", [
    ("t.NetworkFile.graphML", "t.NetworkFile.edges.csv"),
    ("out/t.WeightedNetwork.graphML", "out/t.WeightedNetwork.edges.csv"),
    ("t.temporal.graphml.zip", "t.temporal.edges.csv"),
    ("my.graphml", "my.edges.csv"),
])
def test_csv_file_name(network_file, csv_file):
    assert edge_list_path(network_file) == Path(csv_file)


# --- scrapLog ---------------------------------------------------------------------------------

# Hand-checked against the log: jreiffers@google.com co-edited akuegel@google.com's files in
# two commits, on 6 and 8 January 2024 at UTC-8.
THREE_DEVELOPERS = HEADER + (
    "akuegel@google.com,jreiffers@google.com,2,"
    "2024-01-06T04:03:16-08:00,2024-01-08T06:30:42-08:00,"
    "2024-01-06T12:03:16+00:00,2024-01-08T14:30:42+00:00\n")


@pytest.mark.parametrize("network_type, csv_file", [
    ("inter_individual_graph_unweighted", "t.NetworkFile.edges.csv"),
    ("inter_individual_graph_weighted", "t.WeightedNetwork.edges.csv"),
    ("inter_individual_graph_temporal", "t.temporal.edges.csv"),
])
def test_scraplog_writes_the_edge_list_next_to_the_network(tmp_path, network_type, csv_file):
    shutil.copy(TEST_DATA / "TensorFlow" / "tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN",
                tmp_path / "t.IN")

    scraplog(tmp_path, "-r", "t.IN", "-t", network_type)
    first = (tmp_path / csv_file).read_bytes()
    scraplog(tmp_path, "-r", "t.IN", "-t", network_type)

    assert (tmp_path / csv_file).read_text() == THREE_DEVELOPERS
    assert (tmp_path / csv_file).read_bytes() == first  # byte-identical


def test_weights_and_pairs_match_the_weighted_network(tmp_path):
    shutil.copy(TEST_DATA / "syntetic_data_msr2027" / "syntetic_data_msr2027.IN", tmp_path / "s.IN")

    scraplog(tmp_path, "-r", "s.IN", "-t", "inter_individual_graph_weighted")

    g = nx.read_graphml(tmp_path / "s.WeightedNetwork.graphML")
    email = nx.get_node_attributes(g, "e-mail")
    weights = {tuple(sorted((email[u], email[v]))): w for u, v, w in g.edges(data="weight")}
    with open(tmp_path / "s.WeightedNetwork.edges.csv", newline="") as f:
        rows = {(r["source"], r["target"]): int(r["weight"]) for r in csv.DictReader(f)}
    assert rows == weights
    assert len(rows) == g.number_of_edges() > 0


def test_filtered_developers_are_not_in_the_edge_list(tmp_path):
    shutil.copy(TEST_DATA / "TensorFlow" / "tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN",
                tmp_path / "t.IN")
    (tmp_path / "filter.txt").write_text("jreiffers@google.com\n")

    scraplog(tmp_path, "-r", "t.IN", "-t", "inter_individual_graph_temporal", "-fe", "filter.txt")

    assert "jreiffers@google.com" not in (tmp_path / "t.temporal.edges.csv").read_text()
