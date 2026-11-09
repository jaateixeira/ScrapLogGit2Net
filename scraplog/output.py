"""
Exporting networks to files and printing the processing summary.
"""

import argparse
import sys
import zipfile
from pathlib import Path
import networkx as nx
import networkx_temporal as tx
from scraplog.export import log_data as export_log_data
from scraplog.core.models import ProcessingState
from scraplog.networks.weighted import show_weighted_edges
from scraplog.utils.debugging import ask_yes_or_no_question
from scraplog.utils.string_comparators import find_similar_strings
from scraplog.utils.unified_console import console, traceback, inspect, print_info, print_warning, print_error
from scraplog.coediting import enrich_graph_with_affiliation


def temporal_network_counts(state: ProcessingState) -> tuple[int, int, int, set]:
    """Developers, time-stamped edges, distinct developer pairs and the affiliations
    of the developers in the exported temporal network (all zero if there is none).

    Affiliations come from the parsed commits, as the temporal network file does
    not store them.
    """
    t_graph = state.container_of_extracted_networks.coauthorship_temporal_network_with_time_attributes
    if t_graph is None:
        return 0, 0, 0, set()
    nodes = set().union(*t_graph.nodes())
    edges = list(t_graph.temporal_edges())
    pairs = {frozenset((u, v)) for u, v in edges}
    affiliation_of = {email: affiliation for (email, affiliation), _, _ in state.parsed_change_log_entries}
    affiliations = {affiliation_of[node] for node in nodes if node in affiliation_of}
    return len(nodes), len(edges), len(pairs), affiliations


def print_processing_summary(state: ProcessingState, in_work_file: Path, out_graphml_file: Path) -> None:
    """console.print a summary of processing results."""
    console.print("\n" + "=" * 60)
    console.print("PROCESSING SUMMARY")
    console.print("=" * 60)
    console.print(f"Input log file: {in_work_file}")
    console.print(f"Out network graphml file: {out_graphml_file}")
    console.print(f"Total lines processed: {state.statistics.n_lines}")
    console.print(f"Total commit blocks found: {state.statistics.n_blocks}")
    console.print(f"Successfully processed blocks: {state.statistics.n_blocks - state.statistics.n_skipped_blocks - state.statistics.n_commits_excluded_by_email_filter}")
    console.print(f"Skipped/invalid blocks: {state.statistics.n_skipped_blocks}")
    if state.email_filtering_mode:
        console.print(f"Commits excluded by -fe email filter: {state.statistics.n_commits_excluded_by_email_filter}"
                      f" (emails: {', '.join(sorted(state.excluded_emails)) or 'none found in the log'})")
    console.print(f"Blocks changing code: {state.statistics.n_blocks_changing_code}")
    console.print(f"Files affected: {state.statistics.n_changed_files}")
    console.print(f"Validation errors: {state.statistics.n_validation_errors}")
    if state.network_type == 'inter_individual_graph_temporal':
        # The static network (dev_to_dev_network) is not built for temporal runs:
        # report the temporal network that is exported instead
        nodes, n_temporal_edges, pairs, affiliations = temporal_network_counts(state)
        console.print(f"Network nodes (developers): {nodes}")
        console.print(f"Network edges (time-stamped co-edits): {n_temporal_edges}")
        console.print(f"Developer pairs that co-edited: {pairs}")
    else:
        console.print(f"Network nodes (developers): {state.dev_to_dev_network.number_of_nodes()}")
        console.print(f"Network edges (collaborations): {state.dev_to_dev_network.size()}")
        affiliations = set(state.affiliations.values())
    console.print(f"Unique affiliations: {len(affiliations)}")
    console.print(
        f"Similar affiliation strings: 0.8 threshold {find_similar_strings(affiliations)}")
    # console.print(f"Similar affiliation strings: 0.6 threshold {find_similar_strings(set(state.affiliations.values()),0.6)}")
    console.print("=" * 60)

