"""
Plotting temporal networks (snapshots and animations).
"""

from typing import Literal, Optional, Any
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scraplog.utils.unified_console import print_info, print_warning, console
from typing import Any, Optional
from datetime import datetime


PlotFormat = Literal["snapshots", "animation", "both", "interactive"]


def plot_temporal_network(
        graph,
        state,
        plot_format: PlotFormat = "snapshots",
        max_snapshots: int = 6,
        filename: str = 'temporal_network',
        figsize: tuple = (15, 10),
        animation_interval: int = 800,
        layout_algorithm: str = "spring",
        show_labels: bool = True,
        node_size: int = 300,
        node_color: str = 'lightblue',
        edge_color: str = 'gray',
        title: str = "Temporal Network Evolution"
) -> Optional[Any]:
    """
    Unified function to plot temporal networks in various formats.

    Args:
        graph: Sliced temporal graph (after calling .slice())
        state: Processing state object with debug_mode and verbose flags
        plot_format: Type of plot - "snapshots", "animation", "both", or "interactive"
        max_snapshots: Maximum number of snapshots to show (for snapshots plot)
        filename: Base filename for saving (without extension)
        figsize: Figure size as (width, height)
        animation_interval: Milliseconds between animation frames
        layout_algorithm: Layout algorithm ('spring', 'kamada_kawai', 'circular', 'random')
        show_labels: Whether to show node labels
        node_size: Size of nodes
        node_color: Color of nodes
        edge_color: Color of edges
        title: Plot title

    Returns:
        For "animation" format, returns animation object. For others, returns None.
    """

    # Validate graph has snapshots
    if not hasattr(graph, '__len__') or len(graph) == 0:
        print_warning("No snapshots to plot")
        return None

    n_snapshots = len(graph)

    # Get positions once for all snapshots (for consistent layout)
    combined_pos = _compute_positions(graph, layout_algorithm)

    if plot_format in ["snapshots", "both"]:
        _plot_snapshots(
            graph=graph,
            state=state,
            n_snapshots=n_snapshots,
            max_snapshots=max_snapshots,
            combined_pos=combined_pos,
            figsize=figsize,
            show_labels=show_labels,
            node_size=node_size,
            node_color=node_color,
            edge_color=edge_color,
            title=title,
            filename=filename
        )

    if plot_format in ["animation", "both"]:
        anim = _create_animation(
            graph=graph,
            state=state,
            n_snapshots=n_snapshots,
            combined_pos=combined_pos,
            figsize=figsize,
            show_labels=show_labels,
            node_size=node_size,
            node_color=node_color,
            edge_color=edge_color,
            title=title,
            interval=animation_interval,
            filename=filename
        )

        if plot_format == "animation":
            return anim

    return None


def _compute_positions(graph, layout_algorithm: str = "spring") -> dict:
    """Compute consistent node positions across all snapshots."""
    # Collect all nodes across all snapshots
    all_nodes = set()
    for snapshot in graph:
        all_nodes.update(snapshot.nodes())

    # Create combined graph for layout
    combined = nx.Graph()
    for snapshot in graph:
        combined.add_edges_from(snapshot.edges())

    # Compute layout
    if combined.number_of_nodes() == 0:
        return {}

    if layout_algorithm == "spring":
        return nx.spring_layout(combined, seed=42, k=2)
    elif layout_algorithm == "kamada_kawai":
        return nx.kamada_kawai_layout(combined)
    elif layout_algorithm == "circular":
        return nx.circular_layout(combined)
    elif layout_algorithm == "random":
        return nx.random_layout(combined, seed=42)
    else:
        return nx.spring_layout(combined, seed=42, k=2)


