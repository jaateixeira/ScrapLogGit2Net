#!/usr/bin/env python3
"""
Scrap date, authors, affiliations and file changes from a Git Changelog.
to build networks of who works with who in a
"""

import argparse

from scraplog import version_text
import atexit
import sys
import time
from pathlib import Path
from scraplog.core.models import ProcessingState
from scraplog.utils.unified_console import console, Table, print_info, print_tip, print_fatal_error
from scraplog.identity import load_email_aggregation_config, load_email_filter_file
from scraplog.output import export_results
from scraplog.parsing import load_file_filter_file, process_changelog_file
from scraplog.pipeline import execute_data_processing_pipeline
from scraplog.networks.temporal import parse_duration
from scraplog.hotspots import MAX_TOP_HOTSPOT_FILES, apply_hotspot_filter


def print_exit_info(start_time: float) -> None:
    """console.print execution summary at exit."""
    execution_time = time.time() - start_time
    table = Table(title="Script Execution Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total execution time", f"{execution_time:.2f} seconds")
    table.add_row("Script arguments", str(sys.argv[1:]))
    console.print(table)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Scrap git changelog to create networks/graphs for research purposes'
    )
    parser.add_argument('-l', '--load', type=Path,
                        help='load a change log saved with -s. Not implemented yet: '
                             'stops with an error')
    parser.add_argument('-r', '--raw', type=Path, required=True,
                        help='processes from a raw git changelog')
    parser.add_argument('-s', '--save', type=Path,
                        help='also save the parsed change log to this file (Python pickle)')
    parser.add_argument('-fe', '--filter-emails', type=Path,
                        help='ignores the emails listed in a text file (one email per line)')
    parser.add_argument('-ff', '--filter-files', type=Path,
                        help='ignores the files listed in a text file (one file per line). '
                             'Lines can be exact paths (src/main.py) or wildcard patterns '
                             '(*.md, docs/*); blank lines and lines starting with # are ignored')
    # after the existing -ff / --filter-files argument:
    parser.add_argument(
        '-ie', '--include-only-with-file-extensions',
        nargs='+',
        metavar='EXT',
        help='only process files with these extensions (e.g. -ie .py .cpp .cu)'
    )
    parser.add_argument(
        '-xe', '--exclude-all-with-file-extensions',
        nargs='+',
        metavar='EXT',
        help='skip files with these extensions (e.g. -xe .json .html .php)'
    )
    parser.add_argument('-a', '--aggregate-email-prefixes', type=Path,
                        help='JSON file mapping the organization part of email domains to an organization name '
                             '(exact, case-insensitive match; e.g. {"gmail": "google", "googlemail": "google"})')
    parser.add_argument('-t', '--type-of-network',
                        choices=['inter_individual_graph_unweighted',
                                 'inter_individual_graph_weighted',
                                 'inter_individual_graph_temporal',
                                 'inter_individual_weighted_LOC_temporal',
                                 'inter_individual_graph_weighted_SUM_LOC'],
                        default='inter_individual_graph_unweighted',
                        help='Type of network to generate (default: inter_individual_graph_unweighted)')
    parser.add_argument('-tntr', '--temporal-network-time-resolution', type=int, default=1,
                        help='Temporal network time resolution in seconds. Only 1 (the default) is '
                             'implemented so far; other values stop with an error')
    parser.add_argument('--coedit-window', metavar='DURATION',
                        help='only link developers whose changes to a file are at most this far apart: '
                             'a number with s, m, h or d (e.g. 30d, 12h, 90m, 3600s; a number alone '
                             'means seconds). Default: no limit')
    parser.add_argument('--min-coedits', metavar='N', type=int, default=1,
                        help='only keep developer pairs with at least N time-stamped co-edits '
                             '(counted after --coedit-window). Default: 1 (every pair)')
    parser.add_argument('--max-coedits', metavar='N', type=int, default=None,
                        help='only keep developer pairs with at most N time-stamped co-edits '
                             '(counted after --coedit-window). Default: no limit')
    parser.add_argument('--ignore-top-hotspot-files', metavar='K', type=int, default=0,
                        help='ignore the K files (0-20) changed by the most developers (ties broken by '
                             'path), before building the networks. Listed in <output>.ignored-files.csv')
    parser.add_argument('--ignore-files-with-more-than-developers', metavar='N', type=int, default=None,
                        help='ignore files changed by more than N developers, before building the '
                             'networks. Listed in <output>.ignored-files.csv')
    parser.add_argument('-o', '--output-file', type=Path,
                        help='creates a network/graph graphml file with the given name')

    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity level (use -v, -vv, or -vvv)'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-st', '--strict', action='store_true',
                        help="strict validation mode - fail on validation errors")

    parser.add_argument('--version', action='version', version=version_text(parser.prog))

    return parser.parse_args()


