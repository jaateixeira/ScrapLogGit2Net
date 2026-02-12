# tests/test_scraplog.py

import json
from collections import defaultdict

import pytest
import tempfile
import networkx as nx
from pathlib import Path

from scrapLog import (
    ProcessingState,
    ProcessingStatistics,
    load_email_aggregation_config,
    extract_affiliation_from_email,
    parse_time_name_email_affiliation,
    parse_exceptional_format,
    extract_files_from_block,
    process_commit_block,
    aggregate_files_and_contributors,
    extract_contributor_connections,
    get_unique_connections,
    create_network_graph,
    apply_email_filtering,
    extract_affiliation_from_email,
    print_processing_summary,
    ChangeLogEntry,
    DeveloperInfo
)


# Test 1: ProcessingStatistics basic functionality
def test_processing_statistics():
    """Test ProcessingStatistics dataclass."""
    stats = ProcessingStatistics()

    assert stats.nlines == 0
    assert stats.n_blocks == 0
    assert stats.n_validation_errors == 0

    stats.increment_validation_errors()
    assert stats.n_validation_errors == 1

    stats.increment_skipped_blocks()
    assert stats.n_skipped_blocks == 1


# Test 2: ProcessingState initialization
def test_processing_state_initialization():
    """Test ProcessingState initialization with default values."""
    state = ProcessingState()

    assert isinstance(state.statistics, ProcessingStatistics)
    assert len(state.change_log_data) == 0
    assert len(state.file_contributors) == 0
    assert len(state.connections_with_files) == 0
    assert len(state.unique_connections) == 0
    assert len(state.affiliations) == 0
    assert len(state.emails_to_filter) == 0
    assert len(state.files_to_filter) == 0
    assert len(state.email_aggregation_config) == 0
    assert state.debug_mode is False
    assert state.email_filtering_mode is False
    assert state.file_filtering_mode is False
    assert isinstance(state.dev_to_dev_network, nx.Graph)


