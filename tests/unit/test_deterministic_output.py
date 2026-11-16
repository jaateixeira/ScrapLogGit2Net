"""
The same input must give byte-identical output (see CLAUDE.md).

Graph iteration order follows insertion order, and insertion order used to
come from iterating sets of strings, whose order changes between Python runs
(hash randomization). These tests pin the order down.

Run with:
    pytest tests/unit/test_deterministic_output.py -v
"""

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import networkx as nx

from scraplog.export import log_data as export_log_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EDGES = [
    ("zoe@b.org", "adam@a.com"),
    ("mia@c.net", "zoe@b.org"),
    ("adam@a.com", "mia@c.net"),
    ("bob@a.com", "zoe@b.org"),
]


def build_graph(edges):
    graph = nx.Graph()
    graph.add_edges_from(edges)
    for node in graph:
        graph.nodes[node]["affiliation"] = node.split("@")[1].split(".")[0]
    return graph


def test_graphml_export_does_not_depend_on_insertion_order(tmp_path):
    forward = tmp_path / "forward.graphml"
    backward = tmp_path / "backward.graphml"

    export_log_data.create_graphml_file(build_graph(EDGES), forward, verbose=False)
    reversed_edges = [(v, u) for u, v in reversed(EDGES)]
    export_log_data.create_graphml_file(build_graph(reversed_edges), backward, verbose=False)

    assert forward.read_bytes() == backward.read_bytes()


def test_graphml_export_sorts_nodes_and_edges(tmp_path):
    out = tmp_path / "network.graphml"
    export_log_data.create_graphml_file(build_graph(EDGES), out, verbose=False)

    graph = nx.read_graphml(out)
    emails = [graph.nodes[n]["e-mail"] for n in sorted(graph.nodes, key=int)]
    assert emails == sorted({email for edge in EDGES for email in edge})

    text = out.read_text()
    edge_lines = [line.strip() for line in text.splitlines() if "<edge " in line]
    pairs = [(int(line.split('source="')[1].split('"')[0]), int(line.split('target="')[1].split('"')[0]))
             for line in edge_lines]
    assert all(source < target for source, target in pairs)
    assert pairs == sorted(pairs)


def test_temporal_zip_has_a_fixed_date(tmp_path):
    # Zip entries record when they were written; a fixed date keeps the bytes identical
    network = nx.MultiGraph()
    network.add_edge("a@x.org", "b@x.org", time="2024-01-02T03:04:05+00:00")
    nx.set_node_attributes(network, "x", "affiliation")
    archives = []
    for i in range(2):
        path = tmp_path / f"run{i}" / "net.temporal.graphml.zip"
        path.parent.mkdir()
        export_log_data.write_temporal_graphml_zip(network, path)
        archives.append(path)

    assert archives[0].read_bytes() == archives[1].read_bytes()
    with zipfile.ZipFile(archives[0]) as archive:
        assert archive.namelist() == ["net.temporal.graphml"]
        assert archive.infolist()[0].date_time == (1980, 1, 1, 0, 0, 0)


TEMPORAL_EDGES_SCRIPT = """
import json
from scraplog.core.models import ProcessingState
from scraplog.networks.temporal import extract_temporal_network_from_parsed_change_log_entries

# 12 developers committing to overlapping files, so files gather several
# earlier contributors (a single shared file is not enough to expose the bug)
state = ProcessingState()
state.parsed_change_log_entries = [
    ((f"dev{(i * 7) % 12}@x.com", "x"), [f"f{i % 4}.py", f"f{(i * 3) % 5}.py"],
     f"Mon Jan {i + 1} 12:00:00 2024 +0000")
    for i in range(24)
]
graph = extract_temporal_network_from_parsed_change_log_entries(state)
print(json.dumps([[u, v, d["time"], d["file"]] for u, v, d in graph.temporal_edges(data=True)]))
"""


def temporal_edges_with_hash_seed(seed):
    env = {**os.environ, "PYTHONHASHSEED": str(seed)}
    result = subprocess.run(
        [sys.executable, "-c", TEMPORAL_EDGES_SCRIPT],
        cwd=PROJECT_ROOT, env=env, capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_temporal_edge_order_does_not_depend_on_hash_seed():
    """Before the fix, earlier contributors were iterated from a set, so the
    edge order changed with PYTHONHASHSEED."""
    edges_by_seed = [temporal_edges_with_hash_seed(seed) for seed in (1, 2, 3)]

    assert len(edges_by_seed[0]) == 157
    assert edges_by_seed[0] == edges_by_seed[1] == edges_by_seed[2]
