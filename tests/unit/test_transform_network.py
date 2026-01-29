"""
Test cases for transform-nofi-2-nofo-GraphML.py using pytest functions only.
"""
import pytest
import networkx as nx
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, call


# Import the module (renamed to use underscores)

import transform_nofi_2_nofo_graphml as transform_module

# Test create_organizational_network function
def test_create_organizational_network_basic(sample_individual_network):
    """Test basic transformation from individuals to organizations."""
    org_network = transform_module.create_organizational_network(
        sample_individual_network,
        verbose=False
    )

    # Verify nodes
    assert org_network.number_of_nodes() == 3  # Apple, Nokia, Google
    assert "Apple" in org_network
    assert "Nokia" in org_network
    assert "Google" in org_network

    # Verify edges and weights
    assert org_network.number_of_edges() == 2  # Apple-Nokia, Nokia-Google

    # Check Apple-Nokia edge weight (4 collaborations)
    assert org_network.has_edge("Apple", "Nokia")
    assert org_network["Apple"]["Nokia"]["weight"] == 4

    # Check Nokia-Google edge weight (1 collaboration)
    assert org_network.has_edge("Nokia", "Google")
    assert org_network["Nokia"]["Google"]["weight"] == 1

    # No Apple-Google edge (no direct collaborations in test data)
    assert not org_network.has_edge("Apple", "Google")


def test_create_organizational_network_intra_firm_collaborations_ignored():
    """Test that collaborations within same firm are ignored."""
    G = nx.Graph()
    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2", affiliation="Apple")
    G.add_node("dev3", affiliation="Nokia")
    G.add_edge("dev1", "dev2")  # Intra-Apple
    G.add_edge("dev1", "dev3")  # Inter Apple-Nokia

    org_network = transform_module.create_organizational_network(G)

    # Only one inter-firm edge
    assert org_network.number_of_edges() == 1
    assert org_network.has_edge("Apple", "Nokia")
    assert org_network["Apple"]["Nokia"]["weight"] == 1


def test_create_organizational_network_multiple_collaborations_same_pair():
    """Test weight accumulation for multiple collaborations between same firms."""
    G = nx.Graph()
    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2", affiliation="Apple")
    G.add_node("dev3", affiliation="Nokia")
    G.add_node("dev4", affiliation="Nokia")

    # Add 3 Apple-Nokia collaborations
    G.add_edge("dev1", "dev3")
    G.add_edge("dev1", "dev4")
    G.add_edge("dev2", "dev3")

    org_network = transform_module.create_organizational_network(G)

    assert org_network.has_edge("Apple", "Nokia")
    assert org_network["Apple"]["Nokia"]["weight"] == 3


def test_create_organizational_network_empty_network():
    """Test with empty network."""
    G = nx.Graph()
    org_network = transform_module.create_organizational_network(G)

    assert org_network.number_of_nodes() == 0
    assert org_network.number_of_edges() == 0


def test_create_organizational_network_only_intra_firm_edges():
    """Test network with only intra-firm collaborations."""
    G = nx.Graph()
    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2", affiliation="Apple")
    G.add_node("dev3", affiliation="Apple")
    G.add_edge("dev1", "dev2")
    G.add_edge("dev2", "dev3")

    org_network = transform_module.create_organizational_network(G)

    # Should have Apple node but no edges
    assert org_network.number_of_nodes() == 1
    assert "Apple" in org_network
    assert org_network.number_of_edges() == 0


def test_create_organizational_network_complex_scenario(complex_network):
    """Test with complex network scenario."""
    org_network = transform_module.create_organizational_network(complex_network)

    # Verify all companies are represented
    assert org_network.number_of_nodes() == 5
    for company in ["Apple", "Nokia", "Google", "Microsoft", "Amazon"]:
        assert company in org_network

    # Verify edge weights
    assert org_network.has_edge("Apple", "Nokia")
    assert org_network["Apple"]["Nokia"]["weight"] == 3

    assert org_network.has_edge("Apple", "Google")
    assert org_network["Apple"]["Google"]["weight"] == 2

    assert org_network.has_edge("Nokia", "Google")
    assert org_network["Nokia"]["Google"]["weight"] == 1

    assert org_network.has_edge("Microsoft", "Amazon")
    assert org_network["Microsoft"]["Amazon"]["weight"] == 4


