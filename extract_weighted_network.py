"""
In action with argument 'inter_individual_multigraph_weighted'
from state, mostly parsed_change_log_entries structure, creates an weighted network social network

See for more information
---
Osborne, C., Daneshyan, F., He, R., Ye, H., Zhang, Y., & Zhou, M. (2025). Characterising open source
co-opetition in company-hosted open source software projects: the cases of PyTorch, TensorFlow, and
transformers. Proceedings of the ACM on Human-Computer Interaction, 9(2), 1-30.

and

Teixeira, J., Robles, G. & González-Barahona, J.M. Lessons learned from applying social network analysis
on an  industrial Free/Libre/Open Source Software ecosystem. J Internet Serv Appl 6, 14 (2015).
https://doi.org/10.1186/s13174-015-0028-2
----

"""

import networkx as nx
import networkx_temporal as tx
from networkx_temporal import TemporalGraph
from networkx import Graph
import matplotlib.pyplot as plt
import networkx as nx
from typing import Optional, Dict, Any


from extract_temporal_network import print_first_n_temporal_edges

from utils.unified_console import  console, Table, inspect,print_info, print_error, print_success
from core.models import ProcessingState
from utils.validators import validate_all_graph_edges_have_weights




def show_weighted_edges(G: nx.Graph, max_edges: int = 10, title: str = "Weighted Graph Edges"):
    """
    Display the first N edges of a weighted graph using Rich formatting.

    Parameters:
    -----------
    G : nx.Graph
        The weighted NetworkX graph
    max_edges : int
        Maximum number of edges to display (default: 10)
    title : str
        Title for the display
    """

    # Get all edges with data
    edges = list(G.edges(data=True))
    total_edges = len(edges)

    # Determine how many to show
    show_edges = edges[:max_edges]
    remaining = total_edges - len(show_edges)

    # Create a Rich table
    table = Table(title=f"{title} (showing {len(show_edges)} of {total_edges} edges)")

    # Add columns
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Target", style="magenta", no_wrap=True)
    table.add_column("Weight", style="green", justify="right")
    table.add_column("Additional Data", style="yellow")

    # Add rows
    for u, v, data in show_edges:
        weight = data.get('weight', 'N/A')
        # Get other data excluding 'weight'
        other_data = {k: v for k, v in data.items() if k != 'weight'}

        table.add_row(
            str(u),
            str(v),
            f"{weight:.2f}" if isinstance(weight, (int, float)) else str(weight),
            str(other_data) if other_data else ""
        )

    # Print the table
    console.print(table)

    # Show summary if there are more edges
    if remaining > 0:
        console.print(f"[dim]... and {remaining} more edges not shown[/dim]")

    # Print edge count summary
    console.print(f"\n[bold blue]Edge Statistics:[/bold blue]")
    console.print(f"  Total edges: {total_edges}")
    console.print(f"  Displayed: {len(show_edges)}")
    if remaining > 0:
        console.print(f"  Hidden: {remaining}")

def draw_weighted_network(G: nx.Graph,
                          threshold: float = 0.5,
                          node_size: int = 700,
                          font_size: int = 20,
                          width: int = 6,
                          show_labels: bool = True,
                          show_edge_weights: bool = True,
                          seed: Optional[int] = 7,
                          figsize: tuple = (10, 8),
                          **kwargs) -> None:
    """
    Draw a weighted NetworkX graph with different styles for edges above/below threshold.

    Parameters:
    -----------
    G : nx.Graph
        The weighted graph to draw
    threshold : float
        Threshold for distinguishing between large and small weights
    node_size : int
        Size of nodes
    font_size : int
        Size of node labels
    width : int
        Width of edges
    show_labels : bool
        Whether to show node labels
    show_edge_weights : bool
        Whether to show edge weight labels
    seed : int or None
        Seed for layout reproducibility
    figsize : tuple
        Figure size (width, height)
    **kwargs : dict
        Additional arguments passed to draw_networkx_edges
    """

    # Create figure
    plt.figure(figsize=figsize)

    # Separate edges based on weight threshold
    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d.get("weight", 0) > threshold]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d.get("weight", 0) <= threshold]

    # Calculate layout
    pos = nx.spring_layout(G, seed=seed)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=node_size)

    # Draw edges with different styles
    if elarge:
        nx.draw_networkx_edges(G, pos, edgelist=elarge, width=width, **kwargs)

    if esmall:
        nx.draw_networkx_edges(
            G, pos, edgelist=esmall, width=width, alpha=0.5,
            edge_color="b", style="dashed", **kwargs
        )

    # Draw node labels if requested
    if show_labels:
        nx.draw_networkx_labels(G, pos, font_size=font_size, font_family="sans-serif")

    # Draw edge weight labels if requested
    if show_edge_weights:
        edge_labels = nx.get_edge_attributes(G, "weight")
        # Format weights to 1 decimal place for cleaner display
        edge_labels = {k: f"{v:.1f}" for k, v in edge_labels.items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels)

    # Adjust plot
    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# Example usage with your data
if __name__ == "__main__":
    # Create example graph
    G = nx.Graph()

    G.add_edge("a", "b", weight=0.6)
    G.add_edge("a", "c", weight=0.2)
    G.add_edge("c", "d", weight=0.1)
    G.add_edge("c", "e", weight=0.7)
    G.add_edge("c", "f", weight=0.9)
    G.add_edge("a", "d", weight=0.3)

    # Draw with default parameters
    draw_weighted_network(G)

    # Or customize:
    # draw_weighted_network(G, threshold=0.4, node_size=500, font_size=16, figsize=(12, 8))


def extract_weighted_from_parsed_change_log_entries(state:ProcessingState) -> Graph | None:
    return NotImplemented


def extract_weighted_from_extracted_temporal_network(state:ProcessingState, extracted_temporal_network:TemporalGraph) -> Graph | None:
    """Extract weighted network from parsed changelog entries.

    developers are connected in the network by the number of common edited files

    Returns:
        weighted networks if successful, None if no data available
    """

    #if extracted_temporal_network is None:
    #    console.error("No temporal network data available - Can't transform to weighted network")
    #    return None

    console.rule("\n")
    print_info(f"Extracting weighted network from extracted temporal network {extracted_temporal_network=}")

    if state.verbose_mode or state.very_verbose_mode or state.very_verbose_mode:
        print_first_n_temporal_edges(extracted_temporal_network)


    G = nx.Graph()


    weighted_temporal_graph: tx.TemporalGraph = tx.from_multigraph(extracted_temporal_network)

    if state.verbose_mode or state.very_verbose_mode or state.very_verbose_mode:
        console.print(f"{weighted_temporal_graph.edges()=}")


    static_weighted_graph: nx.Graph = weighted_temporal_graph.to_static()

    if state.verbose_mode or state.very_verbose_mode or state.very_verbose_mode:
        console.print(f"{static_weighted_graph.edges()}")
        show_weighted_edges(static_weighted_graph,title="static_weighted_graph from weighted_temporal_graph.to_static()")


    console.print(f"{ static_weighted_graph=}")


    for u, v, data in static_weighted_graph.edges(data=True):
        try:
            edge_weight= data["weight"]
        except KeyError:
            print(f"Warning: No weight attribute for edge {u}-{v}, using default weight=1")
            edge_weight = 1
        G.add_edge(u,v, weight=edge_weight)



    validate_all_graph_edges_have_weights(G)

    show_weighted_edges(G)

    #draw_weighted_network(G)
    #draw_weighted_network(G, threshold=0.4, node_size=500, font_size=16, figsize=(12, 8))

    return G