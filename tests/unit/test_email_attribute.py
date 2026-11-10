"""
scrapLog writes each developer's address in the 'e-mail' node attribute, but:
- report_nofi.py read 'email', so the isolated-node list showed N/A and the
  Email column of the Excel 'Nodes' sheet was empty;
- deanonymize_github_users.py wrote the corrected address to a new 'email'
  attribute and left the noreply address in 'e-mail', where the other tools
  read it.

Run with:
    pytest tests/unit/test_email_attribute.py -v
"""

import subprocess
import sys
from pathlib import Path

import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def write_nofi(path):
    """Alice and Bob co-edit; Carol is an isolated node. Numeric IDs, as in scrapLog's GraphML
    files, so an address can only reach the report through the 'e-mail' attribute."""
    g = nx.Graph()
    g.add_node("0", **{"e-mail": "alice@google.com", "affiliation": "google"})
    g.add_node("1", **{"e-mail": "bob@nvidia.com", "affiliation": "nvidia"})
    g.add_node("2", **{"e-mail": "carol@ibm.com", "affiliation": "ibm"})
    g.add_edge("0", "1")
    nx.write_graphml(g, path)


def test_nofi_report_shows_emails(tmp_path):
    graph = tmp_path / "net.graphML"
    write_nofi(graph)

    result = subprocess.run(
        [sys.executable, "-m", "scraplog.analysis.report_nofi", str(graph)],
        cwd=tmp_path, capture_output=True, text=True, env=ENV,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "2: carol@ibm.com @ ibm" in result.stdout  # isolated node
    # xlwt stores these ASCII strings uncompressed (8-bit) in the workbook's string table
    workbook = (tmp_path / "net_report.xls").read_bytes()
    for email in ("alice@google.com", "bob@nvidia.com", "carol@ibm.com"):
        assert email.encode() in workbook


DEANONYMIZE = """
import networkx as nx
import scraplog.tools.deanonymize_github_users as d
d.deanonymize_github_user_with_cache_and_pygithub = lambda email, token, known, **kw: ("dev@nvidia.com", "NVIDIA")
d.iterate_graph("in.graphml", "out.graphml", "no-token")
g = nx.read_graphml("out.graphml")
print(sorted((n, dict(sorted(a.items()))) for n, a in g.nodes(data=True)))
"""


def test_deanonymizer_replaces_the_e_mail_attribute(tmp_path):
    g = nx.Graph()
    g.add_node("1", **{"e-mail": "123+dev@users.noreply.github.com", "affiliation": "users"})
    g.add_node("2", **{"e-mail": "alice@google.com", "affiliation": "google"})
    g.add_edge("1", "2")
    nx.write_graphml(g, tmp_path / "in.graphml")

    # a subprocess in tmp_path, so nothing the tool writes lands in the repository
    result = subprocess.run([sys.executable, "-c", DEANONYMIZE],
                            cwd=tmp_path, capture_output=True, text=True, env=ENV)

    assert result.returncode == 0, result.stdout + result.stderr
    out = nx.read_graphml(tmp_path / "out.graphml")
    assert dict(out.nodes["1"]) == {"e-mail": "dev@nvidia.com", "affiliation": "nvidia"}
    assert dict(out.nodes["2"]) == {"e-mail": "alice@google.com", "affiliation": "google"}
