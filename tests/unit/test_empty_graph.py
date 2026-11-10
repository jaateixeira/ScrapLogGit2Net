"""
"An empty graph counts as no graph": checks like `if not self.graph` are also
true for a graph with no nodes. When the filters removed every node:
- nofi_graphml_network_visualizer.py skipped its "Graph is empty after
  filtering!" check, printed "Visualization completed successfully!" and
  exited 0;
- formatFilterAndReport-nofi-GraphML.py crashed with a traceback and the
  message "No graph data to export".
Both now stop with a clear error and exit code 1.

The visualizer imports tkinter, which is not installed everywhere (e.g. CI),
so it runs here with a stub tkinter module.

Run with:
    pytest tests/unit/test_empty_graph.py -v
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOFI_GRAPH = PROJECT_ROOT / "test-data/5-pentagon-with-star.graphML"


def run(tmp_path, module, *args, extra_path=""):
    env = {"PYTHONPATH": f"{extra_path}:{PROJECT_ROOT}" if extra_path else str(PROJECT_ROOT),
           "PATH": "", "COLUMNS": "200", "MPLBACKEND": "Agg"}
    return subprocess.run([sys.executable, "-m", module, *args],
                          cwd=tmp_path, capture_output=True, text=True, env=env, timeout=120)


def test_nofi_report_with_no_nodes_left_is_a_clear_error(tmp_path):
    result = run(tmp_path, "scraplog.analysis.report_nofi", str(NOFI_GRAPH), "-oo", "nosuch")

    assert result.returncode == 1
    assert "no nodes left after filtering" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr
    assert not list(tmp_path.glob("*.xls"))


def test_nofi_visualizer_with_no_nodes_left_exits_1(tmp_path):
    stub = tmp_path / "stub" / "tkinter"
    stub.mkdir(parents=True)
    (stub / "__init__.py").write_text("class Tk:\n    def withdraw(self): pass\n    def destroy(self): pass\n")
    (stub / "filedialog.py").write_text("def askopenfilename(**kw): return ''\n")
    work = tmp_path / "work"
    work.mkdir()
    shutil.copy(NOFI_GRAPH, work)

    result = run(work, "scraplog.viz.nofi_visualizer", NOFI_GRAPH.name, "-oo", "nosuch",
                 extra_path=str(tmp_path / "stub"))

    assert result.returncode == 1, result.stdout + result.stderr
    assert "Graph is empty after filtering!" in result.stdout
    assert "completed successfully" not in result.stdout
    assert sorted(p.name for p in work.iterdir()) == [NOFI_GRAPH.name]  # no image written
