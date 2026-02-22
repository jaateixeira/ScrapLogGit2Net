#!/usr/bin/env python3
"""
Scrap date, authors, affiliations and file changes from a Git Changelog.
"""

import sys
import os
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
from difflib import SequenceMatcher
from itertools import combinations
from email.utils import parseaddr
from urllib.parse import unquote



import networkx as nx

from colorama import Fore, Style

import export_log_data

from utils.unified_console import (console, traceback, Table, inspect, print_info, print_tip, print_warning,
                                   print_error, print_success)
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
Timestamp = str

# =============================================================================
# Type Aliases for Core Data Structures
# =============================================================================

DeveloperInfo: TypeAlias = tuple[Timestamp, Email, Affiliation]
"""
Developer information extracted from a commit header.

Contains:
    - Timestamp: When the commit was made (e.g., '2023-01-15 14:30:22 -0500')
    - Email: Developer's email (e.g., 'john.doe@company.com')
    - Affiliation: Organization from email domain (e.g., 'company', 'google', 'nvidia')
"""

ChangeLogEntry: TypeAlias = tuple[DeveloperInfo, list[Filename]]
"""
A complete changelog entry representing one commit.

Structure:
    - DeveloperInfo: Who made the commit and when
    - list[Filename]: Files changed in that commit (e.g., ['src/main.py', 'README.md'])

Example: (('2023-01-15...', 'alice@co.com', 'co'), ['file1.py', 'file2.py'])
"""

EmailAggregationConfig: TypeAlias = dict[str, str]
"""
Configuration for grouping email addresses by domain patterns.

Maps domain prefixes to consolidated affiliation names.
Example: {'ibm': 'ibm', 'google': 'google', 'gmail': 'personal'}
"""

Connection: TypeAlias = tuple[Email, Email, Timestamp]  # Or store first/last
"""
TODO document
"""

ConnectionWithFile: TypeAlias = tuple[Connection, Filename, Timestamp]

"""
TODO document 
"""


@dataclass
class TimeStampedFileContribution:
    """A single contribution to a file."""
    email: Email
    timestamp: Timestamp
    commit_index: int  # To preserve order if timestamps are identical


@dataclass
class ProcessingStatistics:
    """Track processing statistics."""
    n_lines: int = 0
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

    network_type = None

    """Container for all processing state."""
    statistics: ProcessingStatistics = field(default_factory=ProcessingStatistics)

    parsed_change_log_entries: List[ChangeLogEntry] = field(default_factory=list)

    """Parsed changelog entries from git log

    Each ChangeLogEntry contains:
    - commit_hash: str - Unique identifier for the commit
    - author_email: Email - Email of the commit author
    - author_date: DateTime - When the commit was made  
    - files_changed: List[Filename] - Files modified in this commit
    - commit_message: str - Description of changes

    This is the raw input data that drives all subsequent processing.
    """

    map_files_to_their_contributors: DefaultDict[Filename, List[Email]] = field(
        default_factory=lambda: defaultdict(list)
    )


    """Inverted index mapping files to their contributors.

        Key: Filename - Path to the file within the repository
        Value: List[Email] - All contributors who have modified this file

        Built by aggregating parsed_change_log_entries . Used for:
        - Identifying files with multiple contributors (collaboration points)
        - Generating per-file contribution statistics
        - Filtering files based on contributor criteria
        """

    file_coediting_collaborative_relationships: List[ConnectionWithFile] = field(default_factory=list)

    """File coediting collaborative relationships between contributor pairs.

        Each ConnectionWithFile represents a collaboration event on a specific file:
        - email1: Email - First contributor
        - email2: Email - Second contributor  
        - filename: Filename - The file where they collaborated
        - collaboration_count: int - Number of times they worked on this file
        - first_collaboration: DateTime - Earliest collaboration on this file
        - last_collaboration: DateTime - Most recent collaboration on this file

        This preserves file context before aggregation into pair-level connections.
        """

    aggregated_file_coediting_collaborative_relationships: List[Connection] = field(default_factory=list)

    """Aggregated collaboration relationships between contributor pairs.

        Each Connection represents a unique contributor pair across all files:
        - email1: Email - First contributor
        - email2: Email - Second contributor
        - total_collaborations: int - Total collaborations across all files
        - files_shared: List[Filename] - Files they've both worked on
        - first_interaction: DateTime - When they first collaborated
        - last_interaction: DateTime - Most recent collaboration

        This is the deduplicated view used for network graph construction.
        Populated by aggregating connections_with_files.
        """

    # Add to ProcessingState:
    file_history: DefaultDict[Filename, List[TimeStampedFileContribution]] = field(
        default_factory=lambda: defaultdict(list)
    )

    affiliations: Dict[Email, Affiliation] = field(default_factory=dict)
    emails_to_filter: Set[Email] = field(default_factory=set)
    files_to_filter: Set[Filename] = field(default_factory=set)
    email_aggregation_config: EmailAggregationConfig = field(default_factory=dict)

    # Operational modes
    verbose_mode: bool = False
    very_verbose_mode: bool = False
    debug_mode: bool = False
    save_mode: bool = False
    load_mode: bool = False
    raw_mode: bool = False
    email_filtering_mode: bool = False
    file_filtering_mode: bool = False
    strict_validation: bool = False  # Whether to fail on validation errors

    # Network graph
    dev_to_dev_network: nx.Graph = field(default_factory=nx.Graph)


