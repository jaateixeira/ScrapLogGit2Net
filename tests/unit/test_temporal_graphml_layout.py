"""
The temporal network (written by networkx-temporal) was not valid GraphML: its
node IDs were e-mail addresses ('@' is not allowed in a GraphML ID) and its
edge IDs repeated ("0"). It is now laid out like the unweighted and weighted
files: numeric node IDs with e-mail, color and affiliation attributes, and
one edge per co-edit with its own ID (e0, e1, ...) and a 'time' attribute.

Run with:
    pytest tests/unit/test_temporal_graphml_layout.py -v
"""

import io
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import networkx as nx
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG = PROJECT_ROOT / "test-data" / "TensorFlow" / "tensorFlowGitLog-temporal-10-developers-coediting-the-same-files.IN"
SCHEMA = PROJECT_ROOT / "tests" / "acceptance-test-scripts" / "graphml-schema" / "graphml.xsd"
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def temporal_network(tmp_path, *extra):
    shutil.copy(LOG, tmp_path / "t.IN")
    result = subprocess.run([sys.executable, str(PROJECT_ROOT / "scrapLog.py"), "-r", "t.IN",
                             "-t", "inter_individual_graph_temporal", *extra],
                            cwd=tmp_path, capture_output=True, text=True, env=ENV, timeout=300)
    assert result.returncode == 0, result.stdout + result.stderr


def graphml_in(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
        (name,) = archive.namelist()
        return name, archive.read(name)


def test_temporal_graphml_is_valid(tmp_path):
    xmllint = shutil.which("xmllint")
    if xmllint is None:
        pytest.skip("xmllint is not installed")
    temporal_network(tmp_path)
    _, data = graphml_in(tmp_path / "t.temporal.graphml.zip")
    (tmp_path / "t.temporal.graphml").write_bytes(data)

    result = subprocess.run([xmllint, "--noout", "--schema", str(SCHEMA), str(tmp_path / "t.temporal.graphml")],
                            capture_output=True, text=True, timeout=60)

    assert result.returncode == 0, result.stdout + result.stderr


def test_temporal_layout_matches_the_other_network_types(tmp_path):
    temporal_network(tmp_path)
    name, data = graphml_in(tmp_path / "t.temporal.graphml.zip")
    g = nx.read_graphml(io.BytesIO(data), force_multigraph=True)

    assert name == "t.temporal.graphml"
    emails = [g.nodes[n]["e-mail"] for n in sorted(g.nodes, key=int)]
    assert list(g.nodes) == [str(i) for i in range(len(emails))]  # numeric IDs, in e-mail order
    assert emails == sorted(emails) and all("@" in e for e in emails)
    assert all(g.nodes[n]["affiliation"] and g.nodes[n]["color"] == "turquoise" for n in g.nodes)
    edge_ids = [key for _, _, key in g.edges(keys=True)]
    assert sorted(edge_ids) == sorted(f"e{i}" for i in range(len(edge_ids)))  # one ID per edge
    assert all(time for _, _, time in g.edges(data="time"))


def test_same_co_edits_as_the_edge_list(tmp_path):
    temporal_network(tmp_path)
    _, data = graphml_in(tmp_path / "t.temporal.graphml.zip")
    g = nx.read_graphml(io.BytesIO(data), force_multigraph=True)
    email = nx.get_node_attributes(g, "e-mail")

    counts = {}
    for u, v in g.edges():
        pair = tuple(sorted((email[u], email[v])))
        counts[pair] = counts.get(pair, 0) + 1
    rows = (tmp_path / "t.temporal.edges.csv").read_text().splitlines()[1:]
    assert counts == {(r.split(",")[0], r.split(",")[1]): int(r.split(",")[2]) for r in rows}


def test_output_name_without_zip_is_kept(tmp_path):
    temporal_network(tmp_path, "-o", "net.graphml")

    assert graphml_in(tmp_path / "net.graphml")[0] == "net.graphml"
