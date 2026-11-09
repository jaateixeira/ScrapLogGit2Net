"""
Parsing a raw git log (==name;email;date== blocks) into change log entries.
"""

import argparse
import re
import sys
from datetime import datetime
from fnmatch import fnmatchcase
from pathlib import Path
from typing import List, Optional, Tuple
from scraplog.core.models import ProcessingState, TimeStampedFileContribution
from scraplog.core.types import Filename, DeveloperInfo, ChangeLogEntry
from scraplog.utils.debugging import handle_step_completion, ask_yes_or_no_question
from scraplog.utils.unified_console import console, traceback, inspect, print_info, print_warning, print_error, print_success, print_fatal_error
from scraplog.utils.unified_logger import logger
from scraplog.identity import extract_affiliation_from_email
from scraplog.pipeline import save_processed_data

def parse_time_name_email_affiliation(
        line: str,
        state: ProcessingState
) -> Optional[Tuple[str, str, str, str]]:
    """
    Extract time, name, email, and affiliation from a log line.

    Args:
        line: Input log line
        state: Processing state object

    Returns:
        Tuple of (date_time, last_name, email, affiliation) or None if parsing fails
    """
    try:
        # Pattern to capture: ==Name;email;date_time timezone==
        # The name might contain spaces, so we need to be careful
        pattern = re.compile(r'^==(.+?);(.+?);(.+?)\s([+-]\d{4})==$')
        match = pattern.search(line)

        if not match:
            # Try alternative patterns for exceptional cases
            return parse_exceptional_format(line, state)

        name, email, date_time_str, timezone = match.groups()

        # Clean email
        email = email.strip()

        # Validate email format
        if '@' not in email:
            console.print(f"WARNING: Invalid email format (no @): {email}")
            state.statistics.increment_validation_errors()
            return None

        # Extract affiliation from email domain
        affiliation = extract_affiliation_from_email(email, state)

        # Combine date_time with timezone for complete timestamp
        full_timestamp = f"{date_time_str} {timezone}"

        return (full_timestamp, name, email, affiliation)

    except Exception as e:
        if state.verbose_mode:
            console.print(f"Error parsing line '{line}': {e}")
        state.statistics.increment_validation_errors()
        return None


def parse_exceptional_format(line: str, state: ProcessingState) -> Optional[Tuple[str, str, str, str]]:
    """
    Parse exceptional log line formats.

    Returns the same (date_time, name, email, affiliation) tuple as
    parse_time_name_email_affiliation, or None if no known format matches.
    """
    try:
        # Pattern 1: Name and email together before ;;
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        # The email is the last whitespace-free token before ;; (names can have spaces)
        pattern1 = re.compile(r'^==(.+)\s(\S+@\S+);;(.+?)\s([+-]\d{4})==$')
        match1 = pattern1.search(line)

        if match1:
            name, email, date_str, timezone = match1.groups()
            affiliation = extract_affiliation_from_email(email, state)
            return f"{date_str} {timezone}", name, email, affiliation

        # Pattern 2: Just email before ;;
        # ==bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        pattern2 = re.compile(r'^==(.+?@.+?);;(.+?)\s([+-]\d{4})==$')
        match2 = pattern2.search(line)

        if match2:
            email, date_str, timezone = match2.groups()
            # Extract name from email
            name = email.split('@')[0]
            affiliation = extract_affiliation_from_email(email, state)
            return f"{date_str} {timezone}", name, email, affiliation

        # Pattern 3: Launchpad bot
        # ==Launchpad;;Tue Sep 20 06:50:27 2011 +0000==
        if "Launchpad" in line:
            pattern3 = re.compile(r'^==(.+?);;(.+?)\s([+-]\d{4})==$')
            match3 = pattern3.search(line)
            if match3:
                name, date_str, timezone = match3.groups()
                email = "launchpad@bot.bot"
                affiliation = "bot"
                return f"{date_str} {timezone}", name, email, affiliation

        # If nothing matches, return None
        return None

    except Exception as e:
        if state.verbose_mode:
            console.print(f"Error parsing exceptional format: {e}")
        return None


def is_filtered_file(filename: str, state: ProcessingState) -> bool:
    """
    True if filename should be ignored according to the -ff filter file.

    Matches exact paths (state.files_to_filter) and shell-style wildcard
    patterns (state.file_filter_patterns). Patterns are matched against the
    full path as it appears in the git log, and '*' also matches '/', so
    '*.md' ignores markdown files in every directory.
    """
    if filename in state.files_to_filter:
        return True
    return any(fnmatchcase(filename, pattern) for pattern in state.file_filter_patterns)