def print_exit_info(start_time:float) -> None:
    """console.print execution summary at exit."""
    execution_time = time.time() - start_time
    table = Table(title="Script Execution Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total execution time", f"{execution_time:.2f} seconds")
    table.add_row("Script arguments", str(sys.argv[1:]))
    console.print(table)





def find_similar_strings(strings: set[str], similarity_threshold: float = 0.8) -> set[Tuple[str, str, float]]:
    """
    Find pairs of strings that are at least n% similar to each other.

    Args:
        strings: List of strings to compare
        similarity_threshold: Minimum similarity ratio (0.0 to 1.0), e.g., 0.8 for 80%

    Returns:
        List of tuples (string1, string2, similarity_score) for pairs above threshold
    """
    if not strings:
        console.print()
        sys.exit()

    similar_pairs = []

    # Generate all unique pairs of strings
    for str1, str2 in combinations(strings, 2):

        if None in (str1, str2):
            continue

        # Calculate similarity ratio (0.0 to 1.0)
        similarity = SequenceMatcher(None, str1, str2).ratio()

        if similarity >= similarity_threshold:
            similar_pairs.append((str1, str2, similarity))

    # Sort by similarity score (highest first)
    similar_pairs.sort(key=lambda x: x[2], reverse=True)

    return set(similar_pairs)




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


def _clean_email(email: str) -> str | None:
    """
    Clean an email address by removing common artifacts.
    Uses email.utils.parseaddr for robust parsing.
    """
    if not email or not isinstance(email, str):
        return None

    # Remove all whitespace first
    email = ''.join(email.split())

    # Use Python's built-in email parser (handles "Name <email>", quotes, etc.)
    _, email = parseaddr(email)

    if not email or '@' not in email:
        return None

    # Remove trailing ? if present
    email = email.rstrip('?')

    # URL decode %40 to @
    try:
        from urllib.parse import unquote
        email = unquote(email)
    except ImportError:
        # This should never happen in standard Python, but if it does, exit
        print("Error: urllib.parse.unquote not available. Cannot continue.")
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors during decoding
        print(f"Error: Failed to decode email '{email}': {e}")
        sys.exit(1)

    # Take last @ if multiple (common in malformed emails)
    if email.count('@') > 1:
        parts = email.split('@')
        email = f"{parts[0]}@{parts[-1]}"

    return email.lower()


