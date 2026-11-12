"""
Three fixes:
- nofi visualizer, -a: configparser lower-cases the alias keys, so an
  affiliation with upper-case letters (e.g. NVIDIA) never matched its alias.
  Affiliations are now matched case-insensitively, like scrapLog's -a.
- nofo visualizer, -nc gray-color-to-others-not-in-topn-filter was accepted
  but not implemented (every node was gray, with an error per node). Now the
  N most central organizations keep their color (N from -tf, default 10) and
  the others are gray; ties in centrality are broken by name.
- Every tool has --version.

The nofi visualizer runs here in a subprocess with a stub tkinter module.

Run with:
    pytest tests/unit/test_alias_case_gray_others_version.py -v
"""

import subprocess
import sys
from pathlib import Path

import networkx as nx
import pytest

import scraplog
from scraplog.viz.nofo_visualizer import NetworkConfig, NetworkVisualizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def tk_stub(tmp_path):
    stub = tmp_path / "stub" / "tkinter"
    stub.mkdir(parents=True)
    (stub / "__init__.py").write_text("class Tk:\n    def withdraw(self): pass\n    def destroy(self): pass\n")
    (stub / "filedialog.py").write_text("def askopenfilename(**kw): return ''\n")
    return tmp_path / "stub"


def run(cwd, args, extra_path=""):
    env = {"PYTHONPATH": f"{extra_path}:{PROJECT_ROOT}" if extra_path else str(PROJECT_ROOT),
           "PATH": "", "COLUMNS": "200", "MPLBACKEND": "Agg"}
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True, env=env, timeout=120)


# --- alias case -----------------------------------------------------------------------------

APPLY_ALIASES = """
import networkx as nx
from scraplog.viz.nofi_visualizer import GraphMLVisualizer, VisualizationConfig
v = GraphMLVisualizer(VisualizationConfig(input_file="unused", affiliation_alias_in_config_file="aliases.ini"))
v.graph = nx.Graph()
for node, affiliation in [("1", "NVIDIA"), ("2", "nvidia"), ("3", "ds.MitsubishiElectric.co.jp"), ("4", "google")]:
    v.graph.add_node(node, affiliation=affiliation)
v.apply_affiliation_aliases()
print(sorted(v.graph.nodes(data="affiliation")))
"""


def test_aliases_match_affiliations_in_any_case(tmp_path):
    (tmp_path / "aliases.ini").write_text(
        "[aliases]\nnvidia = NVIDIA Corporation\nds.MitsubishiElectric.co.jp = Mitsubishi\n")

    result = run(tmp_path, ["-c", APPLY_ALIASES], extra_path=str(tk_stub(tmp_path)))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip().splitlines()[-1] == str([
        ("1", "NVIDIA Corporation"), ("2", "NVIDIA Corporation"), ("3", "Mitsubishi"), ("4", "google")])


# --- gray-color-to-others-not-in-topn-filter ------------------------------------------------

def star_visualizer(top_n):
    """hub is the most central; leaves a..d tie (equal centrality); e hangs off d."""
    config = NetworkConfig(input_file="unused", node_coloring_strategy="gray-color-to-others-not-in-topn-filter",
                           filter_by_n_top_central_firms_only=top_n)
    v = NetworkVisualizer(config)
    v.graph = nx.Graph([("hub", "a"), ("hub", "b"), ("hub", "c"), ("hub", "d")])
    v.known_org_node_colors = {}
    v.degree_centrality = {"hub": 0.8, "a": 0.2, "b": 0.2, "c": 0.2, "d": 0.2}
    return v


def colors_by_node(v):
    return dict(zip(v.graph.nodes(), v.get_node_colors()))


def test_top_n_keep_their_color_others_are_gray():
    colors = colors_by_node(star_visualizer(top_n=2))

    # hub, then a (the tie between a, b, c, d is broken by name)
    assert colors["hub"] != "gray" and colors["a"] != "gray"
    assert [colors[n] for n in ("b", "c", "d")] == ["gray", "gray", "gray"]


def test_without_tf_the_top_10_keep_their_color():
    colors = colors_by_node(star_visualizer(top_n=None))

    assert "gray" not in colors.values()  # 5 organizations, all within the top 10


def test_color_map_comes_first():
    v = star_visualizer(top_n=1)
    v.known_org_node_colors = {"d": "red"}

    assert colors_by_node(v)["d"] == "red"


# --- --version --------------------------------------------------------------------------------

TOOLS = ["scrapLog.py", "compare-set-nofi-GraphML.py", "compare-two-nofi-GraphML-metrics.py",
         "deanonymize_github_users.py", "formatFilterAndReport-nofi-GraphML.py",
         "formatFilterAndReport-nofo-GraphML.py", "nofi_graphml_network_visualizer.py",
         "nofo_graphml_network_visualizer.py", "scrap_repo_repositories_logs.py", "solo_contributors.py",
         "transform_nofi_2_nofo_graphml.py"]


@pytest.mark.parametrize("tool", TOOLS)
def test_every_tool_prints_its_version(tmp_path, tool):
    result = run(tmp_path, [str(PROJECT_ROOT / tool), "--version"], extra_path=str(tk_stub(tmp_path)))

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"{tool} (ScrapLogGit2Net) {scraplog.__version__}" in result.stdout


def test_pyproject_reads_the_version_from_the_package():
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert 'dynamic = ["version"]' in pyproject
    assert 'version = {attr = "scraplog._version.__version__"}' in pyproject
