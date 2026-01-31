#!/usr/bin/env python3
"""
Test suite for NetworkVisualizer class and related functionality.
"""

import pytest
import json
import tempfile
import sys
from pathlib import Path
import networkx as nx

# Import the module under test
from nofo_graphml_network_visualizer import NetworkConfig, NetworkVisualizer, parse_arguments


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


@pytest.fixture
def sample_config_with_org_filters():
    """Create a sample NetworkConfig with organization filtering."""
    return NetworkConfig(
        input_file="test.graphml",
        include_only_orgs=["A", "B", "C"],
        exclude_orgs=["D", "E"]
    )


# ============================================================================
# Test NetworkConfig initialization
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
        filter_by_org=True,
        include_only_orgs=["org1", "org2"],
        exclude_orgs=["org3"]
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
    assert config.include_only_orgs == ["org1", "org2"]
    assert config.exclude_orgs == ["org3"]

    # Test default values
    config_default = NetworkConfig(input_file="test.graphml")
    assert config_default.network_layout == "spring"
    assert config_default.node_sizing_strategy == "centrality-score"
    assert config_default.node_coloring_strategy == "random-color-to-unknown-firms"
    assert config_default.show_visualization is False
    assert config_default.verbose is False
    assert config_default.include_only_orgs is None
    assert config_default.exclude_orgs is None


# ============================================================================
# Test NetworkVisualizer initialization and graph loading
# ============================================================================

def test_network_visualizer_initialization_and_load(sample_graphml_file, sample_config):
    """Test NetworkVisualizer initialization and graph loading."""
    sample_config.input_file = sample_graphml_file

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


def test_load_graph_invalid_input_type(sample_config):
    """Test loading graph with invalid input type."""
    sample_config.input_file = 123  # Not a string or Path
    visualizer = NetworkVisualizer(sample_config)

    with pytest.raises(TypeError, match="input_file must be str or Path"):
        visualizer.load_graph()


# ============================================================================
# Test organization filtering
# ============================================================================

def test_filter_by_organization_names_include_only(sample_graphml_file, sample_config_with_org_filters):
    """Test include-only organization filtering."""
    sample_config_with_org_filters.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config_with_org_filters)
    visualizer.load_graph()

    visualizer.filter_by_organization_names()

    assert set(visualizer.graph.nodes()) == {"A", "B", "C"}
    assert visualizer.graph.number_of_nodes() == 3


def test_filter_by_organization_names_exclude_only(sample_graphml_file):
    """Test exclude-only organization filtering."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        exclude_orgs=["D", "E"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.filter_by_organization_names()

    assert set(visualizer.graph.nodes()) == {"A", "B", "C"}
    assert visualizer.graph.number_of_nodes() == 3


def test_filter_by_organization_names_include_and_exclude(sample_graphml_file):
    """Test combined include and exclude organization filtering."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C", "D"],
        exclude_orgs=["B"]  # A should be excluded even though it's in include
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.filter_by_organization_names()

    assert set(visualizer.graph.nodes()) == {"A", "C", "D"}
    assert visualizer.graph.number_of_nodes() == 3


def test_filter_by_organization_names_empty_result(sample_graphml_file):
    """Test that filtering with no matching nodes raises an error."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["NonExistentOrg1", "NonExistentOrg2"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    with pytest.raises(ValueError, match="Collaborative network has no nodes after filtering"):
        visualizer.filter_by_organization_names()


def test_filter_by_organization_names_all_excluded(sample_graphml_file):
    """Test that excluding all nodes raises an error."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        exclude_orgs=["A", "B", "C", "D", "E"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    with pytest.raises(ValueError, match="Collaborative network has no nodes after filtering"):
        visualizer.filter_by_organization_names()


