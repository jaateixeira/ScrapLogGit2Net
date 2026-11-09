"""
-l / --load and -s / --save.

-l used to be accepted and silently ignored (the raw log given with -r was
parsed instead); loading is not implemented, so it now stops with an error.
-s failed for a plain file name (os.makedirs('') raised, and the error was
reported as "Input file not found").

Run with:
    pytest tests/unit/test_load_save_options.py -v
"""

import pickle
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG = PROJECT_ROOT / "test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.IN"
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": "", "COLUMNS": "200"}


def run_scraplog(tmp_path, *extra_args):
    out = tmp_path / "out.graphml"
    result = subprocess.run(
        [sys.executable, "-m", "scraplog.scraplog", "-r", str(LOG), "-o", str(out), *extra_args],
        cwd=tmp_path, capture_output=True, text=True, env=ENV,
    )
    return result, out


def test_load_stops_with_error(tmp_path):
    result, out = run_scraplog(tmp_path, "-l", str(tmp_path / "saved.pkl"))

    assert result.returncode == 1
    assert "not implemented yet" in result.stdout + result.stderr
    assert not out.exists()


@pytest.mark.parametrize("save_name", ["parsed.pkl", "subfolder/parsed.pkl"])
def test_save_writes_parsed_change_log(tmp_path, save_name):
    """A plain file name (relative to the working directory) used to fail."""
    result, out = run_scraplog(tmp_path, "-s", save_name)

    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()

    with open(tmp_path / save_name, "rb") as saved:  # our own file, written just above
        entries = pickle.load(saved)
    assert len(entries) == 3  # the log has 3 commits
    (email, affiliation), files, timestamp = entries[0]
    assert "@" in email and files and timestamp