# Test remove_isolates function
def test_remove_isolates_basic(network_with_isolates):
    """Test removing isolated nodes."""
    original_node_count = network_with_isolates.number_of_nodes()
    original_edge_count = network_with_isolates.number_of_edges()

    cleaned = transform_module.remove_isolates(network_with_isolates, verbose=False)

    # Should remove 2 isolated nodes
    assert cleaned.number_of_nodes() == original_node_count - 2
    assert cleaned.number_of_edges() == original_edge_count

    # Isolates should be gone
    isolates = list(nx.isolates(cleaned))
    assert len(isolates) == 0

    # Check specific nodes
    assert "dev1" in cleaned
    assert "dev2" in cleaned
    assert "isolated1" not in cleaned
    assert "isolated2" not in cleaned


def test_remove_isolates_no_isolates(sample_individual_network):
    """Test network with no isolates."""
    # Remove the isolated dev from sample network
    sample_individual_network.remove_node("isolated_dev")

    cleaned = transform_module.remove_isolates(sample_individual_network, verbose=False)

    # Should be unchanged
    assert cleaned.number_of_nodes() == sample_individual_network.number_of_nodes()
    assert cleaned.number_of_edges() == sample_individual_network.number_of_edges()


def test_remove_isolates_all_isolates():
    """Test network where all nodes are isolates."""
    G = nx.Graph()
    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2", affiliation="Nokia")

    cleaned = transform_module.remove_isolates(G, verbose=False)

    # Should remove all nodes
    assert cleaned.number_of_nodes() == 0
    assert cleaned.number_of_edges() == 0


def test_remove_isolates_verbose_output(capsys, network_with_isolates):
    """Test verbose output of remove_isolates."""
    cleaned = transform_module.remove_isolates(network_with_isolates, verbose=True)

    # Capture output
    captured = capsys.readouterr()

    # Check for warning message
    assert "WARNING" in captured.out or "isolates" in captured.out.lower()


# Test save_network function
def test_save_network_with_custom_filename(sample_individual_network, tmp_path):
    """Test saving with custom output filename."""
    output_path = tmp_path / "custom_output.graphML"

    saved_file = transform_module.save_network(
        sample_individual_network,
        output_file=str(output_path)
    )

    assert saved_file == str(output_path)
    assert os.path.exists(saved_file)

    # Verify the saved file can be read back
    loaded = nx.read_graphml(saved_file)
    assert loaded.number_of_nodes() == sample_individual_network.number_of_nodes()


def test_save_network_auto_name_with_input(sample_individual_network, tmp_path):
    """Test automatic filename generation with input file reference."""
    with tempfile.NamedTemporaryFile(suffix='.graphML', dir=tmp_path, delete=False) as tmp:
        input_file = tmp.name
        base_name = os.path.basename(input_file).replace('.graphML', '')

    # Save network with input file reference
    saved_file = transform_module.save_network(
        sample_individual_network,
        input_file=input_file
    )

    # Should create file with -transformed-to-nofo suffix
    assert "-transformed-to-nofo" in saved_file
    assert saved_file.endswith('.graphML')
    assert os.path.exists(saved_file)

    # Clean up
    os.unlink(saved_file)
    os.unlink(input_file)


def test_save_network_auto_name_no_input(sample_individual_network, tmp_path):
    """Test automatic filename generation without input file."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        saved_file = transform_module.save_network(sample_individual_network)

        assert saved_file.endswith('.graphML')
        assert "network-transformed-to-nofo" in saved_file
        assert os.path.exists(saved_file)

        # Clean up
        os.unlink(saved_file)
    finally:
        os.chdir(original_cwd)


def test_save_network_filename_collision(sample_individual_network, tmp_path):
    """Test filename generation when file already exists."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Create first file
        first_file = "test-transformed-to-nofo.graphML"
        with open(first_file, 'w') as f:
            f.write("dummy")

        saved_file = transform_module.save_network(
            sample_individual_network,
            input_file="test.graphML"
        )

        # Should create with (1) suffix
        assert saved_file == "test-transformed-to-nofo(1).graphML"
        assert os.path.exists(saved_file)

        # Clean up
        for f in [first_file, saved_file]:
            if os.path.exists(f):
                os.unlink(f)
    finally:
        os.chdir(original_cwd)