def test_filter_by_organization_names_preserves_edges(sample_graphml_file):
    """Test that edges between remaining nodes are preserved after filtering."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.filter_by_organization_names()

    # Check edges are preserved
    assert visualizer.graph.has_edge("A", "B")
    assert visualizer.graph.has_edge("B", "C")
    assert visualizer.graph.has_edge("A", "C")
    assert visualizer.graph["A"]["B"]["weight"] == 5.0

    # Check edges to excluded nodes are removed
    assert not visualizer.graph.has_edge("C", "D")


def test_filter_by_org_flag_removes_isolates():
    """Test that --filter_by_org removes isolated nodes."""
    # Create a graph with an isolated node
    isolated_content = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="undirected">
    <node id="A"/>
    <node id="B"/>
    <node id="C"/>  <!-- Isolated node -->
    <edge source="A" target="B"/>
  </graph>
</graphml>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
        f.write(isolated_content)
        temp_path = Path(f.name)

    try:
        # With filter_by_org flag
        config_with = NetworkConfig(
            input_file=temp_path,
            filter_by_org=True
        )

        visualizer_with = NetworkVisualizer(config_with)
        visualizer_with.load_graph()
        visualizer_with.filter_by_organization_names()

        assert set(visualizer_with.graph.nodes()) == {"A", "B"}

        # Without filter_by_org flag
        config_without = NetworkConfig(
            input_file=temp_path,
            filter_by_org=False
        )

        visualizer_without = NetworkVisualizer(config_without)
        visualizer_without.load_graph()
        visualizer_without.filter_by_organization_names()

        assert set(visualizer_without.graph.nodes()) == {"A", "B", "C"}

    finally:
        if temp_path.exists():
            temp_path.unlink()


# ============================================================================
# Test centrality calculation
# ============================================================================

def test_calculate_centralities(sample_graphml_file, sample_config):
    """Test centrality calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    visualizer.calculate_centralities()

    assert visualizer.degree_centrality is not None
    assert len(visualizer.degree_centrality) == 5

    for node, centrality in visualizer.degree_centrality.items():
        assert node in ["A", "B", "C", "D", "E"]
        assert 0 <= centrality <= 1


def test_calculate_centralities_empty_graph():
    """Test centrality calculation with an empty graph."""
    empty_content = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="undirected">
  </graph>
</graphml>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
        f.write(empty_content)
        temp_path = Path(f.name)

    try:
        config = NetworkConfig(input_file=temp_path)
        visualizer = NetworkVisualizer(config)
        visualizer.load_graph()

        visualizer.calculate_centralities()
        assert visualizer.degree_centrality == {}

    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_calculate_centralities_after_org_filtering(sample_graphml_file):
    """Test centrality calculation after organization filtering."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    visualizer.filter_by_organization_names()
    visualizer.calculate_centralities()

    assert set(visualizer.degree_centrality.keys()) == {"A", "B", "C"}
    assert len(visualizer.degree_centrality) == 3


# ============================================================================
# Test filter_top_n_central_firms
# ============================================================================

def test_filter_top_n_central_firms(sample_graphml_file, sample_config_with_filter):
    """Test filtering to show only top N central firms."""
    sample_config_with_filter.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config_with_filter)
    visualizer.load_graph()
    visualizer.calculate_centralities()

    original_nodes = set(visualizer.graph.nodes())
    original_edges = visualizer.graph.number_of_edges()

    visualizer.filter_top_n_central_firms()

    assert visualizer.graph is not None
    assert visualizer.graph.number_of_nodes() == 2
    assert visualizer.graph.number_of_edges() <= original_edges
    assert len(visualizer.degree_centrality) == 2


def test_filter_top_n_central_firms_no_filter(sample_graphml_file, sample_config):
    """Test that filtering doesn't happen when no filter is specified."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()
    visualizer.calculate_centralities()

    original_nodes = set(visualizer.graph.nodes())
    visualizer.filter_top_n_central_firms()

    assert set(visualizer.graph.nodes()) == original_nodes
    assert visualizer.graph.number_of_nodes() == 5


def test_filter_top_n_central_firms_without_centrality(sample_graphml_file, sample_config_with_filter):
    """Test filtering when centrality hasn't been calculated."""
    sample_config_with_filter.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config_with_filter)
    visualizer.load_graph()

    with pytest.raises(ValueError, match="Centrality not calculated"):
        visualizer.filter_top_n_central_firms()


