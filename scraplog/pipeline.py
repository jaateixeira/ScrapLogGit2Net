"""
The processing pipeline from parsed change log entries to networks.
"""

import os
import pickle
from pathlib import Path
from scraplog.networks.temporal import extract_coauthorship_temporal_network_from_parsed_change_log_entries
from scraplog.networks.unweighted import extract_unweighted_from_weighted_network
from scraplog.core.models import ProcessingState
from scraplog.networks.weighted import extract_weighted_from_extracted_temporal_network
from scraplog.utils.debugging import handle_step_completion, ask_yes_or_no_question
from scraplog.utils.unified_console import console, inspect, print_info
from scraplog.coediting import aggregate_files_and_contributors, apply_email_filtering, create_network_graph, extract_contributor_connections, get_unique_connections


def save_processed_data(state: ProcessingState, save_path: Path) -> None:
    """Save processed data to a pickle file."""
    console.print(f"\nSaving processed data to {save_path}")

    def save_data(data, path):
        """Safely save data with pickle."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Save with error handling
        try:
            with open(path, 'wb') as fp:
                pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Successfully saved to {path}")
        except Exception as e:
            print(f"Failed to save: {e}")
            raise

    # Usage
    save_data(state.parsed_change_log_entries, save_path)
    console.print("Data saved successfully")


def execute_data_processing_pipeline(state: ProcessingState) -> None:
    """Execute the main data processing pipeline."""
    process_aggregation_step(state)

    print_info(f"Pipeline stage extract_coauthorship_temporal_network_from_parsed_change_log_entries")

    "inter_individual_graph_temporal networks are always extracted "
    # Temporal network MultiGraph with u,v, time
    dev_to_dev_temporal_graph= extract_coauthorship_temporal_network_from_parsed_change_log_entries(state)
    print_info(f"{dev_to_dev_temporal_graph=}")
    state.container_of_extracted_networks.coauthorship_temporal_network_with_time_attributes=dev_to_dev_temporal_graph



    #console.print(f"{state.map_files_to_their_contributors=}")
    #console.print(f"{state.accumulated_history_of_contributors_by_file =}")

    if state.network_type in ("inter_individual_graph_weighted", "inter_individual_graph_unweighted"):
        print_info(f"Pipeline stage extract_weighted_from_extracted_temporal_network")
        dev_to_dev_weighted_graph = extract_weighted_from_extracted_temporal_network(state,dev_to_dev_temporal_graph)
        print_info(f"{dev_to_dev_weighted_graph=}")
        state.container_of_extracted_networks.dev_to_dev_weighted_network = dev_to_dev_weighted_graph

    if state.network_type == "inter_individual_graph_unweighted":
        print_info(f"Pipeline stage extract_unweighted_from_weighted_network")
        dev_to_dev_unweighted_graph =  extract_unweighted_from_weighted_network(state,   state.container_of_extracted_networks.dev_to_dev_weighted_network )
        print_info(f"{dev_to_dev_unweighted_graph=}")
        state.container_of_extracted_networks.dev_to_dev_unweighted_network = dev_to_dev_unweighted_graph


    process_connections_step(state)
    process_unique_connections_step(state)

    process_network_creation_step(state)
    apply_email_filtering(state)


def process_aggregation_step(state: ProcessingState) -> None:
    """Aggregate files and contributors."""
    console.print("[blue] Aggregating data:[/blue] For each file, what are the contributors.")
    aggregate_files_and_contributors(state)
    console.print("[bold green]Success:[/bold green]" + "\n✓ Data aggregated by files and contributors")

    if state.debug_mode and ask_yes_or_no_question("Do you want to see state.map_files_to_their_contributors?"):
        print_info(f"]"
                   f"{state.map_files_to_their_contributors=}")
    handle_step_completion(state, "process_aggregation_step")


def process_connections_step(state: ProcessingState) -> None:
    """Extract contributor connections."""
    console.print(
        "[blue] Mapping connections between developers:[/blue] Getting tuples of contributors that coded/contributed on the same file")
    extract_contributor_connections(state)
    console.print("[bold green]Success:[/bold green]" + "\n✓ Contributor connections extracted as tuples")

    if state.very_verbose_mode:
        console.print(f'state={inspect(state)}')

    handle_step_completion(state, "process_aggregation_step")


def process_unique_connections_step(state: ProcessingState) -> None:
    """Get unique connections from tuples list."""
    console.print("[blue] Getting unique connections from tuples list.")
    state.aggregated_file_coediting_collaborative_relationships = get_unique_connections(
        state.file_coediting_collaborative_relationships)
    console.print(
        "[bold green]Success:[/bold green]" + f"\n✓ Extracted {len(state.aggregated_file_coediting_collaborative_relationships)} unique connections")

    if state.verbose_mode:
        print(f"{state.aggregated_file_coediting_collaborative_relationships=}")

    if state.very_verbose_mode:
        print(f'state={inspect(state)}')

    handle_step_completion(state, "process_unique_connections_step")


def process_network_creation_step(state: ProcessingState) -> None:
    """Create network graph using NetworkX based on network type."""
    console.print(f"[blue] Creating {state.network_type} network using NetworkX.[/blue]")

    if state.network_type == 'inter_individual_graph_temporal':
        print ("network already created with:")
        print( "extracted_temporal_network= extract_coauthorship_temporal_network_from_parsed_change_log_entries(state)")
        return None
    else:
        # Your existing create_network_graph function for unweighted/weighted
        create_network_graph(state)

    console.print("[bold green]Success:[/bold green]" + "\n✓ Network graph created")

    if state.very_verbose_mode:
        console.print(f'state={inspect(state)}')

    handle_step_completion(state, "process_network_creation_step")
