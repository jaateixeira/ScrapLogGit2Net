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
from collections import defaultdict
from datetime import timedelta, datetime
from typing import Optional, Union
from matplotlib import pyplot as plt
from typing_extensions import deprecated



import networkx_temporal as tx
from networkx_temporal import TemporalGraph, TemporalMultiGraph
import networkx as nx




from rich import box


from core.models import ProcessingState
from utils.debugging import ask_yes_or_no_question
from utils.unified_console import print_success, print_header, print_info, print_warning, print_key_action, console, \
    print_error, inspect, Table, Text, print_note
from utils.unified_logger import logger



def plot_temporal_network_snapshots(graph, state, max_snapshots=6):
    """Plot temporal network snapshots"""
    import matplotlib.pyplot as plt

    # Determine the number of snapshots to plot
    if hasattr(graph, '__len__'):
        n_total = len(graph)
    else:
        n_total = 1

    n_snapshots = min(n_total, max_snapshots)

    if n_snapshots == 0:
        print_warning("No snapshots to plot")
        return

    # Calculate grid dimensions
    n_cols = min(3, n_snapshots)  # Max 3 columns
    n_rows = (n_snapshots + n_cols - 1) // n_cols

    # Create figure and axes
    fig = plt.figure(figsize=(5 * n_cols, 4 * n_rows))

    # Plot each snapshot
    for idx in range(n_snapshots):
        ax = fig.add_subplot(n_rows, n_cols, idx + 1)

        # Get the graph for this snapshot
        if hasattr(graph, 'items') and callable(getattr(graph, 'items')):
            # Dictionary-like
            t, G = list(graph.items())[idx]
            snapshot_label = f"t={t}"
        elif hasattr(graph, '__getitem__') and not isinstance(graph, dict):
            # List-like
            G = graph[idx]
            snapshot_label = f"Snapshot {idx}"
        else:
            # Single graph
            G = graph
            snapshot_label = "Temporal Network"

        # Get timestamp info from edges
        timestamps = []
        try:
            for _, _, data in G.edges(data=True):
                if 'time' in data:
                    timestamps.append(data['time'])
        except:
            # Handle case where edges() returns different format
            pass

        if timestamps:
            try:
                time_str = datetime.fromtimestamp(min(timestamps)).strftime('%Y-%m-%d %H:%M')
            except:
                time_str = str(min(timestamps))
        else:
            time_str = "No timestamp"

        # Draw graph
        if G.number_of_nodes() > 0:
            try:
                pos = nx.spring_layout(G, seed=42, k=2)
                nx.draw(G, pos, ax=ax,
                        node_color='lightblue',
                        node_size=300,
                        with_labels=True,
                        font_size=8,
                        edge_color='gray',
                        width=2)
            except Exception as e:
                ax.text(0.5, 0.5, f'Error drawing graph: {str(e)[:50]}',
                        ha='center', va='center', transform=ax.transAxes)
        else:
            ax.text(0.5, 0.5, 'Empty Graph', ha='center', va='center', transform=ax.transAxes)

        ax.set_title(f"{snapshot_label}\n{time_str}")
        ax.axis('off')

    plt.suptitle("Temporal Network Evolution", fontsize=16)
    plt.tight_layout()

    # Save if in debug mode
    if state.debug_mode:
        plt.savefig('temporal_network_snapshots.png', dpi=150, bbox_inches='tight')
        print_info("Saved temporal network snapshots to 'temporal_network_snapshots.png'")

    plt.show()


