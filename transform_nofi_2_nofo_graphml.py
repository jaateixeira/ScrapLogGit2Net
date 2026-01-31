#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transforms a network of individuals GraphML File into a network of Organization GraphML file.
Edge between org. networks is the sum of developers that worked together.

Example:
Nokia and Apple have three developers co-editing the same files
Nokia and Apple are then connected with an edge weight of 3.
"""
from rich.progress import track

# Path to visualization script
noo_viz_script = "/home/apolinex/rep_clones/own-tools/ScrapLogGit2Net/transform-nofi-2-nofo-GraphML.py"

import sys
import os
import argparse
import subprocess
from collections import defaultdict
from typing import Optional

import networkx as nx


from utils.unified_console import (
    console,
    rprint,
    Table
)

from utils.unified_logger import logger


def print_graph_as_dict_of_dicts(graph: nx.Graph) -> None:
    """Print graph as dictionary of dictionaries."""
    rprint(nx.to_dict_of_dicts(graph))


def print_graph_nodes_and_its_data(graph: nx.Graph) -> None:
    """Print all nodes and their data."""
    for g_node, g_data in graph.nodes(data=True):
        rprint(g_node)
        rprint(g_data)


def print_graph_edges_and_its_data(graph: nx.Graph) -> None:
    """Print all edges and their data."""
    for g_edge in graph.edges(data=True):
        rprint(g_edge)


def determine_file_name(base_name: str) -> str:
    """
    Generate a unique filename by appending counter if file exists.

    Args:
        base_name: Base name without extension

    Returns:
        Unique filename with .graphML extension
    """
    counter = 0
    file_name = f"{base_name}.graphML"

    while os.path.exists(file_name):
        counter += 1
        file_name = f"{base_name}({counter}).graphML"

    return file_name


def create_organizational_network(
        individual_network: nx.Graph,
        verbose: bool = False
) -> nx.Graph:
    """
    Transform individual network into organizational network.

    Args:
        individual_network: Network of individuals
        verbose: Whether to print verbose output

    Returns:
        Network of organizations with weighted edges
    """
    logger.info("Creating organizational network from individual network")
    org_network = nx.Graph()
    org_edges = defaultdict(int)

    console.print("\n[yellow]Iterating over all edges of G (network of individuals)[/yellow]")

    # For every edge in individual network, find inter-organizational edges
    for edge in track(individual_network.edges(), description="Processing edges..."):
        org_affiliation_from = nx.get_node_attributes(
            individual_network, "affiliation"
        )[edge[0]]
        org_affiliation_to = nx.get_node_attributes(
            individual_network, "affiliation"
        )[edge[1]]

        if verbose:
            logger.debug(f"Edge info: {edge} FROM node id {edge[0]} TO node id {edge[1]}")
            logger.debug(f"{org_affiliation_from}  <-->  {org_affiliation_to}")

        # Skip intra-firm relationships
        if org_affiliation_from == org_affiliation_to:
            if verbose:
                logger.debug("Intra-firm relationship - To IGNORE")
            continue

        # Count inter-firm relationships
        if org_affiliation_from != org_affiliation_to:
            if verbose:
                logger.debug("Inter-firm relationship")

            # Use frozenset for immutable edge representation
            org_edges[frozenset([org_affiliation_from, org_affiliation_to])] += 1

            if verbose:
                logger.debug(f"FOUND NEW orgG relation {org_affiliation_from}  <-->  {org_affiliation_to}. "
                             f"Increasing the weight attribute by 1")

    # Add nodes and weighted edges to the organizational network
    if verbose:
        logger.debug("Adding nodes and weighted edges to the inter-organizational network")

    logger.info(f"Number of inter organisational edges={len(org_edges.items())}")

    for org_edge, weight in org_edges.items():
        if verbose:
            logger.debug(f"org_edge={org_edge}, weight={weight}")

        org_u, org_v = list(org_edge)
        org_network.add_edge(org_u, org_v, weight=weight)

    logger.info(f"Organizational network created with {org_network.number_of_nodes()} nodes "
                   f"and {org_network.number_of_edges()} edges")
    return org_network


def remove_isolates(graph: nx.Graph, verbose: bool = False) -> nx.Graph:
    """
    Remove isolated nodes from graph.

    Args:
        graph: Input graph
        verbose: Whether to print verbose output

    Returns:
        Graph with isolates removed
    """
    isolate_ids = list(nx.isolates(graph))

    if isolate_ids:
        logger.warning(f"Found {len(isolate_ids)} isolates:")

        table = Table(title="Isolated Nodes", show_header=True, header_style="bold magenta")
        table.add_column("Node ID", style="cyan")
        table.add_column("Email", style="green")
        table.add_column("Affiliation", style="yellow")

        for node, data in graph.nodes(data=True):
            if node in isolate_ids:
                table.add_row(
                    node,
                    data.get('e-mail', 'N/A'),
                    data.get('affiliation', 'N/A')
                )

        console.print(table)

        console.print("\n[bold yellow]WARNING:[/bold yellow] Removing isolates")
        console.print("[bold yellow]WARNING:[/bold yellow] Networks created with scraplog should only capture "
                      "collaborative relationships (i.e., no isolates)")

        graph.remove_nodes_from(isolate_ids)
        logger.info(f"Removed {len(isolate_ids)} isolates from graph")

    return graph


def save_network(
        graph: nx.Graph,
        output_file: Optional[str] = None,
        input_file: Optional[str] = None
) -> str:
    """
    Save graph to GraphML file.

    Args:
        graph: NetworkX graph to save
        output_file: Output filename (if None, generates automatically)
        input_file: Original input filename (used for auto-naming)

    Returns:
        Path to saved file
    """
    if output_file is None and input_file is not None:
        base_name = os.path.basename(input_file).replace('.graphML', '')
        base_name = base_name.replace('-transformed-to-nofo', '')
        transformed_file_name = determine_file_name(f"{base_name}-transformed-to-nofo")
    elif output_file is None:
        transformed_file_name = determine_file_name("network-transformed-to-nofo")
    else:
        transformed_file_name = output_file
        # Ensure .graphML extension
        if not transformed_file_name.endswith('.graphML'):
            transformed_file_name += '.graphML'

    logger.info(f"Saving network to {transformed_file_name}")
    nx.write_graphml_lxml(graph, transformed_file_name)
    logger.success(f"File saved successfully: {transformed_file_name}")
    return transformed_file_name


def main() -> None:
    """Main function to orchestrate the transformation."""
    console.print("\n[bold blue]transform-nofi-2-nofo-GraphML.py[/bold blue] - "
                  "transforming unweighted networks of individuals into weighted networks "
                  "of organizations since June 2024")
    console.print("[bold green]Let's go![/bold green]\n")

    parser = argparse.ArgumentParser(
        description="Transform unweighted networks of individuals into weighted networks of organizations"
    )

    parser.add_argument(
        "file",
        type=str,
        help="the network file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="increase output verbosity"
    )
    parser.add_argument(
        "-t", "--top-firms-only",
        action="store_true",
        help="only top_firms_that_matter (not implemented yet)"
    )
    parser.add_argument(
        "-f", "--filter-by-org",
        action="store_true",
        help="top_firms_that_do_not_matter (not implemented yet)"
    )
    parser.add_argument(
        "-s", "--show",
        action="store_true",
        help="Shows/plots the result with formatAndViz-nofo-GraphML.py"
    )
    parser.add_argument(
        "-o", "--outfile",
        type=str,
        default=None,
        help="Output filename for the transformed network"
    )

    args = parser.parse_args()

    # Check for unimplemented features
    if args.top_firms_only:
        console.print("\n[bold yellow]In top-firms only mode[/bold yellow]")
        console.print("[bold red]ERROR:[/bold red] Filtering by top firms not implemented yet")
        sys.exit(1)

    if args.filter_by_org:
        console.print("\n[bold yellow]In filtering by org mode[/bold yellow]")
        console.print("[bold red]ERROR:[/bold red] Filtering by organizations not implemented yet")
        sys.exit(1)

    if args.verbose:
        logger.info("Running in verbose mode")

    if args.show:
        logger.info("Will display results after transformation")

    # Read the input graph
    console.print(f"[cyan]Reading graph from {args.file}[/cyan]")
    try:
        g = nx.read_graphml(args.file)
    except Exception as e_read:
        logger.error(f"Error reading graph file: {e_read}")
        console.print_exception()
        sys.exit(1)

    # Display graph statistics
    stats_table = Table(title="Input Graph Statistics", show_header=True)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green", justify="right")

    stats_table.add_row("Number of nodes", str(g.number_of_nodes()))
    stats_table.add_row("Number of edges", str(g.number_of_edges()))
    stats_table.add_row("Number of isolates", str(nx.number_of_isolates(g)))

    console.print(stats_table)

    if args.verbose:
        console.print("\n[bold yellow]Verbose output:[/bold yellow]")
        console.print("[bold]Graph as dictionary of dictionaries:[/bold]")
        print_graph_as_dict_of_dicts(g)
        console.print("\n[bold]Graph nodes and their data:[/bold]")
        print_graph_nodes_and_its_data(g)

    # Remove isolates
    console.print("\n[cyan]Checking for isolates[/cyan]")
    g = remove_isolates(g, args.verbose)

    # Display updated statistics
    stats_table = Table(title="Graph Statistics After Removing Isolates", show_header=True)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green", justify="right")

    stats_table.add_row("Number of nodes", str(g.number_of_nodes()))
    stats_table.add_row("Number of edges", str(g.number_of_edges()))
    stats_table.add_row("Number of isolates", str(nx.number_of_isolates(g)))

    console.print(stats_table)

    console.print("\n[bold green]✓[/bold green] We have network of individuals")
    console.print("[bold green]✓[/bold green] We don't have isolates")
    console.print("[bold yellow]Transforming it into a network of organizations...[/bold yellow]\n")

    # Create organizational network
    org_g: nx.Graph = create_organizational_network(g, args.verbose)

    if args.verbose:
        console.print("\n[bold]Current orgG (network of organizations):[/bold]")
        console.print("\n[bold]The nodes:[/bold]")
        print_graph_nodes_and_its_data(org_g)
        console.print("\n[bold]The edges:[/bold]")
        print_graph_edges_and_its_data(org_g)

    # Display organizational network statistics
    org_stats_table = Table(title="Organizational Network Statistics", show_header=True)
    org_stats_table.add_column("Metric", style="cyan")
    org_stats_table.add_column("Value", style="green", justify="right")

    org_stats_table.add_row("Number of organizations", str(org_g.number_of_nodes()))
    org_stats_table.add_row("Number of inter-org relationships", str(org_g.number_of_edges()))

    console.print(org_stats_table)

    # Save the transformed network
    console.print("\n[yellow]Time to save orgG, the inter-organizational network "
                  "with weighted edges into the GraphML format[/yellow]")

    output_file = save_network(org_g, args.outfile, args.file)

    # Display results if requested
    if args.show:
        console.print("\n[bold cyan]Displaying the results[/bold cyan]")

        if not os.path.exists(noo_viz_script):
            logger.warning(f"Visualization script not found at {noo_viz_script}")
            console.print("[bold yellow]Warning:[/bold yellow] Skipping visualization")
        else:
            # Escape parentheses for shell safety
            safe_output_file = output_file.replace("(", "\\(").replace(")", "\\)")
            show_cmd = f"python3 {noo_viz_script} {safe_output_file}"

            logger.info(f"Invoking visualization script: {show_cmd}")

            try:
                subprocess.call(show_cmd, shell=True)
            except Exception as e_read:
                logger.error(f"Error running visualization script: {e_read}")
                console.print_exception()

    console.print("\n[bold green]✓ Transformation completed successfully![/bold green]")
    logger.info("Transformation process completed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Process interrupted by user[/bold yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print_exception()
        sys.exit(1)
