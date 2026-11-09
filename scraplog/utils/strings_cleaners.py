import sys
import re
from email.utils import parseaddr
from urllib.parse import unquote


def clean_email(email: str) -> str | None:
    """
    Clean an email address by removing common artifacts.

    Handles:
      - Plain addresses:          john@example.com
      - Display name format:      John Doe <john@example.com>
      - GitHub no-reply format:   161369871+app@users.noreply.github.com
      - URL-encoded @:            john%40example.com
      - Trailing ?:               john@example.com?
      - Multiple @ signs:         malformed but recoverable
    """
    if not email or not isinstance(email, str):
        return None

    # Remove all whitespace
    email = ''.join(email.split())

    if not email:
        return None

    # Only invoke parseaddr for addresses that actually contain a display
    # name format — i.e. they have angle brackets or quoted strings.
    # For plain addresses, parseaddr mishandles local parts containing '+'
    # (common in GitHub no-reply addresses) and returns an empty string.
    if '<' in email or '"' in email:
        _, parsed = parseaddr(email)
        if parsed and '@' in parsed:
            email = parsed
        # If parseaddr still fails on a bracketed address, fall through
        # to the plain-address handling below rather than returning None

    # URL-decode %40 → @ (some git configs store emails URL-encoded)
    try:
        email = unquote(email)
    except Exception as e:
        print(f"Warning: Failed to URL-decode email '{email}': {e}")
        # Continue with the un-decoded version rather than aborting

    # Remove trailing ?
    email = email.rstrip('?')

    # Basic sanity check
    if '@' not in email:
        return None

    # If somehow multiple @ signs remain, keep first local-part and last domain
    # e.g. "a@b@c.com" → "a@c.com"
    if email.count('@') > 1:
        parts = email.split('@')
        email = f"{parts[0]}@{parts[-1]}"

    # Final check: must have something on both sides of @
    local, _, domain = email.partition('@')
    if not local or not domain:
        return None

    return email.lower()