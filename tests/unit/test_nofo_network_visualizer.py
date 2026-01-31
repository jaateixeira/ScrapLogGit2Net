#!/usr/bin/env python3
"""
Test suite for NetworkVisualizer class and related functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import networkx as nx

# tests/unit/test_nofo_network_visualizer.py
from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer, parse_arguments


# Note: Replace 'your_module_name' with the actual name of your Python file

# ============================================================================
# Fixtures for test data
# ============================================================================

@pytest.fixture
def sample_graphml_content():
    """Create sample GraphML content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>
  <graph id="G" edgedefault="undirected">
    <node id="A"/>
    <node id="B"/>
    <node id="C"/>
    <node id="D"/>
    <node id="E"/>
    <edge source="A" target="B">
      <data key="weight">5.0</data>
    </edge>
    <edge source="B" target="C">
      <data key="weight">3.0</data>
    </edge>
    <edge source="C" target="D">
      <data key="weight">2.0</data>
    </edge>
    <edge source="D" target="E">
      <data key="weight">1.0</data>
    </edge>
    <edge source="A" target="C">
      <data key="weight">4.0</data>
    </edge>
  </graph>
</graphml>"""


@pytest.fixture
def sample_graphml_file(sample_graphml_content):
    """Create a temporary GraphML file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
        f.write(sample_graphml_content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_color_map_file():
    """Create a temporary color map JSON file for testing."""
    color_map = {
        "A": [1.0, 0.0, 0.0],  # Red
        "B": [0.0, 1.0, 0.0],  # Green
        "C": [0.0, 0.0, 1.0]  # Blue
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(color_map, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_config():
    """Create a sample NetworkConfig for testing."""
    return NetworkConfig(
        input_file="test.graphml",
        network_layout="spring",
        node_sizing_strategy="centrality-score",
        node_coloring_strategy="random-color-to-unknown-firms",
        focal_firm="A",
        color_map_file=None,
        show_visualization=False,
        show_legend=False,
        verbose=False,
        filter_by_n_top_central_firms_only=None,
        filter_by_org=False
    )


@pytest.fixture
def sample_config_with_filter():
    """Create a sample NetworkConfig with filtering enabled."""
    return NetworkConfig(
        input_file="test.graphml",
        network_layout="spring",
        node_sizing_strategy="centrality-score",
        node_coloring_strategy="random-color-to-unknown-firms",
        focal_firm=None,
        color_map_file=None,
        show_visualization=False,
        show_legend=False,
        verbose=False,
        filter_by_n_top_central_firms_only=2,
        filter_by_org=False
    )


# ============================================================================
# Test Case 1: Test NetworkConfig initialization
# ============================================================================

def test_network_config_initialization():
    """Test that NetworkConfig dataclass initializes correctly."""
    config = NetworkConfig(
        input_file="test.graphml",
        network_layout="circular",
        node_sizing_strategy="all-equal",
        node_coloring_strategy="gray-color-to-unknown-firms",
        focal_firm="TestFirm",
        color_map_file="colors.json",
        show_visualization=True,
        show_legend=True,
        verbose=True,
        filter_by_n_top_central_firms_only=5,
        filter_by_org=True
    )

    assert config.input_file == "test.graphml"
    assert config.network_layout == "circular"
    assert config.node_sizing_strategy == "all-equal"
    assert config.node_coloring_strategy == "gray-color-to-unknown-firms"
    assert config.focal_firm == "TestFirm"
    assert config.color_map_file == "colors.json"
    assert config.show_visualization is True
    assert config.show_legend is True
    assert config.verbose is True
    assert config.filter_by_n_top_central_firms_only == 5
    assert config.filter_by_org is True

    # Test default values
    config_default = NetworkConfig(input_file="test.graphml")
    assert config_default.network_layout == "spring"
    assert config_default.node_sizing_strategy == "centrality-score"
    assert config_default.node_coloring_strategy == "random-color-to-unknown-firms"
    assert config_default.show_visualization is False
    assert config_default.verbose is False


# ============================================================================
# Test Case 2: Test NetworkVisualizer initialization and graph loading
# ============================================================================

def test_network_visualizer_initialization_and_load(sample_graphml_file, sample_config):
    """Test NetworkVisualizer initialization and graph loading."""
    # Update config with actual file path
    sample_config.input_file = sample_graphml_file

    # Create visualizer
    visualizer = NetworkVisualizer(sample_config)

    # Test initialization
    assert visualizer.config == sample_config
    assert visualizer.graph is None
    assert visualizer.pos is None
    assert visualizer.known_org_node_colors == {}
    assert visualizer.degree_centrality is None

    # Load graph
    visualizer.load_graph()

    # Test graph properties
    assert visualizer.graph is not None
    assert isinstance(visualizer.graph, nx.Graph)
    assert visualizer.graph.number_of_nodes() == 5
    assert visualizer.graph.number_of_edges() == 5

    # Test node existence
    expected_nodes = {"A", "B", "C", "D", "E"}
    assert set(visualizer.graph.nodes()) == expected_nodes

    # Test edge weights
    assert visualizer.graph["A"]["B"]["weight"] == 5.0
    assert visualizer.graph["B"]["C"]["weight"] == 3.0
    assert visualizer.graph["C"]["D"]["weight"] == 2.0


def test_network_visualizer_load_with_string_path(sample_graphml_file, sample_config):
    """Test loading graph with string path instead of Path object."""
    sample_config.input_file = str(sample_graphml_file)
    visualizer = NetworkVisualizer(sample_config)

    visualizer.load_graph()

    assert visualizer.graph is not None
    assert visualizer.graph.number_of_nodes() == 5
    assert visualizer.graph.number_of_edges() == 5


# ============================================================================
# Test Case 3: Test centrality calculation
# ============================================================================

def test_calculate_centralities(sample_graphml_file, sample_config):
    """Test centrality calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    # Calculate centralities
    visualizer.calculate_centralities()

    # Test centrality results
    assert visualizer.degree_centrality is not None
    assert len(visualizer.degree_centrality) == 5

    # All nodes should have centrality scores between 0 and 1
    for node, centrality in visualizer.degree_centrality.items():
        assert node in ["A", "B", "C", "D", "E"]
        assert 0 <= centrality <= 1

    # Node C should be most central (it has connections to A, B, D)
    centralities = visualizer.degree_centrality
    # Note: This assertion might need adjustment based on actual centrality algorithm
    assert "C" in centralities
    assert "A" in centralities
    assert "B" in centralities


def test_calculate_centralities_empty_graph(sample_config):
    """Test centrality calculation with an empty graph."""
    # Create an empty graph
    with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="undirected">
  </graph>
</graphml>""")
        temp_path = Path(f.name)

    try:
        sample_config.input_file = temp_path
        visualizer = NetworkVisualizer(sample_config)
        visualizer.load_graph()

        # This should handle empty graph gracefully
        visualizer.calculate_centralities()

        # Degree centrality for empty graph should be empty dict
        assert visualizer.degree_centrality == {}
    finally:
        if temp_path.exists():
            temp_path.unlink()


# ============================================================================
# Test Case 4: Test filter_top_n_central_firms (MAIN FILTERING TEST)
# ============================================================================

def test_filter_top_n_central_firms(sample_graphml_file, sample_config_with_filter):
    """Test filtering to show only top N central firms."""
    sample_config_with_filter.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config_with_filter)
    visualizer.load_graph()
    visualizer.calculate_centralities()

    # Store original graph info
    original_nodes = set(visualizer.graph.nodes())
    original_edges = visualizer.graph.number_of_edges()

    # Apply filter for top 2 central firms
    visualizer.filter_top_n_central_firms()

    # Test filtered graph
    assert visualizer.graph is not None
    assert visualizer.graph.number_of_nodes() == 2  # Should have exactly 2 nodes
    assert visualizer.graph.number_of_edges() <= original_edges  # Should have fewer or equal edges

    # Test that we have recalculated centrality for filtered graph
    assert visualizer.degree_centrality is not None
    assert len(visualizer.degree_centrality) == 2

    # Test with different N values
    test_cases = [1, 3, 5]

    for n in test_cases:
        # Reset config
        config = NetworkConfig(
            input_file=sample_graphml_file,
            filter_by_n_top_central_firms_only=n,
            # Other parameters with defaults
        )

        visualizer = NetworkVisualizer(config)
        visualizer.load_graph()
        visualizer.calculate_centralities()
        visualizer.filter_top_n_central_firms()

        # Should have exactly n nodes (or less if n > total nodes)
        expected_nodes = min(n, 5)
        assert visualizer.graph.number_of_nodes() == expected_nodes


def test_filter_top_n_central_firms_no_filter(sample_graphml_file, sample_config):
    """Test that filtering doesn't happen when no filter is specified."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()
    visualizer.calculate_centralities()

    original_nodes = set(visualizer.graph.nodes())

    # This should not change the graph since filter is None
    visualizer.filter_top_n_central_firms()

    # Graph should remain unchanged
    assert set(visualizer.graph.nodes()) == original_nodes
    assert visualizer.graph.number_of_nodes() == 5


def test_filter_top_n_central_firms_with_focal_firm(sample_graphml_file):
    """Test filtering when a focal firm is specified."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        filter_by_n_top_central_firms_only=3,
        focal_firm="A"  # Make sure A is included in top 3
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.calculate_centralities()
    visualizer.filter_top_n_central_firms()

    # After filtering, focal firm should still be in the graph if it was in top 3
    assert visualizer.graph is not None
    # We can't guarantee A is in top 3, but we can test that graph is valid
    assert visualizer.graph.number_of_nodes() == 3


# ============================================================================
# Test Case 5: Test color map loading and node coloring
# ============================================================================

def test_load_color_map(sample_graphml_file, sample_color_map_file, sample_config):
    """Test loading color map from JSON file."""
    sample_config.input_file = sample_graphml_file
    sample_config.color_map_file = sample_color_map_file

    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()
    visualizer.load_color_map()

    # Test that color map was loaded correctly
    assert len(visualizer.known_org_node_colors) == 3
    assert visualizer.known_org_node_colors["A"] == [1.0, 0.0, 0.0]
    assert visualizer.known_org_node_colors["B"] == [0.0, 1.0, 0.0]
    assert visualizer.known_org_node_colors["C"] == [0.0, 0.0, 1.0]

    # Test that D and E are not in the color map (they're not in the JSON file)
    assert "D" not in visualizer.known_org_node_colors
    assert "E" not in visualizer.known_org_node_colors


def test_load_color_map_file_not_found(sample_graphml_file, sample_config):
    """Test handling of missing color map file."""
    sample_config.input_file = sample_graphml_file
    sample_config.color_map_file = "non_existent_file.json"

    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    # This should not raise an exception but log a warning
    visualizer.load_color_map()

    # Color map should be empty
    assert visualizer.known_org_node_colors == {}


def test_get_node_colors(sample_graphml_file, sample_config):
    """Test node color assignment."""
    sample_config.input_file = sample_graphml_file

    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    # Get node colors with random coloring strategy
    colors = visualizer.get_node_colors()

    # Should return one color per node
    assert len(colors) == visualizer.graph.number_of_nodes()

    # All colors should be assigned (no None values)
    assert all(color is not None for color in colors)

    # Test with gray coloring strategy
    sample_config.node_coloring_strategy = "gray-color-to-unknown-firms"
    visualizer2 = NetworkVisualizer(sample_config)
    visualizer2.load_graph()
    colors2 = visualizer2.get_node_colors()

    # All colors should be 'gray' or RGB tuples for known nodes
    # (But since we have no color map, all should be gray)
    assert all(color == 'gray' for color in colors2)


# ============================================================================
# Test Case 6: Test command line argument parsing
# ============================================================================

def test_parse_arguments_basic():
    """Test basic command line argument parsing."""
    test_args = [
        "test.graphml",
        "-n", "circular",
        "-v",
        "-s"
    ]

    with patch('sys.argv', ['script.py'] + test_args):
        config = parse_arguments()

        assert config.input_file == Path("test.graphml")
        assert config.network_layout == "circular"
        assert config.verbose is True
        assert config.show_visualization is True
        assert config.filter_by_n_top_central_firms_only is None


def test_parse_arguments_with_filter():
    """Test command line argument parsing with filter option."""
    test_args = [
        "test.graphml",
        "-tf", "3",
        "-ff", "CompanyA",
        "-l"
    ]

    with patch('sys.argv', ['script.py'] + test_args):
        config = parse_arguments()

        assert config.input_file == Path("test.graphml")
        assert config.filter_by_n_top_central_firms_only == 3
        assert config.focal_firm == "CompanyA"
        assert config.show_legend is True


def test_parse_arguments_with_color_map():
    """Test command line argument parsing with color map."""
    test_args = [
        "test.graphml",
        "-c", "colors.json",
        "-nc", "gray-color-to-unknown-firms",
        "-ns", "all-equal"
    ]

    with patch('sys.argv', ['script.py'] + test_args):
        config = parse_arguments()

        assert config.input_file == Path("test.graphml")
        assert config.color_map_file == "colors.json"
        assert config.node_coloring_strategy == "gray-color-to-unknown-firms"
        assert config.node_sizing_strategy == "all-equal"


def test_parse_arguments_show_plot_aliases():
    """Test that all show/plot aliases work."""
    aliases = ["-s", "--show", "-p", "--plot"]

    for alias in aliases:
        test_args = ["test.graphml", alias]

        with patch('sys.argv', ['script.py'] + test_args):
            config = parse_arguments()
            assert config.show_visualization is True


# ============================================================================
# Test Case 7: Test edge cases and error handling
# ============================================================================

def test_invalid_input_file_type(sample_config):
    """Test handling of invalid input file type."""
    sample_config.input_file = 123  # Not a string or Path
    visualizer = NetworkVisualizer(sample_config)

    with pytest.raises(TypeError, match="input_file must be str or Path"):
        visualizer.load_graph()


def test_missing_graph_operations(sample_config):
    """Test error handling when operations are called before loading graph."""
    visualizer = NetworkVisualizer(sample_config)

    # All these should raise ValueError because graph is not loaded
    with pytest.raises(ValueError, match="Graph not loaded"):
        visualizer.calculate_centralities()

    with pytest.raises(ValueError, match="Graph not loaded"):
        visualizer.visualize()


def test_filter_without_centrality(sample_graphml_file, sample_config_with_filter):
    """Test filtering when centrality hasn't been calculated."""
    sample_config_with_filter.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config_with_filter)
    visualizer.load_graph()

    # Should raise ValueError because centrality hasn't been calculated
    with pytest.raises(ValueError, match="Centrality not calculated"):
        visualizer.filter_top_n_central_firms()


