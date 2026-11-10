"""
Co-editing networks: developers connected when they edited the same file.
"""

import itertools
import sys
from typing import List, Set
import networkx as nx
from scraplog.core.models import ProcessingState
from scraplog.core.types import Filename, ChangeLogEntry, ConnectionWithFile, Connection
from scraplog.utils.debugging import handle_step_completion
from scraplog.utils.unified_console import console, print_fatal_error
from scraplog.utils.unified_logger import logger
from scraplog.utils.validators import AffiliationValidationError
from scraplog.identity import extract_affiliation_from_email


def aggregate_files_and_contributors(state: ProcessingState) -> None:
    """Aggregate data: for each file, what are the contributors."""

    # console.print(f"\nAggregating data: for each file what are the contributors")

    files_visited: Set[Filename] = set()

    # Keep your existing type aliases but add accessor functions
    def get_email_from_entry(entry: ChangeLogEntry) -> str:
        """Extract email from a changelog entry tuple."""
        return entry[0][0]  # DeveloperInfo is at index 0, email at index 0

    def get_files_from_entry(entry: ChangeLogEntry) -> list[Filename]:
        """Extract files from a changelog entry tuple."""
        return entry[1]  # files_changed at index 1

    for entry in state.parsed_change_log_entries:
        email = get_email_from_entry(entry)
        files = get_files_from_entry(entry)

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
        if state.verbose_mode: logger.debug(f"Adding node attributes to {node=}")

        node_email = node
        node_affiliation = extract_affiliation_from_email(node, state)
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

    handle_step_completion(state, "apply_email_filtering")


def enrich_graph_with_names_used_by_each_developer(
        graph: nx.Graph,
        affiliation_map: dict[str, str],
) -> nx.Graph:
    raise NotImplementedError


def enrich_graph_with_files_edited_by_each_developer(
        graph: nx.Graph,
        affiliation_map: dict[str, str],
) -> nx.Graph:
    raise NotImplementedError





def enrich_graph_with_affiliation(
        graph: nx.Graph,
        affiliation_map: dict[str, str],
) -> nx.Graph:
    """
    Set the 'affiliation' attribute on every node in graph
    using a pre-built {node_id: affiliation} mapping.

    Args:
        graph:           NetworkX graph to enrich (mutated in place).
        affiliation_map: Dict mapping node ID (email) to affiliation string.

    Returns:
        The same graph object with affiliation attributes set.

    Raises:
        AffiliationValidationError: If any node has no entry in affiliation_map.
    """

    if graph is None:
        print_fatal_error("The input did not led to the creation of a valid network ")
        sys.exit(1)

    missing = [node for node in graph.nodes() if node not in affiliation_map]
    if missing:
        raise AffiliationValidationError(
            f"{len(missing)} node(s) have no entry in affiliation_map: {missing}"
        )

    for node, affiliation in affiliation_map.items():
        if graph.has_node(node):
            graph.nodes[node]["affiliation"] = affiliation

    return graph
