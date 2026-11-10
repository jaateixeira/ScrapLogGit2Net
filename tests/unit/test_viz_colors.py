"""
The nofi and nofo visualizers gave organizations without a color in the
color map a random color (random.random()), and the nofi visualizer used an
unseeded spring layout, so two runs on the same input gave different images.
Colors now come from the organization name (scraplog/viz/colors.py), the
spring layout uses --seed (default 42) and the PDF has no creation date, so
the same input gives byte-identical PNG and PDF files.

The nofi visualizer imports tkinter, which is not installed everywhere
(e.g. CI), so it runs here with a stub tkinter module.

Run with:
    pytest tests/unit/test_viz_colors.py -v
"""

import shutil
import subprocess
import sys
from pathlib import Path

from scraplog.viz.colors import organization_color

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOFI_GRAPH = PROJECT_ROOT / "test-data/5-pentagon-with-star.graphML"
NOFO_GRAPH = PROJECT_ROOT / "test-data/5-pentagon-with-star-transformed-to-nofo.graphML"


def run(cwd, module, *args, extra_path=""):
    env = {"PYTHONPATH": f"{extra_path}:{PROJECT_ROOT}" if extra_path else str(PROJECT_ROOT),
           "PATH": "", "COLUMNS": "200", "MPLBACKEND": "Agg"}
    return subprocess.run([sys.executable, "-m", module, *args],
                          cwd=cwd, capture_output=True, text=True, env=env, timeout=180)


def images(directory):
    return {p.name: p.read_bytes() for p in sorted(directory.iterdir()) if p.suffix in (".png", ".pdf")}


def test_organization_color_depends_only_on_the_name():
    assert organization_color("google") == organization_color("google")
    assert organization_color("google") != organization_color("microsoft")
    assert all(0.0 <= c <= 1.0 for c in organization_color("google"))
    # kept away from gray, which means "others" in the figures
    r, g, b = organization_color("google")
    assert max(r, g, b) - min(r, g, b) > 0.2


def test_nofi_visualizer_gives_the_same_images_twice(tmp_path):
    stub = tmp_path / "stub" / "tkinter"
    stub.mkdir(parents=True)
    (stub / "__init__.py").write_text("class Tk:\n    def withdraw(self): pass\n    def destroy(self): pass\n")
    (stub / "filedialog.py").write_text("def askopenfilename(**kw): return ''\n")

    outputs = []
    for run_dir in ("first", "second"):
        work = tmp_path / run_dir
        work.mkdir()
        shutil.copy(NOFI_GRAPH, work)
        result = run(work, "scraplog.viz.nofi_visualizer", NOFI_GRAPH.name, "-l",
                     extra_path=str(tmp_path / "stub"))
        assert result.returncode == 0, result.stdout + result.stderr
        outputs.append(images(work))

    assert sorted(outputs[0]) == ["5-pentagon-with-star_spring.pdf", "5-pentagon-with-star_spring.png"]
    assert outputs[0] == outputs[1]


def test_nofo_visualizer_gives_the_same_images_twice(tmp_path):
    outputs = []
    for run_dir in ("first", "second"):
        work = tmp_path / run_dir
        work.mkdir()
        shutil.copy(NOFO_GRAPH, work)
        result = run(work, "scraplog.viz.nofo_visualizer", str(work / NOFO_GRAPH.name), "-l")
        assert result.returncode == 0, result.stdout + result.stderr
        outputs.append(images(work))

    assert len(outputs[0]) == 2
    assert outputs[0] == outputs[1]
