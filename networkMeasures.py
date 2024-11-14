# Get some basic network measures 
# Ideal to get number of nodes and edges from agreByConnWSF list that keeps  agregated tuples of connected authors  due to working on a common file [(a-b),file)]
# Validate that the list of connection is on the right format [(a-b),file)]

from __future__ import absolute_import, print_function
import sys

def validate_connections_format(connections):
    """Validate the format of the connections list."""
    if not connections:
        print("\tWarning - connections list is empty")
        return False

    try:
        ((author1, author2), file_name) = connections[0]
    except (ValueError, TypeError):
        print("\tWarning - connections list is in the wrong format")
        return False

    if len(author1) < 5 or len(author2) < 5 or len(file_name) < 1:
        print("\tWarning - connections list is in the wrong format")
        return False

    return True

def get_number_of_networked_nodes(connections):
    """Get the number of unique nodes/authors from the connections list."""
    if not validate_connections_format(connections):
        print("\tERROR: Invalid connections list format")
        sys.exit()

    contributors = set()

    for connection in connections:
        (contri1, contri2) = connection[0]
        contributors.update([contri1, contri2])

    return len(contributors)

def get_number_of_affiliations(affiliations_dict):
    """Get the number of unique affiliations from the affiliations dictionary."""
    return len(set(affiliations_dict.values()))

def get_number_of_edges(connections):
    """Get the number of edges (collaborations), including duplicates."""
    if not validate_connections_format(connections):
        print("\tERROR: Invalid connections list format")
        sys.exit()

    return len(connections)

def get_number_of_unique_edges(connections):
    """Get the number of unique edges (collaborations)."""
    if not validate_connections_format(connections):
        print("\tERROR: Invalid connections list format")
        sys.exit()

    unique_connections = set()

    for connection in connections:
        (author1, author2) = connection[0]
        edge = tuple(sorted((author1, author2)))  # Ensure order is consistent
        unique_connections.add(edge)

    return len(unique_connections)

def get_number_of_developers():
    """Get the total number of developers (not implemented)."""
    print("To be implemented")
    return -1

def get_number_of_networked_developers(connections):
    """Get the number of developers working in collaboration (not implemented)."""
    print("To be implemented")
    return -1
