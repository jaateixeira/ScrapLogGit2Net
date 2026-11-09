"""
Printing statistics, tables and summaries of temporal networks to the console.
"""

import math
from typing import Any, Union, List
import networkx as nx
import networkx_temporal as tx
from networkx_temporal import utils
from scraplog.utils.unified_console import console, Table
import networkx_temporal as tx
from typing import Dict, Any
from datetime import datetime





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
