read_graphml_fast#!/usr/bin/env python3

import argparse
import networkx as nx
import random
import os
from rich.console import Console
from loguru import logger

def read_graph(file_path):
    """Read a GraphML file and return the graph."""
    logger.info(f"Reading graph from file: {file_path}")
    return nx.read_graphml(file_path, node_type=str)

def reduce_graph(graph, percentage=1.0):
    """Reduce the graph size to a given percentage while preserving node attributes."""
    if percentage <= 0 or percentage > 100:
        raise ValueError("Percentage must be between 0 and 100.")
    
    total_nodes = len(graph.nodes())
    total_edges = len(graph.edges())
    
    # Calculate the number of nodes and edges to keep
    keep_nodes_count = max(1, int(total_nodes * (percentage / 100)))
    keep_edges_count = max(1, int(total_edges * (percentage / 100)))
    
    logger.info(f"Reducing graph: keeping {keep_nodes_count} nodes and {keep_edges_count} edges")
    
    # Randomly sample nodes and edges
    nodes_to_keep = set(random.sample(graph.nodes(), keep_nodes_count))
    edges_to_keep = set(random.sample(graph.edges(), keep_edges_count))
    
    # Create a new graph with the reduced size
    reduced_graph = nx.Graph()
    
    # Preserve node attributes
    for node in nodes_to_keep:
        reduced_graph.add_node(node, **graph.nodes[node])
    
    # Add edges to the reduced graph
    for edge in edges_to_keep:
        u, v = edge
        if u in nodes_to_keep and v in nodes_to_keep:
            reduced_graph.add_edge(u, v, **graph.get_edge_data(u, v))
    
    return reduced_graph

def save_graph(graph, file_path):
    """Save the graph to a GraphML file."""
    logger.info(f"Saving reduced graph to file: {file_path}")
    nx.write_graphml(graph, file_path)

def main():
    console = Console()
    
    parser = argparse.ArgumentParser(description="Reduce the size of a GraphML file by randomly removing nodes and edges.")
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to the input GraphML file.'
    )
    
    parser.add_argument(
        'output_file',
        type=str,
        nargs='?',  # This makes the argument optional
        default=None,  # Default is None, will be set based on input_file
        help='Path to the output GraphML file (default: input_file.100timesmaller.graphML).'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input_file.lower().endswith('.graphml'):
        console.print(f"[bold red]Error:[/bold red] The input file '{args.input_file}' does not have a .graphML extension.")
        return
    
    # Set default for output_file if not provided
    if args.output_file is None:
        base, _ = os.path.splitext(args.input_file)
        args.output_file = f"{base}.100timesmaller.graphML"
    
    # Read the graph from the input file
    graph = read_graph(args.input_file)
    
    # Reduce the graph to 1% of its original size
    reduced_graph = reduce_graph(graph, percentage=1.0)  # 1% of the original graph
    
    # Save the reduced graph to the output file
    save_graph(reduced_graph, args.output_file)
    
    console.print(f"Reduced graph saved to [bold green]{args.output_file}[/bold green]")

if __name__ == "__main__":
    main()

