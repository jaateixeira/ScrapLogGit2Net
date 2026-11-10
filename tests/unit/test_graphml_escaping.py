"""
The GraphML writer used by scrapLog for unweighted and weighted networks wrote
attribute values as they were. A commit e-mail with &, < or > (e.g.
tom&jerry@acme.com) gave a file that is not well-formed XML: scrapLog still
exited 0, but no GraphML reader could open the file. Values are now escaped.

Run with:
    pytest tests/unit/test_graphml_escaping.py -v
"""

import subprocess
import sys
from pathlib import Path

import networkx as nx
import pytest

from scraplog.export.graphml_format import addNode, addEdgeWithAttributes

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": ""}

GIT_LOG = """==Tom & Jerry;tom&jerry@acme.com;Mon Jan 1 10:00:00 2024 +0000==
shared.py

==Bob;bob@nvidia.com;Tue Jan 2 10:00:00 2024 +0000==
shared.py

"""


def test_add_node_escapes_values():
    assert addNode(0, [(0, "a&b<c>@x.com")]) == '\t<node id="0">\n\t<data key="d0">a&amp;b&lt;c&gt;@x.com</data>\n\t</node>\n'


def test_add_edge_escapes_values():
    assert '<data key="d3">a&amp;b</data>' in addEdgeWithAttributes("e0", 0, 1, [(3, "a&b")])


@pytest.mark.parametrize("network_type", ["inter_individual_graph_unweighted", "inter_individual_graph_weighted"])
def test_scraplog_output_with_ampersand_email_is_readable(tmp_path, network_type):
    (tmp_path / "amp.IN").write_text(GIT_LOG)

    result = subprocess.run(
        [sys.executable, "-m", "scraplog.scraplog", "-r", "amp.IN", "-t", network_type, "-o", "out.graphml"],
        cwd=tmp_path, capture_output=True, text=True, env=ENV,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    graph = nx.read_graphml(tmp_path / "out.graphml")
    assert sorted((d["e-mail"], d["affiliation"]) for _, d in graph.nodes(data=True)) == [
        ("bob@nvidia.com", "nvidia"), ("tom&jerry@acme.com", "acme")]
