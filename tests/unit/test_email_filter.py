"""
Tests for -fe / --filter-emails: ignore commits by the emails listed in a file.

Filtered developers must be absent from every network type (unweighted,
weighted and temporal), not only from the unweighted one, and an unreadable
filter file is a fatal error, as for -ff.

Run with:
    pytest tests/unit/test_email_filter.py -v
"""

import subprocess
import sys
import zipfile
from pathlib import Path

import networkx as nx
import pytest

from scraplog.core.models import ProcessingState
from scraplog.identity import load_email_filter_file
from scraplog.parsing import process_commit_block

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALICE, BOB, BOT = "alice@example.com", "bob@example.com", "bot@ci.example"

# Alice, the bot and Bob all edit shared.py; Alice and Bob also share docs.md.
GIT_LOG = f"""==Alice;{ALICE};Mon Jan 1 10:00:00 2024 +0000==
shared.py
docs.md

==CI Bot;{BOT};Tue Jan 2 10:00:00 2024 +0000==
shared.py

==Bob;{BOB};Wed Jan 3 10:00:00 2024 +0000==
shared.py
docs.md

"""


def run_scraplog(tmp_path, network_type, filter_emails=None):
    log_file = tmp_path / "project.IN"
    log_file.write_text(GIT_LOG)
    out = tmp_path / f"{network_type}.graphml"
    cmd = [sys.executable, "-m", "scraplog.scraplog", "-r", str(log_file),
           "-t", f"inter_individual_graph_{network_type}", "-o", str(out)]
    if filter_emails is not None:
        filter_file = tmp_path / "filter.txt"
        filter_file.write_text("\n".join(filter_emails) + "\n")
        cmd += ["-fe", str(filter_file)]
    subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True, check=True,
                   env={"PYTHONPATH": str(PROJECT_ROOT), "MPLBACKEND": "Agg", "PATH": ""})
    return out


def developer_pairs(out, network_type):
    if network_type == "temporal":
        with zipfile.ZipFile(out) as archive:
            xml = out.with_suffix(".xml")
            xml.write_bytes(archive.read(archive.namelist()[0]))
        graph = nx.read_graphml(xml, force_multigraph=True)
        label = lambda n: n
    else:
        graph = nx.read_graphml(out)
        label = (lambda n: graph.nodes[n].get("e-mail", n))
    nodes = {label(n) for n in graph.nodes}
    pairs = {frozenset((label(u), label(v))) for u, v in graph.edges()}
    return nodes, pairs


@pytest.mark.parametrize("network_type", ["unweighted", "weighted", "temporal"])
def test_without_filter_the_bot_is_connected(tmp_path, network_type):
    nodes, pairs = developer_pairs(run_scraplog(tmp_path, network_type), network_type)

    assert nodes == {ALICE, BOB, BOT}
    assert frozenset((ALICE, BOT)) in pairs


@pytest.mark.parametrize("network_type", ["unweighted", "weighted", "temporal"])
def test_filtered_email_is_absent_from_every_network_type(tmp_path, network_type):
    """It used to be removed from the unweighted network only."""
    out = run_scraplog(tmp_path, network_type, filter_emails=[BOT])
    nodes, pairs = developer_pairs(out, network_type)

    assert nodes == {ALICE, BOB}
    assert pairs == {frozenset((ALICE, BOB))}


def test_filtered_commit_is_skipped_and_counted():
    state = ProcessingState()
    state.email_filtering_mode = True
    state.emails_to_filter = {BOT}

    block = [f"==CI Bot;{BOT};Tue Jan 2 10:00:00 2024 +0000==", "shared.py"]
    assert process_commit_block(block, state, 0) is False

    assert state.parsed_change_log_entries == []
    assert state.statistics.n_commits_excluded_by_email_filter == 1
    assert state.excluded_emails == {BOT}
    assert state.statistics.n_skipped_blocks == 0  # filtered on purpose, not invalid


def test_unfiltered_commit_is_kept():
    state = ProcessingState()
    state.email_filtering_mode = True
    state.emails_to_filter = {BOT}

    block = [f"==Alice;{ALICE};Mon Jan 1 10:00:00 2024 +0000==", "shared.py"]
    assert process_commit_block(block, state, 0) is True
    assert state.statistics.n_commits_excluded_by_email_filter == 0


def test_missing_filter_file_exits(tmp_path):
    state = ProcessingState()
    state.email_filtering_mode = True

    with pytest.raises(SystemExit) as exc_info:
        load_email_filter_file(state, tmp_path / "does_not_exist.txt")
    assert exc_info.value.code == 1


def test_unreadable_filter_file_exits(tmp_path):
    state = ProcessingState()
    state.email_filtering_mode = True

    with pytest.raises(SystemExit):
        load_email_filter_file(state, tmp_path)  # a directory
