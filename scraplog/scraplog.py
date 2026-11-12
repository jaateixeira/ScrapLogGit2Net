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


def main() -> None:
    start_time = time.time()
    atexit.register(print_exit_info, start_time)
    console.print(f"[blue]▶ Executing: {' '.join(sys.argv)}[/blue]")

    """Main execution function."""
    state = ProcessingState()
    args = parse_arguments()
    setup_processing_state(state, args)
    process_changelog_file(state, args)
    execute_data_processing_pipeline(state)
    export_results(state, args)


if __name__ == "__main__":
    main()