def extract_files_from_block(
        block: List[str],
        state: ProcessingState
) -> List[Filename]:
    files: List[Filename] = []
    n_filtered_by_name = 0
    n_filtered_by_include_ext = 0
    n_filtered_by_exclude_ext = 0

    for line in block:
        if not line or line == '\n':
            break

        filename = line.rstrip('\n')
        ext = Path(filename).suffix.lower()

        if state.file_filtering_mode and is_filtered_file(filename, state):
            n_filtered_by_name += 1
            continue

        if state.include_extensions and ext not in state.include_extensions:
            n_filtered_by_include_ext += 1
            continue

        if state.exclude_extensions and ext in state.exclude_extensions:
            n_filtered_by_exclude_ext += 1
            continue

        if filename.strip():
            files.append(filename)
            state.statistics.n_blocks_changing_code += 1

    # Distinguish between truly empty commits and filtered-to-empty commits
    if not files and state.verbose_mode:
        if n_filtered_by_include_ext + n_filtered_by_exclude_ext + n_filtered_by_name > 0:
            print_info(
                f"Commit skipped after filtering — "
                f"{n_filtered_by_include_ext} excluded by include-ext, "
                f"{n_filtered_by_exclude_ext} excluded by exclude-ext, "
                f"{n_filtered_by_name} excluded by name filter."
            )
        else:
            print_warning("Commit has no files at all — likely a merge, empty, or submodule-only commit.")

    return files


def process_commit_block(
        block: List[str],
        state: ProcessingState,
        commit_index: int,
        extra_debug: bool = False
) -> bool:
    """
    Process a single commit block from the git changelog.

    A commit block consists of a header line (starting with '==') containing author
    information, followed by lines listing the files changed in that commit and timestamp.

    Args:
        block: List of strings representing one commit block
              - First line: Header with format "==name;email;timestamp timezone=="
              - Subsequent lines: Filenames of changed files
        state: ProcessingState object containing configuration and accumulators
        commit_index: Sequential index of this commit (0-based)
        extra_debug: If True, prints detailed debug information even without verbose mode

    Returns:
        bool: True if the block was successfully processed, False if it was skipped
              due to parsing errors, validation failures, or no changed files

    Side Effects:
        - Updates state.statistics with processing metrics
        - Appends to state.parsed_change_log_entries if successful
        - Appends to state.file_history for temporal analysis
        - May increment validation error or skipped block counters

    Example:
        >>> block = [
        ...     "==John Doe;john@company.com;2023-01-15 14:30:22 -0500==",
        ...     "src/main.py",
        ...     "README.md"
        ... ]
        >>> success = process_commit_block(block, state, 0)

    Notes:
        - Blocks without any files are skipped (returns False)
        - Failed header parsing results in skipped block and warning
        - Files matching filter patterns (if enabled) are excluded
        - In strict validation mode, some errors may cause early exit
    """
    if not block:
        return False

    first_line = block[0]

    if extra_debug: print_info(f"Processing first line of commit block '{first_line}'")

    if not first_line.startswith('=='):
        print_error(f"Invalid block - does not start with '==': {first_line[:50]}...")

        console.print(traceback.format_exc(), style="bold red")

        console.print("[bold red]Error:[/bold red] Processing a block not starting with '=='...")
        sys.exit(1)

    try:
        # Parse the commit header
        time_dev_info = parse_time_name_email_affiliation(first_line, state)

        if extra_debug: print_info(f"{time_dev_info=}")

        if state.verbose_mode or state.very_verbose_mode:
            logger.debug("Retrieved ")
            logger.debug(f"{time_dev_info=}")
        if extra_debug:
            console.print(f"{inspect(time_dev_info)}")

        if not time_dev_info:
            print_warning(f"Could not parse commit header: {first_line[:50]}...")
            print_error(f"Could not get developer information from commit block {first_line}")
            state.statistics.increment_skipped_blocks()
            return False

        commit_time, dev_name, dev_email, dev_affiliation = time_dev_info

        # Extract files
        changed_files = extract_files_from_block(block[1:], state)

        if not changed_files:
            if state.verbose_mode or state.very_verbose_mode:
                print_warning(f"No files in commit block for {first_line}")
            state.statistics.increment_skipped_blocks()
            return False
        # Store the data

        dev_info: DeveloperInfo = (dev_email, dev_affiliation)
        new_change_log_entry: ChangeLogEntry = (dev_info, changed_files, commit_time)

        if extra_debug or state.very_verbose_mode:
            print_info(f"Appending parsed_change_log_entries with {new_change_log_entry=}")

        "appending parsed_change_log_entries with the processed commit block"
        state.parsed_change_log_entries.append(new_change_log_entry)

        # NEW: Build file history for temporal analysis
        for filename in changed_files:
            state.file_history[filename].append(
                TimeStampedFileContribution(
                    email=dev_email,
                    timestamp=commit_time,
                    commit_index=commit_index
                )
            )

        return True

    except Exception as e:
        console.print(f"ERROR processing commit block: {e}")
        if state.verbose_mode:
            logger.debug(f"ERROR processing commit block:")
            logger.debug(f"{block=}")
            console.print(traceback.format_exc(), style="bold red")
        state.statistics.increment_skipped_blocks()
        return False


