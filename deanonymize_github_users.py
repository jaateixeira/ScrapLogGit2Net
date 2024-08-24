#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
This module  deanonymizes GitHub noreply emails in gramphML files created with ScrapLogGit2Net
"""



import sys
import argparse
import networkx as nx

from typing import Tuple 

from loguru import logger


from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table
#from rich.pretty import Pretty
from rich import print as rprint
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown

# For progress while reading GraphML files
from rich.progress import Progress, TaskID
import time

# For configuring 
from rich.traceback import install
# Install the Rich Traceback handler with custom options
install(
    show_locals=True,  # Show local variables in the traceback
    locals_max_length=10, locals_max_string=80, locals_hide_dunder=True, locals_hide_sunder=False,
    indent_guides=True,
    suppress=[__name__],
    # suppress=[your_module],  # Suppress tracebacks from specific modules
    max_frames=3,  # Limit the number of frames shown
    width=50,  # Set the width of the traceback display
    extra_lines=3,  # Show extra lines of code around the error
    theme="solarized-dark",  # Use a different color theme
    word_wrap=True,  # Enable word wrapping for long lines
)



# Create a Rich console
console = Console()

# Add RichHandler to the loguru logger
logger.remove()  # Remove the default logger
logger.add(
    RichHandler(console=console, show_time=True, show_path=True, rich_tracebacks=True),
    format="{message}",  # You can customize this format as needed
    level="DEBUG",  # Set the desired logging level
)

def log_messages():
    rprint("\n\t Testing logger messages:\n")
    
    # Log messages at different levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    rprint("\n")

    rprint("\n\t Testing console messages:\n")

    markdown_text = Markdown("# This is a heading\n\n- This is a list item\n- Another item")
    console.print(markdown_text)

    
    # An example of a styled message
    console.print("[bold blue]Welcome to [blink]Rich[/blink]![/bold blue]")
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.")
    console.print("[bold red]Error:[/bold red] Something went wrong. Please try again.")
    
    rprint("\n\t error traces are handled by rich.traceback\n")


# For the GitHub REST APY
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Use GITHUB_TOKEN in your requests
# Replace with your personal access token if needed

GITHUB_TOKEN = config.get('github', 'token', fallback=None)

rprint("\t Accessing GitHub Rest API with GITHUB_TOKEN=[",GITHUB_TOKEN,"]")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN in the config.ini file")



import requests
import json


import os
import xml.etree.ElementTree as ET

def check_file_exists(file_path):
    return os.path.isfile(file_path)

def is_valid_graphml(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        logger.debug(f"checking graphml file root tag {root.tag=}")

        # Check if the root tag is 'graphml'
        if  'graphml' in root.tag:
            return True
        return False
    except ET.ParseError:
        return False

def deanonymize_github_user(email):
    if '@users.noreply.github.com' not in email:
        raise ValueError("The provided email address is not a valid GitHub noreply email.")

    # Extract the username part from the email
    try:
        username = email.split('+')[1].split('@')[0]
    except IndexError:
        raise ValueError("Unable to extract GitHub username from the email address.")

    # GitHub API URL for the user's profile
    url = f"https://api.github.com/users/jaateixeira"

    # Perform the API request
    response = requests.get(url)

    if response.status_code == 200:
        user_data = response.json()
        
        # Extracting affiliation/organization information
        affiliation = user_data.get('company', 'No affiliation/organization available')
        
        return {
            "username": username,
            "affiliation": affiliation,
            "profile_url": user_data.get("html_url"),
            "name": user_data.get("name", "Name not available"),
            "location": user_data.get("location", "Location not available"),
            "bio": user_data.get("bio", "Bio not available"),
        }
    else:
        raise ValueError(f"Failed to retrieve information for GitHub user: {username}")

# Example Usage
#email = "userID+username@users.noreply.github.com"
#try:
#    result = deanonymize_github_user(email)
#    print(json.dumps(result, indent=4))
#except ValueError as e:
#    print(e)


def print_all_nodes(network: nx.Graph):
    """
    Print all nodes in a NetworkX graph along with their attributes using rich for pretty formatting.

    Parameters:
    network (nx.Graph): The NetworkX graph.
    """

    logger.info(f"Printing all nodes in network {network=}:")
    
    if not isinstance(network, nx.Graph):
        raise TypeError("The input must be a NetworkX graph.")

    console = Console()
    table = Table(title="Nodes and Attributes")

    # Add columns to the table
    table.add_column("Node ID", style="bold cyan")
    table.add_column("Attributes", style="bold magenta")

    # Iterate over the nodes and their attributes
    for node, attributes in network.nodes(data=True):
        attr_str = ", ".join(f"{key}: {value}" for key, value in attributes.items())
        table.add_row(str(node), attr_str if attr_str else "None")

    # Print the table
    console.print(table)



    
def read_graphml_with_progress(file_path: str) -> nx.Graph:
    """
    Read a GraphML file and display a progress bar using rich.

    Parameters:
    file_path (str): The path to the GraphML file.

    Returns:
    nx.Graph: The NetworkX graph.
    """
    progress = Progress(console=console)

    # Create a task for the progress bar
    task_id = progress.add_task("[cyan]Reading GraphML file...", total=100)

    # Start the progress bar
    progress.start()

    try:
        # Read the graph using networkx.read_graphml
        graph = nx.read_graphml(file_path)

        # Simulate progress updates (since networkx.read_graphml does not provide progress callbacks)
        for i in range(100):
            time.sleep(0.01)  # Simulate work being done
            progress.update(task_id, advance=1)

        progress.update(task_id, completed=100)
        progress.stop()

        return graph
    except Exception as e:
        progress.stop()
        console.print(f"[red]Error reading GraphML file: {e}[/red]")
        raise



def copy_graph_with_attributes(source_graph: nx.Graph) -> nx.Graph:
    """
    Copy nodes, edges, and their attributes from the source graph to a new target graph.

    Parameters:
    source_graph (nx.Graph): The source graph.

    Returns:
    nx.Graph: The new target graph with copied nodes, edges, and attributes.
    """
    target_graph = nx.Graph()

    # Copy nodes with attributes
    for node, attributes in source_graph.nodes(data=True):
        target_graph.add_node(node, **attributes)

    # Copy edges with attributes
    for u, v, attributes in source_graph.edges(data=True):
        target_graph.add_edge(u, v, **attributes)

    return target_graph

    
def iterate_graph(input_file, output_file):
    logger.info(f"Iterating network in file graph({input_file=} to copy to {output_file=} with  deanonymized github user emails")
    

    if not check_file_exists(input_file):
        logger.error(f"The file '{input_file}' does not exist.")
        sys.exit()
    else:
        logger.info (f"The file '{input_file}' to be copied and deanonymize  exist.")
    

    #if is_valid_graphml(input_file):
    #    logger.info(f"The file '{input_file}' is a valid GraphML file.")
    #else:
    #    logger.error(f"The file '{input_file}' is an invalid GraphML file.")
    #    sys.exit()



    # Read the input GraphML file
    logger.info(f"Reading input GraphML file: {input_file}")


    # Option 1) With the facing progress 
    try:
        G = read_graphml_with_progress(input_file)
        console.print("[green]Graph read successfully![/green]")
        # You can now work with the graph
        print(f"Number of nodes: {graph.number_of_nodes()}")
        print(f"Number of edges: {graph.number_of_edges()}")
    except Exception as e:
        console.print(f"[red]Failed to read the graph: {e}[/red]")
        

    # Option 2) Without the facing progress 
    #G = nx.read_graphml(input_file)

    # Create a new directed graph for the output
    G_copy = nx.Graph()


    #print_all_nodes(G)
    

  # Retrieve nodes and attributes
    nodes_data = G.nodes(data=True)

    table = Table(title="Nodes and Attributes")

    # Add columns to the table
    table.add_column("Node ID", style="bold cyan")
    table.add_column("Attributes", style="bold magenta")
    
    # Create a Live display
    with Live(table, console=console, refresh_per_second=3) as live:
        # Iterate over the nodes and their attributes
        for node, attributes in nodes_data:
            attr_str = ", ".join(f"{key}: {value}" for key, value in attributes.items())
            table.add_row(str(node), attr_str if attr_str else "None")
            live.update(table)



    logger.info(f"Coping node {G=} to {G_copy=}")
    G_copy=copy_graph_with_attributes(G)

    logger.info(f"Iterating over the copy {G_copy} and replace email atributte")

    sys.exit()
    
        # Write the copied graph to the output GraphML file
    logger.info(f"Writing output GraphML file: {output_file}")
    nx.write_graphml(G_copy, output_file)

    console.print(f"[bold green]Successfully copied the graph to {output_file}[/bold green]")


def main():

    log_messages()
    
    parser = argparse.ArgumentParser(description="Copy nodes from an input GraphML file to an output GraphML file.")
    parser.add_argument("input", type=str, help="Input GraphML file path")
    parser.add_argument("output", type=str, help="Output GraphML file path")
    
    args = parser.parse_args()

    # Call the function to copy the graph
    iterate_graph(args.input, args.output)

if __name__ == "__main__":
    main()



