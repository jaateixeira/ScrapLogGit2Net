"""
report_nofo.py (formatFilterAndReport-nofo-GraphML.py) read only the e-mail and
affiliation node attributes, which a network of organizations (nofo) does not
have: every node showed as 'unknown', -f removed nothing, and -t removed every
node and crashed with a traceback. In a nofo network the node ID is the
organization.

Run with:
    pytest tests/unit/test_report_nofo.py -v
"""

import subprocess
import sys
from pathlib import Path

import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def write_nofo(path):
    """google-nvidia (5 co-edits), google-intel (2), google-tensorflow (7), nvidia-intel (1)."""
    g = nx.Graph()
    g.add_edge("google", "nvidia", weight=5)
    g.add_edge("google", "intel", weight=2)
    g.add_edge("google", "tensorflow", weight=7)
    g.add_edge("nvidia", "intel", weight=1)
    nx.write_graphml(g, path)


def write_nofi(path):
    g = nx.Graph()
    g.add_node("1", **{"e-mail": "alice@google.com", "affiliation": "google"})
    g.add_node("2", **{"e-mail": "bob@nvidia.com", "affiliation": "nvidia"})
    g.add_node("3", **{"e-mail": "carol@gmail.com", "affiliation": "gmail"})
    g.add_edge("1", "2")
    g.add_edge("2", "3")
    nx.write_graphml(g, path)


def run_report(tmp_path, graph_file, *args):
    return subprocess.run(
        [sys.executable, "-m", "scraplog.analysis.report_nofo", str(graph_file), *args],
        cwd=tmp_path, capture_output=True, text=True, env=ENV,
    )


def table_rows(stdout):
    """Ranked rows of the console tables as lists of cell texts (the statistics panel is skipped)."""
    rows = [[c.strip() for c in line.split("│")[1:-1]] for line in stdout.splitlines() if line.startswith("│")]
    return [row for row in rows if row and row[0].isdigit()]


def test_nofo_report_shows_organizations(tmp_path):
    graph = tmp_path / "net.nofo.graphML"
    write_nofo(graph)

    result = run_report(tmp_path, graph)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Most Connected Organizations" in result.stdout
    assert "unknown" not in result.stdout
    # rank, organization, degree, weighted degree, degree centrality; ties broken by weighted degree
    assert table_rows(result.stdout) == [
        ["1", "google", "3", "14", "1.0000"],
        ["2", "nvidia", "2", "6", "0.6667"],
        ["3", "intel", "2", "3", "0.6667"],
        ["4", "tensorflow", "1", "7", "0.3333"],
    ]
    assert (tmp_path / "net.nofo.xls").exists()


def test_nofo_filter_removes_generic_organizations(tmp_path):
    graph = tmp_path / "net.nofo.graphML"
    write_nofo(graph)

    result = run_report(tmp_path, graph, "-f")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Filtered out 1 nodes" in result.stdout
    assert [row[1] for row in table_rows(result.stdout)] == ["google", "nvidia", "intel"]


def test_nofo_top_firms_keeps_listed_organizations(tmp_path):
    graph = tmp_path / "net.nofo.graphML"
    write_nofo(graph)

    result = run_report(tmp_path, graph, "-t", "--top-firms", "google,nvidia")

    assert result.returncode == 0, result.stdout + result.stderr
    assert [row[1] for row in table_rows(result.stdout)] == ["google", "nvidia"]


def test_no_nodes_left_is_a_clear_error(tmp_path):
    graph = tmp_path / "net.nofo.graphML"
    write_nofo(graph)

    result = run_report(tmp_path, graph, "-t", "--top-firms", "nobody")

    assert result.returncode == 1
    assert "no nodes left after filtering" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr
    assert not (tmp_path / "net.nofo.xls").exists()


def test_nofi_report_still_uses_individuals(tmp_path):
    graph = tmp_path / "net.graphML"
    write_nofi(graph)

    result = run_report(tmp_path, graph, "-f")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Most Connected Individuals" in result.stdout
    assert "Filtered out 1 nodes" in result.stdout  # carol@gmail.com
    emails = [row[1] for row in table_rows(result.stdout) if "@" in row[1]]
    assert sorted(emails) == ["alice@google.com", "bob@nvidia.com"]
