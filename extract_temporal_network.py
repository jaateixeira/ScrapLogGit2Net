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

from datetime import datetime

import networkx as nx
import networkx_temporal as tx

from networkx_temporal import TemporalGraph


from typing import Optional, Union
from typing import Optional, List, Dict, Any

import random
from datetime import timedelta, datetime


from collections import defaultdict
from dataclasses import dataclass, field

from utils.unified_console import print_success, print_header, print_info, print_warning, print_key_action, console, print_error, inspect 
from utils.unified_logger import logger
from utils.debugging import  ask_yes_or_no_question
from core.models import ProcessingState



def plot_temporal_network_snapshots(graph, state, max_snapshots=6):
    """Plot temporal network snapshots"""
    import matplotlib.pyplot as plt
    
    n_snapshots = min(len(graph), max_snapshots)
    fig, axes = plt.subplots(2, (n_snapshots + 1) // 2, 
                             figsize=(5 * ((n_snapshots + 1) // 2), 8))
    axes = axes.flatten() if n_snapshots > 1 else [axes]
    
    for idx, (t, G) in enumerate(graph.items()):
        if idx >= n_snapshots:
            break
        
        ax = axes[idx]
        
        # Get timestamp info from edges
        timestamps = []
        for _, _, data in G.edges(data=True):
            if 'time' in data:
                timestamps.append(data['time'])
        
        if timestamps:
            time_str = datetime.fromtimestamp(min(timestamps)).strftime('%Y-%m-%d %H:%M')
        else:
            time_str = f"Snapshot {t}"
        
        # Draw graph
        pos = nx.spring_layout(G, seed=42, k=2)
        nx.draw(G, pos, ax=ax,
                node_color='lightblue',
                node_size=300,
                with_labels=True,
                font_size=8,
                edge_color='gray',
                width=2)
        
        ax.set_title(f"t={t}\n{time_str}")
        ax.axis('off')
    
    # Hide unused subplots
    for idx in range(n_snapshots, len(axes)):
        axes[idx].axis('off')
    
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





import networkx_temporal as tx
import networkx as nx
from datetime import datetime
from typing import Union

def print_temporal_network_summary(temporal_graph: Union[tx.TemporalGraph, tx.TemporalMultiGraph, tx.TemporalDiGraph, tx.TemporalMultiDiGraph]) -> None:
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
    
    # Calculate total edges across all snapshots if sliced, or in the graph if not
    if hasattr(temporal_graph, '__len__') and len(temporal_graph) > 1:
        total_edges = sum(g.number_of_edges() for g in temporal_graph)
        is_sliced = True
        num_snapshots = len(temporal_graph)
        first_graph = temporal_graph[0]
        graph_type = type(first_graph).__name__
        is_directed = first_graph.is_directed() if hasattr(first_graph, 'is_directed') else False
    else:
        total_edges = temporal_graph.number_of_edges()
        is_sliced = False
        num_snapshots = 1
        graph_type = type(temporal_graph).__name__
        is_directed = temporal_graph.is_directed() if hasattr(temporal_graph, 'is_directed') else False
    
    # Enforce edge limit
    if total_edges > MAX_EDGES:
        raise ValueError(
            f"Graph has {total_edges} edges, which exceeds the maximum of {MAX_EDGES} edges. "
            f"Please filter your graph to have 100 edges or less."
        )
    
    # Get time range if possible
    time_min = float('inf')
    time_max = float('-inf')
    time_attr_found = False
    
    def extract_time_from_edge_data(data):
        for key in ['time', 'timestamp', 't', 'date', 'datetime']:
            if key in data:
                val = data[key]
                if isinstance(val, (int, float)):
                    return float(val)
                elif isinstance(val, datetime):
                    return val.timestamp()
        return None
    
    if is_sliced:
        for snapshot in temporal_graph:
            for _, _, data in snapshot.edges(data=True):
                t_val = extract_time_from_edge_data(data)
                if t_val is not None:
                    time_attr_found = True
                    time_min = min(time_min, t_val)
                    time_max = max(time_max, t_val)
    else:
        for _, _, data in temporal_graph.edges(data=True):
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
    print(f"  • Total nodes:     {temporal_graph.temporal_order() if hasattr(temporal_graph, 'temporal_order') else temporal_graph.number_of_nodes()}")
    print(f"  • Total edges:     {total_edges}")
    print(f"  • Snapshots:       {num_snapshots}")
    
    if time_attr_found:
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
            nodes = snapshot.number_of_nodes()
            edges = snapshot.number_of_edges()
            
            snapshot_time = "N/A"
            for _, _, data in snapshot.edges(data=True):
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
                for u, v, data in list(snapshot.edges(data=True))[:3]:
                    time_val = extract_time_from_edge_data(data)
                    time_str = f", time={time_val:.2f}" if time_val else ""
                    attrs = ", ".join(f"{k}={v}" for k, v in data.items() if k not in ['time', 'timestamp'])
                    attrs_str = f", {attrs}" if attrs else ""
                    print(f"      - {u} -> {v}{time_str}{attrs_str}")
                if edges > 3:
                    print(f"      ... and {edges - 3} more edges")
    else:
        nodes = temporal_graph.number_of_nodes()
        edges = temporal_graph.number_of_edges()
        
        print(f"\n  Snapshot (unsliced):")
        print(f"    • Nodes: {nodes}")
        print(f"    • Edges: {edges}")
        
        if edges > 0:
            print(f"    • Sample edges (first 3):")
            for u, v, data in list(temporal_graph.edges(data=True))[:3]:
                time_val = extract_time_from_edge_data(data)
                time_str = f", time={time_val:.2f}" if time_val else ""
                attrs = ", ".join(f"{k}={v}" for k, v in data.items() if k not in ['time', 'timestamp'])
                attrs_str = f", {attrs}" if attrs else ""
                print(f"      - {u} -> {v}{time_str}{attrs_str}")
            if edges > 3:
                print(f"      ... and {edges - 3} more edges")
    
    # Static view
    try:
        static_g = temporal_graph.to_static()
        print(f"\n📋 STATIC VIEW (aggregated):")
        print(f"  • Nodes: {static_g.number_of_nodes()}")
        print(f"  • Edges: {static_g.number_of_edges()}")
        print(f"  • Density: {nx.density(static_g):.6f}")
    except:
        pass
    
    print("\n" + "=" * 80)



def git_timestamp_to_unix(git_timestamp_str: str) -> float:
    """
    Convert Git timestamp string to Unix timestamp.
    
    Example: 'Tue Jan 2 11:19:35 2024 -0800' -> 1704213575.0
    """
    # Parse Git timestamp format
    dt = datetime.strptime(git_timestamp_str, '%a %b %d %H:%M:%S %Y %z')
    # Return Unix timestamp (seconds since epoch)
    return dt.timestamp()


def unix_to_git_timestamp(unix_timestamp: float) -> str:
    """
    Convert Unix timestamp to Git timestamp string.
    
    Example: 1704213575.0 -> 'Tue Jan 2 11:19:35 2024 -0800'
    """
    # Convert Unix timestamp to datetime
    dt = datetime.fromtimestamp(unix_timestamp)
    # Format as Git timestamp
    return dt.strftime('%a %b %d %H:%M:%S %Y %z')



    

def extract_temporal_network_from_parsed_change_log_entries(
        state: ProcessingState,
        time_resolution: timedelta = timedelta(seconds=1)
) -> Optional[TemporalGraph]:
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

    # Overide to debug only this function 

    verbose_mode = True 
    very_verbose_mode = True 
    debug_mode = True 


    # TODO compare to see if is the same by the end of running 
    contributors_by_file=state.map_files_to_their_contributors

    # Log entry point in verbose modes
    if very_verbose_mode or debug_mode:
        print_header(f"Extracting temporal network from parsed change log entries")
        print_info(f"Processing {len(parsed_change_log_entries) if parsed_change_log_entries else 0} entries")
        print_info(f"Temporal network resolution: {time_resolution}")

    if debug_mode and  ask_yes_or_no_question("Do you want to see the parsed_change_log_entries INPUT"):
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
        raise NotImplementedError("Temporal graph construction not yet implemented for time resolution other than 1 second")

    try:
        # Create the temporal graph
        t_graph = tx.temporal_graph()
        
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


        if debug_mode and  ask_yes_or_no_question("Do you want to inspect the sorted_entries by time?"):
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
                print_info(f"Checking if event {developer_email, files, timestamp} relates contributors based on the accumulated history of contributors by file ")


            for file in files:
                print_info(f"checking if {file} was edited before by others in accumulated_history_of_contributors_by_file")
                if file in accumulated_history_of_contributors_by_file.keys():
                    print_key_action(f"NEW relational edge between{developer_email} and others {accumulated_history_of_contributors_by_file[file]} with {timestamp=}")

                    for collaborator in accumulated_history_of_contributors_by_file[file]:
                        t_graph.add_edge(developer_email, collaborator, time=git_timestamp_to_unix(timestamp))
                    
                
                accumulated_history_of_contributors_by_file[file].add(developer_email)
                accumulated_history_of_files_by_contributor[developer_email].add(file)
            
        if debug_mode and  ask_yes_or_no_question("Do you want to see accumulated_history_of_contributors_by_file?"):
            print_info(f"{accumulated_history_of_contributors_by_file=}")

        if debug_mode and  ask_yes_or_no_question("Do you want to see accumulated_history_of_files_by_contributor?"):
            print_info(f"{accumulated_history_of_files_by_contributor=}")
        
        if very_verbose_mode or debug_mode:
            print_success(f"Successfully created temporal graph with {len(t_graph)} snapshots")
            logger.info(f"Created temporal graph with {len(t_graph)} snapshots")




        if debug_mode and ask_yes_or_no_question("Do you want plot the temporal ?"):

            
            
            # After building the graph, slice it
            graph_sliced = t_graph.slice(attr='time')

            print_temporal_network_summary(graph_sliced)

            plot_format="snapshots"
            #plot_format="animation"
            #plot_format="both":
            
            # Plot if requested
            if graph_sliced and len(graph_sliced) > 0:
                if plot_format == "snapshots":
                    plot_temporal_network_snapshots(graph_sliced, state)
                elif plot_format == "animation":
                    animate_and_save(t_graph_sliced, state)
                elif plot_format == "both":
                    plot_temporal_network_snapshots(graph_sliced, state)
                    animate_and_save(graph_sliced, state)


        return t_graph

    except Exception as e:
        # Log any errors that occur during processing
        logger.error(f"Failed to extract temporal network: {str(e)}")
        if debug_mode:
            import traceback
            print_warning(f"Error details: {traceback.format_exc()}")
        return None





if __name__ == "__main__":
    print_header("Temporal Network Extraction Test Harness")
    print_info("To be used by scralLog after the initial parsing for extracting a temporal network")
