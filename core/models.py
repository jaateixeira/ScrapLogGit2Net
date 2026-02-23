from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, DefaultDict, Dict, Set

import networkx as nx

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
