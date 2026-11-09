"""
solo_contributors.py used to crash after printing its summary: main() read
args.list_developers, but there was no --list-developers option, so
--list-files and --csv never ran.

Run with:
    pytest tests/unit/test_solo_contributors.py -v
"""

import csv
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG = PROJECT_ROOT / "test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN"
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def run_solo(tmp_path, *extra_args):
    log = tmp_path / "tf.IN"  # a copy: --csv writes next to the log file
    shutil.copy(LOG, log)
    result = subprocess.run(
        [sys.executable, "-m", "scraplog.analysis.solo_contributors", "--log", str(log), *extra_args],
        cwd=tmp_path, capture_output=True, text=True, env=ENV,
    )
    return result, log


def test_runs_without_options(tmp_path):
    result, _ = run_solo(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "AttributeError" not in result.stderr


def test_all_listings_and_csv(tmp_path):
    result, log = run_solo(tmp_path, "--project", "TensorFlow", "--list-developers", "--list-files", "--csv")

    assert result.returncode == 0, result.stderr
    assert "Solo-only developers [" in result.stdout

    summary = tmp_path / "tf_solo_summary.csv"
    files = tmp_path / "tf_solo_files.csv"
    assert summary.exists() and files.exists()
    with open(summary, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and all(row["project"] == "TensorFlow" for row in rows)