# ============================================================================
# Test Case 8: Test visualization helper methods
# ============================================================================

def test_get_node_sizes(sample_graphml_file, sample_config):
    """Test node size calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()
    visualizer.calculate_centralities()

    # Test centrality-based sizing
    sizes = visualizer.get_node_sizes()
    assert len(sizes) == visualizer.graph.number_of_nodes()
    assert all(size > 0 for size in sizes)

    # Test all-equal sizing
    sample_config.node_sizing_strategy = "all-equal"
    visualizer2 = NetworkVisualizer(sample_config)
    visualizer2.load_graph()
    sizes2 = visualizer2.get_node_sizes()
    assert all(size == 100 for size in sizes2)


def test_get_edge_thickness(sample_graphml_file, sample_config):
    """Test edge thickness calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    thickness = visualizer.get_edge_thickness()
    assert len(thickness) == visualizer.graph.number_of_edges()
    assert all(t >= 1 for t in thickness)  # log2(1) = 0, plus 1


def test_get_layout_positions(sample_graphml_file, sample_config):
    """Test layout position calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    # Test spring layout
    pos = visualizer.get_layout_positions()
    assert len(pos) == visualizer.graph.number_of_nodes()
    for node, (x, y) in pos.items():
        assert isinstance(x, float)
        assert isinstance(y, float)

    # Test circular layout
    sample_config.network_layout = "circular"
    visualizer2 = NetworkVisualizer(sample_config)
    visualizer2.load_graph()
    pos2 = visualizer2.get_layout_positions()
    assert len(pos2) == visualizer2.graph.number_of_nodes()


# ============================================================================
# Integration Test
# ============================================================================

def test_integration_workflow(sample_graphml_file, sample_color_map_file):
    """Test the complete workflow from config to visualization."""
    # Create a comprehensive config
    config = NetworkConfig(
        input_file=sample_graphml_file,
        network_layout="spring",
        node_sizing_strategy="centrality-score",
        node_coloring_strategy="random-color-to-unknown-firms",
        focal_firm="A",
        color_map_file=sample_color_map_file,
        show_visualization=False,  # Don't show during test
        show_legend=True,
        verbose=False,
        filter_by_n_top_central_firms_only=3,
        filter_by_org=False
    )

    # Run the complete workflow
    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    assert visualizer.graph.number_of_nodes() == 5

    visualizer.calculate_centralities()
    assert visualizer.degree_centrality is not None

    visualizer.filter_top_n_central_firms()
    assert visualizer.graph.number_of_nodes() == 3

    visualizer.load_color_map()
    assert len(visualizer.known_org_node_colors) == 3

    # Test visualization preparation methods
    colors = visualizer.get_node_colors()
    sizes = visualizer.get_node_sizes()
    thickness = visualizer.get_edge_thickness()
    pos = visualizer.get_layout_positions()

    assert len(colors) == 3
    assert len(sizes) == 3
    assert len(thickness) == visualizer.graph.number_of_edges()
    assert len(pos) == 3

    # Note: We're not actually calling visualize() because it creates plots
    # But we've tested all the components


# ============================================================================
# Test Case 1: Test empty filtering results in error
# ============================================================================

def test_filter_by_organization_names_empty_result(sample_graphml_file):
    """Test that filtering with no matching nodes raises an error."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    # Test include-only that doesn't match any nodes
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["NonExistentOrg1", "NonExistentOrg2"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    # Should raise ValueError when no nodes remain
    with pytest.raises(ValueError, match="Collaborative network has no nodes after filtering"):
        visualizer.filter_by_organization_names()


def test_filter_by_organization_names_all_excluded(sample_graphml_file):
    """Test that excluding all nodes raises an error."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    config = NetworkConfig(
        input_file=sample_graphml_file,
        exclude_orgs=["A", "B", "C", "D", "E"]  # Exclude all nodes
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    with pytest.raises(ValueError, match="Collaborative network has no nodes after filtering"):
        visualizer.filter_by_organization_names()


# ============================================================================
# Test Case 2: Test combined include-exclude edge cases
# ============================================================================

def test_filter_include_and_exclude_same_organization(sample_graphml_file):
    """Test when an organization is both included and excluded (exclude should win)."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    # "A" is in both include and exclude - exclude should take precedence
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"],
        exclude_orgs=["A"]  # A should be excluded even though it's in include
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.filter_by_organization_names()

    # Should have only B and C (A was excluded)
    assert set(visualizer.graph.nodes()) == {"B", "C"}
    assert visualizer.graph.number_of_nodes() == 2


def test_filter_include_only_with_non_existent_orgs(sample_graphml_file):
    """Test include-only with some organizations that don't exist in the graph."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "C", "NonExistent1", "NonExistent2"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.filter_by_organization_names()

    # Should only keep A and C (the ones that actually exist)
    assert set(visualizer.graph.nodes()) == {"A", "C"}
    assert visualizer.graph.number_of_nodes() == 2


# ============================================================================
# Test Case 3: Test filter_by_org flag with organization filtering
# ============================================================================

def test_filter_by_org_flag_removes_isolates(sample_graphml_content):
    """Test that --filter_by_org removes isolated nodes after organization filtering."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    # Create a graph where filtering leaves isolated nodes
    isolated_content = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>
  <graph id="G" edgedefault="undirected">
    <node id="A"/>
    <node id="B"/>
    <node id="C"/>
    <node id="D"/>  <!-- This will be isolated after filtering -->
    <edge source="A" target="B">
      <data key="weight">5.0</data>
    </edge>
    <edge source="B" target="C">
      <data key="weight">3.0</data>
    </edge>
  </graph>
</graphml>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
        f.write(isolated_content)
        temp_path = Path(f.name)

    try:
        # Test WITH filter_by_org flag
        config_with_flag = NetworkConfig(
            input_file=temp_path,
            include_only_orgs=["A", "B", "C", "D"],  # Include all
            filter_by_org=True  # Should remove isolated node D
        )

        visualizer_with = NetworkVisualizer(config_with_flag)
        visualizer_with.load_graph()
        visualizer_with.filter_by_organization_names()

        # D should be removed because it's isolated
        assert set(visualizer_with.graph.nodes()) == {"A", "B", "C"}
        assert visualizer_with.graph.number_of_nodes() == 3

        # Test WITHOUT filter_by_org flag
        config_without_flag = NetworkConfig(
            input_file=temp_path,
            include_only_orgs=["A", "B", "C", "D"],
            filter_by_org=False  # Should keep isolated node D
        )

        visualizer_without = NetworkVisualizer(config_without_flag)
        visualizer_without.load_graph()
        visualizer_without.filter_by_organization_names()

        # D should be kept even though it's isolated
        assert set(visualizer_without.graph.nodes()) == {"A", "B", "C", "D"}
        assert visualizer_without.graph.number_of_nodes() == 4

    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_filter_by_org_with_empty_graph_after_filtering():
    """Test that filter_by_org doesn't cause issues when graph is already empty."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    # Create a minimal graph
    minimal_content = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="undirected">
    <node id="A"/>
    <node id="B"/>
    <edge source="A" target="B"/>
  </graph>
</graphml>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
        f.write(minimal_content)
        temp_path = Path(f.name)

    try:
        config = NetworkConfig(
            input_file=temp_path,
            include_only_orgs=["NonExistent"],  # No matching nodes
            filter_by_org=True
        )

        visualizer = NetworkVisualizer(config)
        visualizer.load_graph()

        # Should raise error about empty graph, not about filter_by_org
        with pytest.raises(ValueError, match="Collaborative network has no nodes after filtering"):
            visualizer.filter_by_organization_names()

    finally:
        if temp_path.exists():
            temp_path.unlink()


# ============================================================================
# Test Case 4: Test organization filtering with edge preservation
# ============================================================================

def test_organization_filtering_preserves_correct_edges(sample_graphml_file):
    """Test that edges between remaining nodes are preserved after filtering."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"]  # These nodes have edges between them
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.filter_by_organization_names()

    # Check that edges between remaining nodes are preserved
    assert visualizer.graph.has_edge("A", "B")
    assert visualizer.graph.has_edge("B", "C")
    assert visualizer.graph.has_edge("A", "C")

    # Check edge weights are preserved
    assert visualizer.graph["A"]["B"]["weight"] == 5.0
    assert visualizer.graph["B"]["C"]["weight"] == 3.0

    # Edges to D and E should be removed
    assert not visualizer.graph.has_edge("C", "D")
    assert not visualizer.graph.has_edge("D", "E")


