"""
Temporal Network Extraction Module

This module extracts temporal networks from parsed changelog entries.
A temporal network captures how relationships between entities evolve over time.

In action with argument 'inter_individual_graph_temporal'
from state, mostly parsed_change_log_entries structure, creates a temporal network

Test by running:
$ ./scrapLog.py -vv --type-of-network=inter_individual_graph_temporal -r test-data/TensorFlow/tensorFlowGitLog-temporal-2-developers-3-commits-same-file.IN

Related unit tests at tests/unit/test_extract_temporal_network_from_parsed_change_log_entries.py




"""
import sys
import math

from collections import defaultdict
from typing import Literal, Optional, Any, Union, List
from typing_extensions import deprecated

from datetime import timedelta

import networkx as nx
import networkx_temporal as tx
from networkx_temporal import TemporalGraph, TemporalMultiGraph, utils

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from core.models import ProcessingState
from utils.debugging import ask_yes_or_no_question
from utils.unified_console import print_success, print_header, print_info, print_warning, print_key_action, console, \
    print_error, inspect, Table, print_note
from utils.unified_logger import logger


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





def print_temporal_graph_stats(tnet: tx.TemporalMultiGraph, graph_name="Temporal Graph", time_attr="time"):
    """
    Print 8 basic statistics from a TemporalMultiGraph using utils functions.

    Parameters:
    -----------
    tnet : tx.TemporalMultiGraph
        The temporal graph to analyze
    graph_name : str
        Name of the graph for display purposes
    time_attr : str
        The edge attribute key that stores the temporal information (default: "time")
    """

    table = Table(title=f"📊 Statistics for {graph_name}",
                  title_style="bold cyan",
                  border_style="blue")

    table.add_column("Statistic", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Description", style="green")

    # --- 1. Number of Snapshots (Structure) ---
    n_snapshots = len(tnet)
    #table.add_row("Snapshots", str(n_snapshots), "Number of graph snapshots in memory")

    # --- 2. Unique Nodes ---
    total_nodes_unique = tnet.number_of_nodes()
    table.add_row("Unique Nodes", str(total_nodes_unique), "Nodes appearing in any snapshot")

    # --- 3. Unique Edges (across all time, counting each temporal occurrence as one?) ---
    # `tnet.number_of_edges()` counts each edge *once*, even if it exists in multiple snapshots.
    # To get total *temporal* edges (each time-stamped edge instance), you'd need to sum over snapshots.
    total_edges_unique = tnet.number_of_edges() # This counts unique (u,v) pairs across all time
    table.add_row("Unique Edges (Pairs)", str(total_edges_unique), "Unique node pairs connected at any time")


    # --- 6. True Time Span (from edge attributes) ---
    try:
        # Get all unique time values from the specified edge attribute
        unique_times = utils.get_unique_edge_attributes(tnet, attr=time_attr)

        if unique_times:
            # Assuming times are numeric or sortable
            sorted_times = sorted([t for t in unique_times if t is not None and not (isinstance(t, float) and math.isnan(t))])
            if sorted_times:
                time_range = f"{min(sorted_times)} → {max(sorted_times)}"
                table.add_row("Time Span (Events)", time_range, f"First to last unique '{time_attr}' value")
            else:
                table.add_row("Time Span (Events)", "N/A", f"No valid '{time_attr}' values found")
        else:
            # Fallback: use snapshot indices
            time_range = f"0 → {n_snapshots - 1}"
            table.add_row("Time Span (Estimate)", time_range, f"Based on snapshot indices (no '{time_attr}' attr)")

    except Exception as e:
        table.add_row("Time Span", f"Error: {e}", "Could not extract time attribute")



    #table.add_row("Node Persistence", persistence_str, "Avg/Max snapshots per node")

    console.print(table)


def print_first_n_temporal_edges(t_graph: tx.TemporalMultiGraph, n: int = 10) -> None:
    """
    Print the first N temporal edges from a TemporalMultiGraph in a Rich table.

    Dynamically creates columns for all attributes found in the first N edges.
    Always shows 'u' and 'v' as first two columns, followed by all edge attributes.

    Args:
        t_graph: Unsliced TemporalMultiGraph
        n: Number of edges to display (default: 10)
    """

    # Collect first N edges and discover all possible attribute keys
    edges_list: List[tuple] = []
    all_attr_keys: set = set()
    edge_count: int = 0

    for edge in t_graph.temporal_edges(data=True):
        if edge_count >= n:
            break

        edges_list.append(edge)

        # Extract attribute dictionary based on edge format
        if isinstance(edge, tuple) and len(edge) >= 3:
            # Format: (u, v, data_dict) or (u, v, data_dict, key)
            data = edge[2] if len(edge) >= 3 else {}
            if isinstance(data, dict):
                all_attr_keys.update(data.keys())
        elif isinstance(edge, tuple) and len(edge) == 2 and isinstance(edge[1], dict):
            # Format: ((u, v), data_dict)
            data = edge[1]
            all_attr_keys.update(data.keys())

        edge_count += 1

    # If no edges found, show message and return
    if not edges_list:
        console.print("[yellow]No edges found in the temporal graph.[/yellow]")
        return

    # Sort attribute keys for consistent column order
    sorted_attr_keys: List[str] = sorted(all_attr_keys)

    # Create table with dynamic columns
    table = Table(
        title=f"[bold]First {len(edges_list)} Temporal Graph Edges[/bold]",
        title_style="bold cyan",
        header_style="bold white on blue",
        show_lines=True,
        title_justify="center"
    )

    # Always add u and v as first columns
    table.add_column("u", style="green", width=30, overflow="fold")
    table.add_column("v", style="yellow", width=30, overflow="fold")

    # Add columns for each attribute
    attr_colors = ["magenta", "cyan", "blue", "red", "purple", "orange", "pink"]
    for i, attr_key in enumerate(sorted_attr_keys):
        color = attr_colors[i % len(attr_colors)]
        table.add_column(
            attr_key,
            style=color,
            width=25,
            overflow="fold"
        )

    # Reset counter for adding rows
    edges_processed: int = 0

    # Process each edge and add rows
    for edge in edges_list:
        # Extract u, v, and attributes based on format
        u: str = ""
        v: str = ""
        attrs: Dict[str, Any] = {}

        if isinstance(edge, tuple) and len(edge) >= 3:
            # Format: (u, v, data_dict) or (u, v, data_dict, key)
            u = str(edge[0])
            v = str(edge[1])
            if isinstance(edge[2], dict):
                attrs = edge[2]
        elif isinstance(edge, tuple) and len(edge) == 2:
            if isinstance(edge[0], tuple) and len(edge[0]) == 2:
                # Format: ((u, v), data_dict)
                u = str(edge[0][0])
                v = str(edge[0][1])
                if isinstance(edge[1], dict):
                    attrs = edge[1]
            else:
                # Format: (u, v) without data
                u = str(edge[0])
                v = str(edge[1])

        # Build row: start with u and v
        row = [u, v]

        # Add attribute values in the same order as columns
        for attr_key in sorted_attr_keys:
            value = attrs.get(attr_key, "")
            # Convert to string and handle None
            if value is None:
                value = ""
            elif not isinstance(value, str):
                value = str(value)
            row.append(value)

        table.add_row(*row)
        edges_processed += 1

    # Print the table
    console.print(table)

    # Print summary with additional info
    total_edges = sum(1 for _ in t_graph.temporal_edges())
    console.print(
        f"\n[bold cyan]Showing:[/bold cyan] [white]{edges_processed}[/white] of [white]{total_edges}[/white] total edges")

    if edges_processed < total_edges:
        console.print(f"[dim](Limited to first {n} edges. Total edges: {total_edges})[/dim]")

    if sorted_attr_keys:
        console.print(f"[bold cyan]Attributes shown:[/bold cyan] [white]{', '.join(sorted_attr_keys)}[/white]")

def print_temporal_edges_table(t_graph: tx.TemporalMultiGraph) -> None:
    """
    Print temporal edges from a TemporalMultiGraph in a Rich table.

    Dynamically creates columns for all attributes found in the edges.
    Always shows 'u' and 'v' as first two columns, followed by all edge attributes.

    Args:
        t_graph: Unsliced TemporalMultiGraph
    """

    # Collect all edges and discover all possible attribute keys
    edges_list: List[tuple] = []
    all_attr_keys: set = set()

    for edge in t_graph.temporal_edges(data=True):
        edges_list.append(edge)

        # Extract attribute dictionary based on edge format
        if isinstance(edge, tuple) and len(edge) >= 3:
            # Format: (u, v, data_dict) or (u, v, data_dict, key)
            data = edge[2] if len(edge) >= 3 else {}
            if isinstance(data, dict):
                all_attr_keys.update(data.keys())
        elif isinstance(edge, tuple) and len(edge) == 2 and isinstance(edge[1], dict):
            # Format: ((u, v), data_dict)
            data = edge[1]
            all_attr_keys.update(data.keys())

    # Sort attribute keys for consistent column order
    sorted_attr_keys: List[str] = sorted(all_attr_keys)

    # Create table with dynamic columns
    table = Table(
        title="[bold]Temporal Graph Edges[/bold]",
        title_style="bold cyan",
        header_style="bold white on blue",
        show_lines=True
    )

    # Always add u and v as first columns
    table.add_column("u", style="green", width=30, overflow="fold")
    table.add_column("v", style="yellow", width=30, overflow="fold")

    # Add columns for each attribute
    attr_colors = ["magenta", "cyan", "blue", "red", "purple", "orange", "pink"]
    for i, attr_key in enumerate(sorted_attr_keys):
        color = attr_colors[i % len(attr_colors)]
        table.add_column(
            attr_key,
            style=color,
            width=25,
            overflow="fold"
        )

    # Counter for total edges
    edge_count: int = 0

    # Process each edge and add rows
    for edge in edges_list:
        # Extract u, v, and attributes based on format
        u: str = ""
        v: str = ""
        attrs: Dict[str, Any] = {}

        if isinstance(edge, tuple) and len(edge) >= 3:
            # Format: (u, v, data_dict) or (u, v, data_dict, key)
            u = str(edge[0])
            v = str(edge[1])
            if isinstance(edge[2], dict):
                attrs = edge[2]
        elif isinstance(edge, tuple) and len(edge) == 2:
            if isinstance(edge[0], tuple) and len(edge[0]) == 2:
                # Format: ((u, v), data_dict)
                u = str(edge[0][0])
                v = str(edge[0][1])
                if isinstance(edge[1], dict):
                    attrs = edge[1]
            else:
                # Format: (u, v) without data
                u = str(edge[0])
                v = str(edge[1])

        # Build row: start with u and v
        row = [u, v]

        # Add attribute values in the same order as columns
        for attr_key in sorted_attr_keys:
            value = attrs.get(attr_key, "")
            # Convert to string and handle None
            if value is None:
                value = ""
            elif not isinstance(value, str):
                value = str(value)
            row.append(value)

        table.add_row(*row)
        edge_count += 1

    # Print the table
    console.print(table)

    # Print summary
    console.print(f"\n[bold cyan]Total edges displayed:[/bold cyan] [white]{edge_count}[/white]")
    if sorted_attr_keys:
        console.print(f"[bold cyan]Attributes shown:[/bold cyan] [white]{', '.join(sorted_attr_keys)}[/white]")

def print_temporal_network_summary(temporal_graph: Union[
    tx.TemporalGraph, tx.TemporalMultiGraph, tx.TemporalDiGraph, tx.TemporalMultiDiGraph]) -> None:
    """
    Print a rich, formatted summary of a temporal network.

    Args:
        temporal_graph: A NetworkX-Temporal graph object

    Raises:
        ValueError: If the graph has more than 100 edges
        TypeError: If input is not a NetworkX-Temporal graph
    """
    MAX_EDGES = 100  # Internal constant

    # Check if it's a temporal graph
    if not hasattr(temporal_graph, 'slice') and not hasattr(temporal_graph, 'to_static'):
        if not hasattr(temporal_graph, '__len__') or len(temporal_graph) == 0:
            raise TypeError("Input must be a NetworkX-Temporal graph or a sliced temporal graph with snapshots")

    # Helper function to safely get edge count
    def safe_edge_count(graph_obj) -> int:
        """Get edge count, handling both int and list returns"""
        edges = graph_obj.number_of_edges()
        if isinstance(edges, list):
            return sum(edges)
        return edges

    # Helper function to safely iterate through edges
    def safe_edge_iter(graph_obj):
        """Safely iterate through edges, handling different return formats"""
        try:
            # Try standard NetworkX format
            edges = list(graph_obj.edges(data=True))
            if edges and len(edges[0]) == 3:
                return edges
        except:
            pass

        try:
            # Try alternative format (maybe just edges without data)
            edges = list(graph_obj.edges())
            return [(u, v, {}) for u, v in edges]
        except:
            pass

        return []  # Return empty list if all else fails

    # Calculate total edges across all snapshots
    if hasattr(temporal_graph, '__len__') and len(temporal_graph) > 1:
        # It's a sliced graph with multiple snapshots
        total_edges = sum(safe_edge_count(g) for g in temporal_graph)
        is_sliced = True
        num_snapshots = len(temporal_graph)
        first_graph = temporal_graph[0]
        graph_type = type(first_graph).__name__
        is_directed = first_graph.is_directed() if hasattr(first_graph, 'is_directed') else False
    else:
        # It's a single graph (either unsliced or has 1 snapshot)
        total_edges = safe_edge_count(temporal_graph)
        is_sliced = False
        num_snapshots = 1
        graph_type = type(temporal_graph).__name__
        is_directed = temporal_graph.is_directed() if hasattr(temporal_graph, 'is_directed') else False

    # Enforce edge limit
    if total_edges > MAX_EDGES:
        raise ValueError(
            f"Graph has {total_edges} edges, which exceeds the maximum of {MAX_EDGES} edges. "
            f"Please filter your graph to have {MAX_EDGES} edges or less."
        )

    # Get time range if possible
    time_min = float('inf')
    time_max = float('-inf')
    time_attr_found = False

    def extract_time_from_edge_data(data):
        if isinstance(data, dict):
            for key in ['time', 'timestamp', 't', 'date', 'datetime']:
                if key in data:
                    val = data[key]
                    if isinstance(val, (int, float)):
                        return float(val)
                    elif isinstance(val, datetime):
                        return val.timestamp()
        return None

    # Process time range from edges
    if is_sliced:
        for snapshot in temporal_graph:
            for edge_data in safe_edge_iter(snapshot):
                if len(edge_data) == 3:
                    u, v, data = edge_data
                    t_val = extract_time_from_edge_data(data)
                    if t_val is not None:
                        time_attr_found = True
                        time_min = min(time_min, t_val)
                        time_max = max(time_max, t_val)
    else:
        for edge_data in safe_edge_iter(temporal_graph):
            if len(edge_data) == 3:
                u, v, data = edge_data
                t_val = extract_time_from_edge_data(data)
                if t_val is not None:
                    time_attr_found = True
                    time_min = min(time_min, t_val)
                    time_max = max(time_max, t_val)

    # Print header
    print("=" * 80)
    print("📊 TEMPORAL NETWORK SUMMARY")
    print("=" * 80)

    # Basic info
    print("\n📈 BASIC STATISTICS:")
    print(f"  • Graph type:      {graph_type}")
    print(f"  • Directed:        {is_directed}")

    # Handle temporal_order safely
    try:
        if hasattr(temporal_graph, 'temporal_order'):
            total_nodes = temporal_graph.temporal_order()
        else:
            total_nodes = temporal_graph.number_of_nodes()
    except:
        # Fallback: count unique nodes across snapshots
        all_nodes = set()
        if is_sliced:
            for snapshot in temporal_graph:
                all_nodes.update(snapshot.nodes())
        else:
            all_nodes.update(temporal_graph.nodes())
        total_nodes = len(all_nodes)

    print(f"  • Total nodes:     {total_nodes}")
    print(f"  • Total edges:     {total_edges}")
    print(f"  • Snapshots:       {num_snapshots}")

    if time_attr_found and time_min != float('inf') and time_max != float('-inf'):
        try:
            time_min_str = datetime.fromtimestamp(time_min).strftime('%Y-%m-%d %H:%M:%S')
            time_max_str = datetime.fromtimestamp(time_max).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  • Time span:       {time_min_str} to {time_max_str}")
            print(f"  • Duration:        {time_max - time_min:.2f} seconds")
        except:
            print(f"  • Time range:      {time_min} to {time_max}")
    else:
        print(f"  • Time attributes: Not found in edges")

    # Snapshot details
    print(f"\n📸 SNAPSHOT DETAILS:")

    if is_sliced:
        for i, snapshot in enumerate(temporal_graph):
            try:
                nodes = snapshot.number_of_nodes()
            except:
                nodes = len(list(snapshot.nodes()))

            edges = safe_edge_count(snapshot)

            # Find snapshot time
            snapshot_time = "N/A"
            for edge_data in safe_edge_iter(snapshot)[:1]:  # Just check first edge
                if len(edge_data) == 3:
                    u, v, data = edge_data
                    t_val = extract_time_from_edge_data(data)
                    if t_val is not None:
                        try:
                            snapshot_time = datetime.fromtimestamp(t_val).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            snapshot_time = str(t_val)
                        break

            print(f"\n  Snapshot {i}:")
            print(f"    • Nodes: {nodes}")
            print(f"    • Edges: {edges}")
            print(f"    • Time:  {snapshot_time}")

            if edges > 0:
                print(f"    • Sample edges (first 3):")
                sample_edges = safe_edge_iter(snapshot)[:3]
                for edge_data in sample_edges:
                    if len(edge_data) == 3:
                        u, v, data = edge_data
                        time_val = extract_time_from_edge_data(data)
                        time_str = f", time={time_val:.2f}" if time_val else ""
                        attrs = ", ".join(f"{k}={v}" for k, v in data.items() if k not in ['time', 'timestamp'])
                        attrs_str = f", {attrs}" if attrs else ""
                        print(f"      - {u} -> {v}{time_str}{attrs_str}")
                    elif len(edge_data) == 2:
                        u, v = edge_data
                        print(f"      - {u} -> {v}")

                if edges > 3:
                    print(f"      ... and {edges - 3} more edges")
    else:
        try:
            nodes = temporal_graph.number_of_nodes()
        except:
            nodes = len(list(temporal_graph.nodes()))

        edges = safe_edge_count(temporal_graph)

        print(f"\n  Snapshot (unsliced):")
        print(f"    • Nodes: {nodes}")
        print(f"    • Edges: {edges}")

        if edges > 0:
            print(f"    • Sample edges (first 3):")
            sample_edges = safe_edge_iter(temporal_graph)[:3]
            for edge_data in sample_edges:
                if len(edge_data) == 3:
                    u, v, data = edge_data
                    time_val = extract_time_from_edge_data(data)
                    time_str = f", time={time_val:.2f}" if time_val else ""
                    attrs = ", ".join(f"{k}={v}" for k, v in data.items() if k not in ['time', 'timestamp'])
                    attrs_str = f", {attrs}" if attrs else ""
                    print(f"      - {u} -> {v}{time_str}{attrs_str}")
                elif len(edge_data) == 2:
                    u, v = edge_data
                    print(f"      - {u} -> {v}")

            if edges > 3:
                print(f"      ... and {edges - 3} more edges")

    # Static view
    try:
        if hasattr(temporal_graph, 'to_static'):
            static_g = temporal_graph.to_static()
            print(f"\n📋 STATIC VIEW (aggregated):")
            print(f"  • Nodes: {static_g.number_of_nodes()}")
            print(f"  • Edges: {static_g.number_of_edges()}")
            print(f"  • Density: {nx.density(static_g):.6f}")
    except Exception as e:
        if hasattr(temporal_graph, '__len__') and len(temporal_graph) > 0:
            try:
                # Try to create static view by combining snapshots
                combined = nx.Graph()
                for snapshot in temporal_graph:
                    for edge_data in safe_edge_iter(snapshot):
                        if len(edge_data) == 3:
                            u, v, _ = edge_data
                            combined.add_edge(u, v)
                        elif len(edge_data) == 2:
                            u, v = edge_data
                            combined.add_edge(u, v)

                if combined.number_of_edges() > 0:
                    print(f"\n📋 COMBINED VIEW (all snapshots):")
                    print(f"  • Nodes: {combined.number_of_nodes()}")
                    print(f"  • Edges: {combined.number_of_edges()}")
                    print(f"  • Density: {nx.density(combined):.6f}")
            except:
                pass

    print("\n" + "=" * 80)


@deprecated("Use git_timestamp_to_iso() instead which preserves timezone information")
def git_timestamp_to_unix(git_timestamp_str: str) -> float:
    """
    Convert Git timestamp string to Unix timestamp.

    Example: 'Tue Jan 2 11:19:35 2024 -0800' -> 1704213575.0
    """
    # Parse Git timestamp format
    dt = datetime.strptime(git_timestamp_str, '%a %b %d %H:%M:%S %Y %z')
    # Return Unix timestamp (seconds since epoch)
    return dt.timestamp()


@deprecated("Use iso_to_git_timestamp instead which preserves timezone information")
def unix_to_git_timestamp(unix_timestamp: float) -> str:
    """
    Convert Unix timestamp to Git timestamp string.

    Example: 1704213575.0 -> 'Tue Jan 2 11:19:35 2024 -0800'
    """
    # Convert Unix timestamp to datetime
    dt = datetime.fromtimestamp(unix_timestamp)
    # Format as Git timestamp
    return dt.strftime('%a %b %d %H:%M:%S %Y %z')


def git_timestamp_to_iso(git_timestamp_str: str) -> str:
    """Convert Git timestamp to ISO format with timezone."""
    dt = datetime.strptime(git_timestamp_str, '%a %b %d %H:%M:%S %Y %z')
    return dt.isoformat()  # Preserves timezone!


def iso_to_git_timestamp(iso_str: str) -> str:
    """Convert ISO format back to Git timestamp."""
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime('%a %b %d %H:%M:%S %Y %z')


import networkx_temporal as tx
from typing import Set, Tuple, Dict, Any, Optional
from datetime import datetime


def aggregate_to_coauthorship_temporal_network( state: ProcessingState, file_collaboration_graph: tx.TemporalMultiGraph) -> tx.TemporalGraph:
    """
    Convert a temporal multigraph to a developer co-authorship temporal graph.

    This function takes a TemporalMultiGraph with time and file as edge attributes.
    It returns a simpler TemporalGraph where each (developer1, developer2, timestamp)
    combination appears only once, representing a co-authorship relationship.
    It does not matter what files are co-edited, only that they are co-edited and at what time.

    Example:
        ('jreiffers@google.com', 'akuegel@google.com', {'time': '2024-01-06T04:03:16-08:00', 'file': 'third_party/xla/xla/service/gpu/fusions/fusions.cc'})
        ('jreiffers@google.com', 'akuegel@google.com', {'time': '2024-01-06T04:03:16-08:00', 'file': 'third_party/xla/xla/service/gpu/fusions/scatter.cc'})
        ('jreiffers@google.com', 'akuegel@google.com', {'time': '2024-01-08T06:30:42-08:00', 'file': 'third_party/xla/xla/service/gpu/fusions/fusions.cc'})
        ('jreiffers@google.com', 'akuegel@google.com', {'time': '2024-01-08T06:30:42-08:00', 'file': 'third_party/xla/xla/service/gpu/fusions/scatter.cc'})
    Should return:
        ('jreiffers@google.com', 'akuegel@google.com', {'time': '2024-01-06T04:03:16-08:00'})
        ('jreiffers@google.com', 'akuegel@google.com', {'time': '2024-01-08T06:30:42-08:00'})
      """


    verbose_mode = state.verbose_mode
    very_verbose_mode = state.very_verbose_mode
    debug_mode = state.debug_mode

    # Override to debug only this function

    #verbose_mode = True
    #very_verbose_mode = True
    #debug_mode = True


    # Initialize new simple temporal graph for co-authorships
    coauthorship_network: tx.TemporalMultiGraph= tx.TemporalMultiGraph()

    # Track added (dev1, dev2, time) combinations to avoid duplicates
    # Set elements are tuples with developers sorted lexicographically
    added_coauthorships: Set[Tuple[str, str, str]] = set()

    # Process all temporal edges from the input multigraph
    for edge in file_collaboration_graph.temporal_edges(data=True):

        # Unpack edge - TemporalMultiGraph returns (u, v, data_dict)
        if not isinstance(edge, tuple) or len(edge) != 3:
            continue  # Skip malformed edges

        developer1: str = str(edge[0])
        developer2: str = str(edge[1])
        attributes: Dict[str, Any] = edge[2]

        if verbose_mode or very_verbose_mode:
            print_info(f"unpacking temporal edge {edge}")
            print_info(f"{developer1} -> {developer2}")
            for i, attribute in enumerate(attributes, 1):  # start counting from 1
                console.print(f"attribute {i} = {attribute}")

        # Extract and validate timestamp
        timestamp: Optional[str] = attributes.get('time')
        if timestamp is None:
            raise ValueError(f"Edge {developer1} - {developer2} missing required 'time' attribute")

        # Normalize developer order for undirected graph
        # This ensures (A,B) and (B,A) are treated as the same edge
        dev1_normalized: str
        dev2_normalized: str
        if developer1 < developer2:
            dev1_normalized = developer1
            dev2_normalized = developer2
        else:
            dev1_normalized = developer2
            dev2_normalized = developer1

        # Create unique key for this co-authorship
        coauthorship_key: Tuple[str, str, str] = (
            dev1_normalized,
            dev2_normalized,
            timestamp
        )

        # Add edge only if this (dev_pair, time) combination hasn't been seen before
        if coauthorship_key not in added_coauthorships:
            coauthorship_network.add_edge(
                dev1_normalized,
                dev2_normalized,
                time=timestamp  # Only preserve the time attribute
            )
            added_coauthorships.add(coauthorship_key)
        else:
            if verbose_mode or very_verbose_mode:
                console.print(f"{coauthorship_key=} dropped as seen before")


    if verbose_mode or very_verbose_mode:
        console.print(f"{added_coauthorships=}")
        print_info(f"returning coauthorship network {coauthorship_network=}")
    return coauthorship_network





def extract_temporal_network_from_parsed_change_log_entries(
        state: ProcessingState,
        time_resolution: timedelta = timedelta(seconds=1)
) -> Optional[TemporalMultiGraph]:
    """
    Extract a temporal network from parsed changelog entries.

    This function processes a series of change log entries and constructs a temporal
    graph where nodes represent entities and edges represent relationships or interactions
    between them that change over time.

    The temporal graph slices time into windows of size `time_resolution` and creates
    a static graph snapshot for each time window containing the active relationships
    during that period.

    Args:
        state (ProcessingState): The processing state containing:
            - parsed_change_log_entries: List of changelog entries to process
            - verbose_mode: Whether to print verbose output
            - very_verbose_mode: Whether to print very verbose output
            - debug_mode: Whether to print debug output
        time_resolution (timedelta): Time window size for graph snapshots.
            Defaults to 1 second. Smaller values create more granular snapshots.

    Returns:
        Optional[TemporalGraph]: A temporal graph object if successful and data exists,
            None if no data is available or processing fails.

    Notes:
        - The function will warn if time_resolution is not 1 second, as it is the
        default and only implementation so far
        - Very verbose or debug mode will print detailed processing information.
        - Returns None rather than an empty graph if no data is available to
          distinguish between "no data" and "empty graph" states.
    """

    # Extract configuration from state
    parsed_change_log_entries = state.parsed_change_log_entries
    verbose_mode = state.verbose_mode
    very_verbose_mode = state.very_verbose_mode
    debug_mode = state.debug_mode

    # Override to debug only this function

    #verbose_mode = True
    #very_verbose_mode = True
    #debug_mode = True


    # Log entry point in verbose modes
    if very_verbose_mode or debug_mode:
        print_header(f"Extracting temporal network from parsed change log entries")
        print_info(f"Processing {len(parsed_change_log_entries) if parsed_change_log_entries else 0} entries")
        print_info(f"Temporal network resolution: {time_resolution}")

    if debug_mode and ask_yes_or_no_question("Do you want to see the parsed_change_log_entries INPUT"):
        print_info(f"{parsed_change_log_entries=}")

    # Validate input data
    if not parsed_change_log_entries:
        if very_verbose_mode or debug_mode:
            print_warning("No parsed change log entries to process")
            logger.warning("No parsed change log entries to process")
        if state.strict_validation:
            print_error("No parsed change log entries to process")
            logger.error("No parsed change log entries to process")
            sys.exit()
        return None

    # Warn about non-default resolution (performance impact)
    if time_resolution != timedelta(seconds=1):
        print_warning(f"Temporal network resolution is not 1 second (using {time_resolution})")
        logger.warning(f"Temporal network resolution is not 1 second (using {time_resolution})")
        raise NotImplementedError(
            "Temporal graph construction not yet implemented for time resolution other than 1 second")

    try:
        # Create the temporal graph
        t_graph: tx.TemporalMultiGraph = tx.TemporalMultiGraph()

        def _get_timestamp_for_sorting(entry):
            """Extract and parse timestamp from entry"""
            if hasattr(entry, 'timestamp'):
                # It's a ChangeLogEntry object
                return entry.timestamp
            else:
                # Assume it's a tuple: ((email, affiliation), [files], timestamp_str)
                timestamp_str = entry[2]
                return datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %Y %z')

        sorted_entries = sorted(parsed_change_log_entries, key=_get_timestamp_for_sorting)

        if very_verbose_mode or debug_mode:
            print_info(f"Processing {len(sorted_entries)} entries in chronological order")
            print_info(f"{sorted_entries=}")

        if debug_mode and ask_yes_or_no_question("Do you want to inspect the sorted_entries by time?"):
            print_info(f"{inspect(sorted_entries)}")

        # Track unique contributors per file (automatically handles duplicates)
        accumulated_history_of_contributors_by_file = defaultdict(set)
        accumulated_history_of_files_by_contributor = defaultdict(set)

        # Example of how to add contributors:
        # accumulated_history_of_files_by_contributor['alice@example.com'].add('src/main.py')

        # Example of how to add files:
        # accumulated_history_of_contributors_by_file['src/main.py'].add('alice@example.com')

        for developer_info, files, timestamp in sorted_entries:
            developer_email, developer_affiliation = developer_info

            if very_verbose_mode or debug_mode:
                print_info(
                    f"Checking if event {developer_email, files, timestamp} relates contributors based on the accumulated history of contributors by file ")

            for file in files:
                if very_verbose_mode or debug_mode:
                    print_info(
                        f"checking if {file} was edited before by others in accumulated_history_of_contributors_by_file")
                if file in accumulated_history_of_contributors_by_file.keys():
                    for collaborator in accumulated_history_of_contributors_by_file[file]:
                        if developer_email != collaborator:
                            if verbose_mode or very_verbose_mode or debug_mode:
                                print_key_action(
                                    f"NEW relational edge u={developer_email} and v= {collaborator}, on {file=} with {timestamp=}")
                            t_graph.add_edge(developer_email, collaborator, time=git_timestamp_to_iso(timestamp),file=file)

                accumulated_history_of_contributors_by_file[file].add(developer_email)
                accumulated_history_of_files_by_contributor[developer_email].add(file)

        if debug_mode and ask_yes_or_no_question("Do you want to see accumulated_history_of_contributors_by_file?"):
            print_info(f"{accumulated_history_of_contributors_by_file=}")

        if debug_mode and ask_yes_or_no_question("Do you want to see accumulated_history_of_files_by_contributor?"):
            print_info(f"{accumulated_history_of_files_by_contributor=}")

        if very_verbose_mode or debug_mode:
            print_success(f"Successfully created temporal graph with {len(t_graph)} snapshots")
            logger.info(f"Created temporal graph with {len(t_graph)} snapshots")

        if verbose_mode or very_verbose_mode:
            console.print("")

            print_header(f"Extracted temporal network from parsed change log entries:")
            print_info("t_graph nodes")
            console.print(t_graph.nodes())  # Get all nodes
            print_info("t_graph edges")
            for edge in t_graph.temporal_edges(data=True):
                console.print(edge)
            console.print("")
            console.rule("")



        #print("Raw edge data:")
        #print(t_graph_sliced.edges(data=True))

        if debug_mode and ask_yes_or_no_question("Do you want see table with extracted the temporal network edges ?"):
            print_temporal_edges_table(t_graph)

        if debug_mode and ask_yes_or_no_question("Do you want see an summary of the extracted the temporal network (with time and files) ?"):
            print_temporal_network_summary(t_graph)

        if debug_mode and ask_yes_or_no_question("Do you want plot the temporal network (with time and files) ?"):

            t_graph_sliced = t_graph.slice(attr="time")


            plot_temporal_network(
                graph=t_graph_sliced,
                state=state,
                plot_format="snapshots",
                max_snapshots=6,
                filename='temporal_network',
                layout_algorithm='spring',
                show_labels=True)

        state.accumulated_history_of_contributors_by_file=accumulated_history_of_contributors_by_file
        state.accumulated_history_of_files_by_contributor=accumulated_history_of_files_by_contributor
        return t_graph

    except Exception as e:
        # Log any errors that occur during processing
        logger.error(f"Failed to extract temporal network: {str(e)}")
        if debug_mode:
            import traceback
            print_warning(f"Error details: {traceback.format_exc()}")
        return None


def extract_coauthorship_temporal_network_from_parsed_change_log_entries(
        state: ProcessingState,
        time_resolution: timedelta = timedelta(seconds=1)
) -> Optional[TemporalMultiGraph]:

    verbose_mode = state.verbose_mode
    very_verbose_mode = state.very_verbose_mode
    debug_mode = state.debug_mode

    # Override to debug only this function

    #verbose_mode = True
    #very_verbose_mode = True
    #debug_mode = True

    # Log entry point in verbose modes
    if very_verbose_mode or debug_mode:
        print_header(f"Extracting co-authorship temporal network from parsed change log entries")

    console.rule("\n")
    print_info(f"Extracting temporal network from parsed change log entries while keeping time and file information")

    temporal_network_with_time_and_file_attributes=extract_temporal_network_from_parsed_change_log_entries(state)

    print_success(f"Extracted temporal network with (u, v, time, file) edges:")

    console.print("\n")
    print_temporal_graph_stats(temporal_network_with_time_and_file_attributes, "(u, v, time, file) temporal network " )
    print_first_n_temporal_edges(temporal_network_with_time_and_file_attributes,10)

    console.rule("")

    print_info(f"Creating the co-authorship temporal network by aggregating file information")

    coauthorship_temporal_network: TemporalMultiGraph = aggregate_to_coauthorship_temporal_network(state,
        temporal_network_with_time_and_file_attributes)

    print_success(f"Aggregated temporal network with (u, v, time) edges:")
    console.print("\n")
    print_temporal_graph_stats(coauthorship_temporal_network, "(u, v, time) temporal network ")
    print_first_n_temporal_edges(coauthorship_temporal_network, 10)


    console.rule("")

    if verbose_mode or very_verbose_mode:
        console.print("")

        print_header(f"Extracted co-authorship temporal network from the temporal network:")
        print_note("Time preserved, specific files information lost --type-of-network=inter_individual_graph_temporal -vv -d ia aggregation")
        print_info("t_graph nodes")
        console.print(coauthorship_temporal_network.nodes())  # Get all nodes
        print_info("t_graph edges")
        for edge in coauthorship_temporal_network.temporal_edges(data=True):
            console.print(edge)
        console.print("")
        console.rule("")

        # print("Raw edge data:")
        # print(t_graph_sliced.edges(data=True))

    if debug_mode and ask_yes_or_no_question("Do you want see table with coauthorship temporal network edges ?"):
        print_temporal_edges_table(coauthorship_temporal_network)


    #plot_format = "snapshots"  # or "animation", "both"

    if debug_mode and ask_yes_or_no_question("Do you want plot the temporal network (with u,v, time) ?"):
        plot_temporal_network(
            graph=coauthorship_temporal_network.slice(attr="time"),
            state=state,
            plot_format="snapshots",
            max_snapshots=6,
            filename='temporal_network',
            layout_algorithm='spring',
            show_labels=True)

    return     coauthorship_temporal_network




if __name__ == "__main__":
    print_header("Temporal Network Extraction Test Harness")
    print_info("To be used by scralLog after the initial parsing for extracting a temporal network")
