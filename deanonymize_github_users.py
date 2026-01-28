#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module deanonymizes GitHub noreply emails in GraphML files created with ScrapLogGit2Net
"""
import json
import sys
import os
import argparse
import networkx as nx
from typing import Tuple, Optional, Dict, Any, List
import time
from pathlib import Path

# Rich and loguru imports
from loguru import logger
from rich import print as rprint
from rich.console import Console
from rich import print_json
from rich.table import Table
from rich.live import Live
from rich.progress import Progress
from rich.text import Text
from rich.traceback import install

# Initialize the console
console = Console()

# Install Rich traceback handler with custom options
install(
    show_locals=True,
    locals_max_length=10,
    locals_max_string=80,
    locals_hide_dunder=True,
    locals_hide_sunder=False,
    indent_guides=True,
    suppress=[__name__],
    max_frames=5,
    width=100,
    extra_lines=3,
    theme="solarized-dark",
    word_wrap=True,
)

# For the GitHub REST API
import requests
import configparser
import requests_cache
from github import Github, GithubException, RateLimitExceededException

# For validating a GraphML File
import xml.etree.ElementTree as ET

# Set up requests-cache
requests_cache.install_cache('github_cache', expire_after=3600)

# Global dictionary for caching user affiliations
already_known_user_affiliations: Dict[str, Tuple[str, str]] = {}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file or environment variables.

    Priority order:
    1. Command line arguments (config file path)
    2. Environment variables
    3. Default config.ini file
    4. Raise error if no configuration found

    Args:
        config_path: Optional path to config file

    Returns:
        Dictionary with configuration values
    """
    config_values: Dict[str, Any] = {}

    # Try environment variables first (recommended for production)
    github_token = os.getenv('GITHUB_TOKEN')
    current_project = os.getenv('CURRENT_PROJECT')

    if github_token:
        config_values['token'] = github_token
        console.print("[green]✓ Using GITHUB_TOKEN from environment variables[/green]")
    if current_project:
        config_values['current_project'] = current_project
        console.print("[green]✓ Using CURRENT_PROJECT from environment variables[/green]")

    # If we have both from env, return early
    if 'token' in config_values and 'current_project' in config_values:
        return config_values

    # Try config file if not fully configured from env
    config_files_to_try: List[str] = []

    if config_path:
        config_files_to_try.append(config_path)
    config_files_to_try.append('config.ini')  # Default

    config_parser = configparser.ConfigParser()

    for config_file in config_files_to_try:
        config_file_path = Path(config_file)
        if config_file_path.exists():
            try:
                console.print(f"Reading configuration from: {config_file_path}")
                config_parser.read(config_file_path)

                # Get values with fallbacks
                if 'token' not in config_values:
                    token_from_file = config_parser.get('github', 'token', fallback=None)
                    if token_from_file:
                        config_values['token'] = token_from_file
                        console.print(f"[green]✓ Using GITHUB_TOKEN from {config_file_path}[/green]")

                if 'current_project' not in config_values:
                    project_from_file = config_parser.get('github', 'current_project', fallback=None)
                    if project_from_file:
                        config_values['current_project'] = project_from_file
                        console.print(f"[green]✓ Using CURRENT_PROJECT from {config_file_path}[/green]")

                # Break if we found all required values
                if 'token' in config_values and 'current_project' in config_values:
                    break

            except (configparser.Error, OSError) as e:
                console.print(f"[yellow]Warning: Could not read {config_file_path}: {e}[/yellow]")
                continue

    # Validate we have all required configuration
    if 'token' not in config_values:
        raise ValueError(
            "GitHub token not found. Please set it via:\n"
            "1. Environment variable: GITHUB_TOKEN\n"
            "2. Config file: [github] section with 'token' key\n"
            "3. Command line: --config path/to/config.ini"
        )

    if 'current_project' not in config_values:
        raise ValueError(
            "Current project not found. Please set it via:\n"
            "1. Environment variable: CURRENT_PROJECT\n"
            "2. Config file: [github] section with 'current_project' key\n"
            "3. Command line: --config path/to/config.ini"
        )

    return config_values


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(file_path)