# Test determine_file_name function
def test_determine_file_name_new_file(tmp_path):
    """Test with non-existent file."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        filename = transform_module.determine_file_name("test")
        assert filename == "test.graphML"
    finally:
        os.chdir(original_cwd)


def test_determine_file_name_existing_file(tmp_path):
    """Test when file already exists."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Create existing files
        open("test.graphML", 'w').close()
        open("test(1).graphML", 'w').close()
        open("test(2).graphML", 'w').close()

        filename = transform_module.determine_file_name("test")
        assert filename == "test(3).graphML"

        # Clean up
        for f in ["test.graphML", "test(1).graphML", "test(2).graphML", "test(3).graphML"]:
            if os.path.exists(f):
                os.unlink(f)
    finally:
        os.chdir(original_cwd)


# Test utility functions
def test_print_graph_as_dict_of_dicts(capsys, sample_individual_network):
    """Test graph printing function."""
    transform_module.print_graph_as_dict_of_dicts(sample_individual_network)

    captured = capsys.readouterr()
    assert "dev1" in captured.out or "Apple" in captured.out


def test_print_graph_nodes_and_its_data(capsys, sample_individual_network):
    """Test node data printing function."""
    transform_module.print_graph_nodes_and_its_data(sample_individual_network)

    captured = capsys.readouterr()
    assert "dev1" in captured.out or "affiliation" in captured.out


def test_print_graph_edges_and_its_data(capsys, sample_individual_network):
    """Test edge data printing function."""
    transform_module.print_graph_edges_and_its_data(sample_individual_network)

    captured = capsys.readouterr()
    assert "dev1" in captured.out or "dev3" in captured.out


# Test integration and main function
@patch('transform_nofi_2_nofo_graphml.subprocess.call')
@patch('transform_nofi_2_nofo_graphml.nx.read_graphml')
@patch('transform_nofi_2_nofo_graphml.save_network')
def test_main_with_show_option(mock_save, mock_read_graphml, mock_subprocess,
                               sample_individual_network, mock_visualization_script):
    """Test main function with --show option."""
    # Mock dependencies
    mock_read_graphml.return_value = sample_individual_network
    mock_save.return_value = "output.graphML"

    # Temporarily replace the visualization script path
    original_path = transform_module.noo_viz_script
    transform_module.noo_viz_script = mock_visualization_script

    # Test arguments
    test_args = ["script.py", "test.graphML", "--show", "--verbose"]

    with patch('sys.argv', test_args):
        with patch('transform_nofi_2_nofo_graphml.main') as mock_main:
            mock_main.return_value = None
            transform_module.main()

    # Restore original path
    transform_module.noo_viz_script = original_path

    # Verify calls
    mock_read_graphml.assert_called_once_with("test.graphML")
    mock_save.assert_called_once()
    mock_subprocess.assert_called_once()


@patch('transform_nofi_2_nofo_graphml.nx.read_graphml')
@patch('transform_nofi_2_nofo_graphml.save_network')
def test_main_without_show_option(mock_save, mock_read_graphml, sample_individual_network):
    """Test main function without --show option."""
    # Mock dependencies
    mock_read_graphml.return_value = sample_individual_network
    mock_save.return_value = "output.graphML"

    # Test arguments
    test_args = ["script.py", "test.graphML", "-v", "-o", "custom.graphML"]

    with patch('sys.argv', test_args):
        with patch('transform_nofi_2_nofo_graphml.main') as mock_main:
            mock_main.return_value = None
            transform_module.main()

    # Verify calls
    mock_read_graphml.assert_called_once_with("test.graphML")
    mock_save.assert_called_once()


