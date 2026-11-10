"""
Several fatal errors ended the program with sys.exit() or exit(), that is with
exit code 0, so scripts could not tell a failed run from a good one:
- scrapLog.py on a log without co-edits (no network can be built);
- scrapLog.py with an -o name that does not end in .graphml;
- scrap_repo_logs.py on a folder that is not a git repository.
They now exit with code 1.

Run with:
    pytest tests/unit/test_exit_codes.py -v
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DATA = PROJECT_ROOT / "test-data/TensorFlow"
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": os.environ.get("PATH", "")}


def run(tmp_path, module, *args):
    return subprocess.run([sys.executable, "-m", module, *args],
                          cwd=tmp_path, capture_output=True, text=True, env=ENV, timeout=120)


def test_scraplog_without_co_edits_exits_1(tmp_path):
    result = run(tmp_path, "scraplog.scraplog", "-r", str(TEST_DATA / "tensorFlowGitLog-3-commits-0-edges.IN"))

    assert "input did not led to the creation of a valid network" in result.stdout
    assert result.returncode == 1


def test_scraplog_output_name_without_graphml_exits_1(tmp_path):
    result = run(tmp_path, "scraplog.scraplog", "-r", str(TEST_DATA / "tensorFlowGitLog-3-commits-1-edge.IN"),
                 "-o", "out.txt")

    assert "outfilename must finish with .graphml" in result.stdout
    assert result.returncode == 1
    assert not (tmp_path / "out.txt").exists()


def test_batch_miner_on_a_folder_that_is_not_a_repository_exits_1(tmp_path):
    (tmp_path / "not-a-repo").mkdir()

    result = run(tmp_path, "scraplog.tools.scrap_repo_logs", "not-a-repo")

    assert "Not a git repository" in result.stdout + result.stderr
    assert result.returncode == 1