def load_file_filter_file(state: ProcessingState, filter_file_path: Path) -> None:
    """
    Load the -ff file filter list.

    One entry per line: an exact path as it appears in the git log
    (e.g. 'src/main.py') or a shell-style wildcard pattern (e.g. '*.md',
    'docs/*'). Blank lines and lines starting with '#' are ignored.

    Exits with an error if the file is missing or cannot be read.
    """
    try:
        with open(filter_file_path, 'r', encoding='utf-8') as filter_file:
            entries = [line.strip() for line in filter_file]
    except (OSError, UnicodeDecodeError) as e:
        print_fatal_error(f"Could not read file filter list {filter_file_path}", str(e))
        sys.exit(1)

    entries = [entry for entry in entries if entry and not entry.startswith('#')]

    state.files_to_filter = {entry for entry in entries if not any(c in entry for c in '*?[')}
    state.file_filter_patterns = [entry for entry in entries if any(c in entry for c in '*?[')]

    if not entries:
        print_warning(f"File filter list {filter_file_path} has no entries; no files will be ignored")

    console.print(f"\tLoaded {len(state.files_to_filter)} file paths and "
                  f"{len(state.file_filter_patterns)} wildcard patterns to filter")


def process_changelog_file(state: ProcessingState, args: argparse.Namespace) -> None:
    """Process the raw changelog file."""
    work_file = args.raw

    start_scrapping_time = datetime.now()
    # console.print(f"\nStarting processing of {work_file} at {start_scrapping_time}")
    console.print(f"\nStarting processing of {work_file} at {start_scrapping_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        with open(work_file, 'r') as f:
            lines = f.readlines()

        process_file_lines(lines, state)

        print_success(f"\n✓ Successfully processed {len(state.parsed_change_log_entries)} commits")

        if state.debug_mode and ask_yes_or_no_question('do you want to inspect parsed_change_log_entries?'):
            console.print(inspect(state.parsed_change_log_entries))

        handle_step_completion(state, 'parsed_change_log_entries')

        if args.save:
            save_processed_data(state, args.save)

    except FileNotFoundError:
        console.print(f"ERROR: Input file not found: {work_file}")
        sys.exit(1)
    except Exception as e:
        console.print(f"ERROR processing file: {e}")
        traceback.print_exc()
        sys.exit(1)


def process_file_lines(lines: List[str], state: ProcessingState) -> None:
    """Process all lines from the input file."""
    current_block: List[str] = []
    commit_index = 0  # Add counter for commit order

    for line_num, line in enumerate(lines, 1):
        if line == "\n":
            continue

        state.statistics.n_lines += 1

        if line.startswith('=='):
            if current_block:
                log_and_validate_current_block_being_processed(state, current_block)
                process_commit_block(current_block, state, commit_index)
                # process_commit_block(current_block, state, commit_index, extra_debug=True)
                commit_index += 1  # Increment after processing

            current_block = [line]
            state.statistics.n_blocks += 1

        elif '.' in line or '/' in line or len(line.strip()) >= 3:
            current_block.append(line)
        elif line == '--\n':
            continue
        else:
            if state.verbose_mode:
                print_warning(f"WARNING: Unexpected line format at line {line_num}: {line[:50]}...")
    #
    # Process final block
    if current_block:
        log_and_validate_current_block_being_processed(state, current_block)
        process_commit_block(current_block, state, commit_index)
        # process_commit_block(current_block, state, commit_index, extra_debug=True)


def log_and_validate_current_block_being_processed(state: ProcessingState, current_block: List[str]) -> None:
    """Handle logging for the current block being processed."""
    if state.verbose_mode:
        logger.debug(f"Processing {current_block[0]=}")
    elif state.very_verbose_mode or state.debug_mode:
        logger.debug(f"Processing {current_block=}")

    if state.debug_mode:
        has_valid_format = current_block[0].startswith('==') and ';' in current_block[0]
        logger.debug(f"  - Valid format: {has_valid_format}")
        logger.debug(f"  - Block size: {len(current_block)} lines")

    if not current_block[0].startswith('=='):
        if state.strict_validation:
            raise ValueError(f"Invalid block header: {current_block[0][:50]}")
            sys.exit(1)
        else:
            logger.warning(f"Block {current_block} has invalid header format")
            print_warning(f"Block {current_block[0][:50]} has invalid header format")
