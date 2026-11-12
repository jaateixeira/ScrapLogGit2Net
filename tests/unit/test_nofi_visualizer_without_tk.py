"""
The nofi visualizer imported tkinter at start-up, so without Tk it failed
before parsing any option, even --help or when a file was given. Tk is now
imported only for the file dialog (no infile given); without Tk that case
stops with a clear message and exit code 1.

Tk is made unavailable with a tkinter package that raises ImportError.

Run with:
    pytest tests/unit/test_nofi_visualizer_without_tk.py -v
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL = PROJECT_ROOT / "nofi_graphml_network_visualizer.py"
SAMPLE = PROJECT_ROOT / "test-data" / "5-pentagon-with-star.graphML"


def run_without_tk(tmp_path, *args):
    broken = tmp_path / "no_tk" / "tkinter"
    broken.mkdir(parents=True)
    (broken / "__init__.py").write_text("raise ImportError('libtk8.6.so: cannot open shared object file')\n")
    env = {"PYTHONPATH": f"{tmp_path / 'no_tk'}:{PROJECT_ROOT}", "PATH": "", "COLUMNS": "200",
           "MPLBACKEND": "Agg"}
    return subprocess.run([sys.executable, str(TOOL), *args], cwd=tmp_path, capture_output=True, text=True,
                          env=env, timeout=120)


def test_help_works_without_tk(tmp_path):
    result = run_without_tk(tmp_path, "--help")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "usage:" in result.stdout


def test_draws_a_given_file_without_tk(tmp_path):
    result = run_without_tk(tmp_path, str(SAMPLE))

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "5-pentagon-with-star_spring.png").is_file()
    assert (tmp_path / "5-pentagon-with-star_spring.pdf").is_file()


def test_file_dialog_without_tk_stops_with_a_clear_message(tmp_path):
    result = run_without_tk(tmp_path)

    assert result.returncode == 1
    output = " ".join((result.stdout + result.stderr).split())
    assert "needs Tk (tkinter)" in output
    assert "Traceback" not in output