def extract_affiliation_from_email(
        email: Email,
        state: ProcessingState
) -> str | None:
    """Get affiliation from an email address with aggregation support."""

    if state.verbose_mode or state.very_verbose_mode:
        logger.info(f"\textract_affiliation_from_email({email})")

    # Input validation
    if not email or not isinstance(email, str):
        return None

        # Clean the email
    cleaned_email = _clean_email(email)
    if not cleaned_email:
        return None
    email = cleaned_email.lower()

    try:
        # Clean email
        email = email.strip()
        if email.endswith('?'):
            email = email[:-1]

        # Validate email format
        if '@' not in email:
            if state.verbose_mode:
                console.print(f"WARNING: No @ in email: {email}")
            return None

        # Extract domain and normalize to lowercase
        domain_part = email.split('@')[-1].lower()

        # Handle case where there's nothing after @
        if not domain_part:
            if state.verbose_mode:
                console.print(f"WARNING: Empty domain in email: {email}")
            return None

        domain_parts = domain_part.split('.')

        # Remove any empty parts from trailing/leading dots
        domain_parts = [part for part in domain_parts if part]

        # If no valid domain parts after cleaning, return None
        if not domain_parts:
            if state.verbose_mode:
                console.print(f"WARNING: No valid domain parts in: {email}")
            return None

        # The organization is almost always the second-to-last component
        # Examples:
        # - abo.fi -> "abo" (fi is TLD)
        # - mit.edu -> "mit" (edu is TLD)
        # - us.ibm.com -> "ibm" (com is TLD, us is subdomain)
        # - ca.us.ibm.com -> "ibm" (com is TLD, ca.us are subdomains)
        # - alumni.mit.edu -> "mit" (edu is TLD, alumni is subdomain)
        # - company.co.uk -> "company" (co.uk is compound TLD)
        # - gmail.com -> "gmail" (com is TLD)

        # Check for compound TLDs (co.uk, com.au, etc.)
        # The organization is usually the part before the compound TLD
        if len(domain_parts) >= 3 and domain_parts[-2] in {'co', 'com', 'ac', 'edu', 'gov', 'net', 'org', 'ltd', 'plc'}:
            potential_org = domain_parts[-3]
        elif len(domain_parts) >= 2:
            # Default case: organization is the second-to-last part
            # abo.fi -> abo
            # mit.edu -> mit
            # ibm.com -> ibm
            # gmail.com -> gmail
            # whitehouse.gov -> whitehouse
            potential_org = domain_parts[-2]
        else:
            # Single part domain (e.g., "localhost", "internal")
            potential_org = domain_parts[0]

        # Apply email aggregation if configured
        for prefix, consolidated_name in state.email_aggregation_config.items():
            prefix_lower = prefix.lower()
            if potential_org == prefix_lower or potential_org.startswith(prefix_lower):
                if state.verbose_mode or state.very_verbose_mode:
                    logger.info(f"\textracted_affiliation_from_email({email})={potential_org}")
                return potential_org

        # No config match, return the potential organization
        if state.verbose_mode or state.very_verbose_mode:
            logger.info(f"\textracted_affiliation_from_email({email})={potential_org}")
        return potential_org

    except Exception as e:
        if state.verbose_mode or state.very_verbose_mode:
            console.print(f"Error extracting affiliation from {email}: {e}")
        return None

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
        if state.verbose_mode:
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
        if state.verbose_mode:
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
        state: ProcessingState,
        commit_index: int,
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

        if state.verbose_mode or state.very_verbose_mode:
            logger.debug("Retrieved ")
            logger.debug(f"{time_dev_info=}")


        if not time_dev_info:
            print_warning(f"Could not parse commit header: {first_line[:50]}...")
            print_error(f"Could not get developer information from commit block {first_line}")
            state.statistics.increment_skipped_blocks()
            #sys.exit(1)

        commit_time, dev_name, dev_email, dev_affiliation = time_dev_info

        # Extract files
        changed_files = extract_files_from_block(block[1:], state)

        if not changed_files:
            if state.verbose_mode or state.very_verbose_mode:
                print_warning(f"No files in commit block for {first_line}")
            state.statistics.increment_skipped_blocks()
            return False
        # Store the data
        state.parsed_change_log_entries.append(((dev_name, dev_email, dev_affiliation), changed_files))
        # NEW: Build file history for temporal analysis
        for filename in changed_files:
            state.file_history[filename].append(
                TimeStampedFileContribution(
                    email=dev_email,
                    timestamp=commit_time,
                    commit_index=commit_index
                )
            )

        return True

    except Exception as e:
        console.print(f"ERROR processing commit block: {e}")
        if state.verbose_mode:
            logger.debug(f"ERROR processing commit block:")
            logger.debug(f"{block=}")
            console.print(traceback.Traceback(), style="bold red")
        state.statistics.increment_skipped_blocks()
        return False


