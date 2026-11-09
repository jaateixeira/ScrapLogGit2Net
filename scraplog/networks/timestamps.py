"""
Conversions between git, ISO 8601 and Unix timestamps.
"""

from typing_extensions import deprecated
from datetime import datetime


@deprecated("Use git_timestamp_to_iso() instead which preserves timezone information")
def git_timestamp_to_unix(git_timestamp_str: str) -> float:
    """
    Convert Git timestamp string to Unix timestamp.

    Example: 'Tue Jan 2 11:19:35 2024 -0800' -> 1704213575.0
    """
    # Parse Git timestamp format
    dt = datetime.strptime(git_timestamp_str, '%a %b %d %H:%M:%S %Y %z')
    # Return Unix timestamp (seconds since epoch)
    return dt.timestamp()


@deprecated("Use iso_to_git_timestamp instead which preserves timezone information")
def unix_to_git_timestamp(unix_timestamp: float) -> str:
    """
    Convert Unix timestamp to Git timestamp string.

    Example: 1704213575.0 -> 'Tue Jan 2 11:19:35 2024 -0800'
    """
    # Convert Unix timestamp to datetime
    dt = datetime.fromtimestamp(unix_timestamp)
    # Format as Git timestamp
    return dt.strftime('%a %b %d %H:%M:%S %Y %z')


def git_timestamp_to_iso(git_timestamp_str: str) -> str:
    """Convert Git timestamp to ISO format with timezone."""
    dt = datetime.strptime(git_timestamp_str, '%a %b %d %H:%M:%S %Y %z')
    return dt.isoformat()  # Preserves timezone!


def iso_to_git_timestamp(iso_str: str) -> str:
    """Convert ISO format back to Git timestamp."""
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime('%a %b %d %H:%M:%S %Y %z')
