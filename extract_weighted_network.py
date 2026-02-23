"""
In action with argument 'inter_individual_multigraph_weighted'
from state, mostly parsed_change_log_entries structure, creates an weighted network social network

See for more information
---
Osborne, C., Daneshyan, F., He, R., Ye, H., Zhang, Y., & Zhou, M. (2025). Characterising open source
co-opetition in company-hosted open source software projects: the cases of PyTorch, TensorFlow, and
transformers. Proceedings of the ACM on Human-Computer Interaction, 9(2), 1-30.

and

Teixeira, J., Robles, G. & González-Barahona, J.M. Lessons learned from applying social network analysis
on an  industrial Free/Libre/Open Source Software ecosystem. J Internet Serv Appl 6, 14 (2015).
https://doi.org/10.1186/s13174-015-0028-2
----

"""

import networkx as nx
from networkx import Graph

from core.models import ProcessingState
from utils.validators import validate_all_graph_edges_have_weights


def extract_weighted_from_parsed_change_log_entries(state:ProcessingState) -> Graph | None:
    """Extract weighted network from parsed changelog entries.

    developers are connected in the network by the number of common edited files

    Returns:
        weighted networks if successful, None if no data available
    """
    # Implementation here

    parsed_change_log_entries = state.parsed_change_log_entries

    graph = nx.Graph()

    validate_all_graph_edges_have_weights(graph)

    return None