def test_organization_filtering_edge_count_correct(sample_graphml_file):
    """Test that edge count is correctly reduced after organization filtering."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    # Original graph has 5 edges total
    # If we keep A, B, C only, we should keep edges: A-B, B-C, A-C (3 edges)
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    original_edges = visualizer.graph.number_of_edges()  # Should be 5
    visualizer.filter_by_organization_names()
    new_edges = visualizer.graph.number_of_edges()  # Should be 3

    assert original_edges == 5
    assert new_edges == 3
    assert new_edges < original_edges


# ============================================================================
# Test Case 5: Test CLI argument parsing for organization filters
# ============================================================================

def test_parse_arguments_comma_separated_include():
    """Test parsing of comma-separated include-only argument."""
    from nofo_graphml_network_visualizer import parse_arguments

    test_args = [
        "test.graphml",
        "--include-only", "nvidia,google,amazon",
        "--exclude", "user,test"
    ]

    with patch('sys.argv', ['script.py'] + test_args):
        config = parse_arguments()

        assert config.include_only_orgs == ["nvidia", "google", "amazon"]
        assert config.exclude_orgs == ["user", "test"]


def test_parse_arguments_comma_separated_with_spaces():
    """Test parsing of comma-separated values with spaces."""
    from nofo_graphml_network_visualizer import parse_arguments

    test_args = [
        "test.graphml",
        "--include-only", "nvidia, google, amazon web services",
        "--exclude", "user , test , unknown"
    ]

    with patch('sys.argv', ['script.py'] + test_args):
        config = parse_arguments()

        # Spaces should be stripped
        assert config.include_only_orgs == ["nvidia", "google", "amazon web services"]
        assert config.exclude_orgs == ["user", "test", "unknown"]


def test_parse_arguments_empty_comma_separated():
    """Test parsing of empty comma-separated strings."""
    from nofo_graphml_network_visualizer import parse_arguments

    test_args = [
        "test.graphml",
        "--include-only", "",
        "--exclude", ",,,"  # Multiple commas
    ]

    with patch('sys.argv', ['script.py'] + test_args):
        config = parse_arguments()

        # Empty strings should result in None (converted from empty list)
        assert config.include_only_orgs is None
        assert config.exclude_orgs is None


def test_parse_arguments_no_org_filters():
    """Test when organization filters are not specified."""
    from nofo_graphml_network_visualizer import parse_arguments

    test_args = ["test.graphml"]

    with patch('sys.argv', ['script.py'] + test_args):
        config = parse_arguments()

        assert config.include_only_orgs is None
        assert config.exclude_orgs is None


# ============================================================================
# Test Case 6: Test integration of organization filtering with other features
# ============================================================================

def test_organization_filtering_before_centrality(sample_graphml_file):
    """Test that organization filtering happens before centrality calculation."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    # Filter first
    visualizer.filter_by_organization_names()
    assert set(visualizer.graph.nodes()) == {"A", "B", "C"}

    # Then calculate centrality
    visualizer.calculate_centralities()

    # Centrality should only be calculated for A, B, C
    assert set(visualizer.degree_centrality.keys()) == {"A", "B", "C"}
    assert len(visualizer.degree_centrality) == 3


