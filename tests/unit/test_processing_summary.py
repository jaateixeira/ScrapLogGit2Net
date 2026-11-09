"""
The processing summary must describe the network that was exported.

For temporal runs it used to report 0 nodes, 0 edges and 0 affiliations,
because it counted the static network, which is not built for that type.

Run with:
    pytest tests/unit/test_processing_summary.py -v
"""

import re
import subprocess
import sys
import zipfile
from pathlib import Path

import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG = PROJECT_ROOT / "test-data/TensorFlow/tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN"


def run_scraplog(tmp_path, network_type):
    out = tmp_path / f"{network_type}.graphml"
    result = subprocess.run(
        [sys.executable, "-m", "scraplog.scraplog", "-r", str(LOG),
         "-t", f"inter_individual_graph_{network_type}", "-o", str(out)],
        cwd=tmp_path, capture_output=True, text=True, check=True,
        env={"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": "", "COLUMNS": "200"},
    )
    summary = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    return summary, out


def summary_value(summary, label):
    match = re.search(rf"^{re.escape(label)}: (\d+)$", summary, re.M)
    assert match, f"'{label}' not in summary"
    return int(match.group(1))


def test_temporal_summary_matches_exported_network(tmp_path):
    summary, out = run_scraplog(tmp_path, "temporal")

    with zipfile.ZipFile(out) as archive:
        xml = tmp_path / "temporal.xml"
        xml.write_bytes(archive.read(archive.namelist()[0]))
    graph = nx.read_graphml(xml, force_multigraph=True)
    pairs = {frozenset((u, v)) for u, v in graph.edges()}

    assert graph.number_of_nodes() > 0
    assert summary_value(summary, "Network nodes (developers)") == graph.number_of_nodes()
    assert summary_value(summary, "Network edges (time-stamped co-edits)") == graph.number_of_edges()
    assert summary_value(summary, "Developer pairs that co-edited") == len(pairs)
    assert summary_value(summary, "Unique affiliations") > 0


def test_temporal_and_unweighted_summaries_agree(tmp_path):
    """Same developers, pairs and affiliations, whatever the network type."""
    temporal, _ = run_scraplog(tmp_path, "temporal")
    unweighted, _ = run_scraplog(tmp_path, "unweighted")

    assert summary_value(temporal, "Network nodes (developers)") == summary_value(unweighted, "Network nodes (developers)")
    assert summary_value(temporal, "Developer pairs that co-edited") == summary_value(unweighted, "Network edges (collaborations)")
    assert summary_value(temporal, "Unique affiliations") == summary_value(unweighted, "Unique affiliations")