def _plot_snapshots(graph, state, n_snapshots, max_snapshots, combined_pos,
                    figsize, show_labels, node_size, node_color, edge_color,
                    title, filename):
    """Plot individual snapshots in a grid."""

    n_to_plot = min(n_snapshots, max_snapshots)
    n_cols = min(3, n_to_plot)
    n_rows = (n_to_plot + n_cols - 1) // n_cols

    fig = plt.figure(figsize=figsize)

    for idx in range(n_to_plot):
        ax = fig.add_subplot(n_rows, n_cols, idx + 1)

        snapshot = graph[idx]
        time_str = _get_snapshot_time(snapshot, idx)

        if snapshot.number_of_nodes() > 0:
            # Filter positions to only nodes in this snapshot
            pos = {node: combined_pos[node] for node in snapshot.nodes()
                   if node in combined_pos}

            nx.draw(
                snapshot, pos, ax=ax,
                node_color=node_color,
                node_size=node_size,
                with_labels=show_labels,
                font_size=8,
                edge_color=edge_color,
                width=2
            )
        else:
            ax.text(0.5, 0.5, 'Empty Snapshot',
                    ha='center', va='center', transform=ax.transAxes)

        ax.set_title(f"Snapshot {idx}\n{time_str}", fontsize=10)
        ax.axis('off')

    plt.suptitle(title, fontsize=16)
    plt.tight_layout()

    # Save if in debug mode
    if hasattr(state, 'debug_mode') and state.debug_mode:
        save_path = f'{filename}_snapshots.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print_info(f"Saved snapshots to '{save_path}'")

    plt.show()


def _create_animation(graph, state, n_snapshots, combined_pos,
                      figsize, show_labels, node_size, node_color, edge_color,
                      title, interval, filename):
    """Create animation of temporal evolution."""

    fig, ax = plt.subplots(figsize=figsize)

    def update(frame):
        ax.clear()
        snapshot = graph[frame]
        time_str = _get_snapshot_time(snapshot, frame)

        if snapshot.number_of_nodes() > 0:
            # Filter positions to nodes in this snapshot
            pos = {node: combined_pos[node] for node in snapshot.nodes()
                   if node in combined_pos}

            nx.draw(
                snapshot, pos, ax=ax,
                node_color=node_color,
                node_size=node_size,
                with_labels=show_labels,
                font_size=9,
                edge_color=edge_color,
                width=2
            )
        else:
            ax.text(0.5, 0.5, 'Empty Snapshot',
                    ha='center', va='center', transform=ax.transAxes)

        ax.set_title(f"{title}\n{time_str}", fontsize=14)
        ax.axis('off')

    anim = animation.FuncAnimation(
        fig, update,
        frames=n_snapshots,
        interval=interval,
        repeat=True
    )

    # Save animation
    if hasattr(state, 'debug_mode') and state.debug_mode:
        save_path = f'{filename}_animation.gif'
        anim.save(save_path, writer='pillow', dpi=100)
        print_info(f"Saved animation to '{save_path}'")

    plt.close(fig)
    return anim


def _get_snapshot_time(snapshot, default_idx: int) -> str:
    """Extract time information from a snapshot."""
    timestamps = []

    try:
        for _, _, data in snapshot.edges(data=True):
            if isinstance(data, dict) and 'time' in data:
                timestamps.append(data['time'])
    except:
        console.warn("Could not extract time information from snapshot.")
        pass

    if timestamps:
        try:
            # Try to parse as datetime
            time_val = timestamps[0]
            if isinstance(time_val, (int, float)):
                return datetime.fromtimestamp(time_val).strftime('%Y-%m-%d %H:%M')
            elif isinstance(time_val, str):
                # Try ISO format
                try:
                    dt = datetime.fromisoformat(time_val.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M')
                except:
                    return time_val[:16]  # Truncate long strings
            else:
                return str(time_val)
        except:
            return str(timestamps[0])

    return f"t={default_idx}"


# Example usage in your main code:
"""
# In your main code, replace the old plotting block with:

t_graph_sliced = t_graph.slice(attr="time")
plot_format = "snapshots"  # or "animation", "both"

if t_graph_sliced and len(t_graph_sliced) > 0:
    plot_temporal_network(
        graph=t_graph_sliced,
        state=state,
        plot_format=plot_format,
        max_snapshots=6,
        filename='temporal_network',
        layout_algorithm='spring',
        show_labels=True
    )
"""