def aggregate_files_and_contributors(state: ProcessingState) -> None:
    """Aggregate data: for each file, what are the contributors."""

    # console.print(f"\nAggregating data: for each file what are the contributors")

    files_visited: Set[Filename] = set()

    for entry in state.parsed_change_log_entries:
        email = entry[0][1]
        files = entry[1]

        for filename in files:
            if filename not in files_visited:
                files_visited.add(filename)
                state.map_files_to_their_contributors[filename] = [email]
            elif email not in state.map_files_to_their_contributors[filename]:
                state.map_files_to_their_contributors[filename].append(email)

    state.statistics.n_changed_files = len(files_visited)


def extract_contributor_connections(state: ProcessingState) -> None:
    """Get tuples of authors that coded/contributed on the same file."""

    # console.print("\nGetting tuples of contributors that coded/contributed on the same file")

    state.file_coediting_collaborative_relationships.clear()

    for filename, contributors in state.map_files_to_their_contributors.items():
        if len(contributors) > 1:
            for connection in itertools.combinations(contributors, 2):
                state.file_coediting_collaborative_relationships.append((connection, filename))


def extract_temporal_connections(state: ProcessingState) -> None:
    """
    Extract temporal connections between developers who worked on the same file.
    Preserves the exact time of each collaboration.
    """
    if state.verbose_mode:
        console.print("[blue] Extracting temporal connections with timestamps[/blue]")

    state.file_coediting_collaborative_relationships.clear()

    # For each file, look at all contributions in chronological order
    for filename, contributions in state.file_history.items():
        if len(contributions) < 2:
            continue  # Need at least 2 contributors for collaboration

        # Sort contributions by timestamp to preserve chronology
        contributions.sort(key=lambda c: (c.timestamp, c.commit_index))

        # For each pair of contributors to this file
        # We consider ALL pairs, not just adjacent ones, because
        # collaboration can happen non-sequentially
        for i, contrib1 in enumerate(contributions):
            for contrib2 in contributions[i + 1:]:
                if contrib1.email == contrib2.email:
                    continue  # Same contributor

                # Normalize email order for consistent storage
                if contrib1.email < contrib2.email:
                    email1, email2 = contrib1.email, contrib2.email
                    # Store the timestamp of the LATER contribution
                    # as the collaboration moment
                    timestamp = contrib2.timestamp
                else:
                    email1, email2 = contrib2.email, contrib1.email
                    timestamp = contrib2.timestamp  # Still use later timestamp

                # Create connection with timestamp
                connection = (email1, email2, timestamp)
                state.file_coediting_collaborative_relationships.append(
                    (connection, filename, timestamp)
                )
    _handle_step_completion(state, "extract_temporal_connections")


