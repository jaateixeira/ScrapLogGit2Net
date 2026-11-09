import networkx as nx
from networkx import Graph

class AffiliationValidationError(ValueError):
    """Raised when a graph cannot be made safe for GraphML export."""


def validate_all_graph_edges_have_weights(wg: Graph) -> bool:
    """Check all edges have weight attribute."""
    for u, v, data in wg.edges(data=True):
        if 'weight' not in data:
            return False
    return True


def _nodes_missing_affiliation(graph: nx.Graph) -> list[str]:
    """Return a list of node IDs that have no 'affiliation' attribute."""
    return [
        node
        for node in graph.nodes()
        if "affiliation" not in graph.nodes[node]
           or graph.nodes[node]["affiliation"] is None
    ]

def validate_all_graph_nodes_have_affiliation_attributes(graph: nx.Graph) -> tuple[bool, list[str]]:
    """
    Validate that every node in *graph* carries a non-None 'affiliation' attribute.

    Returns:
        (is_valid, missing_nodes)
        is_valid     – True if the graph is ready for export, False otherwise.
        missing_nodes – List of node IDs lacking the attribute (empty if valid).

    Example:
        >>> is_valid, missing = validate_affiliation_attributes(g)
        >>> if not is_valid:
        ...     print(f"{len(missing)} nodes need affiliation before export")
    """
    missing = _nodes_missing_affiliation(graph)
    return (len(missing) == 0), missing