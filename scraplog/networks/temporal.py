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
from typing import Optional, Any
from datetime import timedelta
import networkx_temporal as tx
from networkx_temporal import TemporalMultiGraph
from scraplog.core.models import ProcessingState
from scraplog.utils.debugging import ask_yes_or_no_question
from scraplog.utils.unified_console import print_success, print_header, print_info, print_warning, print_key_action, console, print_error, inspect, print_note
from scraplog.utils.unified_logger import logger
import networkx_temporal as tx
from typing import Set, Tuple, Dict, Any, Optional
from datetime import datetime
from scraplog.networks.temporal_plot import plot_temporal_network
from scraplog.networks.temporal_report import print_first_n_temporal_edges, print_temporal_edges_table, print_temporal_graph_stats, print_temporal_network_summary
from scraplog.networks.timestamps import git_timestamp_to_iso


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
            sys.exit(1)
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
                    # sorted: set order varies between runs; sorting keeps output deterministic
                    for collaborator in sorted(accumulated_history_of_contributors_by_file[file]):
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