def animate_and_save(graph, state, filename='temporal_network.gif'):
    """Create and save animation"""
    import matplotlib.animation as animation

    fig, ax = plt.subplots(figsize=(10, 8))

    # Precompute positions
    all_nodes = set()
    for G in graph:
        all_nodes.update(G.nodes())

    combined = nx.Graph()
    for G in graph:
        combined.add_edges_from(G.edges())

    pos = nx.spring_layout(combined, seed=42, k=2)

    def update(frame):
        ax.clear()
        G = graph[frame]

        # Get timestamp
        timestamps = [data.get('time', 'N/A') for _, _, data in G.edges(data=True)]
        if timestamps and timestamps[0] != 'N/A':
            time_str = datetime.fromtimestamp(min(timestamps)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = f"Snapshot {frame}"

        # Draw
        nx.draw(G, pos, ax=ax,
                node_color='lightblue',
                node_size=400,
                with_labels=True,
                font_size=9,
                edge_color='darkblue',
                width=2,
                arrows=True)

        ax.set_title(f"Temporal Network Evolution\n{time_str}", fontsize=14)
        ax.axis('off')

    anim = animation.FuncAnimation(fig, update,
                                   frames=len(graph),
                                   interval=800,
                                   repeat=True)

    # Save
    anim.save(filename, writer='pillow', dpi=100)
    print_info(f"Saved animation to '{filename}'")

    plt.close()

    # Display in Jupyter if applicable
    try:
        from IPython.display import HTML
        return HTML(anim.to_html5_video())
    except:
        return anim


from rich.console import Console
from rich.table import Table
from typing import Union
import networkx_temporal as tx

from rich.console import Console
from rich.table import Table
import networkx_temporal as tx
from typing import Dict, Any, List


def print_temporal_edges_table(t_graph: tx.TemporalMultiGraph) -> None:
    """
    Print temporal edges from a TemporalMultiGraph in a Rich table.

    Dynamically creates columns for all attributes found in the edges.
    Always shows 'u' and 'v' as first two columns, followed by all edge attributes.

    Args:
        t_graph: Unsliced TemporalMultiGraph
    """
    console = Console()

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

    verbose_mode = True
    very_verbose_mode = True
    debug_mode = True


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

    verbose_mode = True
    very_verbose_mode = True
    debug_mode = True

    # TODO compare to see if is the same by the end of running 
    contributors_by_file = state.map_files_to_their_contributors

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
            print_info(f"{contributors_by_file=}")

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
                print_info(
                    f"checking if {file} was edited before by others in accumulated_history_of_contributors_by_file")
                if file in accumulated_history_of_contributors_by_file.keys():
                    for collaborator in accumulated_history_of_contributors_by_file[file]:
                        if developer_email != collaborator:
                            print_key_action(
                                f"NEW relational edge between{developer_email} and others {collaborator}, on file {file=}with {timestamp=}")
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
            plot_format = "snapshots"
            # plot_format="animation"
            # plot_format="both":

            # Plot if requested
            if t_graph_sliced and len(t_graph_sliced) > 0:
                if plot_format == "snapshots":
                    plot_temporal_network_snapshots(t_graph_sliced, state)
                elif plot_format == "animation":
                    animate_and_save(t_graph_sliced, state)
                elif plot_format == "both":
                    plot_temporal_network_snapshots(t_graph_sliced, state)
                    animate_and_save(t_graph_sliced, state)


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

    verbose_mode = True
    very_verbose_mode = True
    debug_mode = True

    # Log entry point in verbose modes
    if very_verbose_mode or debug_mode:
        print_header(f"Extracting co-authorship temporal network from parsed change log entries")

    print_info(f"Extracting temporal network from parsed change log entries while keeping time and file information")

    temporal_network_with_time_and_file_attributes=extract_temporal_network_from_parsed_change_log_entries(state)

    print_info(f"Creating the co-authorship temporal network by aggregating file information")

    coauthorship_temporal_networks: TemporalMultiGraph = aggregate_to_coauthorship_temporal_network(state,
        temporal_network_with_time_and_file_attributes)

    if verbose_mode or very_verbose_mode:
        console.print("")

        print_header(f"Extracted co-authorship temporal network from the temporal network:")
        print_note("Time preserved, specific files information lost bia aggregation")
        print_info("t_graph nodes")
        console.print(coauthorship_temporal_networks.nodes())  # Get all nodes
        print_info("t_graph edges")
        for edge in coauthorship_temporal_networks.temporal_edges(data=True):
            console.print(edge)
        console.print("")
        console.rule("")

        # print("Raw edge data:")
        # print(t_graph_sliced.edges(data=True))

    if debug_mode and ask_yes_or_no_question("Do you want see table with coauthorship temporal network edges ?"):
        print_temporal_edges_table(coauthorship_temporal_networks)

    return     coauthorship_temporal_networks




if __name__ == "__main__":
    print_header("Temporal Network Extraction Test Harness")
    print_info("To be used by scralLog after the initial parsing for extracting a temporal network")
