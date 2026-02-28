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

import networkx_temporal as tx
from networkx_temporal import TemporalGraph

import random
from datetime import timedelta, datetime

from typing import Optional, List, Dict, Any

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
