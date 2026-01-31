#!/usr/bin/env python3
"""
Scrap date, authors, affiliations and file changes from a Git Changelog.
"""

import sys
import re
import argparse
import pickle
import atexit
import time
import itertools
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, DefaultDict, Tuple
from collections import defaultdict

import networkx as nx
from colorama import Fore, Style

import export_log_data

from utils.unified_console import (console, traceback, Table)
from utils.unified_logger import logger

from utils.validators import (
    validate_git_name,
    validate_git_email,
    validate_git_time,
    validate_git_files,
    validate_git_commit_block
)



from typing import TypeAlias

# Type aliases using built-in types
Email = str
Affiliation = str
Filename = str
Date = str

DeveloperInfo: TypeAlias = tuple[Date, Email, Affiliation]  # Note: lowercase tuple, list, dict
ChangeLogEntry: TypeAlias = tuple[DeveloperInfo, list[Filename]]
EmailAggregationConfig: TypeAlias = dict[str, str]
Connection: TypeAlias = tuple[Email, Email]
ConnectionWithFile: TypeAlias = tuple[Connection, Filename]

start_time = time.time()


@dataclass
class ProcessingStatistics:
    """Track processing statistics."""
    nlines: int = 0
    n_blocks: int = 0
    n_blocks_changing_code: int = 0
    n_blocks_not_changing_code: int = 0
    n_changed_files: int = 0
    n_validation_errors: int = 0
    n_skipped_blocks: int = 0

    def increment_validation_errors(self) -> None:
        """Increment validation error count."""
        self.n_validation_errors += 1

    def increment_skipped_blocks(self) -> None:
        """Increment skipped blocks count."""
        self.n_skipped_blocks += 1


@dataclass
class ProcessingState:
    """Container for all processing state."""
    statistics: ProcessingStatistics = field(default_factory=ProcessingStatistics)
    change_log_data: List[ChangeLogEntry] = field(default_factory=list)
    file_contributors: DefaultDict[Filename, List[Email]] = field(
        default_factory=lambda: defaultdict(list)
    )
    connections_with_files: List[ConnectionWithFile] = field(default_factory=list)
    unique_connections: List[Connection] = field(default_factory=list)
    affiliations: Dict[Email, Affiliation] = field(default_factory=dict)
    emails_to_filter: Set[Email] = field(default_factory=set)
    files_to_filter: Set[Filename] = field(default_factory=set)
    email_aggregation_config: EmailAggregationConfig = field(default_factory=dict)

    # Operational modes
    debug_mode: bool = False
    save_mode: bool = False
    load_mode: bool = False
    raw_mode: bool = False
    email_filtering_mode: bool = False
    file_filtering_mode: bool = False
    strict_validation: bool = False  # Whether to fail on validation errors

    # Network graph
    dev_to_dev_network: nx.Graph = field(default_factory=nx.Graph)


def print_exit_info() -> None:
    """console.print execution summary at exit."""
    execution_time = time.time() - start_time
    table = Table(title="Script Execution Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total execution time", f"{execution_time:.2f} seconds")
    table.add_row("Script arguments", str(sys.argv[1:]))
    console.print(table)


atexit.register(print_exit_info)
console.print(f"Executing {sys.argv}")


