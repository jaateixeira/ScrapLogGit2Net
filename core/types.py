from typing import TypeAlias

# Type aliases using built-in types
Email = str
Affiliation = str
Filename = str
Timestamp = str

# =============================================================================
# Type Definitions for Core Data Structures
# =============================================================================

DeveloperInfo: TypeAlias = tuple[Email, Affiliation]
"""
Developer information extracted from a commit header.

Contains:
    - Email: Developer's email (e.g., 'john.doe@company.com')
    - Affiliation: Organization from email domain (e.g., 'company', 'google', 'nvidia')
"""

ChangeLogEntry: TypeAlias = tuple[DeveloperInfo, list[Filename],Timestamp]
"""
A complete changelog entry representing one commit.

Structure:
    - DeveloperInfo: Who made the commit and when
    - list[Filename]: Files changed in that commit (e.g., ['src/main.py', 'README.md'])
    - Timestamp: When the commit was made (e.g., '2023-01-15 14:30:22 -0500')

Example: ( 'alice@co.com', 'co'), ['file1.py', 'file2.py'],('2023-01-15...'))
"""

EmailAggregationConfig: TypeAlias = dict[str, str]
"""
Configuration for grouping email addresses by domain patterns.

Maps domain prefixes to consolidated affiliation names.
Example: {'ibm': 'ibm', 'google': 'google', 'gmail': 'personal'}
"""

Connection: TypeAlias = tuple[Email, Email, Timestamp]
"""
Represents an connection/relationship between two developers with unique email addresses.

A Connection captures the fundamental relationship between two developers a specific point in time. 
In StapLog, this connection comes from co-editing the same source-code files (aka commit to code 
file commited by someone else)

Tuple Structure:
    [0]: Email - First developer's email
    [1]: Email - Second developer's (collaborator) email
    [2]: Timestamp - When this connection was established/observed

Example:
    >>> connection = ("john@example.com", "jane@example.com", datetime.now())
    >>> source, target, time = connection  # Tuple unpacking
    >>> print(f"{source} connected to {target} at {time}")
"""

ConnectionWithFile: TypeAlias = tuple[Connection, Filename, Timestamp]
"""
Extends a Connection with the name of modified files and time developers got connected 

The structure enables tracing back any connection to its original source file,
which is crucial for debugging, reprocessing, and understanding data origins.

Tuple Structure:
    [0]: Connection - The email relationship (source, target, timestamp)
    [1]: Filename - Name/path of the source file where this was found
    [2]: Timestamp - When this relationship was processed/recorded

Example:
    >>> conn = ("alice@work.com", "bob@work.com", datetime(2024, 1, 15, 10, 30))
    >>> conn_with_file = (conn, "january_emails.mbox", datetime.now())
    >>> relationship, filename, processed_at = conn_with_file
    >>> print(f"Found {relationship[0]} → {relationship[1]} in {filename}")
"""