def create_temporal_network_graph(state: ProcessingState) -> None:
    """Create a temporal network graph with time-aware edges."""
    if state.verbose_mode:
        console.print("\nCreating temporal network graph")

    state.dev_to_dev_network.clear()

    # Group collaborations by developer pair
    pair_collaborations = defaultdict(list)

    for (email1, email2, collab_time), filename, timestamp in state.file_coediting_collaborative_relationships:
        pair = (email1, email2)  # Already normalized
        pair_collaborations[pair].append({
            'timestamp': collab_time,
            'filename': filename,
            'time': timestamp  # Keep the full timestamp for reference
        })

    # Add edges with temporal attributes
    for (email1, email2), collaborations in pair_collaborations.items():
        # Sort collaborations by timestamp
        collaborations.sort(key=lambda c: c['timestamp'])

        # Extract temporal metadata
        first_collab = collaborations[0]['timestamp']
        last_collab = collaborations[-1]['timestamp']
        collab_times = [c['timestamp'] for c in collaborations]
        files = list(set(c['filename'] for c in collaborations))

        # Add edge with temporal attributes
        state.dev_to_dev_network.add_edge(
            email1, email2,
            weight=len(collaborations),  # Number of collaborations
            first_collaboration=first_collab,
            last_collaboration=last_collab,
            collaboration_timeline=collab_times,
            files_shared=files,
            collaboration_count=len(collaborations)
        )

    # Add node attributes (same as before)
    for node in state.dev_to_dev_network.nodes():
        node_affiliation = extract_affiliation_from_email(node, state)
        state.dev_to_dev_network.nodes[node]['email'] = node
        state.dev_to_dev_network.nodes[node]['affiliation'] = node_affiliation
        state.affiliations[node] = node_affiliation


def get_unique_connections(
        tuples_list: List[ConnectionWithFile]
) -> List[Connection]:
    """Get unique connections from tuples list."""
    if not tuples_list:
        return []

    seen: Set[Connection] = set()

    for connection in tuples_list:
        (author1, author2), _ = connection


        if author1 < author2:
            pair: Connection = (author1, author2)
        else:
            pair: Connection = (author2, author1)


        seen.add(pair)

    return list(seen)






def create_network_graph(state: ProcessingState) -> None:
    """Create and populate the network graph."""
    if state.verbose_mode:
        console.print("\nCreating network graph from unique connections")

    state.dev_to_dev_network.clear()
    state.dev_to_dev_network.add_edges_from(state.aggregated_file_coediting_collaborative_relationships)

    # Add node attributes
    for node in state.dev_to_dev_network.nodes():
        if state.verbose_mode: logger.debug( f"Adding node attributes to {node=}")

        node_email = node
        node_affiliation = extract_affiliation_from_email(node,state)
        state.dev_to_dev_network.nodes[node]['email'] = node_email
        state.dev_to_dev_network.nodes[node]['affiliation'] = node_affiliation
        state.affiliations[node] = node_affiliation



def apply_email_filtering(state: ProcessingState) -> None:
    """Remove filtered emails from the network."""
    if not state.email_filtering_mode:
        return

    if state.verbose_mode:
        console.print("\nRemoving filtered emails from the network graph")

    nodes_removed = 0
    for email in state.emails_to_filter:
        if state.dev_to_dev_network.has_node(email):
            if state.verbose_mode:
                console.print(f"\t removing node {email}")
            state.dev_to_dev_network.remove_node(email)
            nodes_removed += 1

    # Remove isolates after filtering
    isolates = list(nx.isolates(state.dev_to_dev_network))
    if isolates:
        if state.verbose_mode:
            console.print(f"\nRemoving {len(isolates)} isolates that resulted from filtering")
        state.dev_to_dev_network.remove_nodes_from(isolates)

    _handle_step_completion(state, "apply_email_filtering")


