#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
This module  deanonymizes GitHub noreply emails in gramphML files created with ScrapLogGit2Net
"""



import sys
import argparse
import networkx as nx


from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import track


# Initialize Rich console for formatted output
console = Console()

# Configure Loguru to use Rich for logging
logger.remove()  # Remove the default logger configuration

# Add a new logger with RichHandler to format the output
logger.add(
    RichHandler(console=console, level="DEBUG", show_time=True, show_level=True, show_path=True),
    level="DEBUG"
)

def log_messages():
    # Log messages at different levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

# Configure Loguru to use Rich for formatting exceptions
logger.remove()  # Remove default logger
logger.add(sys.stdout, level="DEBUG", format="{message}", backtrace=True, diagnose=True)



# For the GitHub REST APY
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Use GITHUB_TOKEN in your requests
# Replace with your personal access token if needed

GITHUB_TOKEN = config.get('github', 'token', fallback=None)

print("\tGITHUB_TOKEN=[",GITHUB_TOKEN,"]")

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

        # Check if the root tag is 'graphml'
        if root.tag == 'graphml':
            # Check if the namespace is correct
            if root.attrib.get('xmlns') == 'http://graphml.graphdrawing.org/xmlns':
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
email = "userID+username@users.noreply.github.com"
try:
    result = deanonymize_github_user(email)
    print(json.dumps(result, indent=4))
except ValueError as e:
    print(e)



def iterate_graph(input_file, output_file):
    logger.info(f"Iterating network in file graph({input_file=} to copy to {output_file=} with  deanonymize github user emails")
    

    if not check_file_exists(input_file):
        logger.error(f"The file '{file_path}' does not exist.")
        sys.exit()

    if is_valid_graphml(input_file):
        logger.error(f"The file '{file_path}' is a valid GraphML file.")
    else:
        sys.exit()

    
    

    # Read the input GraphML file
    logger.info(f"Reading input GraphML file: {input_file}")
    G = nx.read_graphml(input_file)

    # Create a new directed graph for the output
    G_copy = nx.DiGraph()

    # Copy nodes from the input graph to the new graph
    for node in track(G.nodes(), description="Copying nodes..."):
        loger.debug("Iterating {node=}")

        G_copy.add_node(node)
        logger.debug(f"Copied node: {node}")

        # We want to copy edges also to preserve network 
        # for edge in G.edges():
        G_copy.add_edge(*edge)
        logger.debug(f"Copied edge: {edge}")

        # Write the copied graph to the output GraphML file
        logger.info(f"Writing output GraphML file: {output_file}")
        nx.write_graphml(G_copy, output_file)

        console.print(f"[bold green]Successfully copied the graph to {output_file}[/bold green]")


def main():
    parser = argparse.ArgumentParser(description="Copy nodes from an input GraphML file to an output GraphML file.")
    parser.add_argument("input", type=str, help="Input GraphML file path")
    parser.add_argument("output", type=str, help="Output GraphML file path")
    
    args = parser.parse_args()

    # Call the function to copy the graph
    iterate_graph(args.input, args.output)

if __name__ == "__main__":
    main()