# ============================================================================
# Test color map loading and node coloring
# ============================================================================

def test_load_color_map(sample_graphml_file, sample_color_map_file, sample_config):
    """Test loading color map from JSON file."""
    sample_config.input_file = sample_graphml_file
    sample_config.color_map_file = sample_color_map_file

    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()
    visualizer.load_color_map()

    assert len(visualizer.known_org_node_colors) == 3
    assert visualizer.known_org_node_colors["A"] == [1.0, 0.0, 0.0]
    assert visualizer.known_org_node_colors["B"] == [0.0, 1.0, 0.0]
    assert visualizer.known_org_node_colors["C"] == [0.0, 0.0, 1.0]
    assert "D" not in visualizer.known_org_node_colors
    assert "E" not in visualizer.known_org_node_colors


def test_load_color_map_file_not_found(sample_graphml_file, sample_config):
    """Test handling of missing color map file."""
    sample_config.input_file = sample_graphml_file
    sample_config.color_map_file = "non_existent_file.json"

    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()
    visualizer.load_color_map()

    assert visualizer.known_org_node_colors == {}


def test_get_node_colors(sample_graphml_file, sample_config):
    """Test node color assignment."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    colors = visualizer.get_node_colors()

    assert len(colors) == visualizer.graph.number_of_nodes()
    assert all(color is not None for color in colors)


# ============================================================================
# Test command line argument parsing
# ============================================================================

def test_parse_arguments_basic(mocker):
    """Test basic command line argument parsing."""
    test_args = ["test.graphml", "-n", "circular", "-v", "-s"]

    mocker.patch.object(sys, 'argv', ['script.py'] + test_args)
    config = parse_arguments()

    assert config.input_file == Path("test.graphml")
    assert config.network_layout == "circular"
    assert config.verbose is True
    assert config.show_visualization is True
    assert config.filter_by_n_top_central_firms_only is None


def test_parse_arguments_with_org_filters(mocker):
    """Test parsing of organization filter arguments."""
    test_args = [
        "test.graphml",
        "--include-only", "nvidia,google,amazon",
        "--exclude", "user,test"
    ]

    mocker.patch.object(sys, 'argv', ['script.py'] + test_args)
    config = parse_arguments()

    assert config.include_only_orgs == ["nvidia", "google", "amazon"]
    assert config.exclude_orgs == ["user", "test"]


def test_parse_arguments_comma_separated_with_spaces(mocker):
    """Test parsing of comma-separated values with spaces."""
    test_args = [
        "test.graphml",
        "--include-only", "nvidia, google, amazon web services",
        "--exclude", "user , test , unknown"
    ]

    mocker.patch.object(sys, 'argv', ['script.py'] + test_args)
    config = parse_arguments()

    assert config.include_only_orgs == ["nvidia", "google", "amazon web services"]
    assert config.exclude_orgs == ["user", "test", "unknown"]


def test_parse_arguments_empty_comma_separated(mocker):
    """Test parsing of empty comma-separated strings."""
    test_args = [
        "test.graphml",
        "--include-only", "",
        "--exclude", ",,,"
    ]

    mocker.patch.object(sys, 'argv', ['script.py'] + test_args)
    config = parse_arguments()

    assert config.include_only_orgs is None
    assert config.exclude_orgs is None


def test_parse_arguments_no_org_filters(mocker):
    """Test when organization filters are not specified."""
    mocker.patch.object(sys, 'argv', ['script.py', 'test.graphml'])
    config = parse_arguments()

    assert config.include_only_orgs is None
    assert config.exclude_orgs is None


def test_parse_arguments_show_plot_aliases(mocker):
    """Test that all show/plot aliases work."""
    aliases = ["-s", "--show", "-p", "--plot"]

    for alias in aliases:
        test_args = ["test.graphml", alias]
        mocker.patch.object(sys, 'argv', ['script.py'] + test_args)
        config = parse_arguments()
        assert config.show_visualization is True


# ============================================================================
# Test edge cases and error handling
# ============================================================================

def test_missing_graph_operations(sample_config):
    """Test error handling when operations are called before loading graph."""
    visualizer = NetworkVisualizer(sample_config)

    with pytest.raises(ValueError, match="Graph not loaded"):
        visualizer.calculate_centralities()

    with pytest.raises(ValueError, match="Graph not loaded"):
        visualizer.visualize()


# ============================================================================
# Test visualization helper methods
# ============================================================================

def test_get_node_sizes(sample_graphml_file, sample_config):
    """Test node size calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()
    visualizer.calculate_centralities()

    sizes = visualizer.get_node_sizes()
    assert len(sizes) == visualizer.graph.number_of_nodes()
    assert all(size > 0 for size in sizes)