def is_valid_graphml(file_path: str) -> bool:
    """Validate if a file is a valid GraphML file."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        logger.debug(f"Checking GraphML file root tag: {root.tag}")
        return 'graphml' in root.tag
    except ET.ParseError:
        return False


def get_rate_limit(headers: Dict[str, str]) -> Dict[str, Any]:
    """Get GitHub API rate limit information."""
    logger.info("Getting rate limit")
    response = requests.get("https://api.github.com/rate_limit", headers=headers)
    data = response.json()
    return data["resources"]["core"]


def display_rate_limit(headers: Dict[str, str]) -> None:
    """Display GitHub API rate limit information."""
    logger.info("Displaying rate limit")
    rate_limit = get_rate_limit(headers)
    console.print(rate_limit)


def print_github_user_data(user_data: Dict[str, Any]) -> None:
    """Print GitHub user data in a formatted table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key")
    table.add_column("Value")

    for key, value in user_data.items():
        table.add_row(key, str(value))

    console.print(table)


def get_user_organizations(username: str, headers: Dict[str, str]) -> List[str]:
    """
    Fetch the organizations a GitHub user belongs to.

    Args:
        username: GitHub username
        headers: Authentication headers

    Returns:
        List of organization names
    """
    url = f'https://api.github.com/users/{username}/orgs'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        orgs_data = response.json()
        organizations = [org['login'] for org in orgs_data]

        console.print("\n")
        console.print(":star_struck: :astonished: Found organizations!")
        console.print(f"Organizations for {username}:")
        for org in organizations:
            console.print(f"{org=}")
        console.print("\n")

        return organizations
    else:
        logger.warning(f"Failed to retrieve organizations: {response.status_code}")
        return []


def deanonymize_github_user_with_cache_and_pygithub(
        email: str,
        github_token: str,
        already_known_user_affiliations: Dict[str, Tuple[str, str]]
) -> Tuple[str, str]:
    """
    De-anonymizes a GitHub user using PyGithub with caching.

    Args:
        email: GitHub noreply email
        github_token: GitHub API token
        already_known_user_affiliations: Cache dictionary

    Returns:
        Tuple of (email, affiliation)
    """
    logger.info(f"Deanonymizing GitHub user for email: {email}")

    if '@users.noreply.github.com' not in email:
        raise ValueError("The provided email address is not a valid GitHub noreply email.")

    if email in already_known_user_affiliations:
        logger.info(f"Key {email} already exists in cache. Skipping API call.")
        return already_known_user_affiliations[email]

    github_email = "unknown-by-GitHub"
    github_affiliation = "unknown-by-GitHub"

    # Extract the username from the email address
    try:
        if '+' in email:
            username = email.split('+')[1].split('@')[0]
        else:
            username = email.split('@')[0]
    except IndexError:
        raise ValueError("Unable to extract GitHub username from the email address.")

    # Use PyGithub to retrieve user information
    g = Github(github_token)
    try:
        user = g.get_user(username)
        logger.debug(f"Successfully retrieved information for GitHub user: {username}")

        print_github_user_data(user.raw_data)

        if user.email:
            github_email = user.email

        if user.company:
            github_affiliation = user.company

        # Check organizations
        logger.info(f"Checking if user {username} is a member of organizations")
        organizations = [org.login for org in user.get_orgs()]
        console.print(f"Organizations for {username}: {organizations}")

        # Use first organization if available and not the current project
        if organizations:
            github_affiliation = organizations[0]

    except RateLimitExceededException:
        logger.warning("API rate limit exceeded. Sleeping for one hour...")
        time.sleep(3600)
        logger.info("Resuming API requests...")
        # Retry after sleep
        return deanonymize_github_user_with_cache_and_pygithub(
            email, github_token, already_known_user_affiliations
        )
    except GithubException as e:
        logger.warning(f"Unexpected API error: {e}")

    already_known_user_affiliations[email] = (github_email, github_affiliation)
    return (github_email, github_affiliation)


def print_all_nodes(network: nx.Graph) -> None:
    """Print all nodes in a NetworkX graph with their attributes."""
    logger.info(f"Printing all nodes in network")

    if not isinstance(network, nx.Graph):
        raise TypeError("The input must be a NetworkX graph.")

    table = Table(title="Nodes and Attributes")
    table.add_column("Node ID", style="bold cyan")
    table.add_column("Attributes", style="bold magenta")

    for node, attributes in network.nodes(data=True):
        attr_str = ", ".join(f"{key}: {value}" for key, value in attributes.items())
        table.add_row(str(node), attr_str if attr_str else "None")

    console.print(table)


def read_graphml_with_progress(file_path: str) -> nx.Graph:
    """Read a GraphML file with progress bar."""
    total_size = os.path.getsize(file_path)

    with Progress() as progress:
        task = progress.add_task("[cyan]Reading file...", total=total_size)

        with open(file_path, "rb") as file:
            content = b""
            while not progress.finished:
                chunk = file.read(1024)
                if not chunk:
                    break
                progress.update(task, advance=len(chunk))
                content += chunk

    content_str = content.decode('utf-8')
    graph = nx.parse_graphml(content_str)

    console.print(
        f"Graph loaded: {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges",
        style="bold green"
    )

    return graph


