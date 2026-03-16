from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, DefaultDict, Dict, Set

import networkx as nx
import networkx_temporal as tx

""" Import the more simple str based types"""
from core.types import Email, Affiliation, Filename, Timestamp

""" Import more complex types """
from core.types import  ChangeLogEntry # tuple[DeveloperInfo, list[Filename],Timestamp]
from core.types import EmailAggregationConfig # dict[str, str]
from core.types import ConnectionWithFile # tuple[Connection, Filename, Timestamp]
from core.types import Connection # tuple[Email, Email, Timestamp]

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

    # Structures added by extract_temporal_network.py
    # Temporal network with u,v, time
    coauthorship_temporal_network: tx.TemporalMultiGraph = tx.TemporalMultiGraph()

    # Track unique contributors per file (automatically handles duplicates)
    accumulated_history_of_contributors_by_file = defaultdict(set)
    # Track unique files per contributor (automatically handles duplicates)
    accumulated_history_of_files_by_contributor = defaultdict(set)


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




@dataclass
class NetworkContainer:
    """Container for temporal and static network representations of developer collaboration."""

    # Temporal networks
    temporal_network_with_time_and_file_attributes: tx.TemporalMultiGraph = field(
        default_factory=tx.TemporalMultiGraph
    )
    """Temporal multi-graph capturing developer-file interactions over time.

    This network preserves the temporal dimension of developer collaborations on files.
    Each edge represents a co-editing event and includes:
    - Timestamp: When the collaboration occurred
    - File path: Which file was being edited

    Use for:
    - Analyzing how collaboration patterns evolve
    - Identifying temporal communities
    - Studying developer specialization over time
    """

    coauthorship_temporal_network_with_time_attributes: tx.TemporalMultiGraph = field(
        default_factory=tx.TemporalMultiGraph
    )
    """Temporal co-authorship network from commit history.

    Captures when developers commit together, creating temporal collaboration edges.
    Each edge includes timestamp attributes. 
    
    In this data structure. Developers commiting at the same time one or more files, does not matter. 
    At least one is enough to assume collaboration . 

    Use for:
    - Studying team formation dynamics
    - Analyzing collaboration bursts
    - Temporal community evolution
    """

    # Static network graphs
    dev_to_dev_weighted_network: nx.Graph = field(default_factory=nx.Graph)
    """Weighted static collaboration graph.

    Aggregates all collaboration events into edge weights.
    Edge weight = total collaboration frequency (e.g., number of shared commits).

    Use for:
    - Community detection algorithms
    - Weighted centrality measures
    - Identifying key collaborators
    - Strength of ties analysis
    
    Used by Cailean Osborne, Farbod Daneshyan, Runzhi He, Hengzhi Ye, Yuxia Zhang, and Minghui Zhou. 2025. Characterising Open Source Co-opetition in Company-hosted Open Source Software Projects: The Cases of PyTorch, TensorFlow, and Transformers. Proc. ACM Hum.-Comput. Interact. 9, 2, Article CSCW046 (May 2025), 30 pages. https://doi.org/10.1145/3710944
    
    """

    dev_to_dev_unweighted_network: nx.Graph = field(default_factory=nx.Graph)
    """Unweighted static collaboration graph.

    Binary version showing if any collaboration exists between developers.
    Typically derived by thresholding the weighted network (weight >= 1).

    Use for:
    - Connectivity analysis
    - Component detection
    - Algorithms requiring unweighted inputs
    - Basic network visualization
    
    Used by Teixeira, J., Robles, G. & González-Barahona, J.M. Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. J Internet Serv Appl 6, 14 (2015). https://doi.org/10.1186/s13174-015-0028-2
    
    """
