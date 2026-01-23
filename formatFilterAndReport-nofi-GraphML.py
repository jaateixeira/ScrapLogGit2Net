#!/usr/bin/env python3

"""
formatAndReportGraphML - Reporter for GraphML files

TODO: Should report on TOP 20 companies with more nodes
TODO: Should report on TOP 20 companies with more edges
TODO: Should report on % of edges by companies on top 20 with more nodes
TODO: Should report on % of edges by companies on top 20 with more nodes
TODO: Should report on centrality of developers and organizations
TODO: Should export in XML, html, latex, MD, CSV and txt files
"""

import argparse
import os
import sys
import networkx as nx
import xlwt
from utils.unified_logger import logger
from utils.unified_console import console


def list_of_strings(arg):
    """Convert comma-separated string to list of strings."""
    """Used for parsing arguments, mostly"""
    return arg.split(',')


def parse_arguments():
    """Parse command line arguments."""
    console.print("\tParsing command line arguments")

    parser = argparse.ArgumentParser(description="Reporter for GraphML files")
    parser.add_argument("file", type=str, help="the network file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-oi", "--org_list_to_ignore", type=list_of_strings,
                        help="Filter out developers affiliated with organizations in a given list. Example: -oi microsoft,meta,amazon.")
    parser.add_argument("-oo", "--org_list_only", type=list_of_strings,
                        help="Consider only developers affiliated with organizations in a given list. Example: -oo google,microsoft.")

    return parser.parse_args()


def normalize_affiliations(graph, verbose=False):
    """
    Normalize affiliation domains that represent the same organization.

    Examples:
    - alum.mit and .mit should be same
    - cz.ibm.com and us.ibm.com should also be the same
    """
    for node, data in graph.nodes(data=True):
        if data.get('affiliation') == 'alum':
            data['affiliation'] = 'alum.mit.edu'
            if verbose:
                logger.info(f"Normalized affiliation for node {node}: alum -> alum.mit.edu")

    return graph


def print_graph_as_dict_of_dicts(graph):
    """Print graph as dictionary of dictionaries."""
    console.print(nx.to_dict_of_dicts(graph))


def print_graph_nodes_and_data(graph):
    """Print graph nodes and their data."""
    for node, data in graph.nodes(data=True):
        console.print(node)
        console.print(data)


def filter_graph_by_organizations(graph, org_list, exclude=True, verbose=False):
    """
    Filter graph by organizations.

    Args:
        graph: NetworkX graph
        org_list: List of organizations to filter
        exclude: If True, remove nodes with these affiliations
                 If False, keep only nodes with these affiliations
        verbose: Whether to print verbose output
    """
    if not org_list:
        return graph

    operation = "excluding" if exclude else "keeping only"
    console.print(f"\t{operation} nodes affiliated with {org_list}")

    nodes_to_remove = []

    for node, data in graph.nodes(data=True):
        affiliation = data.get('affiliation', '')
        should_remove = (affiliation in org_list) if exclude else (affiliation not in org_list)

        if should_remove:
            nodes_to_remove.append(node)
            if verbose:
                action = "Removing" if exclude else "Filtering out"
                logger.info(f"\t\t {action} node {node}: {data}")

    graph.remove_nodes_from(nodes_to_remove)
    console.print(f"\tRemoved {len(nodes_to_remove)} nodes")

    return graph


def calculate_graph_statistics(graph):
    """Calculate and return basic graph statistics."""
    stats = {
        'num_nodes': graph.number_of_nodes(),
        'num_edges': graph.number_of_edges(),
        'num_isolates': nx.number_of_isolates(graph),
        'isolates': list(nx.isolates(graph))
    }
    return stats


def export_graph_statistics(workbook, stats):
    """Export graph statistics to Excel sheet."""
    sheet = workbook.add_sheet("Graph SNA Stats")

    sheet.write(0, 0, "Number_of_nodes")
    sheet.write(0, 1, str(stats['num_nodes']))

    sheet.write(1, 0, "Number_of_edges")
    sheet.write(1, 1, str(stats['num_edges']))

    sheet.write(2, 0, "Number_of_isolates")
    sheet.write(2, 1, str(stats['num_isolates']))

    console.print("\tDONE: Exported graph stats")
    return workbook


def print_isolates(graph, stats):
    """Print isolate information if any exist."""
    if stats['isolates']:
        console.print("\t Isolates:")
        for isolate in stats['isolates']:
            data = graph.nodes[isolate]
            console.print(f"\t {isolate}, {data.get('e-mail', 'N/A')}, {data.get('affiliation', 'N/A')}")


def calculate_and_print_centralities(graph, verbose=False):
    """Calculate and print centrality measures."""
    console.print("\n\tCalculating centralities")

    degree_centrality = nx.centrality.degree_centrality(graph)
    sorted_degree_centrality = sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)

    if verbose:
        logger.info(f"Degree centrality: {degree_centrality}")

    return sorted_degree_centrality


def analyze_top_connected_individuals(graph, sorted_centrality, top_n=10, verbose=False):
    """Analyze and print top connected individuals."""
    console.print(f"\nTOP {top_n} ind. with most edges:")

    top_connected = sorted_centrality[:top_n]
    top_ids = dict(top_connected).keys()

    if verbose:
        logger.info(f"Top {top_n} connected individuals: {top_connected}")
        logger.info(f"IDs of top {top_n} connected individuals: {list(top_ids)}")

    for node_id in top_ids:
        data = graph.nodes[node_id]
        console.print(data.get('e-mail', 'N/A'))

    return top_connected


