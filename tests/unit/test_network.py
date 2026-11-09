"""
Tests for building the co-editing network from parsed change log entries.

Covers the two scrapLog steps that turn commits into collaborations:
  - aggregate_files_and_contributors: file -> contributors
    (state.map_files_to_their_contributors)
  - extract_contributor_connections: pairs of contributors per shared file
    (state.file_coediting_collaborative_relationships, as ((dev1, dev2), file))

A parsed change log entry is ((email, affiliation), [files], timestamp).

Run with:
    pytest tests/unit/test_network.py -v
"""

from collections import defaultdict

import pytest

from scraplog.coediting import aggregate_files_and_contributors, extract_contributor_connections
from scraplog.core.models import ProcessingState


def entry(email, affiliation, files, timestamp="Mon Jan 1 12:00:00 2024 +0000"):
    return ((email, affiliation), files, timestamp)


def state_with_entries(entries):
    state = ProcessingState()
    state.parsed_change_log_entries = entries
    return state


def state_with_contributors(mapping):
    state = ProcessingState()
    state.map_files_to_their_contributors = defaultdict(list, mapping)
    return state


@pytest.fixture
def sample_entries():
    return [
        entry("dev1@a.com", "a", ["file1"], "Sun Jan 1 12:00:00 2023 +0000"),
        entry("dev2@b.com", "b", ["file1", "file2"], "Mon Jan 2 12:00:00 2023 +0000"),
        entry("dev3@c.com", "c", ["file2"], "Tue Jan 3 12:00:00 2023 +0000"),
    ]


# =============================================================================
# aggregate_files_and_contributors
# =============================================================================

def test_aggregate_files_and_contributors(sample_entries):
    state = state_with_entries(sample_entries)

    aggregate_files_and_contributors(state)

    contributors = state.map_files_to_their_contributors
    assert set(contributors) == {"file1", "file2"}
    assert set(contributors["file1"]) == {"dev1@a.com", "dev2@b.com"}
    assert set(contributors["file2"]) == {"dev2@b.com", "dev3@c.com"}
    assert state.statistics.n_changed_files == 2


def test_aggregate_empty_data():
    state = state_with_entries([])

    aggregate_files_and_contributors(state)

    assert len(state.map_files_to_their_contributors) == 0
    assert state.statistics.n_changed_files == 0


def test_aggregate_single_commit():
    state = state_with_entries([entry("dev1@company.com", "company", ["main.py", "utils.py"])])

    aggregate_files_and_contributors(state)

    assert dict(state.map_files_to_their_contributors) == {
        "main.py": ["dev1@company.com"],
        "utils.py": ["dev1@company.com"],
    }


def test_aggregate_lists_each_contributor_once():
    """A developer editing the same file twice is listed once for that file."""
    state = state_with_entries([
        entry("dev1@a.com", "a", ["file1"]),
        entry("dev1@a.com", "a", ["file1"]),
    ])

    aggregate_files_and_contributors(state)

    assert state.map_files_to_their_contributors["file1"] == ["dev1@a.com"]


@pytest.mark.parametrize("entries,expected_contributors", [
    # Basic
    ([entry("dev1@a.com", "a", ["file1"]),
      entry("dev2@b.com", "b", ["file1", "file2"])],
     {"file1": {"dev1@a.com", "dev2@b.com"}, "file2": {"dev2@b.com"}}),

    # Same developer, multiple files
    ([entry("dev@company.com", "company", ["file1", "file2", "file3"])],
     {"file1": {"dev@company.com"}, "file2": {"dev@company.com"}, "file3": {"dev@company.com"}}),

    # Multiple developers, same file
    ([entry("dev1@a.com", "a", ["shared.py"]),
      entry("dev2@b.com", "b", ["shared.py"]),
      entry("dev3@c.com", "c", ["shared.py"])],
     {"shared.py": {"dev1@a.com", "dev2@b.com", "dev3@c.com"}}),
])
def test_aggregate_parametrized(entries, expected_contributors):
    state = state_with_entries(entries)

    aggregate_files_and_contributors(state)

    actual = {f: set(devs) for f, devs in state.map_files_to_their_contributors.items()}
    assert actual == expected_contributors


# =============================================================================
# extract_contributor_connections
# =============================================================================

def test_extract_connections_basic():
    state = state_with_contributors({
        "file1": ["dev1@a.com", "dev2@b.com", "dev3@c.com"],
        "file2": ["dev2@b.com", "dev3@c.com"],
        "file3": ["dev1@a.com"],
    })

    extract_contributor_connections(state)

    connections = state.file_coediting_collaborative_relationships
    # file1: 3 choose 2 = 3 pairs, file2: 1 pair, file3: none
    assert sorted(connections) == sorted([
        (("dev1@a.com", "dev2@b.com"), "file1"),
        (("dev1@a.com", "dev3@c.com"), "file1"),
        (("dev2@b.com", "dev3@c.com"), "file1"),
        (("dev2@b.com", "dev3@c.com"), "file2"),
    ])


def test_extract_connections_single_contributor():
    """Files with a single contributor create no connections."""
    state = state_with_contributors({
        "file1": ["dev1@a.com"],
        "file2": ["dev2@b.com"],
    })

    extract_contributor_connections(state)

    assert state.file_coediting_collaborative_relationships == []


def test_extract_connections_empty():
    state = state_with_contributors({})

    extract_contributor_connections(state)

    assert state.file_coediting_collaborative_relationships == []


def test_extract_connections_replaces_previous_results():
    """Running the step twice does not duplicate connections."""
    state = state_with_contributors({"file1": ["dev1@a.com", "dev2@b.com"]})

    extract_contributor_connections(state)
    extract_contributor_connections(state)

    assert state.file_coediting_collaborative_relationships == [(("dev1@a.com", "dev2@b.com"), "file1")]


# =============================================================================
# Both steps together
# =============================================================================

def test_integrated_workflow(sample_entries):
    state = state_with_entries(sample_entries)

    aggregate_files_and_contributors(state)
    extract_contributor_connections(state)

    connections = state.file_coediting_collaborative_relationships
    assert connections
    for (dev1, dev2), file in connections:
        assert dev1 != dev2
        assert file in {"file1", "file2"}

    pairs = {(frozenset(devs), file) for devs, file in connections}
    assert pairs == {
        (frozenset({"dev1@a.com", "dev2@b.com"}), "file1"),
        (frozenset({"dev2@b.com", "dev3@c.com"}), "file2"),
    }
