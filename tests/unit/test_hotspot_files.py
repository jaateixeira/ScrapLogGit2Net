"""
Ignoring hotspot files (scraplog/hotspots.py):
    --ignore-top-hotspot-files K               the K files (0-20) changed by the most developers
    --ignore-files-with-more-than-developers N files changed by more than N developers
The files are removed from every commit before any network is built, and listed
in <output>.ignored-files.csv.

Run with:
    pytest tests/unit/test_hotspot_files.py -v
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scraplog.hotspots import developers_per_file, drop_files, select_hotspot_files

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = {"PYTHONPATH": str(PROJECT_ROOT), "PATH": "", "COLUMNS": "200"}


def commit(email, files):
    return ((email, "x"), files, "Mon Jan 1 00:00:00 2024 +0000")


ENTRIES = [commit("a@x.org", ["BUILD", "a.py", "z.py"]), commit("b@x.org", ["BUILD", "z.py"]),
           commit("c@x.org", ["BUILD", "a.py"]), commit("a@x.org", ["BUILD"])]  # a changes BUILD twice


def test_developers_are_counted_once_per_file():
    assert developers_per_file(ENTRIES) == {"BUILD": 3, "a.py": 2, "z.py": 2}


def test_top_k_breaks_ties_by_path():
    counts = developers_per_file(ENTRIES)
    assert select_hotspot_files(counts, top=2) == [("BUILD", 3, "top"), ("a.py", 2, "top")]
    assert select_hotspot_files(counts, top=20) == [("BUILD", 3, "top"), ("a.py", 2, "top"), ("z.py", 2, "top")]
    assert select_hotspot_files(counts, top=0) == []


def test_more_than_n_developers():
    counts = developers_per_file(ENTRIES)
    assert select_hotspot_files(counts, max_developers=2) == [("BUILD", 3, "more_than_max")]
    assert select_hotspot_files(counts, max_developers=3) == []


def test_both_options_together():
    assert select_hotspot_files(developers_per_file(ENTRIES), top=1, max_developers=1) == [
        ("BUILD", 3, "top+more_than_max"), ("a.py", 2, "more_than_max"), ("z.py", 2, "more_than_max")]


def test_files_are_removed_from_every_commit():
    assert [files for _, files, _ in drop_files(ENTRIES, ["BUILD"])] == [["a.py", "z.py"], ["z.py"], ["a.py"], []]


# --- scrapLog ---------------------------------------------------------------------------------

LOG = PROJECT_ROOT / "test-data" / "TensorFlow" / "tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN"
TEN = PROJECT_ROOT / "test-data" / "TensorFlow" / "tensorFlowGitLog-temporal-10-developers-coediting-the-same-files.IN"


def run(tmp_path, log, *args, name="t"):
    shutil.copy(log, tmp_path / f"{name}.IN")
    return subprocess.run([sys.executable, str(PROJECT_ROOT / "scrapLog.py"), "-r", f"{name}.IN",
                           "-t", "inter_individual_graph_temporal", *args],
                          cwd=tmp_path, capture_output=True, text=True, env=ENV, timeout=300)


def data_lines(path):
    return [line for line in path.read_text().splitlines() if not line.startswith("#")]


# Only fusions.cc and scatter.cc have two developers (akuegel, jreiffers); fusions.cc sorts first.
@pytest.mark.parametrize("args, ignored, pairs", [
    (["--ignore-top-hotspot-files", "1"],
     ["third_party/xla/xla/service/gpu/fusions/fusions.cc,2,top"], 1),
    (["--ignore-top-hotspot-files", "2"],
     ["third_party/xla/xla/service/gpu/fusions/fusions.cc,2,top",
      "third_party/xla/xla/service/gpu/fusions/scatter.cc,2,top"], 0),
    (["--ignore-files-with-more-than-developers", "1"],
     ["third_party/xla/xla/service/gpu/fusions/fusions.cc,2,more_than_max",
      "third_party/xla/xla/service/gpu/fusions/scatter.cc,2,more_than_max"], 0),
    (["--ignore-files-with-more-than-developers", "2"], [], 1),
])
def test_scraplog_ignores_hotspot_files(tmp_path, args, ignored, pairs):
    result = run(tmp_path, LOG, *args)

    assert result.returncode == 0, result.stdout + result.stderr
    assert data_lines(tmp_path / "t.temporal.ignored-files.csv") == ["file,developers,reason", *ignored]
    assert len(data_lines(tmp_path / "t.temporal.edges.csv")) - 1 == pairs
    assert (tmp_path / "t.temporal.ignored-files.csv").read_text().startswith("# scraplog_tool: scrapLog.py\n")


def test_same_network_as_deleting_the_files_from_the_log(tmp_path):
    result = run(tmp_path, TEN, "--ignore-top-hotspot-files", "3")
    assert result.returncode == 0, result.stdout + result.stderr
    ignored = [line.split(",")[0] for line in data_lines(tmp_path / "t.temporal.ignored-files.csv")[1:]]
    assert len(ignored) == 3

    reduced = [line for line in TEN.read_text().splitlines() if line.strip() not in ignored]
    (tmp_path / "reduced.txt").write_text("\n".join(reduced) + "\n")
    result = run(tmp_path, tmp_path / "reduced.txt", name="u")
    assert result.returncode == 0, result.stdout + result.stderr

    assert data_lines(tmp_path / "t.temporal.edges.csv") == data_lines(tmp_path / "u.temporal.edges.csv")


def test_no_list_without_the_options(tmp_path):
    assert run(tmp_path, LOG).returncode == 0
    assert not (tmp_path / "t.temporal.ignored-files.csv").exists()


@pytest.mark.parametrize("args", [["--ignore-top-hotspot-files", "21"], ["--ignore-top-hotspot-files", "-1"],
                                  ["--ignore-files-with-more-than-developers", "0"]])
def test_invalid_values_stop(tmp_path, args):
    result = run(tmp_path, LOG, *args)

    assert result.returncode == 1
    assert "Invalid --ignore-" in result.stdout + result.stderr
    assert not (tmp_path / "t.temporal.graphml.zip").exists()