def setup_processing_state(state: ProcessingState, args: argparse.Namespace) -> None:
    """Configure the processing state based on arguments."""
    # Set modes
    state.verbose_mode = True if args.verbose == 1 else False
    state.very_verbose_mode = True if args.verbose == 2 else False
    state.debug_mode = True if args.debug else False
    state.strict_validation = args.strict

    state.network_type = args.type_of_network

    # Loading a saved change log is not implemented: stop instead of silently
    # parsing the raw log given with -r.
    if args.load:
        print_fatal_error(
            "Loading a saved change log (-l) is not implemented yet",
            "Leave out -l; scrapLog parses the raw git log given with -r.")
        sys.exit(1)

    # Only a 1-second temporal resolution is implemented. Stop instead of silently
    # ignoring another value, which would give a network the user did not ask for.
    if args.temporal_network_time_resolution != 1:
        print_fatal_error(
            f"Temporal network time resolution {args.temporal_network_time_resolution} is not implemented yet",
            "Only -tntr 1 (one second, the default) is supported. Leave out -tntr.")
        sys.exit(1)

    if args.coedit_window is not None:
        try:
            state.coedit_window = parse_duration(args.coedit_window)
        except ValueError as error:
            print_fatal_error(f"Invalid --coedit-window: {error}",
                              "Give a positive number with s, m, h or d, e.g. 30d, 12h, 90m or 3600s.")
            sys.exit(1)

    if args.min_coedits < 1:
        print_fatal_error(f"Invalid --min-coedits: {args.min_coedits}", "Give a whole number of at least 1.")
        sys.exit(1)
    state.min_coedits = args.min_coedits

    if args.max_coedits is not None and args.max_coedits < args.min_coedits:
        print_fatal_error(f"Invalid --max-coedits: {args.max_coedits}",
                          f"Give a whole number of at least --min-coedits ({args.min_coedits}).")
        sys.exit(1)
    state.max_coedits = args.max_coedits

    if not 0 <= args.ignore_top_hotspot_files <= MAX_TOP_HOTSPOT_FILES:
        print_fatal_error(f"Invalid --ignore-top-hotspot-files: {args.ignore_top_hotspot_files}",
                          f"Give a whole number from 0 to {MAX_TOP_HOTSPOT_FILES}.")
        sys.exit(1)
    state.ignore_top_hotspot_files = args.ignore_top_hotspot_files

    if args.ignore_files_with_more_than_developers is not None and args.ignore_files_with_more_than_developers < 1:
        print_fatal_error(f"Invalid --ignore-files-with-more-than-developers: {args.ignore_files_with_more_than_developers}",
                          "Give a whole number of at least 1.")
        sys.exit(1)
    state.max_developers_per_file = args.ignore_files_with_more_than_developers

    if state.verbose_mode:
        print_info('Verbose mode')

    if state.very_verbose_mode:
        print_info('Very verbose mode')

    if state.debug_mode:
        print_info('Debug mode')
        print_info('You will be called to continue step after step')
        print_info('You will be invited to ask for processing state')

    # Load email aggregation config
    if args.aggregate_email_prefixes:
        state.email_aggregation_config = load_email_aggregation_config(
            args.aggregate_email_prefixes
        )

    # Set filtering modes
    if args.filter_emails:
        state.email_filtering_mode = True
        print_info("Email filtering turned on.")
        print_tip("The filtering based on  only happen when creating the graphml network output file.")

    if args.filter_files:
        state.file_filtering_mode = True
        console.print("\nFile filtering turned on")
        load_file_filter_file(state, args.filter_files)

    # Load specific filter files
    if state.email_filtering_mode and args.filter_emails:
        load_email_filter_file(state, args.filter_emails)


    # Lot file extensions to be filtered
    if args.include_only_with_file_extensions:
        state.include_extensions = {
            ext if ext.startswith('.') else f'.{ext}'
            for ext in args.include_only_with_file_extensions
        }
        print_info(f"Include-extensions filter active: {sorted(state.include_extensions)}")

    if args.exclude_all_with_file_extensions:
        state.exclude_extensions = {
            ext if ext.startswith('.') else f'.{ext}'
            for ext in args.exclude_all_with_file_extensions
        }
        print_info(f"Exclude-extensions filter active: {sorted(state.exclude_extensions)}")

    if state.include_extensions and state.exclude_extensions:
        overlap = state.include_extensions & state.exclude_extensions
        if overlap:
            print_fatal_error(
                f"Conflicting extension filters: {sorted(overlap)} appear in both "
                f"-ie and -xe. Remove them from one of the two arguments."
            )
            sys.exit(1)


def report_ignored_hotspot_files(ignored) -> None:
    """Print the hotspot files left out (see scraplog/hotspots.py)."""
    table = Table(title=f"Ignored hotspot files ({len(ignored)})")
    table.add_column("File")
    table.add_column("Developers", justify="right")
    table.add_column("Reason")
    for file, developers, reason in ignored:
        table.add_row(file, str(developers), reason)
    console.print(table)


def main() -> None:
    start_time = time.time()
    atexit.register(print_exit_info, start_time)
    console.print(f"[blue]▶ Executing: {' '.join(sys.argv)}[/blue]")

    """Main execution function."""
    state = ProcessingState()
    args = parse_arguments()
    setup_processing_state(state, args)
    process_changelog_file(state, args)
    if state.ignore_top_hotspot_files or state.max_developers_per_file is not None:
        report_ignored_hotspot_files(apply_hotspot_filter(state))
    execute_data_processing_pipeline(state)
    export_results(state, args)


if __name__ == "__main__":
    main()