def print_processing_summary(state: ProcessingState, in_work_file: Path, out_graphml_file: Path ) -> None:
    """console.print a summary of processing results."""
    console.print("\n" + "=" * 60)
    console.print("PROCESSING SUMMARY")
    console.print("=" * 60)
    console.print(f"Input log file: {in_work_file}")
    console.print(f"Out network graphml file: {out_graphml_file}")
    console.print(f"Total lines processed: {state.statistics.n_lines}")
    console.print(f"Total commit blocks found: {state.statistics.n_blocks}")
    console.print(f"Successfully processed blocks: {state.statistics.n_blocks - state.statistics.n_skipped_blocks}")
    console.print(f"Skipped/invalid blocks: {state.statistics.n_skipped_blocks}")
    console.print(f"Blocks changing code: {state.statistics.n_blocks_changing_code}")
    console.print(f"Files affected: {state.statistics.n_changed_files}")
    console.print(f"Validation errors: {state.statistics.n_validation_errors}")
    console.print(f"Network nodes (developers): {state.dev_to_dev_network.number_of_nodes()}")
    console.print(f"Network edges (collaborations): {state.dev_to_dev_network.size()}")
    console.print(f"Unique affiliations: {len(set(state.affiliations.values()))}")
    console.print(f"Similar affiliation strings: 0.8 threshold {find_similar_strings(set(state.affiliations.values()))}")
    #console.print(f"Similar affiliation strings: 0.6 threshold {find_similar_strings(set(state.affiliations.values()),0.6)}")
    console.print("=" * 60)


def _ask_yes_or_no_question( question: str) -> bool:
    response = input(f"{question} (y/n): ").strip().lower()
    return response in ['y', 'yes', 'Y', 'YES']

def _ask_continue() -> bool:
    response = input("Do you want to continue? (y/n): ").strip().lower()
    return response in ['y', 'yes', 'Y', 'YES']


def _ask_inspect_processing_state() -> bool:
    response = input("Do you want to inspect processing state ? (y/n): ").strip().lower()
    return response in ['y', 'yes', 'Y', 'YES']



def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Scrap changelog to create networks/graphs for research purposes'
    )
    parser.add_argument('-l', '--load', type=Path,
                        help='loads and processes a serialized changelog')
    parser.add_argument('-r', '--raw', type=Path, required=True,
                        help='processes from a raw git changelog')
    parser.add_argument('-s', '--save', type=Path,
                        help='processes from a raw git changelog and saves it into a serialized changelog')
    parser.add_argument('-fe', '--filter-emails', type=Path,
                        help='ignores the emails listed in a text file (one email per line)')
    parser.add_argument('-ff', '--filter-files', type=Path,
                        help='ignores the files listed in a text file (one file per line)')
    parser.add_argument('-a', '--aggregate-email-prefixes', type=Path,
                        help='JSON file defining email domain prefixes to aggregate (e.g., {"ibm": "ibm", "google": "google"})')
    parser.add_argument('-t', '--type-of-network',
                        choices=['inter_individual_graph_unweighted',
                                 'inter_individual_multigraph_weighted',
                                 'inter_individual_graph_temporal'],
                        default='inter_individual_graph_unweighted',
                        help='Type of network to generate (default: inter_individual_graph_unweighted)')
    parser.add_argument('-o','--output-file', type=Path,
                         help='creates a network/graph graphml file with the given name')

    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity level (use -v, -vv, or -vvv)'
    )
    parser.add_argument('-d','--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-st','--strict', action='store_true',
                        help="strict validation mode - fail on validation errors")

    return parser.parse_args()


def setup_processing_state(state: ProcessingState, args: argparse.Namespace) -> None:
    """Configure the processing state based on arguments."""
    # Set modes
    state.verbose_mode = True if args.verbose == 1 else False
    state.very_verbose_mode = True if args.verbose == 2 else False
    state.debug_mode = True if args.debug else False
    state.strict_validation = args.strict

    state.network_type = args.type_of_network

    if state.verbose_mode:
        print_info('Verbose mode')

    if state.very_verbose_mode:
        print_info('Very verbose mode')

    if state.debug_mode:
        print_info('Debug mode')
        print_info('You will be called to continue step after step')
        print_info('You will be invited to ask for processing state')

    # Load email aggregation config
    if args.aggregate_email_prefixes:
        state.email_aggregation_config = load_email_aggregation_config(
            args.aggregate_email_prefixes
        )

    # Set filtering modes
    if args.filter_emails:
        state.email_filtering_mode = True
        print_info("Email filtering turned on.")
        print_tip("The filtering based on  only happen when creating the graphml network output file.")

    if args.filter_files:
        state.file_filtering_mode = True
        console.print("\nFile filtering turned on")

    # Load filter files
    if state.email_filtering_mode and args.filter_emails:
        load_email_filter_file(state, args.filter_emails)


