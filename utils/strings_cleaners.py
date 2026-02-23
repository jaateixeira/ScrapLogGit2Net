import sys
from email.utils import parseaddr


def clean_email(email: str) -> str | None:
    """
    Clean an email address by removing common artifacts.
    Uses email.utils.parseaddr for robust parsing.
    """
    if not email or not isinstance(email, str):
        return None

    # Remove all whitespace first
    email = ''.join(email.split())

    # Use Python's built-in email parser (handles "Name <email>", quotes, etc.)
    _, email = parseaddr(email)

    if not email or '@' not in email:
        return None

    # Remove trailing ? if present
    email = email.rstrip('?')

    # URL decode %40 to @
    try:
        from urllib.parse import unquote
        email = unquote(email)
    except ImportError:
        # This should never happen in standard Python, but if it does, exit
        print("Error: urllib.parse.unquote not available. Cannot continue.")
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors during decoding
        print(f"Error: Failed to decode email '{email}': {e}")
        sys.exit(1)

    # Take last @ if multiple (common in malformed emails)
    if email.count('@') > 1:
        parts = email.split('@')
        email = f"{parts[0]}@{parts[-1]}"

    return email.lower()
