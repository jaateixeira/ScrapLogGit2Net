"""
Test cases for temporal network analysis feature.
"""

import pytest
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import networkx as nx
from typing import List, Tuple

# Import your module
from your_script import (
    ProcessingState,
    ProcessingStatistics,
    extract_temporal_connections,
    create_temporal_network_graph,
    FileContribution,
    ChangeLogEntry,
    DeveloperInfo,
    Connection,
    ConnectionWithFile
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_file_history():
    """Create a sample file history with multiple contributions."""
    history = defaultdict(list)
    
    # File A: Multiple developers over time
    history["src/module1.py"] = [
        FileContribution("alice@company.com", "2023-01-15 10:30:00 -0500", 0),
        FileContribution("bob@company.com", "2023-01-16 14:20:00 -0500", 1),
        FileContribution("alice@company.com", "2023-01-17 09:15:00 -0500", 2),
        FileContribution("charlie@company.com", "2023-01-18 11:45:00 -0500", 3),
        FileContribution("bob@company.com", "2023-01-19 16:30:00 -0500", 4),
    ]
    
    # File B: Two developers collaborating
    history["src/module2.py"] = [
        FileContribution("alice@company.com", "2023-02-01 10:00:00 -0500", 5),
        FileContribution("bob@company.com", "2023-02-02 11:30:00 -0500", 6),
        FileContribution("alice@company.com", "2023-02-03 09:45:00 -0500", 7),
    ]
    
    # File C: Single developer (should not create connections)
    history["README.md"] = [
        FileContribution("alice@company.com", "2023-03-01 15:00:00 -0500", 8),
    ]
    
    # File D: Developers in different order
    history["src/module3.py"] = [
        FileContribution("bob@company.com", "2023-04-01 10:00:00 -0400", 9),
        FileContribution("charlie@company.com", "2023-04-02 11:00:00 -0400", 10),
        FileContribution("david@company.com", "2023-04-03 12:00:00 -0400", 11),
    ]
    
    return history


@pytest.fixture
def processing_state_with_history(sample_file_history):
    """Create a processing state with file history."""
    state = ProcessingState()
    state.statistics = ProcessingStatistics()
    state.verbose_mode = False
    state.network_type = "inter_individual_graph_temporal"
    state.file_history = sample_file_history
    state.affiliations = {}
    return state


@pytest.fixture
def temporal_connections_expected():
    """Expected connections from sample_file_history."""
    # Format: (email1, email2, timestamp) - normalized order
    return [
        # From module1.py
        ("alice@company.com", "bob@company.com", "2023-01-16 14:20:00 -0500"),
        ("alice@company.com", "bob@company.com", "2023-01-19 16:30:00 -0500"),
        ("alice@company.com", "charlie@company.com", "2023-01-18 11:45:00 -0500"),
        ("bob@company.com", "charlie@company.com", "2023-01-18 11:45:00 -0500"),
        ("bob@company.com", "charlie@company.com", "2023-01-19 16:30:00 -0500"),
        
        # From module2.py
        ("alice@company.com", "bob@company.com", "2023-02-02 11:30:00 -0500"),
        ("alice@company.com", "bob@company.com", "2023-02-03 09:45:00 -0500"),
        
        # From module3.py
        ("bob@company.com", "charlie@company.com", "2023-04-02 11:00:00 -0400"),
        ("bob@company.com", "david@company.com", "2023-04-03 12:00:00 -0400"),
        ("charlie@company.com", "david@company.com", "2023-04-03 12:00:00 -0400"),
    ]


# =============================================================================
# Test Case 1: Test temporal connection extraction
# =============================================================================

def test_extract_temporal_connections(processing_state_with_history, temporal_connections_expected):
    """
    Test that temporal connections are correctly extracted from file history.
    
    Verifies:
    - All expected connections are created
    - No extra connections are created
    - Timestamps are correctly preserved
    - Connections are normalized (email1 < email2)
    """
    # Extract connections
    extract_temporal_connections(processing_state_with_history)
    
    # Get actual connections
    actual_connections = [
        conn for conn, _, _ in processing_state_with_history.file_coediting_collaborative_relationships
    ]
    
    # Check count
    assert len(actual_connections) == len(temporal_connections_expected)
    
    # Check each expected connection exists
    for expected_conn in temporal_connections_expected:
        assert expected_conn in actual_connections, f"Missing connection: {expected_conn}"
    
    # Verify email normalization (email1 < email2)
    for conn in actual_connections:
        email1, email2, _ = conn
        assert email1 < email2, f"Connection not normalized: {email1} >= {email2}"
    
    # Verify timestamps are strings (not modified)
    for conn in actual_connections:
        assert isinstance(conn[2], str), f"Timestamp not preserved as string: {conn[2]}"


# =============================================================================
# Test Case 2: Test temporal graph creation
# =============================================================================

def test_create_temporal_network_graph(processing_state_with_history):
    """
    Test that temporal network graph is correctly created with temporal attributes.
    
    Verifies:
    - Nodes are correctly added
    - Edges have correct temporal attributes
    - First/last collaboration times are correct
    - Collaboration counts are correct
    - Files shared are correctly tracked
    """
    # First extract connections
    extract_temporal_connections(processing_state_with_history)
    
    # Then create graph
    create_temporal_network_graph(processing_state_with_history)
    
    graph = processing_state_with_history.dev_to_dev_network
    
    # Check node count (alice, bob, charlie, david)
    assert graph.number_of_nodes() == 4
    
    # Check edge count (pairs that collaborated)
    expected_edges = [
        ("alice@company.com", "bob@company.com"),
        ("alice@company.com", "charlie@company.com"),
        ("bob@company.com", "charlie@company.com"),
        ("bob@company.com", "david@company.com"),
        ("charlie@company.com", "david@company.com"),
    ]
    assert graph.number_of_edges() == len(expected_edges)
    
    # Check Alice-Bob edge attributes
    edge_data = graph.get_edge_data("alice@company.com", "bob@company.com")
    assert edge_data is not None
    
    # Verify temporal attributes
    assert edge_data["first_collaboration"] == "2023-01-16 14:20:00 -0500"
    assert edge_data["last_collaboration"] == "2023-02-03 09:45:00 -0500"
    assert edge_data["collaboration_count"] == 4  # Two from module1 + two from module2
    
    # Check files shared
    expected_files = ["src/module1.py", "src/module2.py"]
    assert set(edge_data["files_shared"]) == set(expected_files)
    
    # Check collaboration timeline
    assert len(edge_data["collaboration_timeline"]) == 4
    
    # Check Bob-Charlie edge
    edge_data = graph.get_edge_data("bob@company.com", "charlie@company.com")
    assert edge_data is not None
    assert edge_data["collaboration_count"] == 3  # Two from module1 + one from module3
    assert "src/module1.py" in edge_data["files_shared"]
    assert "src/module3.py" in edge_data["files_shared"]


# =============================================================================
# Test Case 3: Test edge cases and error handling
# =============================================================================

def test_temporal_network_edge_cases():
    """
    Test edge cases for temporal network feature.
    
    Verifies:
    - Empty file history
    - Single contributor files
    - Identical timestamps
    - Very large number of contributors
    - Email ordering normalization
    """
    
    # Test 1: Empty file history
    state_empty = ProcessingState()
    state_empty.file_history = defaultdict(list)
    state_empty.network_type = "inter_individual_graph_temporal"
    
    extract_temporal_connections(state_empty)
    assert len(state_empty.file_coediting_collaborative_relationships) == 0
    
    create_temporal_network_graph(state_empty)
    assert state_empty.dev_to_dev_network.number_of_nodes() == 0
    assert state_empty.dev_to_dev_network.number_of_edges() == 0
    
    # Test 2: Single contributor files (should not create connections)
    state_single = ProcessingState()
    state_single.file_history = defaultdict(list)
    state_single.file_history["file1.txt"] = [
        FileContribution("alice@company.com", "2023-01-01 10:00:00 -0500", 0),
        FileContribution("alice@company.com", "2023-01-02 11:00:00 -0500", 1),  # Same contributor
    ]
    state_single.file_history["file2.txt"] = [
        FileContribution("bob@company.com", "2023-01-03 12:00:00 -0500", 2),
    ]
    
    extract_temporal_connections(state_single)
    assert len(state_single.file_coediting_collaborative_relationships) == 0
    
    # Test 3: Identical timestamps (should still create connections)
    state_identical = ProcessingState()
    state_identical.file_history = defaultdict(list)
    state_identical.file_history["file1.txt"] = [
        FileContribution("alice@company.com", "2023-01-01 10:00:00 -0500", 0),
        FileContribution("bob@company.com", "2023-01-01 10:00:00 -0500", 1),  # Same timestamp
    ]
    
    extract_temporal_connections(state_identical)
    assert len(state_identical.file_coediting_collaborative_relationships) == 1
    
    # Test 4: Multiple contributors with mixed ordering
    state_mixed = ProcessingState()
    state_mixed.file_history = defaultdict(list)
    state_mixed.file_history["file1.txt"] = [
        FileContribution("bob@company.com", "2023-01-01 10:00:00 -0500", 0),
        FileContribution("alice@company.com", "2023-01-02 11:00:00 -0500", 1),
        FileContribution("charlie@company.com", "2023-01-03 12:00:00 -0500", 2),
    ]
    
    extract_temporal_connections(state_mixed)
    
    # Check normalization
    for conn, _, _ in state_mixed.file_coediting_collaborative_relationships:
        email1, email2, _ = conn
        assert email1 < email2
    
    # Test 5: Large number of contributors (performance sanity check)
    state_large = ProcessingState()
    state_large.file_history = defaultdict(list)
    
    # Create 10 contributors
    contributors = [f"dev{i}@company.com" for i in range(10)]
    for i, email in enumerate(contributors):
        state_large.file_history["bigfile.py"].append(
            FileContribution(email, f"2023-01-{i+1:02d} 10:00:00 -0500", i)
        )
    
    # Should create combinations (n choose 2 = 45 connections)
    extract_temporal_connections(state_large)
    expected_connections = 45  # 10 choose 2
    assert len(state_large.file_coediting_collaborative_relationships) == expected_connections


# =============================================================================
# Test Case 4: Test integration with real commit data (Optional)
# =============================================================================

def test_temporal_network_with_mock_commits():
    """
    Test temporal network with mock commit data to verify end-to-end flow.
    """
    state = ProcessingState()
    state.network_type = "inter_individual_graph_temporal"
    state.file_history = defaultdict(list)
    
    # Simulate 3 commits
    mock_commits = [
        # Commit 0: Alice changes module1.py
        (("2023-01-01 10:00:00 -0500", "alice@company.com", "company"), 
         ["src/module1.py"]),
        
        # Commit 1: Bob changes module1.py (collaboration with Alice)
        (("2023-01-02 11:00:00 -0500", "bob@company.com", "company"), 
         ["src/module1.py"]),
        
        # Commit 2: Alice changes module2.py
        (("2023-01-03 09:00:00 -0500", "alice@company.com", "company"), 
         ["src/module2.py"]),
        
        # Commit 3: Bob changes module2.py (another collaboration)
        (("2023-01-04 14:00:00 -0500", "bob@company.com", "company"), 
         ["src/module2.py"]),
    ]
    
    # Build file history from mock commits
    for idx, (dev_info, files) in enumerate(mock_commits):
        timestamp, email, _ = dev_info
        for filename in files:
            state.file_history[filename].append(
                FileContribution(email, timestamp, idx)
            )
    
    # Extract temporal connections
    extract_temporal_connections(state)
    
    # Verify connections
    assert len(state.file_coediting_collaborative_relationships) == 4
    
    # Create graph
    create_temporal_network_graph(state)
    
    # Verify graph
    assert state.dev_to_dev_network.number_of_nodes() == 2
    assert state.dev_to_dev_network.number_of_edges() == 1
    
    edge_data = state.dev_to_dev_network.get_edge_data("alice@company.com", "bob@company.com")
    assert edge_data["collaboration_count"] == 4
    assert edge_data["first_collaboration"] == "2023-01-02 11:00:00 -0500"
    assert edge_data["last_collaboration"] == "2023-01-04 14:00:00 -0500"
    assert set(edge_data["files_shared"]) == {"src/module1.py", "src/module2.py"}