def read_graphml_fast(file_path: str) -> nx.Graph:
    """Read a GraphML file quickly."""
    return nx.read_graphml(file_path)


def copy_graph_with_attributes(source_graph: nx.Graph) -> nx.Graph:
    """Copy nodes, edges, and their attributes from source to target graph."""
    target_graph = nx.Graph()

    # Copy nodes with attributes
    for node, attributes in source_graph.nodes(data=True):
        target_graph.add_node(node, **attributes)

    # Copy edges without attributes
    for u, v in source_graph.edges(data=False):
        target_graph.add_edge(u, v)

    return target_graph


def iterate_graph(
        input_file: str,
        output_file: str,
        github_token: str,
        current_project: str
) -> None:
    """
    Process GraphML file to deanonymize GitHub emails.

    Args:
        input_file: Path to input GraphML file
        output_file: Path to output GraphML file
        github_token: GitHub API token
        current_project: Current project name
    """
    logger.info(f"Iterating network: {input_file} -> {output_file}")

    if not check_file_exists(input_file):
        logger.error(f"The file '{input_file}' does not exist.")
        sys.exit(1)

    logger.info(f"Reading input GraphML file: {input_file}")

    try:
        G = read_graphml_fast(input_file)
        console.print("[green]Graph read successfully![/green]")
        console.print(f"Number of nodes: {G.number_of_nodes()}")
        console.print(f"Number of edges: {G.number_of_edges()}")
    except Exception as e:
        console.print(f"[red]Failed to read the graph: {e}[/red]")
        sys.exit(1)

    # Create a copy of the graph
    G_copy = copy_graph_with_attributes(G)

    # Prepare authentication headers for REST API
    git_hub_auth_headers = {'Authorization': f'token {github_token}'}

    # Display rate limit before starting
    display_rate_limit(git_hub_auth_headers)

    console.rule("Replacing emails and affiliations using GitHub REST API")
    logger.info("Looking for @users.noreply.github.com emails to deanonymize")

    for node, data in G_copy.nodes(data=True):
        logger.debug(f"Iterating over node: {node}")

        old_email = data.get('e-mail', '')
        old_affiliation = data.get('affiliation', '')

        console.print(f"Checking node={node} with email={old_email} and affiliation={old_affiliation}")

        if '@users.noreply.github.com' in old_email:
            new_email, new_affiliation = deanonymize_github_user_with_cache_and_pygithub(
                old_email,
                github_token,
                already_known_user_affiliations
            )

            logger.info(f"Updating node={node} with email={new_email} and affiliation={new_affiliation}")
            data['e-mail'] = new_email
            data['affiliation'] = new_affiliation

    # Write the modified graph to output file
    logger.info(f"Writing output GraphML file: {output_file}")
    nx.write_graphml(G_copy, output_file)

    console.print(f"[bold green]Successfully processed graph to {output_file}[/bold green]")


def validate_input_file(input_file: str) -> None:
    """Validate that input file has .graphml extension."""
    if not input_file.lower().endswith('.graphml'):
        logger.error(f"Error: The input file '{input_file}' does not have a .graphml extension.")
        sys.exit(1)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Creates a more correct GraphML file by correcting e-mails and affiliations via the GitHub REST API."
    )

    # Required input file argument
    parser.add_argument(
        'input',
        type=str,
        help='Path to the input GraphML file.'
    )

    # Optional output file argument
    parser.add_argument(
        'output',
        type=str,
        nargs='?',
        default=None,
        help='Path to the output file (default: input_file.out.graphml).'
    )

    # Config file argument
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file (default: config.ini or environment variables).'
    )

    args = parser.parse_args()

    # Validate input file
    validate_input_file(args.input)

    # Set default output file if not provided
    if args.output is None:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}.out.graphml"

    # Load configuration
    try:
        config = load_config(args.config)
        github_token = config['token']
        current_project = config['current_project']

        console.print(f"[green]✓ Configuration loaded successfully[/green]")
        console.print(f"  Token: {github_token[:10]}...")
        console.print(f"  Project: {current_project}")

    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)

    # Process the graph
    iterate_graph(
        input_file=args.input,
        output_file=args.output,
        github_token=github_token,
        current_project=current_project
    )


if __name__ == "__main__":
    main()