"""
In action with argument 'inter_individual_graph_unweighted'
from state, mostly parsed_change_log_entries structure, creates an unweighted network social network

See for more information
----
Teixeira, J., Robles, G. & González-Barahona, J.M. Lessons learned from applying social network analysis
on an  industrial Free/Libre/Open Source Software ecosystem. J Internet Serv Appl 6, 14 (2015).
https://doi.org/10.1186/s13174-015-0028-2
----

"""

import networkx as nx
from networkx import Graph
from typing import Optional

from core.models import ProcessingState

from utils.unified_console import console, Table, inspect, print_info, print_error, print_success, print_warning


def extract_unweighted_from_parsed_change_log_entries(state:ProcessingState) -> Graph | None:
    """Extract temporal network from parsed changelog entries.

    Returns:
        TemporalGraph if successful, None if no data available
    """
    # Implementation here

    parsed_change_log_entries = state.parsed_change_log_entries


    graph = nx.Graph()
    return NotImplemented



def extract_unweighted_from_weighted_network(
        state: ProcessingState,
        weighted_graph: nx.Graph,
        min_weight_threshold: int = 1
) -> Optional[nx.Graph]:
    """Extract unweighted network from weighted graph by thresholding edges.

    Args:
        state: ProcessingState for debug output
        weighted_graph: Input weighted graph (all edges must have 'weight' attribute)
        min_weight_threshold: Minimum weight to keep edge (default: 1)

    Returns:
        New unweighted graph or None if input empty

    Raises:
        ValueError: If threshold negative or any edge missing weight
    """

    console.rule("\n")
    print_info(f"Extracting unweighted network from extracted weighted static network {weighted_graph=}")


    if min_weight_threshold < 0:
        raise ValueError(f"Threshold must be non-negative, got {min_weight_threshold}")

    if weighted_graph is None or weighted_graph.number_of_nodes() == 0:
        if state.verbose_mode:
            print_warning("Input graph empty, returning None")
        return None

    # Validate all edges have weights
    edges_missing_weight = [(u, v) for u, v, d in weighted_graph.edges(data=True) if 'weight' not in d]
    if edges_missing_weight:
        error_msg = f"{len(edges_missing_weight)} edges missing 'weight' attribute"
        if state.very_verbose_mode:
            print_error(error_msg)
            print_info(f"Sample: {edges_missing_weight[:5]}")
        raise ValueError(error_msg)

    if state.verbose_mode:
        weights = [d['weight'] for _, _, d in weighted_graph.edges(data=True)]
        print_info(f"\nThresholding: {weighted_graph.number_of_edges()} edges, "
              f"threshold={min_weight_threshold}, "
              f"weights=[{min(weights):.1f}-{max(weights):.1f}]")

    # Filter edges and create new graph
    edges_to_keep = [
        (u, v) for u, v, d in weighted_graph.edges(data=True)
        if d['weight'] >= min_weight_threshold
    ]

    result = nx.Graph()
    result.add_nodes_from(weighted_graph)
    result.add_edges_from(edges_to_keep)

    if state.verbose_mode:
        kept = len(edges_to_keep)
        total = weighted_graph.number_of_edges()
        print_info(f"Kept: {kept}/{total} edges ({kept / total * 100:.1f}%)")
        print_info(f"Isolated nodes: {len(list(nx.isolates(result)))}")

    print_success("Extracted unweighted network")

    return result