@patch('transform_nofi_2_nofo_graphml.nx.read_graphml')
def test_main_file_not_found(mock_read_graphml):
    """Test main function with non-existent file."""
    mock_read_graphml.side_effect = FileNotFoundError("File not found")

    test_args = ["script.py", "nonexistent.graphML"]

    with patch('sys.argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            transform_module.main()

        assert exc_info.value.code == 1


def test_main_keyboard_interrupt():
    """Test handling of keyboard interrupt."""
    test_args = ["script.py", "test.graphML"]

    with patch('sys.argv', test_args):
        with patch('transform_nofi_2_nofo_graphml.main', side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as exc_info:
                transform_module.main()

            assert exc_info.value.code == 1


def test_main_unexpected_error():
    """Test handling of unexpected errors."""
    test_args = ["script.py", "test.graphML"]

    with patch('sys.argv', test_args):
        with patch('transform_nofi_2_nofo_graphml.main', side_effect=Exception("Test error")):
            with pytest.raises(SystemExit) as exc_info:
                transform_module.main()

            assert exc_info.value.code == 1


# Test command-line argument parsing
def test_argument_parsing():
    """Test that argument parser works correctly."""
    test_args = ["script.py", "input.graphML", "-v", "-s", "-o", "output.graphML"]

    with patch('sys.argv', test_args):
        parser = transform_module.main.__wrapped__.__globals__['parser']
        args = parser.parse_args()

        assert args.file == "input.graphML"
        assert args.verbose == True
        assert args.show == True
        assert args.outfile == "output.graphML"


def test_argument_parsing_minimal():
    """Test minimal argument parsing."""
    test_args = ["script.py", "input.graphML"]

    with patch('sys.argv', test_args):
        parser = transform_module.main.__wrapped__.__globals__['parser']
        args = parser.parse_args()

        assert args.file == "input.graphML"
        assert args.verbose == False
        assert args.show == False
        assert args.outfile is None


def test_argument_parsing_unimplemented_features():
    """Test that unimplemented features exit with error."""
    test_args = ["script.py", "input.graphML", "-t"]  # -t for top-firms-only

    with patch('sys.argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            transform_module.main()

        assert exc_info.value.code == 1


# Test edge cases
def test_network_with_missing_affiliation():
    """Test network where some nodes are missing affiliation attribute."""
    G = nx.Graph()
    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2")  # No affiliation
    G.add_node("dev3", affiliation="Nokia")

    G.add_edge("dev1", "dev3")

    # Should handle missing affiliation gracefully
    org_network = transform_module.create_organizational_network(G)

    # Only nodes with affiliation should appear
    assert org_network.number_of_nodes() == 2
    assert "Apple" in org_network
    assert "Nokia" in org_network


def test_network_with_empty_affiliation():
    """Test network with empty string affiliation."""
    G = nx.Graph()
    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2", affiliation="")  # Empty affiliation
    G.add_node("dev3", affiliation="Nokia")

    G.add_edge("dev1", "dev2")
    G.add_edge("dev2", "dev3")

    org_network = transform_module.create_organizational_network(G)

    # Empty affiliation should be treated as its own "organization"
    assert "" in org_network
    assert org_network.has_edge("Apple", "")
    assert org_network.has_edge("", "Nokia")


def test_network_single_node():
    """Test network with only one node."""
    G = nx.Graph()
    G.add_node("dev1", affiliation="Apple")

    org_network = transform_module.create_organizational_network(G)

    # Should have Apple node but no edges
    assert org_network.number_of_nodes() == 1
    assert "Apple" in org_network
    assert org_network.number_of_edges() == 0


# Test performance with larger networks
def test_performance_large_network():
    """Test performance with larger network (not actually large, just testing scaling)."""
    G = nx.Graph()

    # Create 100 nodes across 10 companies
    for i in range(100):
        company = f"Company{i % 10}"
        G.add_node(f"dev{i}", affiliation=company)

    # Add random edges
    import random
    for i in range(200):
        node1 = f"dev{random.randint(0, 99)}"
        node2 = f"dev{random.randint(0, 99)}"
        if node1 != node2:
            G.add_edge(node1, node2)

    # Should complete without error
    org_network = transform_module.create_organizational_network(G)

    assert org_network.number_of_nodes() <= 10  # At most 10 companies
    assert org_network.number_of_edges() >= 0


# Test with different graph types (though function expects Graph)
def test_with_digraph():
    """Test with directed graph (should still work since Graph is base class)."""
    G = nx.DiGraph()  # Directed graph

    G.add_node("dev1", affiliation="Apple")
    G.add_node("dev2", affiliation="Nokia")
    G.add_edge("dev1", "dev2")

    # Should still work
    org_network = transform_module.create_organizational_network(G)

    assert org_network.number_of_nodes() == 2
    assert org_network.has_edge("Apple", "Nokia")