def analyze_organizations_by_nodes(graph, verbose=False):
    """Analyze organizations by number of nodes."""
    console.print("\n\tFinding the organizations with most nodes")

    affiliations_freq = {}
    for node, data in graph.nodes(data=True):
        affiliation = data.get('affiliation', '')
        if affiliation:
            affiliations_freq[affiliation] = affiliations_freq.get(affiliation, 0) + 1

    sorted_affiliations = dict(sorted(affiliations_freq.items(),
                                      key=lambda item: item[1],
                                      reverse=True))

    if verbose:
        logger.info(f"All affiliations frequency: {sorted_affiliations}")

    return sorted_affiliations


def export_organizations_to_excel(workbook, organizations):
    """Export organization statistics to Excel sheet."""
    sheet = workbook.add_sheet("Organization with most nodes")

    for index, (org, count) in enumerate(organizations.items()):
        sheet.write(index, 0, org)
        sheet.write(index, 1, count)

    console.print("\tDONE: Exported organizations with most nodes")
    return workbook


def export_nodes_to_excel(workbook, graph):
    """Export node list to Excel sheet."""
    sheet = workbook.add_sheet("Nodes aka developers list")

    # Write headers
    sheet.write(0, 0, "id")
    sheet.write(0, 1, "e-mail")
    sheet.write(0, 2, "affiliation")

    # Write node data
    for node, data in graph.nodes(data=True):
        try:
            row = int(node) + 1
            sheet.write(row, 0, node)
            sheet.write(row, 1, data.get('e-mail', ''))
            sheet.write(row, 2, data.get('affiliation', ''))
        except ValueError:
            # If node ID is not an integer, write to next available row
            row = sheet.last_used_row + 1 if hasattr(sheet, 'last_used_row') else 1
            sheet.write(row, 0, node)
            sheet.write(row, 1, data.get('e-mail', ''))
            sheet.write(row, 2, data.get('affiliation', ''))
            sheet.last_used_row = row

    console.print("\tDONE: Exported node list")
    return workbook


def process_graphml_file(input_file, args):
    """
    Main processing pipeline for GraphML file.

    Args:
        input_file: Path to GraphML file
        args: Command line arguments

    Returns:
        tuple: (graph, output_filename_prefix)
    """
    console.print("\n\tReading the required INPUT GraphML file")

    try:
        graph = nx.read_graphml(input_file)
        console.print("\tGraph imported successfully")
    except Exception as e:
        logger.error(f"Failed to read GraphML file: {e}")
        return None, None

    # Set output filename prefix
    output_filename_prefix = os.path.basename(input_file)

    # Normalize affiliations
    graph = normalize_affiliations(graph, args.verbose)

    # Print graph details if verbose
    if args.verbose:
        console.print("\nPrinting graph as dict of dicts:")
        print_graph_as_dict_of_dicts(graph)
        console.print("\nPrinting graph nodes and data:")
        print_graph_nodes_and_data(graph)

    # Filter graph based on arguments
    if args.org_list_to_ignore:
        graph = filter_graph_by_organizations(graph, args.org_list_to_ignore,
                                              exclude=True, verbose=args.verbose)

    if args.org_list_only:
        graph = filter_graph_by_organizations(graph, args.org_list_only,
                                              exclude=False, verbose=args.verbose)

    return graph, output_filename_prefix


def main():
    """Main function to orchestrate the GraphML reporting."""
    console.print("Welcome to formatAndReportGraphML")
    console.print("Reporter of GraphML is only now being implemented")
    console.print("")

    # Parse arguments
    args = parse_arguments()

    if args.verbose:
        console.print("In verbose mode")

    # Process GraphML file
    graph, output_filename_prefix = process_graphml_file(args.file, args)

    if graph is None:
        logger.error("Failed to process GraphML file. Exiting.")
        sys.exit(1)

    # Calculate and print graph statistics
    stats = calculate_graph_statistics(graph)
    console.print(f"\nNumber_of_nodes={stats['num_nodes']}")
    console.print(f"Number_of_edges={stats['num_edges']}")
    console.print(f"Number_of_isolates={stats['num_isolates']}")

    # Print isolates if any exist
    print_isolates(graph, stats)

    # Create Excel workbook
    console.print("\nExporting graph stats to Excel")
    workbook = xlwt.Workbook(encoding="utf-8")

    # Export graph statistics
    workbook = export_graph_statistics(workbook, stats)

    # Calculate centralities
    sorted_centrality = calculate_and_print_centralities(graph, args.verbose)

    # Analyze top connected individuals
    analyze_top_connected_individuals(graph, sorted_centrality, top_n=10, verbose=args.verbose)

    # Analyze organizations
    top_organizations = analyze_organizations_by_nodes(graph, args.verbose)

    # Export organizations to Excel
    workbook = export_organizations_to_excel(workbook, top_organizations)

    # Export nodes to Excel
    workbook = export_nodes_to_excel(workbook, graph)

    # Save Excel file
    output_filename = f"{output_filename_prefix}.xls"
    console.print(f"\n\tWriting the Excel file [{output_filename}]")

    try:
        workbook.save(output_filename)
        console.print(f"\tSuccessfully saved to {output_filename}")
    except Exception as e:
        logger.error(f"Failed to save Excel file: {e}")
        sys.exit(1)

    console.print("\nProcessing completed successfully!")


if __name__ == "__main__":
    main()