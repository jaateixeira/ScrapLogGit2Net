"""
Options that were accepted but did nothing are now either removed or made to work:
- nofi visualizer: -g removed; -ll upper_left/center_left/lower_left used to fall back
  to center right; -lt top10+others behaved like top10 (top10+1 is removed);
- nofi and nofo reports: -c removed (the color map was loaded but never used);
- batch miner: --years, --output-dir and --dry-run removed;
- compare-two-nofi-GraphML-metrics: --verbose now prints node and edge counts per file.

Run with:
    pytest tests/unit/test_option_cleanup.py -v
"""

import subprocess
import sys
import types
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200", "MPLBACKEND": "Agg"}


def run(tmp_path, module, *args):
    return subprocess.run([sys.executable, "-m", module, *args],
                          cwd=tmp_path, capture_output=True, text=True, env=ENV, timeout=120)


@pytest.fixture
def visualizer_module(monkeypatch):
    """Import the nofi visualizer with a stub tkinter (Tk is not installed everywhere)."""
    tkinter = types.ModuleType("tkinter")
    tkinter.filedialog = types.ModuleType("tkinter.filedialog")
    monkeypatch.setitem(sys.modules, "tkinter", tkinter)
    monkeypatch.setitem(sys.modules, "tkinter.filedialog", tkinter.filedialog)
    monkeypatch.delitem(sys.modules, "scraplog.viz.nofi_visualizer", raising=False)
    import scraplog.viz.nofi_visualizer as module
    return module


def legend_of(module, **config):
    """Draw the legend for 12 organizations: org00 has 12 developers, org01 11, ... org11 1."""
    vis = module.GraphMLVisualizer(module.VisualizationConfig(input_file="x.graphML", legend=True, **config))
    vis.filtered_graph = nx.Graph()
    vis.affiliation_counts = {}
    for i in range(12):
        org = f"org{i:02d}"
        vis.affiliation_counts[org] = 12 - i
        for d in range(12 - i):
            vis.filtered_graph.add_node(f"{org}-{d}", affiliation=org)
    fig, ax = plt.subplots()
    vis._add_legend(fig, ax)
    legend = ax.get_legend()
    labels = [t.get_text() for t in legend.get_texts()]
    location = legend._loc
    plt.close(fig)
    return labels, location


@pytest.mark.parametrize("choice,matplotlib_loc", [
    ("upper_left", 2), ("center_left", 6), ("lower_left", 3), ("center_right", 7),
])
def test_legend_locations(visualizer_module, choice, matplotlib_loc):
    _, location = legend_of(visualizer_module, legend_location=choice)
    assert location == matplotlib_loc  # matplotlib codes: 2 upper left, 3 lower left, 6 center left, 7 center right


def test_legend_top10_plus_others(visualizer_module):
    labels, _ = legend_of(visualizer_module, legend_type="top10+others", legend_extra_organizations=["org11", "org00"])

    # top 10, then org11 from -le (org00 is already listed, so it is not repeated), then the rest
    assert labels == [f"org{i:02d} ({12 - i})" for i in range(10)] + ["org11 (1)", "others (2)"]


def test_legend_top10_has_no_others_entry(visualizer_module):
    labels, _ = legend_of(visualizer_module, legend_type="top10")
    assert len(labels) == 10 and not any(label.startswith("others") for label in labels)


@pytest.mark.parametrize("module,args", [
    ("scraplog.viz.nofi_visualizer", ["-g", "token", "x.graphML"]),
    ("scraplog.viz.nofi_visualizer", ["-lt", "top10+1", "x.graphML"]),
    ("scraplog.analysis.report_nofi", ["-c", "colors.json", "x.graphML"]),
    ("scraplog.analysis.report_nofo", ["-c", "colors.json", "x.graphML"]),
    ("scraplog.tools.scrap_repo_logs", ["--dry-run", "."]),
    ("scraplog.tools.scrap_repo_logs", ["--years", "2020", "2021", "."]),
    ("scraplog.tools.scrap_repo_logs", ["--output-dir", "out", "."]),
])
def test_removed_options_are_rejected(tmp_path, module, args):
    stub = tmp_path / "stub" / "tkinter"
    stub.mkdir(parents=True)
    (stub / "__init__.py").write_text("")
    (stub / "filedialog.py").write_text("")
    result = subprocess.run([sys.executable, "-m", module, *args], cwd=tmp_path, capture_output=True, text=True,
                            env={**ENV, "PYTHONPATH": f"{tmp_path / 'stub'}:{PROJECT_ROOT}"}, timeout=120)

    assert result.returncode == 2  # argparse: unrecognized argument or invalid choice
    assert "unrecognized arguments" in result.stderr or "invalid choice" in result.stderr


def test_compare_two_verbose_prints_node_and_edge_counts(tmp_path):
    a = PROJECT_ROOT / "test-data/5-pentagon-with-star.graphML"
    b = PROJECT_ROOT / "test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML"

    quiet = run(tmp_path, "scraplog.analysis.compare_nofi_metrics", str(a), str(b), "--no-show")
    verbose = run(tmp_path, "scraplog.analysis.compare_nofi_metrics", str(a), str(b), "--no-show", "--verbose")

    assert quiet.returncode == verbose.returncode == 0, verbose.stdout + verbose.stderr
    assert "5-pentagon-with-star.graphML: 5 nodes, 10 edges" in verbose.stdout
    assert "NetworkFile.graphML: 2 nodes, 1 edges" in verbose.stdout
    assert "nodes," not in quiet.stdout
