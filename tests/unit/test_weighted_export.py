"""
The weighted network (-t inter_individual_graph_weighted) used to be written
with email node IDs and no node attributes, and with the weight as the edge
ID (so edge IDs repeated). transform_nofi_2_nofo_graphml.py then crashed with
a KeyError, because it reads the 'affiliation' attribute. It is now written
like the unweighted network (numeric IDs; e-mail, color and affiliation),
plus a 'weight' attribute on each edge.

Run with:
    pytest tests/unit/test_weighted_export.py -v
"""

import subprocess
import sys
from pathlib import Path

import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": ""}

# Alice and Bob co-edit a.py at two times (weight 2); Bob and Carol co-edit b.py once (weight 1).
GIT_LOG = """==Alice;alice@google.com;Mon Jan 1 10:00:00 2024 +0000==
a.py

==Bob;bob@nvidia.com;Tue Jan 2 10:00:00 2024 +0000==
a.py
b.py

==Alice;alice@google.com;Wed Jan 3 10:00:00 2024 +0000==
a.py

==Carol;carol@ibm.com;Thu Jan 4 10:00:00 2024 +0000==
b.py

"""


def run(tmp_path, module, *args):
    return subprocess.run([sys.executable, "-m", module, *args],
                          cwd=tmp_path, capture_output=True, text=True, env=ENV)


def build_weighted(tmp_path):
    (tmp_path / "project.IN").write_text(GIT_LOG)
    result = run(tmp_path, "scraplog.scraplog", "-r", "project.IN",
                 "-t", "inter_individual_graph_weighted", "-o", "w.graphML")
    assert result.returncode == 0, result.stdout + result.stderr
    return tmp_path / "w.graphML"


def test_weighted_output_has_node_attributes_and_weights(tmp_path):
    out = build_weighted(tmp_path)
    graph = nx.read_graphml(out)

    nodes = {data["e-mail"]: data for _, data in graph.nodes(data=True)}
    assert {email: data["affiliation"] for email, data in nodes.items()} == {
        "alice@google.com": "google", "bob@nvidia.com": "nvidia", "carol@ibm.com": "ibm"}

    email = {node: data["e-mail"] for node, data in graph.nodes(data=True)}
    weights = {frozenset((email[u], email[v])): data["weight"] for u, v, data in graph.edges(data=True)}
    assert weights == {frozenset(("alice@google.com", "bob@nvidia.com")): 2,
                       frozenset(("bob@nvidia.com", "carol@ibm.com")): 1}

    edge_ids = [line.split('id="')[1].split('"')[0] for line in out.read_text().splitlines() if "<edge " in line]
    assert len(edge_ids) == len(set(edge_ids)) == 2


def test_transformer_accepts_weighted_output(tmp_path):
    build_weighted(tmp_path)

    result = run(tmp_path, "scraplog.analysis.transform_nofi_to_nofo", "w.graphML", "-o", "nofo.graphML")

    assert result.returncode == 0, result.stdout + result.stderr
    nofo = nx.read_graphml(tmp_path / "nofo.graphML")
    # one tie per developer pair, as for unweighted input: the developer weights are not summed
    assert {frozenset((u, v)): d["weight"] for u, v, d in nofo.edges(data=True)} == {
        frozenset(("google", "nvidia")): 1, frozenset(("ibm", "nvidia")): 1}