def load_email_filter_file(state: ProcessingState, filter_file_path: str) -> None:
    """Load email filter list from file."""
    try:
        with open(filter_file_path, 'r') as ff:
            state.emails_to_filter = {line.strip() for line in ff if line.strip()}
        console.print(f"\tLoaded {len(state.emails_to_filter)} emails to filter")
    except IOError as e:
        console.print(f"WARNING: Could not read filter file {filter_file_path}: {e}")
        state.email_filtering_mode = False


def process_changelog_file(state: ProcessingState, args: argparse.Namespace) -> None:
    """Process the raw changelog file."""
    work_file = args.raw

    start_scrapping_time = datetime.now()
    # console.print(f"\nStarting processing of {work_file} at {start_scrapping_time}")
    console.print(f"\nStarting processing of {work_file} at {start_scrapping_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        with open(work_file, 'r') as f:
            lines = f.readlines()

        process_file_lines(lines, state)

        print_success(f"\n✓ Successfully processed {len(state.parsed_change_log_entries)} commits")

        if _ask_yes_or_no_question('do you want to inspect parsed_change_log_entries?'):
            console.print(inspect(state.parsed_change_log_entries))

        _handle_step_completion(state, 'parsed_change_log_entries')


        if args.save:
            save_processed_data(state, args.save)

    except FileNotFoundError:
        console.print(f"ERROR: Input file not found: {work_file}")
        sys.exit(1)
    except Exception as e:
        console.print(f"ERROR processing file: {e}")
        sys.exit(1)


def process_file_lines(lines: List[str], state: ProcessingState) -> None:
    """Process all lines from the input file."""
    current_block: List[str] = []
    commit_index = 0  # Add counter for commit order

    for line_num, line in enumerate(lines, 1):
        if line == "\n":
            continue

        state.statistics.n_lines += 1

        if line.startswith('=='):
            if current_block:
                process_current_block(state, current_block)
                process_commit_block(current_block, state, commit_index)
                commit_index += 1  # Increment after processing

            current_block = [line]
            state.statistics.n_blocks += 1

    # Process final block
    if current_block:
        process_commit_block(current_block, state, commit_index)

def process_current_block(state: ProcessingState, current_block: List[str]) -> None:
    """Handle logging for the current block being processed."""
    if state.verbose_mode:
        logger.debug(f"Processing {current_block[0]=}")
    elif state.very_verbose_mode:
        logger.debug(f"Processing {current_block=}")


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

    # Branch based on network type
    if state.network_type == 'inter_individual_graph_temporal':
        # For temporal networks, use the temporal extraction
        extract_temporal_connections(state)
        # Skip unique connections step - we keep all temporal data
        console.print(
            f"[blue] Extracted {len(state.file_coediting_collaborative_relationships)} temporal connections[/blue]")
    else:
        process_connections_step(state)
        process_unique_connections_step(state)

    process_network_creation_step(state)
    apply_email_filtering(state)



def _handle_step_completion(state: ProcessingState, step_name: str) -> None:
        """
        Handle the completion of a processing step with optional inspection and continuation.

        Args:
            state: The current processing state
            step_name: Name of the step being completed (for logging)
        """
        # Format a generic success message from the step name

        print_success(f"{step_name} completed successfully ✓")

        if state.debug_mode:
            if _ask_inspect_processing_state():
                print_info(f"Inspecting state at stage {step_name}")
                console.print(f'state={inspect(state)}')

            if not _ask_continue():
                print_info(f"Aborted by user at stage {step_name}")
                sys.exit()

def process_aggregation_step(state: ProcessingState) -> None:
    """Aggregate files and contributors."""
    console.print("[blue] Aggregating data:[/blue] For each file, what are the contributors.")
    aggregate_files_and_contributors(state)
    console.print("[bold green]Success:[/bold green]" + "\n✓ Data aggregated by files and contributors")

    _handle_step_completion(state, "process_aggregation_step")


def process_connections_step(state: ProcessingState) -> None:
    """Extract contributor connections."""
    console.print(
        "[blue] Mapping connections between developers:[/blue] Getting tuples of contributors that coded/contributed on the same file")
    extract_contributor_connections(state)
    console.print("[bold green]Success:[/bold green]" + "\n✓ Contributor connections extracted as tuples")

    if state.very_verbose_mode:
        console.print(f'state={inspect(state)}')

    _handle_step_completion(state, "process_aggregation_step")


def process_unique_connections_step(state: ProcessingState) -> None:
    """Get unique connections from tuples list."""
    console.print("[blue] Getting unique connections from tuples list.")
    state.aggregated_file_coediting_collaborative_relationships = get_unique_connections(state.file_coediting_collaborative_relationships)
    console.print(
        "[bold green]Success:[/bold green]" + f"\n✓ Extracted {len(state.aggregated_file_coediting_collaborative_relationships)} unique connections")

    if state.verbose_mode:
        print(f"{state.aggregated_file_coediting_collaborative_relationships=}")

    if state.very_verbose_mode:
        print(f'state={inspect(state)}')

    _handle_step_completion(state, "process_unique_connections_step")


def process_network_creation_step(state: ProcessingState) -> None:
    """Create network graph using NetworkX based on network type."""
    console.print(f"[blue] Creating {state.network_type} network using NetworkX.[/blue]")

    if state.network_type == 'inter_individual_graph_temporal':
        create_temporal_network_graph(state)
    else:
        # Your existing create_network_graph function for unweighted/weighted
        create_network_graph(state)

    console.print("[bold green]Success:[/bold green]" + "\n✓ Network graph created")

    if state.very_verbose_mode:
        console.print(f'state={inspect(state)}')

    _handle_step_completion(state, "process_network_creation_step")

def export_results(state: ProcessingState, args: argparse.Namespace) -> None:
    """Export results to GraphML and print summary."""

    if args.output_file:
        graphml_filename = Path(args.output_file)
    else:
        base = Path(args.raw).stem
        if state.network_type == 'inter_individual_graph_temporal':
            graphml_filename = base + ".TemporalNetwork.graphML"
        elif state.network_type == 'inter_individual_multigraph_weighted':
            graphml_filename = base + ".WeightedNetwork.graphML"
        else:
            graphml_filename = base + ".NetworkFile.graphML"

    try:
        # For temporal networks, ensure complex attributes are string fied for GraphML
        if state.network_type == 'inter_individual_graph_temporal':
            # Create a copy with string field lists for GraphML compatibility
            g = state.dev_to_dev_network.copy()
            for u, v, data in g.edges(data=True):
                if 'collaboration_timeline' in data:
                    data['collaboration_timeline'] = str(data['collaboration_timeline'])
                if 'files_shared' in data:
                    data['files_shared'] = str(data['files_shared'])
            export_log_data.create_graphml_file(g, graphml_filename)
        else:
            export_log_data.create_graphml_file(state.dev_to_dev_network, graphml_filename)

        console.print(f"\n✓ Network exported to GraphML file: {graphml_filename}")
        console.print()
    except Exception as e:
        console.print(f"ERROR exporting to GraphML: {e}")

    print_processing_summary(state, args.raw, args.output_file)


def main() -> None:
    start_time = time.time()
    atexit.register(print_exit_info,start_time)
    console.print(f"[blue]▶ Executing: {' '.join(sys.argv)}[/blue]")

    """Main execution function."""
    state = ProcessingState()
    args = parse_arguments()
    setup_processing_state(state, args)
    process_changelog_file(state, args)
    execute_data_processing_pipeline(state)
    export_results(state, args)


if __name__ == "__main__":
    main()