"""
With -ns centrality-score, both visualizers sized nodes by degree centrality
only, so a node with no edges got size 0 and was not drawn visibly. Sizes now
have a minimum, MIN_NODE_SIZE (10); larger sizes are unchanged.

The nofi visualizer runs in a subprocess with a stub tkinter module (as in
test_alias_case_gray_others_version.py).

Run with:
    pytest tests/unit/test_min_node_size.py -v
"""

import json
import subprocess
import sys
from pathlib import Path

import networkx as nx

from scraplog.viz.nofo_visualizer import NetworkConfig, NetworkVisualizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_nofo_isolated_node_gets_the_minimum_size():
    v = NetworkVisualizer(NetworkConfig(input_file="unused", node_sizing_strategy="centrality-score"))
    v.graph = nx.Graph([("a", "b"), ("b", "c")])
    v.graph.add_node("alone")
    v.degree_centrality = nx.degree_centrality(v.graph)

    sizes = dict(zip(v.graph.nodes(), v.get_node_sizes()))

    assert sizes["alone"] == 10
    assert sizes["b"] == 2 / 3 * 2000  # unchanged above the minimum
    assert sizes["a"] == 1 / 3 * 2000


NOFI_SIZES = """
import networkx as nx
import json
from scraplog.viz.nofi_visualizer import GraphMLVisualizer, VisualizationConfig
v = GraphMLVisualizer(VisualizationConfig(input_file="unused", node_sizing_strategy="centrality-score"))
v.filtered_graph = nx.Graph([("a", "b"), ("b", "c")])
v.filtered_graph.add_node("alone")
v.degree_centrality = nx.degree_centrality(v.filtered_graph)
print(json.dumps(dict(zip(v.filtered_graph.nodes(), v.get_node_sizes()))))
"""


def test_nofi_isolated_node_gets_the_minimum_size(tmp_path):
    stub = tmp_path / "stub" / "tkinter"
    stub.mkdir(parents=True)
    (stub / "__init__.py").write_text("")
    (stub / "filedialog.py").write_text("")
    env = {"PYTHONPATH": f"{tmp_path / 'stub'}:{PROJECT_ROOT}", "PATH": "", "MPLBACKEND": "Agg"}

    result = subprocess.run([sys.executable, "-c", NOFI_SIZES], cwd=tmp_path, capture_output=True, text=True,
                            env=env, timeout=120)

    assert result.returncode == 0, result.stdout + result.stderr
    sizes = json.loads(result.stdout.strip().splitlines()[-1])
    assert sizes["alone"] == 10
    assert sizes["b"] == 2 / 3 * 100  # unchanged above the minimum
    assert sizes["a"] == 1 / 3 * 100