def load_email_aggregation_config(config_file: str) -> EmailAggregationConfig:
    """
    Load email aggregation configuration from a JSON file.
    Format: {"prefix": "consolidated_name", ...}
    Example: {"ibm": "ibm", "google": "google"}
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        if not isinstance(config, dict):
            raise ValueError("Config file must contain a JSON object/dictionary")

        for prefix, consolidated_name in config.items():
            if not isinstance(prefix, str) or not isinstance(consolidated_name, str):
                raise ValueError(f"Invalid entry in config: {prefix}: {consolidated_name}")

        console.print(f"Loaded email aggregation config from {config_file}")
        for prefix, name in config.items():
            console.print(f"  {prefix}.* -> {name}")

        return config

    except FileNotFoundError:
        console.print(f"Warning: Email aggregation config file not found: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        console.print(f"Error: Invalid JSON in config file {config_file}: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"Error loading email aggregation config: {e}")
        sys.exit(1)


def extract_affiliation_from_email(
        email: Email,
        state: ProcessingState
) -> str | None:

    affiliation : str= "Unknown"

    """Get affiliation from an email address with aggregation support."""
    if state.debug_mode:
        logger.info(f"\textract_affiliation_from_email({email})")

    if state.email_filtering_mode and email in state.emails_to_filter:
        return "filtered - included in file passed with -f argument"

    # Extract domain using regex - more robust version
    try:
        # Handle emails with potential issues
        if email.endswith('?'):
            email = email[:-1]

        # Simple extraction: get domain part after @
        if '@' not in email:
            console.print(f"WARNING: No @ in email: {email}")
            return "unknown"

        domain_part = email.split('@')[-1]

        # Get first component before first dot
        domain_component = domain_part.split('.')[0]

        # Apply email aggregation if configured
        for prefix, consolidated_name in state.email_aggregation_config.items():
            if domain_component.startswith(prefix) or prefix in domain_component:
                affiliation = consolidated_name

        affiliation= domain_component

        if state.debug_mode:
            logger.info(f"\textracted_affiliation_from_email({email})={affiliation}")
        return affiliation

    except Exception as e:
        if state.debug_mode:
            console.print(f"Error extracting affiliation from {email}: {e}")
        return "unknown"


def parse_time_name_email_affiliation(
        line: str,
        state: ProcessingState
) -> Optional[Tuple[str, str, str, str]]:
    """
    Extract time, name, email, and affiliation from a log line.

    Args:
        line: Input log line
        state: Processing state object

    Returns:
        Tuple of (date_time, last_name, email, affiliation) or None if parsing fails
    """
    try:
        # Pattern to capture: ==Name;email;date_time timezone==
        # The name might contain spaces, so we need to be careful
        pattern = re.compile(r'^==(.+?);(.+?);(.+?)\s([+-]\d{4})==$')
        match = pattern.search(line)

        if not match:
            # Try alternative patterns for exceptional cases
            return parse_exceptional_format(line, state)

        name, email, date_time_str, timezone = match.groups()

        # Clean email
        email = email.strip()

        # Validate email format
        if '@' not in email:
            console.print(f"WARNING: Invalid email format (no @): {email}")
            state.statistics.increment_validation_errors()
            return None

        # Extract affiliation from email domain
        affiliation = extract_affiliation_from_email(email, state)

        # Combine date_time with timezone for complete timestamp
        full_timestamp = f"{date_time_str} {timezone}"

        return (full_timestamp, name, email, affiliation)

    except Exception as e:
        if state.debug_mode:
            console.print(f"Error parsing line '{line}': {e}")
        state.statistics.increment_validation_errors()
        return None





def parse_exceptional_format(line: str, state: ProcessingState) -> Optional[DeveloperInfo]:
    """Parse exceptional log line formats."""
    try:
        # Pattern 1: Name and email together before ;;
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        pattern1 = re.compile(r'^==(.+?)\s(.+?@.+?);;(.+?)\s([+-]\d{4})==$')
        match1 = pattern1.search(line)

        if match1:
            name_part, email, date_str, timezone = match1.groups()
            name = name_part.split()[0] if ' ' in name_part else name_part
            affiliation = extract_affiliation_from_email(email, state)
            return (date_str, email, affiliation)

        # Pattern 2: Just email before ;;
        pattern2 = re.compile(r'^==(.+?@.+?);;(.+?)\s([+-]\d{4})==$')
        match2 = pattern2.search(line)

        if match2:
            email, date_str, timezone = match2.groups()
            # Extract name from email
            name = email.split('@')[0]
            affiliation = extract_affiliation_from_email(email, state)
            return (date_str, email, affiliation)

        # Pattern 3: Launchpad bot
        if "Launchpad" in line:
            pattern3 = re.compile(r'^==(.+?);;(.+?)\s([+-]\d{4})==$')
            match3 = pattern3.search(line)
            if match3:
                name_part, date_str, timezone = match3.groups()
                email = "launchpad@bot.bot"
                affiliation = "bot"
                return (date_str, email, affiliation)

        # If nothing matches, return None
        return None

    except Exception as e:
        if state.debug_mode:
            console.print(f"Error parsing exceptional format: {e}")
        return None


def extract_files_from_block(
        block: List[str],
        state: ProcessingState
) -> List[Filename]:
    """Extract list of files from a block."""
    files: List[Filename] = []

    for line in block:
        if not line or line == '\n':
            break

        filename = line.rstrip('\n')

        # Skip files in filter list
        if state.file_filtering_mode and filename in state.files_to_filter:
            continue

        # Basic validation: file should not be empty
        if filename.strip():
            files.append(filename)
            state.statistics.n_blocks_changing_code += 1

    return files


def process_commit_block(
        block: List[str],
        state: ProcessingState
) -> bool:
    """Process a block of changelog."""
    if not block:
        return False

    first_line = block[0]
    if not first_line.startswith('=='):
        console.print(f"ERROR: Invalid block - does not start with '==': {first_line[:50]}...")

        console.print(traceback.Traceback(), style="bold red")

        console.print("[bold red]Error:[/bold red] Processing a block not starting with '=='...")
        sys.exit(1)

    try:
        # Parse the commit header
        time_dev_info = parse_time_name_email_affiliation(first_line, state)

        if state.debug_mode:
            logger.debug("Retrieved ")
            logger.debug(f"{time_dev_info=}")


        if not time_dev_info:
            console.print(f"WARNING: Could not parse commit header: {first_line[:50]}...")
            console.print(f"[bold red]Error:[/bold red] Could not get developer information from commit block {first_line}")
            state.statistics.increment_skipped_blocks()
            sys.exit(1)

        commit_time, dev_name, dev_email, dev_affiliation = time_dev_info

        # Extract files
        changed_files = extract_files_from_block(block[1:], state)

        if not changed_files:
            if state.debug_mode:
                console.print(f"WARNING: No files in commit block for {first_line}")
            state.statistics.increment_skipped_blocks()
            return False

        # Store the data
        state.change_log_data.append(((dev_name, dev_email, dev_affiliation), changed_files))
        return True

    except Exception as e:
        console.print(f"ERROR processing commit block: {e}")
        if state.debug_mode:
            logger.debug(f"ERROR processing commit block:")
            logger.debug(f"{block=}")
            console.print(traceback.Traceback(), style="bold red")
        state.statistics.increment_skipped_blocks()
        return False


def aggregate_files_and_contributors(state: ProcessingState) -> None:
    """Aggregate data: for each file, what are the contributors."""
    if state.debug_mode:
        console.print("\nAggregating data: for each file what are the contributors")

    files_visited: Set[Filename] = set()

    for entry in state.change_log_data:
        email = entry[0][1]
        files = entry[1]

        for filename in files:
            if filename not in files_visited:
                files_visited.add(filename)
                state.file_contributors[filename] = [email]
            elif email not in state.file_contributors[filename]:
                state.file_contributors[filename].append(email)

    state.statistics.n_changed_files = len(files_visited)


def extract_contributor_connections(state: ProcessingState) -> None:
    """Get tuples of authors that coded/contributed on the same file."""
    if state.debug_mode:
        console.print("\nGetting tuples of contributors that coded/contributed on the same file")

    state.connections_with_files.clear()

    for filename, contributors in state.file_contributors.items():
        if len(contributors) > 1:
            for connection in itertools.combinations(contributors, 2):
                state.connections_with_files.append((connection, filename))


def get_unique_connections(
        tuples_list: List[ConnectionWithFile]
) -> List[Connection]:
    """Get unique connections from tuples list."""
    if not tuples_list:
        return []

    seen: Set[Connection] = set()

    for connection in tuples_list:
        (author1, author2), _ = connection
        # Add both directions to ensure uniqueness
        pair = tuple(sorted((author1, author2)))
        seen.add(pair)

    return list(seen)


def create_network_graph(state: ProcessingState) -> None:
    """Create and populate the network graph."""
    if state.debug_mode:
        console.print("\nCreating network graph from unique connections")

    state.dev_to_dev_network.clear()
    state.dev_to_dev_network.add_edges_from(state.unique_connections)

    # Add node attributes
    for node in state.dev_to_dev_network.nodes():
        if state.debug_mode: logger.debug( f"Adding node attributes to {node=}")


        state.dev_to_dev_network.nodes[node]['email'] = str(node)
        state.dev_to_dev_network.nodes[node]['affiliation'] = extract_affiliation_from_email(node,state)




def apply_email_filtering(state: ProcessingState) -> None:
    """Remove filtered emails from the network."""
    if not state.email_filtering_mode:
        return

    if state.debug_mode:
        console.print("\nRemoving filtered emails from the network graph")

    nodes_removed = 0
    for email in state.emails_to_filter:
        if state.dev_to_dev_network.has_node(email):
            if state.debug_mode:
                console.print(f"\t removing node {email}")
            state.dev_to_dev_network.remove_node(email)
            nodes_removed += 1

    # Remove isolates after filtering
    isolates = list(nx.isolates(state.dev_to_dev_network))
    if isolates:
        if state.debug_mode:
            console.print(f"\nRemoving {len(isolates)} isolates that resulted from filtering")
        state.dev_to_dev_network.remove_nodes_from(isolates)


def print_processing_summary(state: ProcessingState, work_file: str) -> None:
    """console.print a summary of processing results."""
    console.print("\n" + "=" * 60)
    console.print("PROCESSING SUMMARY")
    console.print("=" * 60)
    console.print(f"Input file: {work_file}")
    console.print(f"Total lines processed: {state.statistics.nlines}")
    console.print(f"Total commit blocks found: {state.statistics.n_blocks}")
    console.print(f"Successfully processed blocks: {state.statistics.n_blocks - state.statistics.n_skipped_blocks}")
    console.print(f"Skipped/invalid blocks: {state.statistics.n_skipped_blocks}")
    console.print(f"Blocks changing code: {state.statistics.n_blocks_changing_code}")
    console.print(f"Files affected: {state.statistics.n_changed_files}")
    console.print(f"Validation errors: {state.statistics.n_validation_errors}")
    console.print(f"Network nodes (developers): {state.dev_to_dev_network.number_of_nodes()}")
    console.print(f"Network edges (collaborations): {state.dev_to_dev_network.size()}")
    console.print(f"Unique affiliations: {len(set(state.affiliations.values()))}")
    console.print("=" * 60)


def main() -> None:
    """Main execution function."""
    state = ProcessingState()

    parser = argparse.ArgumentParser(
        description='Scrap changelog to create networks/graphs for research purposes'
    )
    parser.add_argument('-l', '--load', type=str,
                        help='loads and processes a serialized changelog')
    parser.add_argument('-r', '--raw', type=str, required=True,
                        help='processes from a raw git changelog')
    parser.add_argument('-s', '--save', type=str,
                        help='processes from a raw git changelog and saves it into a serialized changelog')
    parser.add_argument('-fe', '--filter-emails', type=str,
                        help='ignores the emails listed in a text file (one email per line)')
    parser.add_argument('-ff', '--filter-files', type=str,
                        help='ignores the files listed in a text file (one file per line)')
    parser.add_argument('-a', '--aggregate-email-prefixes', type=str,
                        help='JSON file defining email domain prefixes to aggregate (e.g., {"ibm": "ibm", "google": "google"})')
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increased output verbosity")
    parser.add_argument("--strict", action="store_true",
                        help="strict validation mode - fail on validation errors")

    args = parser.parse_args()

    # Set modes
    state.debug_mode = args.verbose
    state.strict_validation = args.strict

    if state.debug_mode:
        console.print("\nVerbosity turned on")


    # Load email aggregation config
    if args.aggregate_email_prefixes:
        state.email_aggregation_config = load_email_aggregation_config(
            args.aggregate_email_prefixes
        )

    # Set filtering modes
    if args.filter_emails:
        state.email_filtering_mode = True
        console.print("\nEmail filtering turned on")

    if args.filter_files:
        state.file_filtering_mode = True
        console.print("\nFile filtering turned on")

    # Determine input file
    work_file = args.raw

    # Load filter files
    if state.email_filtering_mode and args.filter_emails:
        try:
            with open(args.filter_emails, 'r') as ff:
                state.emails_to_filter = {line.strip() for line in ff if line.strip()}
            console.print(f"\tLoaded {len(state.emails_to_filter)} emails to filter")
        except IOError as e:
            console.print(f"WARNING: Could not read filter file {args.filter_emails}: {e}")
            state.email_filtering_mode = False


    # Process based on mode
    start_scrapping_time = time.time()
    console.print(f"\nStarting processing of {work_file} at {start_scrapping_time}")

    try:
        with open(work_file, 'r') as f:
            lines = f.readlines()

        current_block: List[str] = []

        for line_num, line in enumerate(lines, 1):
            if line == "\n":
                continue

            state.statistics.nlines += 1

            if line.startswith('=='):
                if current_block:
                    if state.debug_mode:
                        logger.debug(f"processing {current_block=}")
                    process_commit_block(current_block, state)

                current_block = [line]
                state.statistics.n_blocks += 1
            elif '.' in line or '/' in line or len(line.strip()) >= 3:
                current_block.append(line)
            elif line == '--\n':
                continue
            else:
                if state.debug_mode:
                    console.print(f"WARNING: Unexpected line format at line {line_num}: {line[:50]}...")

        # Process final block
        if current_block:
            process_commit_block(current_block, state)

        console.print(f"\n✓ Successfully processed {len(state.change_log_data)} commits")
        console.print()

        if args.save:
            console.print(f"\nSaving processed data to {args.save}")
            with open(args.save, 'wb') as fp:
                pickle.dump(state.change_log_data, fp)
            console.print("Data saved successfully")

    except FileNotFoundError:
        console.print(f"ERROR: Input file not found: {work_file}")
        sys.exit(1)
    except Exception as e:
        console.print(f"ERROR processing file: {e}")
        sys.exit(1)

    # Process the data
    aggregate_files_and_contributors(state)
    console.print("[bold green]Success:[/bold green]" + "\n✓ Data aggregated by files and contributors")


    extract_contributor_connections(state)
    console.print("[bold green]Success:[/bold green]" + "\n✓ Contributor connections extracted")


    state.unique_connections = get_unique_connections(state.connections_with_files)
    console.print("[bold green]Success:[/bold green]" + f"\n✓ Extracted {len(state.unique_connections)} unique connections")


    if state.debug_mode:
        print(f"{state.unique_connections=}")



    create_network_graph(state)

    console.print("[bold green]Success:[/bold green]" + "\n✓ Network graph created")


    apply_email_filtering(state)

    # Export to GraphML
    graphml_filename = Path(work_file).stem + ".NetworkFile.graphML"
    try:
        export_log_data.createGraphML(state.dev_to_dev_network, graphml_filename)
        console.print(f"\n✓ Network exported to GraphML file: {graphml_filename}")
        console.print()
    except Exception as e:
        console.print(f"ERROR exporting to GraphML: {e}")

    # console.print summary
    print_processing_summary(state, work_file)


if __name__ == "__main__":
    main()