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

from utils.unified_console import print_success, print_header, print_info, print_warning, console, print_error
from utils.unified_logger import logger
from utils.debugging import  ask_yes_or_no_question
from core.models import ProcessingState




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
        graph = tx.temporal_graph()
        
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
            

        # Track unique contributors per file (automatically handles duplicates)
        accumulated_history_of_contributors_by_file = defaultdict(set)

        # Example of how to add contributors
        #file_contributors_unique['src/main.py'].add('alice@example.com')
            
        for developer, files, timestamp in sorted_entries:
            if very_verbose_mode or debug_mode:
                print_info(f"Checking if event {developer, files, timestamp} relates contributors based on the accumulated history of contributors by file ")



                # Example: Add edge between entities based on change
                # snapshot.add_edge(entry.entity_id, entry.attribute,
                #                  timestamp=entry.timestamp,
                #                  old_value=entry.old_value,
                #                  new_value=entry.new_value)
            

            


        if very_verbose_mode or debug_mode:
            print_success(f"Successfully created temporal graph with {len(graph)} snapshots")
            logger.info(f"Created temporal graph with {len(graph)} snapshots")

        return graph

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
