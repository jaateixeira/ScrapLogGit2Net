"""
-tntr / --temporal-network-time-resolution: only 1 second is implemented.

The option used to be accepted and silently ignored, so `-tntr 86400` gave the
same network as the default. Any other value must now stop with an error.

Run with:
    pytest tests/unit/test_tntr_option.py -v
"""

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SMALL_LOG = PROJECT_ROOT / "test-data/TensorFlow/tensorFlowGitLog-temporal-2-developers-3-commits-same-file.IN"


def run_scraplog(tmp_path, *extra_args):
    out = tmp_path / "out.temporal.graphml.zip"
    result = subprocess.run(
        [sys.executable, "-m", "scraplog.scraplog", "-r", str(SMALL_LOG),
         "-t", "inter_individual_graph_temporal", "-o", str(out), *extra_args],
        cwd=tmp_path, capture_output=True, text=True,
        env={"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": "", "COLUMNS": "200"},
    )
    return result, out


@pytest.mark.parametrize("resolution", ["86400", "60", "0"])
def test_unsupported_resolution_stops_with_error(tmp_path, resolution):
    result, out = run_scraplog(tmp_path, "-tntr", resolution)

    assert result.returncode == 1
    assert "not implemented yet" in result.stdout + result.stderr
    assert not out.exists()


def test_resolution_one_second_works(tmp_path):
    result, out = run_scraplog(tmp_path, "-tntr", "1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()


def test_default_resolution_works(tmp_path):
    result, out = run_scraplog(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()