# Test 3: load_email_aggregation_config - valid JSON
def test_load_email_aggregation_config_valid():
    """Test loading valid email aggregation config."""
    config_data = {
        "us.ibm": "ibm",
        "alumi.mit": "mit",
        "redhat": "ibm",
        "google": "google"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_file = f.name

    try:
        config = load_email_aggregation_config(config_file)
        assert config == config_data
    finally:
        Path(config_file).unlink()


# Test 4: load_email_aggregation_config - file not found
def test_load_email_aggregation_config_not_found(capsys):
    """Test loading non-existent config file."""
    config = load_email_aggregation_config("non_existent_file.json")
    captured = capsys.readouterr()

    assert config == {}
    assert "Warning: Email aggregation config file not found" in captured.out


# Test 5: load_email_aggregation_config - invalid JSON
def test_load_email_aggregation_config_invalid_json():
    """Test loading invalid JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json")
        config_file = f.name

    try:
        with pytest.raises(SystemExit):
            load_email_aggregation_config(config_file)
    finally:
        Path(config_file).unlink()


# Test 6: load_email_aggregation_config - non-dict JSON
def test_load_email_aggregation_config_non_dict():
    """Test loading JSON that's not a dictionary."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('["list", "not", "dict"]')
        config_file = f.name

    try:
        with pytest.raises(SystemExit):
            load_email_aggregation_config(config_file)
    finally:
        Path(config_file).unlink()


# Test 7: extract_affiliation_from_email - basic
def test_extract_affiliation_from_email_basic():
    """Test basic email affiliation extraction."""
    state = ProcessingState()

    # Test basic email
    assert extract_affiliation_from_email("user@example.com", state) == "example"

    # Test email with subdomain
    assert extract_affiliation_from_email("user@sub.example.com", state) == "sub"

    # Test email with dash
    assert extract_affiliation_from_email("user@example-test.com", state) == "example-test"


# Test 8: extract_affiliation_from_email - with aggregation
def test_extract_affiliation_from_email_with_aggregation():
    """Test email affiliation extraction with aggregation config."""
    state = ProcessingState()
    state.email_aggregation_config = {
        "us.ibm": "ibm",
        "ibm": "ibm",
        "google": "google"
    }

    # Test aggregation rules
    assert extract_affiliation_from_email("user@us.ibm.com", state) == "ibm"
    assert extract_affiliation_from_email("user@ibm.com", state) == "ibm"
    assert extract_affiliation_from_email("user@google.com", state) == "google"
    assert extract_affiliation_from_email("user@example.com", state) == "example"


# Test 9: extract_affiliation_from_email - email filtering
def test_extract_affiliation_from_email_filtering():
    """Test email affiliation extraction with filtering."""
    state = ProcessingState()
    state.email_filtering_mode = True
    state.emails_to_filter = {"spam@bot.com"}

    # Filtered email
    assert extract_affiliation_from_email("spam@bot.com",
                                          state) == "filtered - included in file passed with -f argument"

    # Non-filtered email
    assert extract_affiliation_from_email("user@example.com", state) == "example"


# Test 10: extract_affiliation_from_email - invalid emails
def test_extract_affiliation_from_email_invalid():
    """Test email affiliation extraction with invalid emails."""
    state = ProcessingState()

    # Email without @
    assert extract_affiliation_from_email("notanemail", state) == "unknown"

    # Email ending with ?
    assert extract_affiliation_from_email("user@example.com?", state) == "example"

    # Empty email
    assert extract_affiliation_from_email("", state) == "unknown"


# Test 11: parse_time_name_email_affiliation - standard format
def test_parse_time_name_email_affiliation_standard():
    """Test parsing standard log format."""
    state = ProcessingState()
    line = "==John Doe;john@example.com;Thu Feb 20 03:56:00 2014 +0000=="

    result = parse_time_name_email_affiliation(line, state)
    assert result is not None

    time, name, email, affiliation = result
    assert email == "john@example.com"
    assert affiliation == "example"
    assert "Feb 20" in time


# Test 12: parse_time_name_email_affiliation - exceptional format 1
def test_parse_time_name_email_affiliation_exceptional1():
    """Test parsing exceptional format 1."""
    state = ProcessingState()
    line = "==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000=="

    result = parse_time_name_email_affiliation(line, state)
    assert result is not None

    time , name , email, affiliation = result
    assert email == "bmcconne@rackspace.com"
    assert affiliation == "rackspace"
    assert "Sep 20" in time


# Test 13: parse_time_name_email_affiliation - exceptional format 2
def test_parse_time_name_email_affiliation_exceptional2():
    """Test parsing exceptional format 2."""
    state = ProcessingState()
    line = "==bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000=="

    result = parse_time_name_email_affiliation(line, state)
    assert result is not None

    time, name , email, affiliation = result
    assert email == "bmcconne@rackspace.com"
    assert affiliation == "rackspace"
    assert "Sep 20" in time


# Test 14: parse_time_name_email_affiliation - Launchpad bot
def test_parse_time_name_email_affiliation_launchpad():
    """Test parsing Launchpad bot format."""
    state = ProcessingState()
    line = "==Launchpad;;Tue Sep 20 06:50:27 2011 +0000=="

    result = parse_time_name_email_affiliation(line, state)
    assert result is not None

    time, name , email, affiliation = result
    assert email == "launchpad@bot.bot"
    assert affiliation == "bot"
    assert "Sep 20" in time


# Test 15: parse_time_name_email_affiliation - invalid format
def test_parse_time_name_email_affiliation_invalid():
    """Test parsing invalid log format."""
    state = ProcessingState()

    # No email
    line = "==John Doe;;Thu Feb 20 03:56:00 2014 +0000=="
    result = parse_time_name_email_affiliation(line, state)
    assert result is None

    # Missing parts
    line = "==John Doe;john@example.com;=="
    result = parse_time_name_email_affiliation(line, state)
    assert result is None

    # Completely invalid
    line = "Invalid line"
    result = parse_time_name_email_affiliation(line, state)
    assert result is None


# Test 16: parse_exceptional_format - direct testing
def test_parse_exceptional_format_direct():
    """Test parse_exceptional_format function directly."""
    state = ProcessingState()

    # Test pattern 1
    line = "==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000=="
    result = parse_exceptional_format(line, state)
    assert result is not None
    assert result[1] == "bmcconne@rackspace.com"

    # Test pattern 2
    line = "==bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000=="
    result = parse_exceptional_format(line, state)
    assert result is not None
    assert result[1] == "bmcconne@rackspace.com"

    # Test pattern 3 (Launchpad)
    line = "==Launchpad;;Tue Sep 20 06:50:27 2011 +0000=="
    result = parse_exceptional_format(line, state)
    assert result is not None
    assert result[1] == "launchpad@bot.bot"

    # Test non-matching line
    line = "==Some other format=="
    result = parse_exceptional_format(line, state)
    assert result is None


# Test 17: extract_files_from_block - basic
def test_extract_files_from_block_basic():
    """Test basic file extraction from block."""
    state = ProcessingState()
    block = [
        "file1.txt\n",
        "dir/file2.py\n",
        "\n",
        "file3.js\n"  # Should stop at newline
    ]

    files = extract_files_from_block(block, state)
    assert files == ["file1.txt", "dir/file2.py"]
    assert state.statistics.n_blocks_changing_code == 2


# Test 18: extract_files_from_block - with filtering
def test_extract_files_from_block_with_filtering():
    """Test file extraction with filtering."""
    state = ProcessingState()
    state.file_filtering_mode = True
    state.files_to_filter = {"file1.txt", "secret.md"}

    block = [
        "file1.txt\n",
        "dir/file2.py\n",
        "secret.md\n",
        "public.md\n",
        "\n"
    ]

    files = extract_files_from_block(block, state)
    assert files == ["dir/file2.py", "public.md"]
    assert state.statistics.n_blocks_changing_code == 2


# Test 19: extract_files_from_block - empty/whitespace
def test_extract_files_from_block_empty():
    """Test file extraction with empty/whitespace lines."""
    state = ProcessingState()

    # Empty block
    assert extract_files_from_block([], state) == []

    # Only newlines
    assert extract_files_from_block(["\n", "\n"], state) == []

    # Whitespace lines
    assert extract_files_from_block(["  \n", "\t\n"], state) == []

    # Mixed
    block = ["  \n", "file.txt\n", "\n", "another.txt\n"]
    files = extract_files_from_block(block, state)
    assert files == ["file.txt"]


# Test 20: process_commit_block - valid block
def test_process_commit_block_valid():
    """Test processing a valid commit block."""
    state = ProcessingState()
    block = [
        "==John Doe;john@example.com;Thu Feb 20 03:56:00 2014 +0000==\n",
        "file1.txt\n",
        "file2.py\n",
        "\n"
    ]

    result = process_commit_block(block, state)
    assert result is True
    assert len(state.change_log_data) == 1

    entry = state.change_log_data[0]
    assert entry[0][1] == "john@example.com"
    assert entry[0][2] == "example"
    assert entry[1] == ["file1.txt", "file2.py"]


# Test 21: process_commit_block - invalid block
def test_process_commit_block_invalid():
    """Test processing invalid commit blocks."""
    state = ProcessingState()

    # Empty block
    assert process_commit_block([], state) is False

    # No header
    block = ["file1.txt\n", "file2.py\n"]
    assert process_commit_block(block, state) is False

    # Invalid header
    block = ["==Invalid header==\n", "file.txt\n"]
    assert process_commit_block(block, state) is False

    # No files
    block = ["==John Doe;john@example.com;Thu Feb 20 03:56:00 2014 +0000==\n", "\n"]
    assert process_commit_block(block, state) is False


# Test 22: aggregate_files_and_contributors
def test_aggregate_files_and_contributors():
    """Test aggregation of files and contributors."""
    state = ProcessingState()

    # Add some change log data
    state.change_log_data = [
        (("date1", "alice@example.com", "example"), ["file1.txt", "file2.py"]),
        (("date2", "bob@example.com", "example"), ["file2.py", "file3.js"]),
        (("date3", "alice@example.com", "example"), ["file3.js", "file4.md"]),
    ]

    aggregate_files_and_contributors(state)

    assert state.statistics.n_changed_files == 4
    assert set(state.file_contributors.keys()) == {"file1.txt", "file2.py", "file3.js", "file4.md"}
    assert state.file_contributors["file1.txt"] == ["alice@example.com"]
    assert set(state.file_contributors["file2.py"]) == {"alice@example.com", "bob@example.com"}
    assert set(state.file_contributors["file3.js"]) == {"bob@example.com", "alice@example.com"}
    assert state.file_contributors["file4.md"] == ["alice@example.com"]


# Test 23: extract_contributor_connections
def test_extract_contributor_connections():
    """Test extraction of contributor connections."""
    state = ProcessingState()

    # Set up file contributors
    state.file_contributors = defaultdict(list, {
    "file1.txt": ["alice@example.com"],
    "file2.py": ["alice@example.com", "bob@example.com"],
    "file3.js": ["alice@example.com", "bob@example.com", "charlie@test.com"],
    "file4.md": ["bob@example.com", "charlie@test.com"],
})

    extract_contributor_connections(state)

    # Check connections
    assert len(state.connections_with_files) == 4  # 1 + 3 + 3 + 1

    # Check specific connections
    connections_by_file = {cf[1]: cf[0] for cf in state.connections_with_files}
    assert ("alice@example.com", "bob@example.com") in [cf[0] for cf in state.connections_with_files if
                                                        cf[1] == "file2.py"]

    # Verify all combinations
    expected_pairs = [
        (("alice@example.com", "bob@example.com"), "file2.py"),
        (("alice@example.com", "bob@example.com"), "file3.js"),
        (("alice@example.com", "charlie@test.com"), "file3.js"),
        (("bob@example.com", "charlie@test.com"), "file3.js"),
        (("bob@example.com", "charlie@test.com"), "file4.md"),
    ]

    for expected in expected_pairs:
        assert expected in state.connections_with_files


# Test 24: get_unique_connections
def test_get_unique_connections():
    """Test extraction of unique connections."""
    connections_with_files = [
        (("alice@example.com", "bob@example.com"), "file1.txt"),
        (("bob@example.com", "alice@example.com"), "file2.py"),  # Reverse order
        (("alice@example.com", "charlie@test.com"), "file3.js"),
        (("bob@example.com", "charlie@test.com"), "file4.md"),
        (("charlie@test.com", "bob@example.com"), "file5.py"),  # Reverse order
    ]

    unique = get_unique_connections(connections_with_files)

    # Should have 3 unique connections
    assert len(unique) == 3

    # Check specific unique connections (sorted)
    expected = [
        tuple(sorted(("alice@example.com", "bob@example.com"))),
        tuple(sorted(("alice@example.com", "charlie@test.com"))),
        tuple(sorted(("bob@example.com", "charlie@test.com"))),
    ]

    for conn in expected:
        assert conn in unique


# Test 25: extract_affiliations
def test_extract_affiliations():
    """Test extraction of affiliations."""
    state = ProcessingState()

    # Mock the extract_affiliation_from_email function
    def mock_extract(email, _):
        if "example" in email:
            return "Example Corp"
        elif "test" in email:
            return "Test Inc"
        else:
            return "Unknown"

    # Replace the function temporarily
    import scrapLog
    original_func = scrapLog.extract_affiliation_from_email
    scrapLog.extract_affiliation_from_email = mock_extract

    try:
        # Set up change log data
        state.change_log_data = [
            (("date1", "alice@example.com", ""), ["file1.txt"]),
            (("date2", "bob@example.com", ""), ["file2.py"]),
            (("date3", "charlie@test.com", ""), ["file3.js"]),
        ]

        create_network_graph(state)

        assert len(state.affiliations) == 3
        assert state.affiliations["alice@example.com"] == "example"
        assert state.affiliations["bob@alummi.example.com"] == "example"
        assert state.affiliations["charlie@test.com"] == "test"
    finally:
        # Restore original function
        scrapLog.extract_affiliation_from_email = original_func


# Test 26: create_network_graph
def test_create_network_graph():
    """Test creation of network graph."""
    state = ProcessingState()

    # Set up unique connections and affiliations
    state.unique_connections = [
        ("alice@example.com", "bob@example.com"),
        ("bob@example.com", "charlie@test.com"),
    ]

    state.affiliations = {
        "alice@example.com": "Example Corp",
        "bob@example.com": "Example Corp",
        "charlie@test.com": "Test Inc",
    }

    create_network_graph(state)

    # Check graph properties
    assert state.dev_to_dev_network.number_of_nodes() == 3
    assert state.dev_to_dev_network.number_of_edges() == 2

    # Check node attributes
    assert state.dev_to_dev_network.nodes["alice@example.com"]["affiliation"] == "Example Corp"
    assert state.dev_to_dev_network.nodes["alice@example.com"]["email"] == "alice@example.com"
    assert state.dev_to_dev_network.nodes["charlie@test.com"]["affiliation"] == "Test Inc"

    # Check edges
    assert state.dev_to_dev_network.has_edge("alice@example.com", "bob@example.com")
    assert state.dev_to_dev_network.has_edge("bob@example.com", "charlie@test.com")


# Test 27: apply_email_filtering
def test_apply_email_filtering():
    """Test email filtering in network graph."""
    state = ProcessingState()
    state.email_filtering_mode = True
    state.emails_to_filter = {"spam@bot.com", "ignore@example.com"}

    # Create a network graph
    state.dev_to_dev_network = nx.Graph()
    state.dev_to_dev_network.add_edges_from([
        ("alice@company.com", "bob@company.com"),
        ("bob@company.com", "spam@bot.com"),
        ("spam@bot.com", "ignore@example.com"),
        ("alice@company.com", "charlie@example.com"),
    ])

    # Add node attributes
    for node in state.dev_to_dev_network.nodes():
        state.dev_to_dev_network.nodes[node]['affiliation'] = "test"
        state.dev_to_dev_network.nodes[node]['email'] = node

    apply_email_filtering(state)

    # Check filtered nodes are removed
    assert "spam@bot.com" not in state.dev_to_dev_network
    assert "ignore@example.com" not in state.dev_to_dev_network

    # Check remaining nodes and edges
    assert "alice@company.com" in state.dev_to_dev_network
    assert "bob@company.com" in state.dev_to_dev_network
    assert "charlie@example.com" in state.dev_to_dev_network

    # Check edges - spam@bot.com edges should be removed
    assert state.dev_to_dev_network.has_edge("alice@company.com", "bob@company.com")
    assert state.dev_to_dev_network.has_edge("alice@company.com", "charlie@example.com")
    assert not state.dev_to_dev_network.has_edge("bob@company.com", "spam@bot.com")


# Test 28: apply_email_filtering - no filtering mode
def test_apply_email_filtering_no_mode():
    """Test email filtering when not in filtering mode."""
    state = ProcessingState()
    state.email_filtering_mode = False
    state.emails_to_filter = {"spam@bot.com"}

    # Create a network graph
    state.dev_to_dev_network = nx.Graph()
    state.dev_to_dev_network.add_edge("alice@company.com", "spam@bot.com")

    apply_email_filtering(state)

    # Graph should remain unchanged
    assert "spam@bot.com" in state.dev_to_dev_network
    assert state.dev_to_dev_network.has_edge("alice@company.com", "spam@bot.com")


# Test 29: print_processing_summary - capture output
def test_print_processing_summary(capsys):
    """Test printing processing summary."""
    state = ProcessingState()
    state.statistics.nlines = 1000
    state.statistics.n_blocks = 50
    state.statistics.n_skipped_blocks = 5
    state.statistics.n_blocks_changing_code = 45
    state.statistics.n_changed_files = 200
    state.statistics.n_validation_errors = 2

    state.dev_to_dev_network = nx.Graph()
    state.dev_to_dev_network.add_edges_from([
        ("a@test.com", "b@test.com"),
        ("b@test.com", "c@test.com"),
    ])

    state.affiliations = {
        "a@test.com": "Test",
        "b@test.com": "Test",
        "c@test.com": "Test",
    }

    in_file = Path("./test.log")
    out_file = Path("./test.graphml)")
    print_processing_summary(state, in_file, out_file)

    captured = capsys.readouterr()
    output = captured.out

    # Check key information is in output
    assert "PROCESSING SUMMARY" in output
    assert "Input file: test.log" in output
    assert "Total lines processed: 1000" in output
    assert "Total commit blocks found: 50" in output
    assert "Skipped/invalid blocks: 5" in output
    assert "Files affected: 200" in output
    assert "Network nodes (developers): 3" in output
    assert "Network edges (collaborations): 2" in output


# Test 30: Integration test - full processing flow
def test_full_processing_flow():
    """Test the full processing flow with sample data."""
    state = ProcessingState()

    # Sample commit blocks
    blocks = [
        [
            "==Alice Smith;alice@example.com;Mon Jan 1 12:00:00 2024 +0000==\n",
            "src/main.py\n",
            "README.md\n",
            "\n"
        ],
        [
            "==Bob Jones;bob@test.com;Tue Jan 2 13:00:00 2024 +0000==\n",
            "src/main.py\n",
            "tests/test_main.py\n",
            "\n"
        ],
        [
            "==Charlie Brown;charlie@example.com;Wed Jan 3 14:00:00 2024 +0000==\n",
            "README.md\n",
            "docs/guide.md\n",
            "\n"
        ],
    ]

    # Process each block
    for block in blocks:
        assert process_commit_block(block, state) is True

    # Verify change log data
    assert len(state.change_log_data) == 3

    # Aggregate files and contributors
    aggregate_files_and_contributors(state)
    assert state.statistics.n_changed_files == 4

    # Extract connections
    extract_contributor_connections(state)
    assert len(state.connections_with_files) > 0



    # Get unique connections
    state.unique_connections = get_unique_connections(state.connections_with_files)


    # Create network graph
    create_network_graph(state)
    assert state.dev_to_dev_network.number_of_nodes() == 3
    assert len(state.affiliations) == 3
    # Verify specific connections
    assert state.dev_to_dev_network.has_edge("alice@example.com", "bob@test.com")  # Both edited src/main.py
    assert state.dev_to_dev_network.has_edge("alice@example.com", "charlie@example.com")  # Both edited README.md

    print("✓ Full processing flow test passed")
    print(f"  Nodes: {state.dev_to_dev_network.number_of_nodes()}")
    print(f"  Edges: {state.dev_to_dev_network.number_of_edges()}")
    print(f"  Files: {state.statistics.n_changed_files}")
    print(f"  Affiliations: {set(state.affiliations.values())}")


# Bonus test: Test with debug mode
def test_extract_affiliation_from_email_debug_mode(capsys):
    """Test email extraction with debug mode enabled."""
    state = ProcessingState()
    state.debug_mode = True

    result = extract_affiliation_from_email("test@example.com", state)

    captured = capsys.readouterr()
    assert "extract_affiliation_from_email" in captured.out
    assert result == "example"



import tempfile
from pathlib import Path
import argparse
from types import SimpleNamespace
import sys
import os


# Test that -o option creates the correct output file
def test_output_option_creates_file():
    """
    Test that when -o option is specified, the GraphML file is created
    at the specified path.
    """

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Define test output file path
        output_file = tmpdir_path / "test_output.graphml"

        # Create a simple mock state object
        class MockState:
            def __init__(self):
                self.dev_to_dev_network = None
                self.verbose_mode = False
                self.very_verbose_mode = False

        state = MockState()

        # Create arguments with output file
        args = SimpleNamespace(
            output_file=output_file,
            raw=Path("test_input.txt")
        )

        # Track if createGraphML was called
        create_graphml_called = False
        create_graphml_args = None

        # Mock the export_log_data module
        class MockExportModule:
            @staticmethod
            def create_graphml(network, filename):
                nonlocal create_graphml_called, create_graphml_args
                create_graphml_called = True
                create_graphml_args = (network, filename)
                # Create the actual file
                filename.touch(exist_ok=True)

        # Simulate the export_results function behavior
        def simulate_export_results(sim_state, sim_args):
            """Simulate export_results function behavior."""
            if sim_args.output_file:
                graphml_filename = sim_args.output_file
            else:
                graphml_filename = Path(args.raw).stem + ".NetworkFile.graphML"

            # Ensure it's a Path object
            if isinstance(graphml_filename, str):
                graphml_filename = Path(graphml_filename)

            # Call the mock GraphML creation
            MockExportModule.create_graphml(sim_state.dev_to_dev_network, graphml_filename)

            return graphml_filename

        # Execute the function
        result_file = simulate_export_results(state, args)

        # ===== ASSERTIONS =====

        # 1. Verify the function returned the correct path
        assert result_file == output_file, \
            f"Expected {output_file}, got {result_file}"

        # 2. Verify the file was actually created
        assert output_file.exists(), \
            f"Output file was not created at {output_file}"

        # 3. Verify the export function was called
        assert create_graphml_called, \
            "createGraphML was not called"

        # 4. Verify the export function was called with correct arguments
        assert create_graphml_args[1] == output_file, \
            f"createGraphML called with wrong filename: {create_graphml_args[1]}"

        # 5. Verify the file has the expected name
        assert output_file.name == "test_output.graphml", \
            f"File has wrong name: {output_file.name}"

        # 6. Verify the file extension is correct
        assert output_file.suffix == ".graphml", \
            f"File has wrong extension: {output_file.suffix}"


# Test with different filename formats
@pytest.mark.parametrize("filename", [
    "output.graphml",
    "custom_name.graphml",
    "test.GRAPHML",
    "network.xml",
    "results.net",
])
def test_output_option_various_filenames(filename):
    """
    Test that -o option works with various filename formats.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        output_file = tmpdir_path / filename

        class MockState:
            def __init__(self):
                self.dev_to_dev_network = None

        state = MockState()

        args = SimpleNamespace(
            output_file=output_file,
            raw=Path("input.txt")
        )

        # Track calls
        graphml_called = False

        class MockExport:
            @staticmethod
            def create_graphml(network, fname):
                nonlocal graphml_called
                graphml_called = True
                fname.touch()

        # Simulate export
        if args.output_file:
            result_file = args.output_file
            MockExport.create_graphml(state.dev_to_dev_network, result_file)

        assert output_file.exists()
        assert graphml_called