def test_organization_filtering_then_top_n_filter(sample_graphml_file):
    """Test combination of organization filtering followed by top-N filtering."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C", "D", "E"],  # Keep all initially
        filter_by_n_top_central_firms_only=2
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    # Organization filtering (keeps all in this case)
    visualizer.filter_by_organization_names()
    assert visualizer.graph.number_of_nodes() == 5

    # Calculate centrality on all nodes
    visualizer.calculate_centralities()

    # Then apply top-N filter
    visualizer.filter_top_n_central_firms()

    # Should have exactly 2 nodes (top 2 most central from A-E)
    assert visualizer.graph.number_of_nodes() == 2
    assert len(visualizer.degree_centrality) == 2


def test_organization_filtering_then_top_n_filter_with_color_map(sample_graphml_file, sample_color_map_file):
    """Test organization filtering, top-N filtering, and color map integration."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"],  # Filter to A, B, C
        filter_by_n_top_central_firms_only=2,  # Then take top 2
        color_map_file=sample_color_map_file
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    # Organization filtering
    visualizer.filter_by_organization_names()
    assert set(visualizer.graph.nodes()) == {"A", "B", "C"}

    # Calculate centrality
    visualizer.calculate_centralities()

    # Top-N filtering
    visualizer.filter_top_n_central_firms()
    assert visualizer.graph.number_of_nodes() == 2

    # Load color map (should only load colors for remaining nodes)
    visualizer.load_color_map()

    # Color map should only contain colors for nodes that are still in the graph
    # After organization filtering and top-N filtering
    remaining_nodes = set(visualizer.graph.nodes())
    for node in visualizer.known_org_node_colors:
        assert node in remaining_nodes


# ============================================================================
# Test Case 7: Test error messages and console output
# ============================================================================

def test_filter_error_message_includes_filter_details(sample_graphml_file):
    """Test that error message includes details about applied filters."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["NonExistent1", "NonExistent2"],
        exclude_orgs=["AlsoNonExistent"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    # Capture the error and check its message
    with pytest.raises(ValueError) as exc_info:
        visualizer.filter_by_organization_names()

    error_msg = str(exc_info.value)

    # Check that error message contains filter information
    assert "Collaborative network has no nodes after filtering" in error_msg
    assert "Include filter" in error_msg or "Include-only" in error_msg
    # Note: The exact format depends on your implementation


def test_filter_with_case_sensitivity(sample_graphml_file):
    """Test that organization filtering is case-sensitive."""
    from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer

    # Graph has nodes "A", "B", "C" (uppercase)
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["a", "b"]  # lowercase - should not match
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    # Should raise error because "a" and "b" don't match "A" and "B"
    with pytest.raises(ValueError, match="Collaborative network has no nodes after filtering"):
        visualizer.filter_by_organization_names()



if __name__ == "__main__":
    # Run tests directly if needed
    pytest.main([__file__, "-v"])