"""
scrapLog wrote the unweighted network twice to the same file: first the
network derived from the temporal network, then state.dev_to_dev_network,
which overwrote it. Both are the same graph (checked on the TensorFlow log
with -fe, -ff, -ie, -xe and -a), so the file is now written once and its
content is unchanged.

Run with:
    pytest tests/unit/test_single_write.py -v
"""

import subprocess
import sys
from pathlib import Path

import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = PROJECT_ROOT / "test-data/syntetic_data_msr2027/syntetic_data_msr2027.IN"


def test_unweighted_network_is_written_once(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "scraplog.scraplog", "-r", str(EXAMPLE), "-o", "out.graphml"],
        cwd=tmp_path, capture_output=True, text=True,
        env={"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": "", "COLUMNS": "200"},
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("Writing graphml file") == 1
    # the hand-computed network of the MSR 2027 example: 5 developers, 7 ties
    graph = nx.read_graphml(tmp_path / "out.graphml")
    assert (graph.number_of_nodes(), graph.number_of_edges()) == (5, 7)