def test_get_edge_thickness(sample_graphml_file, sample_config):
    """Test edge thickness calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    thickness = visualizer.get_edge_thickness()
    assert len(thickness) == visualizer.graph.number_of_edges()
    assert all(t >= 1 for t in thickness)


def test_get_layout_positions(sample_graphml_file, sample_config):
    """Test layout position calculation."""
    sample_config.input_file = sample_graphml_file
    visualizer = NetworkVisualizer(sample_config)
    visualizer.load_graph()

    pos = visualizer.get_layout_positions()
    assert len(pos) == visualizer.graph.number_of_nodes()

    for node, (x, y) in pos.items():
        assert isinstance(x, float)
        assert isinstance(y, float)


# ============================================================================
# Integration tests
# ============================================================================

def test_integration_workflow(sample_graphml_file, sample_color_map_file):
    """Test the complete workflow from config to visualization."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        network_layout="spring",
        node_sizing_strategy="centrality-score",
        node_coloring_strategy="random-color-to-unknown-firms",
        focal_firm="A",
        color_map_file=sample_color_map_file,
        show_visualization=False,
        show_legend=True,
        verbose=False,
        filter_by_n_top_central_firms_only=3,
        filter_by_org=False
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()
    assert visualizer.graph.number_of_nodes() == 5

    visualizer.calculate_centralities()
    assert visualizer.degree_centrality is not None

    visualizer.filter_top_n_central_firms()
    assert visualizer.graph.number_of_nodes() == 3

    visualizer.load_color_map()
    assert len(visualizer.known_org_node_colors) == 3

    colors = visualizer.get_node_colors()
    sizes = visualizer.get_node_sizes()
    thickness = visualizer.get_edge_thickness()
    pos = visualizer.get_layout_positions()

    assert len(colors) == 3
    assert len(sizes) == 3
    assert len(thickness) == visualizer.graph.number_of_edges()
    assert len(pos) == 3


def test_organization_filtering_then_top_n_filter(sample_graphml_file):
    """Test combination of organization filtering followed by top-N filtering."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C", "D", "E"],
        filter_by_n_top_central_firms_only=2
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    visualizer.filter_by_organization_names()
    assert visualizer.graph.number_of_nodes() == 5

    visualizer.calculate_centralities()
    visualizer.filter_top_n_central_firms()

    assert visualizer.graph.number_of_nodes() == 2
    assert len(visualizer.degree_centrality) == 2


def test_case_sensitive_filtering(sample_graphml_file):
    """Test that organization filtering is case-sensitive."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["a", "b"]  # lowercase
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    with pytest.raises(ValueError, match="Collaborative network has no nodes after filtering"):
        visualizer.filter_by_organization_names()


# ============================================================================
# Test edge preservation
# ============================================================================

def test_organization_filtering_edge_count(sample_graphml_file):
    """Test that edge count is correctly reduced after organization filtering."""
    config = NetworkConfig(
        input_file=sample_graphml_file,
        include_only_orgs=["A", "B", "C"]
    )

    visualizer = NetworkVisualizer(config)
    visualizer.load_graph()

    original_edges = visualizer.graph.number_of_edges()
    visualizer.filter_by_organization_names()
    new_edges = visualizer.graph.number_of_edges()

    assert original_edges == 5
    assert new_edges == 3
    assert new_edges < original_edges


if __name__ == "__main__":
    # Run tests directly if needed
    pytest.main([__file__, "-v"])