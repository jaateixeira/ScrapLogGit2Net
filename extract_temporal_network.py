"""
In action with argument 'inter_individual_graph_temporal'
from state, mostly parsed_change_log_entries structure, creates a temporal network
"""

import networkx_temporal as tx
from networkx_temporal import TemporalGraph  # Import the actual type

from core.models import ProcessingState


def extract_temporal_network_from_parsed_change_log_entries(state:ProcessingState) -> TemporalGraph | None:
    """Extract temporal network from parsed changelog entries.

    Returns:
        TemporalGraph if successful, None if no data available
    """
    # Implementation here

    parsed_change_log_entries = state.parsed_change_log_entries

    graph = tx.temporal_graph()  # Create the graph
    # Add edges, etc.
    return None