"""
Test cases for the temporal network feature (-t inter_individual_graph_temporal).

These tests feed parsed change log entries to
extract_temporal_network_from_parsed_change_log_entries() and check the
resulting temporal network.

How the temporal network is built: entries are processed in chronological
order, and whenever a developer edits a file, one time-stamped edge is added
between that developer and every *earlier* contributor of the same file.
Each edge carries a `time` (ISO 8601) and a `file` attribute.

A parsed change log entry is a tuple:
    ((email, affiliation), [filenames], "Mon Jan 16 14:20:00 2023 -0500")

Run with:
    pytest tests/unit/test_parsing_to_temporal_networks.py -v
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import pytest

from scraplog.core.models import ProcessingState
from scraplog.networks.temporal import extract_temporal_network_from_parsed_change_log_entries


# =============================================================================
# Helpers
# =============================================================================

def git_ts(year, month, day, hour, minute, utc_offset_hours=-5):
    """Build a timestamp in git log format, e.g. 'Mon Jan 16 14:20:00 2023 -0500'."""
    tz = timezone(timedelta(hours=utc_offset_hours))
    return datetime(year, month, day, hour, minute, tzinfo=tz).strftime("%a %b %d %H:%M:%S %Y %z")


def iso_ts(year, month, day, hour, minute, utc_offset_hours=-5):
    """The same moment in the ISO format stored on temporal edges."""
    tz = timezone(timedelta(hours=utc_offset_hours))
    return datetime(year, month, day, hour, minute, tzinfo=tz).isoformat()


def entry(email, files, timestamp, affiliation="company"):
    """Build one parsed change log entry."""
    return ((email, affiliation), list(files), timestamp)


def make_state(entries):
    state = ProcessingState()
    state.network_type = "inter_individual_graph_temporal"
    state.parsed_change_log_entries = entries
    return state


def temporal_edges(t_graph):
    """All edges as (frozenset({u, v}), time, file) tuples, order-independent."""
    return [
        (frozenset((u, v)), data["time"], data["file"])
        for u, v, data in t_graph.temporal_edges(data=True)
    ]


def all_nodes(t_graph):
    """Nodes across all snapshots (nodes() returns one NodeView per snapshot)."""
    return set().union(*t_graph.nodes())


def pair(a, b):
    return frozenset((a, b))


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_entries():
    """Commits touching four files, mirroring a small project history."""
    return [
        # src/module1.py: several developers over time
        entry("alice@company.com", ["src/module1.py"], git_ts(2023, 1, 15, 10, 30)),
        entry("bob@company.com", ["src/module1.py"], git_ts(2023, 1, 16, 14, 20)),
        entry("alice@company.com", ["src/module1.py"], git_ts(2023, 1, 17, 9, 15)),
        entry("charlie@company.com", ["src/module1.py"], git_ts(2023, 1, 18, 11, 45)),
        entry("bob@company.com", ["src/module1.py"], git_ts(2023, 1, 19, 16, 30)),

        # src/module2.py: two developers collaborating
        entry("alice@company.com", ["src/module2.py"], git_ts(2023, 2, 1, 10, 0)),
        entry("bob@company.com", ["src/module2.py"], git_ts(2023, 2, 2, 11, 30)),
        entry("alice@company.com", ["src/module2.py"], git_ts(2023, 2, 3, 9, 45)),

        # README.md: single developer (no connections)
        entry("alice@company.com", ["README.md"], git_ts(2023, 3, 1, 15, 0)),

        # src/module3.py: different developers, different time zone
        entry("bob@company.com", ["src/module3.py"], git_ts(2023, 4, 1, 10, 0, -4)),
        entry("charlie@company.com", ["src/module3.py"], git_ts(2023, 4, 2, 11, 0, -4)),
        entry("david@company.com", ["src/module3.py"], git_ts(2023, 4, 3, 12, 0, -4)),
    ]


@pytest.fixture
def expected_edges():
    """Expected temporal edges for sample_entries: (pair, time, file)."""
    a, b, c, d = ("alice@company.com", "bob@company.com",
                  "charlie@company.com", "david@company.com")
    m1, m2, m3 = "src/module1.py", "src/module2.py", "src/module3.py"
    return [
        # module1.py
        (pair(a, b), iso_ts(2023, 1, 16, 14, 20), m1),      # bob joins alice
        (pair(a, b), iso_ts(2023, 1, 17, 9, 15), m1),       # alice edits again
        (pair(a, c), iso_ts(2023, 1, 18, 11, 45), m1),      # charlie joins
        (pair(b, c), iso_ts(2023, 1, 18, 11, 45), m1),
        (pair(a, b), iso_ts(2023, 1, 19, 16, 30), m1),      # bob edits again
        (pair(b, c), iso_ts(2023, 1, 19, 16, 30), m1),
        # module2.py
        (pair(a, b), iso_ts(2023, 2, 2, 11, 30), m2),
        (pair(a, b), iso_ts(2023, 2, 3, 9, 45), m2),
        # module3.py
        (pair(b, c), iso_ts(2023, 4, 2, 11, 0, -4), m3),
        (pair(b, d), iso_ts(2023, 4, 3, 12, 0, -4), m3),
        (pair(c, d), iso_ts(2023, 4, 3, 12, 0, -4), m3),
    ]


# =============================================================================
# Test Case 1: Temporal connection extraction
# =============================================================================

def test_extract_temporal_connections(sample_entries, expected_edges):
    """
    Verifies:
    - All expected time-stamped connections are created
    - No extra connections are created
    - Timestamps and files are preserved on each edge
    """
    t_graph = extract_temporal_network_from_parsed_change_log_entries(make_state(sample_entries))

    assert t_graph is not None
    assert Counter(temporal_edges(t_graph)) == Counter(expected_edges)


def test_entries_are_processed_in_chronological_order(sample_entries, expected_edges):
    """The input order does not matter: entries are sorted by timestamp first."""
    shuffled = list(reversed(sample_entries))
    t_graph = extract_temporal_network_from_parsed_change_log_entries(make_state(shuffled))

    assert Counter(temporal_edges(t_graph)) == Counter(expected_edges)


# =============================================================================
# Test Case 2: Collaboration summary derived from the temporal network
# =============================================================================

def test_collaboration_summary_per_pair(sample_entries):
    """
    Verifies, per developer pair:
    - Nodes and pairs that collaborated
    - First/last collaboration times
    - Collaboration counts
    - Files shared
    """
    t_graph = extract_temporal_network_from_parsed_change_log_entries(make_state(sample_entries))

    a, b, c, d = ("alice@company.com", "bob@company.com",
                  "charlie@company.com", "david@company.com")

    assert all_nodes(t_graph) == {a, b, c, d}

    times, files = defaultdict(list), defaultdict(set)
    for p, time, file in temporal_edges(t_graph):
        times[p].append(datetime.fromisoformat(time))
        files[p].add(file)

    assert set(times) == {pair(a, b), pair(a, c), pair(b, c), pair(b, d), pair(c, d)}

    # Alice-Bob: three collaborations on module1 + two on module2
    assert len(times[pair(a, b)]) == 5
    assert min(times[pair(a, b)]) == datetime.fromisoformat(iso_ts(2023, 1, 16, 14, 20))
    assert max(times[pair(a, b)]) == datetime.fromisoformat(iso_ts(2023, 2, 3, 9, 45))
    assert files[pair(a, b)] == {"src/module1.py", "src/module2.py"}

    # Bob-Charlie: two on module1 + one on module3
    assert len(times[pair(b, c)]) == 3
    assert files[pair(b, c)] == {"src/module1.py", "src/module3.py"}


# =============================================================================
# Test Case 3: Edge cases
# =============================================================================

def test_empty_history_returns_none():
    assert extract_temporal_network_from_parsed_change_log_entries(make_state([])) is None


def test_single_contributor_files_create_no_connections():
    entries = [
        entry("alice@company.com", ["file1.txt"], git_ts(2023, 1, 1, 10, 0)),
        entry("alice@company.com", ["file1.txt"], git_ts(2023, 1, 2, 11, 0)),  # same contributor
        entry("bob@company.com", ["file2.txt"], git_ts(2023, 1, 3, 12, 0)),
    ]
    t_graph = extract_temporal_network_from_parsed_change_log_entries(make_state(entries))

    assert temporal_edges(t_graph) == []


def test_identical_timestamps_still_create_a_connection():
    same_time = git_ts(2023, 1, 1, 10, 0)
    entries = [
        entry("alice@company.com", ["file1.txt"], same_time),
        entry("bob@company.com", ["file1.txt"], same_time),
    ]
    t_graph = extract_temporal_network_from_parsed_change_log_entries(make_state(entries))

    assert [p for p, _, _ in temporal_edges(t_graph)] == [pair("alice@company.com", "bob@company.com")]


def test_many_contributors_on_one_file():
    """10 developers editing one file in turn connect every pair once: 10 choose 2 = 45."""
    entries = [
        entry(f"dev{i}@company.com", ["bigfile.py"], git_ts(2023, 1, i + 1, 10, 0))
        for i in range(10)
    ]
    t_graph = extract_temporal_network_from_parsed_change_log_entries(make_state(entries))

    edges = temporal_edges(t_graph)
    assert len(edges) == 45
    assert len({p for p, _, _ in edges}) == 45


def test_non_default_time_resolution_not_implemented(sample_entries):
    with pytest.raises(NotImplementedError):
        extract_temporal_network_from_parsed_change_log_entries(
            make_state(sample_entries), time_resolution=timedelta(days=1))


# =============================================================================
# Test Case 4: End-to-end with mock commits
# =============================================================================

def test_temporal_network_with_mock_commits():
    alice, bob = "alice@company.com", "bob@company.com"
    entries = [
        entry(alice, ["src/module1.py"], git_ts(2023, 1, 1, 10, 0)),
        entry(bob, ["src/module1.py"], git_ts(2023, 1, 2, 11, 0)),   # collaboration with Alice
        entry(alice, ["src/module2.py"], git_ts(2023, 1, 3, 9, 0)),
        entry(bob, ["src/module2.py"], git_ts(2023, 1, 4, 14, 0)),   # another collaboration
    ]
    t_graph = extract_temporal_network_from_parsed_change_log_entries(make_state(entries))

    assert all_nodes(t_graph) == {alice, bob}
    assert sorted(temporal_edges(t_graph), key=lambda e: e[1]) == [
        (pair(alice, bob), iso_ts(2023, 1, 2, 11, 0), "src/module1.py"),
        (pair(alice, bob), iso_ts(2023, 1, 4, 14, 0), "src/module2.py"),
    ]
