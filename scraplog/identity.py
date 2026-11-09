"""
Developer identity: email aggregation config, affiliation from email, email filter list.
"""

import json
import sys
from scraplog.core.models import ProcessingState
from scraplog.core.types import EmailAggregationConfig, Email
from scraplog.utils.strings_cleaners import clean_email
from scraplog.utils.unified_console import console, print_fatal_error
from scraplog.utils.unified_logger import logger


def load_email_aggregation_config(config_file: str) -> EmailAggregationConfig:
    """
    Load email aggregation configuration from a JSON file.
    Format: {"prefix": "consolidated_name", ...}
    Example: {"ibm": "ibm", "google": "google"}
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        if not isinstance(config, dict):
            raise ValueError("Config file must contain a JSON object/dictionary")

        for prefix, consolidated_name in config.items():
            if not isinstance(prefix, str) or not isinstance(consolidated_name, str):
                raise ValueError(f"Invalid entry in config: {prefix}: {consolidated_name}")

        console.print(f"Loaded email aggregation config from {config_file}")
        for prefix, name in config.items():
            console.print(f"  {prefix}.* -> {name}")

        return config

    except FileNotFoundError:
        console.print(f"Warning: Email aggregation config file not found: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        console.print(f"Error: Invalid JSON in config file {config_file}: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"Error loading email aggregation config: {e}")
        sys.exit(1)


def extract_affiliation_from_email(
        email: Email,
        state: ProcessingState
) -> str:
    """
    Get affiliation from an email address with aggregation support.

    Returns the inferred organisation name, or "unknown_by_ScrapLog" if the
    domain is valid but affiliation cannot be determined.

    Returns None only for genuinely invalid input (not a string, empty, or
    unparseable email) — callers should treat None as a signal to skip the
    record entirely, whereas "unknown_by_ScrapLog" means the record is valid
    but unresolved.
    """

    if state.verbose_mode or state.very_verbose_mode:
        logger.info(f"\textract_affiliation_from_email({email})")

    # ── Input validation — return None for bad input, not unknown ────────────
    if not email or not isinstance(email, str):
        return None

    cleaned_email = clean_email(email)
    if not cleaned_email:
        return None

    email = cleaned_email.lower()

    try:
        email = email.strip()
        if email.endswith('?'):
            email = email[:-1]

        if '@' not in email:
            if state.verbose_mode:
                console.print(f"WARNING: No @ in email: {email}")
            return "unknown_by_ScrapLog"

        domain_part = email.split('@')[-1].lower()

        if not domain_part:
            if state.verbose_mode:
                console.print(f"WARNING: Empty domain in email: {email}")
            return "unknown_by_ScrapLog"

        domain_parts = domain_part.split('.')
        domain_parts = [part for part in domain_parts if part]

        if not domain_parts:
            if state.verbose_mode:
                console.print(f"WARNING: No valid domain parts in: {email}")
            return "unknown_by_ScrapLog"

        # Resolve organisation from domain
        # Examples:
        #   abo.fi            -> "abo"
        #   mit.edu           -> "mit"
        #   us.ibm.com        -> "ibm"
        #   alumni.mit.edu    -> "mit"
        #   company.co.uk     -> "company"
        #   gmail.com         -> "gmail"
        if len(domain_parts) >= 3 and domain_parts[-2] in {
            'co', 'com', 'ac', 'edu', 'gov', 'net', 'org', 'ltd', 'plc'
        }:
            potential_org = domain_parts[-3]
        elif len(domain_parts) >= 2:
            potential_org = domain_parts[-2]
        else:
            potential_org = domain_parts[0]

        # Apply aggregation config if provided
        for prefix, consolidated_name in state.email_aggregation_config.items():
            prefix_lower = prefix.lower()
            if potential_org == prefix_lower or potential_org.startswith(prefix_lower):
                if state.verbose_mode or state.very_verbose_mode:
                    logger.info(f"\textracted_affiliation_from_email({email})={potential_org}")
                return potential_org.lower()

        # Valid domain, no config match — return as-is
        if state.verbose_mode or state.very_verbose_mode:
            logger.info(f"\textracted_affiliation_from_email({email})={potential_org}")
        return potential_org.lower()

    except Exception as e:
        if state.verbose_mode or state.very_verbose_mode:
            console.print(f"Error extracting affiliation from {email}: {e}")
        return "unknown_by_ScrapLog"

def load_email_filter_file(state: ProcessingState, filter_file_path: str) -> None:
    """Load email filter list from file."""
    try:
        with open(filter_file_path, 'r') as ff:
            state.emails_to_filter = {line.strip() for line in ff if line.strip()}
        console.print(f"\tLoaded {len(state.emails_to_filter)} emails to filter")
    except (OSError, UnicodeDecodeError) as e:
        # Fatal, as for -ff: continuing would silently keep the developers (e.g. bots)
        # that were meant to be excluded
        print_fatal_error(f"Could not read email filter file {filter_file_path}", str(e))
        sys.exit(1)
