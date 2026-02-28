"""
Basic unit tests for temporal network extraction function inextract_temporal_network.py

Run with:
pytest tests/unit/test_extract_temporal_network_from_parsed_change_log_entries.py

For specific tests run with:
pytest tests/unit/test_extract_temporal_network_from_parsed_change_log_entries.py::test_empty_entries_returns_none

Run pytest with -v or -vv for more verbose output
Run pytest with  -s to show stdout (pring statements)

Here is a sample data structure for parsed_change_log_entries
 parsed_change_log_entries =
[
  (
    ('dasenov@google.com', 'google'),
    ['third_party/xla/xla/tests/BUILD', 'tensorflow/core/kernels/gpu_utils.cc', 'tensorflow/core/platform/logger.h'],
    'Wed Jan 3 04:05:02 2024 -0800' ),
  )
  (
    ('ddunleavy@google.com', 'google'),
    ['third_party/xla/xla/tests/BUILD'],
    'Tue Jan 2 11:19:35 2024 -0800'),
  ),
  (
    ('ddunleavy@google.com', 'google'),
    ['third_party/xla/xla/tests/BUILD', 'tensorflow/core/kernels/gpu_utils.cc'],
    'Tue Jan 2 07:34:17 2024 -0800')
  )
]                                                         ]


"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from collections import defaultdict
from typing import List, Optional

import networkx_temporal as tx

# Import your actual types
from core.types import (
    Email, Affiliation, Filename, Timestamp,
    ChangeLogEntry, DeveloperInfo, Connection, ConnectionWithFile,
)

from core.models import ProcessingState, ProcessingStatistics

from extract_temporal_network import extract_temporal_network_from_parsed_change_log_entries


# Test 1: Empty input returns None
def test_empty_entries_returns_none():
    """Test that function returns None when no entries provided
     pytest -svv tests/unit/test_extract_temporal_network_from_parsed_change_log_entries.py::test_empty_entries_returns_none
    """

    # Arrange
    state = ProcessingState()
    state.parsed_change_log_entries = []
    state.verbose_mode = False
    state.very_verbose_mode = True
    state.debug_mode = True

    # Act
    result = extract_temporal_network_from_parsed_change_log_entries(state)

    # Assert
    assert result is None, "Should return None for empty entries"


# Test 2: Single developer, single file - no edges (developer_coediting)
def test_single_developer_no_edges():
    """
    Test that with one developer editing one file,
    no edges are created in co-editing network

     pytest -svv tests/unit/test_extract_temporal_network_from_parsed_change_log_entries.py::test_single_developer_no_edges
    """
    # Arrange
    now = datetime.now()
    email = Email("alice@example.com")
    filename = Filename("src/main.py")
    affiliation = Affiliation("Example Corp")
    timestamp = "Tue Jan 2 11:19:35 2024 -0800"

    # Create DeveloperInfo
    dev_info = ( email, affiliation)

    # Create ChangeLogEntry (tuple[DeveloperInfo, list[Filename], Timestamp])
    entry = (dev_info,[filename],timestamp)


    state = ProcessingState()
    state.parsed_change_log_entries = [entry, entry]  # Two edits by same developer
    state.verbose_mode = False
    state.very_verbose_mode = True
    state.debug_mode = True

    # Act with default window resolution
    result = extract_temporal_network_from_parsed_change_log_entries(
        state
    )

    # Assert
    assert result is not None, "Should return a graph object"
    assert len(result) > 0, "Should have at least one snapshot"

    # Check total edges across all snapshots
    total_edges = sum(G.number_of_edges() for G in result)
    assert total_edges == 0, f"Expected 0 edges for single developer, got {total_edges}"

    # Check nodes - should have 1 developer (by email)
    all_nodes = set()
    for G in result:
        all_nodes.update(G.nodes())
    assert email in all_nodes, f"{email} should be a node"
    assert len(all_nodes) == 1, f"Expected 1 node, got {len(all_nodes)}"


# Test 3: Two developers editing same file creates edge (developer_coediting)
def test_two_developers_creates_edge():
    """
    Test that with two developers editing the same file within time window,
    an edge is created between them
    """
    # Arrange
    base_time = datetime.now()
    email1 = Email("alice@example.com")
    email2 = Email("bob@example.com")
    filename = Filename("src/main.py")

    # Create DeveloperInfo objects
    dev_info1 = DeveloperInfo(
        email=email1,
        name="Alice",
        affiliation=Affiliation("Example Corp")
    )
    dev_info2 = DeveloperInfo(
        email=email2,
        name="Bob",
        affiliation=Affiliation("Example Corp")
    )

    # Create ChangeLogEntry objects
    entry1 = ChangeLogEntry(
        developer_info=dev_info1,
        filenames=[filename],
        timestamp=Timestamp(base_time)
    )
    entry2 = ChangeLogEntry(
        developer_info=dev_info2,
        filenames=[filename],
        timestamp=Timestamp(base_time + timedelta(minutes=30))  # Within 1 hour window
    )

    state = ProcessingState()
    state.parsed_change_log_entries = [entry1, entry2]
    state.verbose_mode = False
    state.very_verbose_mode = False
    state.debug_mode = False

    # Act
    result = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="developer_coediting",
        relationship_window=timedelta(hours=1),
        time_resolution=timedelta(hours=1)  # Coarse resolution for testing
    )

    # Assert
    assert result is not None, "Should return a graph object"
    assert len(result) > 0, "Should have at least one snapshot"

    # Check that edge exists
    total_edges = 0
    edge_found = False

    for snapshot_idx, G in enumerate(result):
        total_edges += G.number_of_edges()

        # Check if edge between emails exists in this snapshot
        if G.has_edge(email1, email2):
            edge_found = True
            # Check edge attributes
            edge_data = G.get_edge_data(email1, email2)
            assert edge_data is not None, "Edge should have data"

            # If it's a MultiGraph, check first edge's attributes
            if hasattr(G, 'is_multigraph') and G.is_multigraph():
                for key, data in edge_data.items():
                    assert 'file' in data, "Edge should have file attribute"
                    assert data['file'] == filename, f"File attribute should be {filename}"
                    assert 'time' in data, "Edge should have time attribute"

    assert total_edges > 0, "Should have at least one edge"
    assert edge_found, f"Edge between {email1} and {email2} should exist"

    # Check nodes
    all_nodes = set()
    for G in result:
        all_nodes.update(G.nodes())
    assert email1 in all_nodes, f"{email1} should be a node"
    assert email2 in all_nodes, f"{email2} should be a node"
    assert len(all_nodes) == 2, f"Expected 2 nodes, got {len(all_nodes)}"


# Test 4: Two developers but outside time window - no edge (developer_coediting)
def test_two_developers_outside_window_no_edge():
    """
    Test that with two developers editing same file but outside time window,
    no edge is created
    """
    # Arrange
    base_time = datetime.now()
    email1 = Email("alice@example.com")
    email2 = Email("bob@example.com")
    filename = Filename("src/main.py")

    # Create DeveloperInfo objects
    dev_info1 = DeveloperInfo(
        email=email1,
        name="Alice",
        affiliation=Affiliation("Example Corp")
    )
    dev_info2 = DeveloperInfo(
        email=email2,
        name="Bob",
        affiliation=Affiliation("Example Corp")
    )

    # Create ChangeLogEntry objects
    entry1 = ChangeLogEntry(
        developer_info=dev_info1,
        filenames=[filename],
        timestamp=Timestamp(base_time)
    )
    entry2 = ChangeLogEntry(
        developer_info=dev_info2,
        filenames=[filename],
        timestamp=Timestamp(base_time + timedelta(hours=2))  # Outside 1 hour window
    )

    state = ProcessingState()
    state.parsed_change_log_entries = [entry1, entry2]
    state.verbose_mode = False
    state.very_verbose_mode = False
    state.debug_mode = False

    # Act
    result = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="developer_coediting",
        relationship_window=timedelta(hours=1)  # Only 1 hour window
    )

    # Assert
    assert result is not None, "Should return a graph object"

    # Check total edges across all snapshots
    total_edges = sum(G.number_of_edges() for G in result)
    assert total_edges == 0, f"Expected 0 edges (outside time window), got {total_edges}"

    # Check nodes - both developers should still be nodes
    all_nodes = set()
    for G in result:
        all_nodes.update(G.nodes())
    assert email1 in all_nodes, f"{email1} should be a node"
    assert email2 in all_nodes, f"{email2} should be a node"
    assert len(all_nodes) == 2, f"Expected 2 nodes, got {len(all_nodes)}"


# Test 5: Test developer_file network type (bipartite)
def test_developer_file_bipartite_network():
    """Test the bipartite developer-file network creation"""
    # Arrange
    now = datetime.now()
    email1 = Email("alice@example.com")
    email2 = Email("bob@example.com")
    filename1 = Filename("src/main.py")
    filename2 = Filename("src/utils.py")

    # Create DeveloperInfo objects
    dev_info1 = DeveloperInfo(
        email=email1,
        name="Alice",
        affiliation=Affiliation("Example Corp")
    )
    dev_info2 = DeveloperInfo(
        email=email2,
        name="Bob",
        affiliation=Affiliation("Example Corp")
    )

    # Create ChangeLogEntry objects
    entry1 = ChangeLogEntry(
        developer_info=dev_info1,
        filenames=[filename1],
        timestamp=Timestamp(now)
    )
    entry2 = ChangeLogEntry(
        developer_info=dev_info2,
        filenames=[filename2],
        timestamp=Timestamp(now + timedelta(minutes=5))
    )

    state = ProcessingState()
    state.parsed_change_log_entries = [entry1, entry2]
    state.verbose_mode = False
    state.very_verbose_mode = False
    state.debug_mode = False

    # Act
    result = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="developer_file"
    )

    # Assert
    assert result is not None, "Should return a graph object"

    # Check that edges exist between developers and files
    edges_found = 0
    for G in result:
        edges_found += G.number_of_edges()

        # Check for developer-file connections
        for node in G.nodes():
            if isinstance(node, str) and node.startswith("dev_"):
                email_part = node.replace("dev_", "")
                assert email_part in [str(email1), str(email2)], f"Unexpected developer node: {node}"
            elif isinstance(node, str) and node.startswith("file_"):
                file_part = node.replace("file_", "")
                assert file_part in [str(filename1), str(filename2)], f"Unexpected file node: {node}"

    assert edges_found == 2, f"Expected 2 edges, got {edges_found}"


# Test 6: Test with multiple files in same commit
def test_multiple_files_same_commit():
    """
    Test that when a developer changes multiple files in one commit,
    it creates appropriate edges in different network types
    """
    # Arrange
    now = datetime.now()
    email = Email("alice@example.com")
    filename1 = Filename("src/main.py")
    filename2 = Filename("src/utils.py")
    filename3 = Filename("tests/test_main.py")

    # Create DeveloperInfo
    dev_info = DeveloperInfo(
        email=email,
        name="Alice",
        affiliation=Affiliation("Example Corp")
    )

    # Create ChangeLogEntry with multiple files
    entry = ChangeLogEntry(
        developer_info=dev_info,
        filenames=[filename1, filename2, filename3],
        timestamp=Timestamp(now)
    )

    state = ProcessingState()
    state.parsed_change_log_entries = [entry]
    state.verbose_mode = False
    state.very_verbose_mode = False
    state.debug_mode = False

    # Test file dependency network
    result = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="file_dependency"
    )

    assert result is not None, "Should return a graph object"

    # In file dependency network, files changed together should be connected
    total_edges = sum(G.number_of_edges() for G in result)

    # With 3 files, number of edges should be C(3,2) = 3
    # (main.py-utils.py, main.py-test_main.py, utils.py-test_main.py)
    expected_edges = 3
    assert total_edges == expected_edges, f"Expected {expected_edges} edges, got {total_edges}"


# Test 7: Test min_interactions threshold
def test_min_interactions_threshold():
    """Test that min_interactions filter works"""
    # Arrange
    base_time = datetime.now()
    email1 = Email("alice@example.com")
    email2 = Email("bob@example.com")
    filename = Filename("src/main.py")

    # Create DeveloperInfo objects
    dev_info1 = DeveloperInfo(
        email=email1,
        name="Alice",
        affiliation=Affiliation("Example Corp")
    )
    dev_info2 = DeveloperInfo(
        email=email2,
        name="Bob",
        affiliation=Affiliation("Example Corp")
    )

    # Create multiple co-editing events (4 total)
    entries = [
        ChangeLogEntry(
            developer_info=dev_info1,
            filenames=[filename],
            timestamp=Timestamp(base_time)
        ),
        ChangeLogEntry(
            developer_info=dev_info2,
            filenames=[filename],
            timestamp=Timestamp(base_time + timedelta(minutes=5))
        ),
        ChangeLogEntry(
            developer_info=dev_info1,
            filenames=[filename],
            timestamp=Timestamp(base_time + timedelta(minutes=10))
        ),
        ChangeLogEntry(
            developer_info=dev_info2,
            filenames=[filename],
            timestamp=Timestamp(base_time + timedelta(minutes=15))
        ),
    ]

    state = ProcessingState()
    state.parsed_change_log_entries = entries
    state.verbose_mode = False
    state.very_verbose_mode = False
    state.debug_mode = False

    # Act - with min_interactions=2
    result_high = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="developer_coediting",
        relationship_window=timedelta(hours=1),
        min_interactions=2
    )

    # Act - with min_interactions=1
    result_low = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="developer_coediting",
        relationship_window=timedelta(hours=1),
        min_interactions=1
    )

    # Assert
    edges_high = sum(G.number_of_edges() for G in result_high) if result_high else 0
    edges_low = sum(G.number_of_edges() for G in result_low) if result_low else 0

    # With 4 entries (multiple co-edits), min_interactions=2 should still create edges
    assert edges_high > 0, f"Expected edges with min_interactions=2, got {edges_high}"
    assert edges_low >= edges_high, "Lower threshold should have at least as many edges"


# Fixture for common test setup
@pytest.fixture
def basic_entries():
    """Fixture providing basic test entries"""
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    email1 = Email("alice@example.com")
    email2 = Email("bob@example.com")
    email3 = Email("charlie@example.com")

    dev_info1 = DeveloperInfo(email=email1, name="Alice", affiliation=Affiliation("Corp A"))
    dev_info2 = DeveloperInfo(email=email2, name="Bob", affiliation=Affiliation("Corp A"))
    dev_info3 = DeveloperInfo(email=email3, name="Charlie", affiliation=Affiliation("Corp B"))

    return [
        ChangeLogEntry(
            developer_info=dev_info1,
            filenames=[Filename("src/main.py")],
            timestamp=Timestamp(base_time)
        ),
        ChangeLogEntry(
            developer_info=dev_info2,
            filenames=[Filename("src/main.py")],
            timestamp=Timestamp(base_time + timedelta(minutes=30))
        ),
        ChangeLogEntry(
            developer_info=dev_info3,
            filenames=[Filename("src/utils.py")],
            timestamp=Timestamp(base_time + timedelta(hours=2))
        ),
    ]


# Test 8: Using fixture with different network types
def test_with_fixture_different_networks(basic_entries):
    """Test different network types with fixture data"""
    state = ProcessingState()
    state.parsed_change_log_entries = basic_entries
    state.verbose_mode = False
    state.very_verbose_mode = False
    state.debug_mode = False

    # Test co-editing network
    result1 = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="developer_coediting",
        relationship_window=timedelta(hours=1)
    )
    assert result1 is not None

    # Test sequential network
    result2 = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="developer_sequential",
        relationship_window=timedelta(hours=1)
    )
    assert result2 is not None

    # Test file dependency network
    result3 = extract_temporal_network_from_parsed_change_log_entries(
        state,
        network_type="file_dependency"
    )
    assert result3 is not None


# Test 9: Test with Connection and ConnectionWithFile types (if used)
def test_connection_types():
    """Test that function handles Connection types correctly"""
    # This test assumes your function might use these types internally
    # You can add this if your function uses Connection or ConnectionWithFile

    # Create a Connection (tuple[Email, Email, Timestamp])
    email1 = Email("alice@example.com")
    email2 = Email("bob@example.com")
    timestamp = Timestamp(datetime.now())
    connection = Connection((email1, email2, timestamp))

    # Create a ConnectionWithFile (tuple[Connection, Filename, Timestamp])
    filename = Filename("src/main.py")
    connection_with_file = ConnectionWithFile((connection, filename, timestamp))

    # This is just to verify the types exist
    assert connection is not None
    assert connection_with_file is not None
    assert connection[0] == email1
    assert connection[1] == email2
    assert connection_with_file[0] == connection
    assert connection_with_file[1] == filename