"""
In action with argument 'inter_individual_graph_unweighted'
from state, mostly parsed_change_log_entries structure, creates an unweighted network social network

See for more information
----
Teixeira, J., Robles, G. & González-Barahona, J.M. Lessons learned from applying social network analysis
on an  industrial Free/Libre/Open Source Software ecosystem. J Internet Serv Appl 6, 14 (2015).
https://doi.org/10.1186/s13174-015-0028-2
----

"""

import networkx as nx
from networkx import Graph

from core.models import ProcessingState


def extract_unweighted_from_parsed_change_log_entries(state:ProcessingState) -> Graph | None:
    """Extract temporal network from parsed changelog entries.

    Returns:
        TemporalGraph if successful, None if no data available
    """
    # Implementation here

    parsed_change_log_entries = state.parsed_change_log_entries


    graph = nx.Graph()
    return None