def normalize_zip_timestamps(zip_path: Path) -> None:
    """
    Rewrite a zip archive with a fixed timestamp on every entry.

    Zip entries record when they were written, so the same network exported
    twice would otherwise give different bytes. Content, compression and
    file attributes are kept as they are.
    """
    with zipfile.ZipFile(zip_path) as archive:
        entries = [(info, archive.read(info)) for info in archive.infolist()]

    with zipfile.ZipFile(zip_path, 'w') as archive:
        for info, data in entries:
            fixed_info = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0))
            fixed_info.compress_type = info.compress_type
            fixed_info.external_attr = info.external_attr
            archive.writestr(fixed_info, data)


def export_results(state: ProcessingState, args: argparse.Namespace) -> None:
    """Export results to GraphML and print summary."""

    if args.output_file:
        graphml_filename = Path(args.output_file)
    else:
        base = Path(args.raw).stem
        if state.network_type == 'inter_individual_graph_temporal':
            graphml_filename = base + ".temporal.graphml.zip"

        elif state.network_type == 'inter_individual_graph_weighted':
            graphml_filename = base + ".WeightedNetwork.graphML"
        elif state.network_type == 'inter_individual_graph_unweighted':
            graphml_filename = base + ".NetworkFile.graphML"
        else:
            print_error("Unknown network type")
            print_info(f"{state.network_type=}")
            sys.exit(1)
    try:
        # For temporal networks, ensure complex attributes are string fied for GraphML
        if state.network_type == 'inter_individual_graph_temporal':
            output_static_w_graph : tx.TemporalGraph = state.container_of_extracted_networks.coauthorship_temporal_network_with_time_attributes
            tx.write_graph(output_static_w_graph, graphml_filename)
            normalize_zip_timestamps(Path(graphml_filename))
        elif state.network_type == 'inter_individual_graph_weighted':
            output_static_w_graph: nx.Graph= state.container_of_extracted_networks.dev_to_dev_weighted_network
            #nx.write_graphml(output_temporal_graph, graphml_filename,  named_key_ids='email')

            if state.verbose_mode:
                console.print(f"Exporting{output_static_w_graph=}")
                console.print(f"to file{graphml_filename=}")

            if state.debug_mode and ask_yes_or_no_question("Do you want to inspect output_weighted_graph?"):
                inspect(output_static_w_graph)
                show_weighted_edges(output_static_w_graph)

            #nx.write_graphml(output_static_w_graph, graphml_filename)
            nx.write_graphml(output_static_w_graph, graphml_filename,edge_id_from_attribute='weight')


        elif state.network_type == 'inter_individual_graph_unweighted':
            output_static_uw_graph : nx.Graph = state.container_of_extracted_networks.dev_to_dev_unweighted_network

            if state.verbose_mode:
                console.print(f"Exporting{output_static_uw_graph=}")
                console.print(f"to file{graphml_filename=}")

            if state.debug_mode and ask_yes_or_no_question("Do you want to inspect output_unweighted_graph?"):
                inspect(output_static_uw_graph)
                show_weighted_edges(output_static_uw_graph)

            if  output_static_uw_graph  is None :
                print_warning(f"No unweighted graph found for {state.network_type=}, {output_static_uw_graph=}")

            "add the affiliation attributes back"

            output_static_uw_graph_with_affiliation = enrich_graph_with_affiliation(output_static_uw_graph,state.affiliations)

            export_log_data.create_graphml_file(output_static_uw_graph_with_affiliation, graphml_filename)
            #nx.write_graphml(output_static_uw_graph_with_affiliation, graphml_filename)
            export_log_data.create_graphml_file(state.dev_to_dev_network, graphml_filename)

        else:
            print_error("Unknown network type at writing graphml files")
            print_info(f"{state.network_type=}")
            sys.exit(1)


        console.print(f"\n✓ Network exported to GraphML file: {graphml_filename}")
        console.print()
    except Exception as e:
        console.print(f"ERROR exporting to GraphML: {e}")
        traceback.print_exc()
        sys.exit(1)

    print_processing_summary(state, args.raw, graphml_filename )
