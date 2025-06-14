import re
from typing import Tuple, List, Optional
from email_validator import validate_email, EmailNotValidError
from dateutil.parser import parse
from dateutil import tz


# --- Name Validation ---
def validate_git_name(name: str) -> Tuple[bool, str]:
    """Validate Git author/committer name format.

    Rules:
    - Must be non-empty
    - Allows Unicode letters, spaces, hyphens, apostrophes
    - No trailing/leading whitespace

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(name, str):
        return False, "Name must be a string"

    name = name.strip()

    if len(name) == 0:
        return False, "Name cannot be empty"

    if not re.fullmatch(r'^[\p{L}\s\-\'’.]+$', name, re.UNICODE):
        return False, "Name contains invalid characters"

    return True, ""


# --- Email Validation ---
def validate_git_email(email: str) -> Tuple[bool, str]:
    """Validate Git commit email using RFC-compliant validator."""
    try:
        validate_email(email, check_deliverability=False)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)


# --- Time Validation ---
def validate_git_time(time_str: str) -> Tuple[bool, str]:
    """Validate Git commit timestamp format (Unix timestamp + timezone offset)."""
    try:
        parts = time_str.split()
        if len(parts) != 2:
            raise ValueError("Must contain timestamp and timezone offset")

        timestamp_str, offset_str = parts

        # Validate Unix timestamp
        timestamp = int(timestamp_str)
        if timestamp < 0:
            raise ValueError("Timestamp must be positive")

        # Validate timezone offset (+/-HHMM)
        if not re.fullmatch(r'[+-]\d{4}', offset_str):
            raise ValueError("Timezone offset must be ±HHMM")

        return True, ""
    except (ValueError, AttributeError, TypeError) as e:
        return False, f"Invalid Git time format: {str(e)}"


# --- Files Validation ---
def validate_git_files(files: List[str]) -> Tuple[bool, str]:
    """Validate list of files in commit.

    Rules:
    - Must be list
    - Each file must be non-empty string
    - No path traversal attempts (basic check)
    """
    if not isinstance(files, list):
        return False, "Files must be a list"

    for file in files:
        if not isinstance(file, str):
            return False, f"File path must be string: {file}"
        if not file.strip():
            return False, "File path cannot be empty"
        if '../' in file or '..\\' in file:
            return False, f"Potential path traversal detected: {file}"

    return True, ""


# --- Full Commit Validation ---
def validate_git_commit_block(
        name: str,
        email: str,
        time_str: str,
        files: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """Validate all components of a Git commit.

    Args:
        name: Committer name
        email: Committer email
        time_str: Git timestamp
        files: Optional list of changed files

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Validate name
    valid, msg = validate_git_name(name)
    if not valid:
        return False, f"Name validation failed: {msg}"

    # Validate email
    valid, msg = validate_git_email(email)
    if not valid:
        return False, f"Email validation failed: {msg}"

    # Validate time
    valid, msg = validate_git_time(time_str)
    if not valid:
        return False, f"Time validation failed: {msg}"

    # Validate files if provided
    if files is not None:
        valid, msg = validate_git_files(files)
        if not valid:
            return False, f"Files validation failed: {msg}"

    return True, ""