#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script mines all repository logs for a given Repo / Directory
Accepts a directory of files / Repo
It can filter by year range or release names
It also provides networks and network visualizations for every branch. Can be release branches or feature branches.
"""

"""
Repo is a tool built on top of Git. 
Repo helps manage many Git repositories, does the uploads to revision control systems, and automates parts of the development workflow.
Repo is not meant to replace Git, only to make it easier to work with Git. The repo command is an executable Python script that you can put anywhere in your path.
"""




import sys
import os


import re

from pathlib import Path
import subprocess
import shlex

import argparse
import networkx as nx

from datetime import datetime

from typing import Optional, Tuple
from typing import Tuple

import time
from time import sleep


# Combining loguru with rich provides a powerful logging setup that enhances readability and adds visual appeal to your logs. This integration makes it easier to debug and monitor applications by presenting log messages in a clear, color-coded, and structured format while using loguru's other features, such as log rotation and filtering,
from loguru import logger

# You can then print strings or objects to the terminal in the usual way. Rich will do some basic syntax highlighting and format data structures to make them easier to read.
from rich import print as rprint


# For complete control over terminal formatting, Rich offers a Console class.
# Most applications will require a single Console instance, so you may want to create one at the module level or as an attribute of your top-level object.
from rich.console import Console

# Initialize the console
console = Console()

# JSON gets easier to understand
from rich import print_json
from rich.json import JSON





# Strings may contain Console Markup which can be used to insert color and styles in to the output.
from rich.markdown import Markdown

# Python data structures can be automatically pretty printed with syntax highlighting.
from rich import pretty
from rich.pretty import pprint
pretty.install()

# Rich has an inspect() function which can generate a report on any Python object. It is a fantastic debug aid
from rich import inspect
from rich.color import Color

#Rich supplies a logging handler which will format and colorize text written by Python’s logging module.
from rich.logging import RichHandler


def setup_logging(verbose: int = 0, console: Optional[Console] = None) -> None:
    """Configure loguru logger with RichHandler.

    Args:
        verbose: Verbosity level (0=WARNING, 1=INFO, >=2=DEBUG)
        console: Optional Rich Console instance (creates new if None)
    """
    # Determine log level from verbosity
    log_level = "WARNING"
    if verbose == 1:
        log_level = "INFO"
    elif verbose >= 2:
        log_level = "DEBUG"

    # Create console if not provided
    if console is None:
        console = Console()

    # Remove default handler and add RichHandler
    logger.remove()
    logger.add(
        RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            rich_tracebacks=True,
            markup=True,
            show_level=True,
        ),
        format="{message}",
        level=log_level,
        backtrace=True,
        diagnose=True,
    )



# Rich’s Table class offers a variety of ways to render tabular data to the terminal.
from rich.table import Table


# Rich provides the Live  class to to animate parts of the terminal
# It's handy to annimate tables that grow row by row
from rich.live import Live

# Rich provides the Align class to align rendable objects
from rich.align import Align

# Rich can display continuously updated information regarding the progress of long running tasks / file copies etc. The information displayed is configurable, the default will display a description of the ‘task’, a progress bar, percentage complete, and estimated time remaining.
from rich.progress import Progress, TaskID

# Rich has a Text class you can use to mark up strings with color and style attributes.
from rich.text import Text


from rich.traceback import Traceback

# For configuring
from rich.traceback import install
# Install the Rich Traceback handler with custom options
install(
    show_locals=True,  # Show local variables in the traceback
    locals_max_length=10, locals_max_string=80, locals_hide_dunder=True, locals_hide_sunder=False,
    indent_guides=True,
    suppress=[__name__],
    # suppress=[your_module],  # Suppress tracebacks from specific modules
    #max_frames=3,  # Limit the number of frames shown
    max_frames=5,  # Limit the number of frames shown
    #width=50,  # Set the width of the traceback display
    width=100,  # Set the width of the traceback display
    extra_lines=3,  # Show extra lines of code around the error
    theme="solarized-dark",  # Use a different color theme
    word_wrap=True,  # Enable word wrapping for long lines
)





def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Deanonymize GitHub noreply emails in gramphML files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        'input_dir',
        type=str,
        help='Directory containing gramphML files to process'
    )

    # Year range option (now optional)
    parser.add_argument(
        '--years',
        nargs='*',
        metavar=('START_YEAR', 'END_YEAR'),
        help='Range of years to process (inclusive). '
             'Specify exactly 2 years (start and end)'
    )

    # Releases list option (optional)
    parser.add_argument(
        '--releases',
        nargs='*',
        metavar='RELEASE',
        default=None,
        help='List of specific releases to process. '
             'If not specified, all releases are processed'
    )

    # Optional arguments
    parser.add_argument(
        '--output-dir',
        type=str,
        default='processed',
        help='Directory to save processed files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='count',
        default=0,
        help='Increase verbosity level (use -v, -vv, -vvv)'
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> Tuple[bool, str]:
    """Validate command line arguments."""
    # Validate input directory
    if not os.path.isdir(args.input_dir):
        return False, f"Input directory does not exist: {args.input_dir}"

    # Validate year range if specified
    if args.years is not None:
        if len(args.years) != 2:
            return False, "Must specify exactly 2 years (start and end)"
        try:
            start_year = int(args.years[0])
            end_year = int(args.years[1])
            if start_year > end_year:
                return False, "Start year must be <= end year"
            if start_year < 1970 or end_year > 2100:
                return False, "Years must be between 1970 and 2100"
        except ValueError:
            return False, "Years must be integers"

    return True, ""



def validate_args(args: argparse.Namespace) -> Tuple[bool, str]:
    """Validate command line arguments."""
    # Validate input directory
    if not os.path.isdir(args.input_dir):
        return False, f"Input directory does not exist: {args.input_dir}"

    # Validate year range if specified
    if args.years:
        try:
            start_year = int(args.years[0])
            end_year = int(args.years[1])
            if start_year > end_year:
                return False, "Start year must be <= end year"
            if start_year < 1970 or end_year > 2100:  # Reasonable bounds
                return False, "Years must be between 1970 and 2100"
        except ValueError:
            return False, "Years must be integers"

    return True, ""





def check_if_directory_is_a_git_repository(directory_path: str) -> bool:
    """
    Check if the specified directory is a Git repository using git command.

    Args:
        directory_path (str): Path to the directory to check

    Returns:
        bool: True if the directory is a Git repository, False otherwise

    Raises:
        ValueError: If the directory_path doesn't exist
        subprocess.CalledProcessError: If git command fails
    """
    path = Path(directory_path)

    if not path.exists():
        raise ValueError(f"Path does not exist: {directory_path}")
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")

    try:
        # Run git rev-parse --git-dir to check if it's a repo
        result = subprocess.run(
            ['git', '-C', str(path), 'rev-parse', '--git-dir'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


import subprocess
from pathlib import Path
from typing import List

import subprocess
from pathlib import Path
from typing import List


def get_git_tags(repo_path: str) -> List[str]:
    """
    Get all Git tags from a repository directory (typically used for releases).

    Args:
        repo_path: Path to the Git repository directory

    Returns:
        List of version tags (e.g., ['v1.0.0', 'v2.1.3'])

    Raises:
        ValueError: If path is not a valid Git repository
        RuntimeError: If git command fails
    """
    path = Path(repo_path)

    # Verify it's a Git repo
    if not (path / '.git').exists():
        raise ValueError(f"Not a Git repository: {repo_path}")

    try:
        # Get tags sorted by version (newest first)
        result = subprocess.run(
            ['git', '-C', str(path), 'tag', '-l', '--sort=-v:refname'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10  # Safety timeout
        )

        tags = result.stdout.splitlines()
        return [t for t in tags if t.strip()]  # Filter empty strings

    except subprocess.TimeoutExpired:
        raise RuntimeError("Git command timed out while fetching tags")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get Git tags: {e.stderr.strip()}")




def run_cmd_subprocess(
    cmd_args: List[str],
    shell: bool = False,
    check: bool = True,
    cwd: Optional[str] = None,
    verbose: bool = False
) -> Tuple[Optional[str], Optional[str], int]:
    """
    Run a command using subprocess with rich output formatting.

    Args:
        cmd_args: List of command arguments (e.g., ['git', 'log'])
        shell: Whether to use shell mode (avoid unless needed)
        check: Raise exception if command fails
        cwd: Working directory for command
        verbose: Print debug info

    Returns:
        Tuple of (stdout, stderr, returncode)
        Returns (None, None, -1) if KeyboardInterrupt occurs
    """
    if verbose:
        console.rule(f"Running command (shell={shell})")
        console.print(f"[bold cyan]$ {' '.join(shlex.quote(arg) for arg in cmd_args)}[/]")

    try:
        result = subprocess.run(
            cmd_args,
            shell=shell,
            check=check,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        if verbose:
            if result.stdout:
                console.print("[green]STDOUT:[/]", result.stdout)
            if result.stderr:
                console.print("[yellow]STDERR:[/]", result.stderr)

        return (result.stdout, result.stderr, result.returncode)

    except subprocess.CalledProcessError as e:
        console.print("[bold red]Command failed![/]")
        console.print(f"[red]Error ({e.returncode}):[/] {e.stderr.strip()}")
        if verbose:
            console.print_exception()
        raise  # Re-raise if check=True

    except KeyboardInterrupt:
        console.print("[yellow]Command interrupted by user[/]")
        return (None, None, -1)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/] {str(e)}")
        if verbose:
            console.print_exception()
        raise


def validate_and_parse_datetime(date_str: str) -> Optional[datetime]:
    """
    Validate the format '2025-04-02 06:01:34' and return a datetime object.
    Returns None if invalid.
    """
    # Regex to match exactly 'YYYY-MM-DD HH:MM:SS'
    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"

    if not re.match(pattern, date_str.strip()):
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def get_commit_dates_for_release(repo_path: str, release_branch: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Get first and last commit dates for a specific release branch.

    Args:
        repo_path: Path to Git repository
        release_branch: Name of release branch (e.g., 'release/1.0')

    Returns:
        Tuple of (first_commit_date, last_commit_date) as datetime objects

    Raises:
        ValueError: If invalid repository or branch doesn't exist
        RuntimeError: If Git commands fail
    """

    logger.info(f"get_commit_dates_for_release("+repo_path+", "+release_branch+")")

    path = Path(repo_path)

    # Validate repository
    if not (path / '.git').exists():
        raise ValueError(f"Not a Git repository: {repo_path}")

    # Checkout the release branch
    cmd = ['git', '-C', str(path), 'checkout', release_branch]
    logger.info(f"Checking out at {str(path)} release b"
                f""
                f"ranch {release_branch}")
    try:
        stdout, stderr, rc = run_cmd_subprocess(
            cmd,
            check=True
        )
        logger.info(f"\t git -C {str(path)}  checkout  {release_branch} [bold green]Success![/]")
    except subprocess.CalledProcessError:
        print("Failed to Git Checkout")




    # Getting the last commit

    cmd = f"git -C {str(path)} log -1 --format=\"%cd\" --date=format:'%Y-%m-%d %H:%M:%S'"

    logger.info(f"Getting last commit using [ $ {cmd}]")

    try:
        stdout, stderr, rc = run_cmd_subprocess(
            cmd,
            check=True,
            shell=True,
        )
        logger.info(f"\t {cmd} [bold green]Success![/]")
        logger.info(f"\t Extracting the date from [{stdout.strip()}]")

        date_str = stdout.strip()

        # Validate format
        last_commit_date_time = validate_and_parse_datetime(date_str)

        if last_commit_date_time:
            logger.info(f"Valid last commit datetime: {last_commit_date_time} (Type: {type(last_commit_date_time)})")
        else:
            logger.info("Invalid last commit datetime format!")


        logger.success(f"Valid commit date: {date_str}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed (exit {e.returncode}): {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("Git not installed or command not found!")
        sys.exit(1)
    except Exception as e:  # Catch-all for other errors
        console.print(f"[bold yellow]{e} occurred:[/bold yellow]", style="bold red")
        # Print formatted traceback using Rich
        console.print(Traceback(), style="bold red")
        console.print("-" * 40)  # Separator for clarity
        sys.exit(1)

    # First commit (oldest)
    cmd = f"git -C {str(path)} rev-list --max-parents=0 HEAD --format=\"%cd\" --date=format:'%Y-%m-%d %H:%M:%S' | tail -1"

    logger.info(f"Getting the first commit (oldest) using [ $ {cmd}]")

    try:
        stdout, stderr, rc = run_cmd_subprocess(
            cmd,
            check=True,
            shell=True,
        )
        logger.info(f"\t {cmd} [bold green]Success![/]")
        logger.info(f"\t Extracting the date from [{stdout.strip()}]")

        date_str = stdout.strip()

        # Validate format
        first_commit_date_time = validate_and_parse_datetime(date_str)

        if first_commit_date_time:
            logger.info(f"Valid first commit datetime: {first_commit_date_time} (Type: {type(first_commit_date_time)})")
        else:
            logger.info("Invalid first commit (oldest) datetime format!")

        logger.success(f"Valid commit date: {date_str}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed (exit {e.returncode}): {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("Git not installed or command not found!")
        sys.exit(1)
    except Exception as e:  # Catch-all for other errors
        console.print(f"[bold yellow]{e} occurred:[/bold yellow]", style="bold red")
        # Print formatted traceback using Rich
        console.print(Traceback(), style="bold red")
        console.print("-" * 40)  # Separator for clarity
        sys.exit(1)


    return (first_commit_date_time, last_commit_date_time)



def print_commit_dates(repo_path: str, release_branch: str):
    """Print commit dates with rich formatting"""


    logger.info(f"print_commit_dates({repo_path},{release_branch})")

    try:
        first_date, last_date = get_commit_dates_for_release(repo_path, release_branch)

        table = Table(title=f"Commit Timeline for {release_branch}", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Date", style="magenta")
        table.add_column("ISO Format", style="green")

        table.add_row("First Commit",
                      first_date.strftime('%b %d, %Y'),
                      first_date.isoformat())

        table.add_row("Last Commit",
                      last_date.strftime('%b %d, %Y'),
                      last_date.isoformat())

        table.add_row("Duration",
                      f"{(last_date - first_date).days} days",
                      f"{(last_date - first_date).days} days")

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}", style="bold red")

def get_release_branches(repo_path: str) -> List[str]:
    """
    Get all release branches from a Git repository.

    Args:
        repo_path: Path to the Git repository directory

    Returns:
        List of release branches (e.g., ['release/1.0', 'release/2.1'])

    Raises:
        ValueError: If path is not a valid Git repository
        RuntimeError: If git command fails
    """
    path = Path(repo_path)

    if not (path / '.git').exists():
        raise ValueError(f"Not a Git repository: {repo_path}")

    try:
        # Get all remote branches
        result = subprocess.run(
            ['git', '-C', str(path), 'branch', '-r', '--list',],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        branches = result.stdout.splitlines()

        # Clean branch names and filter
        cleaned = []
        for branch in branches:
            branch = branch.strip()
            if branch and not branch.endswith('HEAD'):
                # Remove 'origin/' prefix if present
                if branch.startswith('origin/'):
                    branch = branch[7:]
                cleaned.append(branch)

        return cleaned

    except subprocess.TimeoutExpired:
        raise RuntimeError("Git command timed out while fetching branches")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get release branches: {e.stderr.strip()}")

def main():
    args = parse_args()


    setup_logging(verbose=args.verbose)

    # Test logging
    #logger.debug("Debug message - visible with -vv")
    #logger.info("Info message - visible with -v")
    #logger.warning("Warning message - always visible")
    #logger.error("Error message - always visible")


    # Validate arguments
    is_valid, validation_msg = validate_args(args)
    if not is_valid:
        logger.error(validation_msg)
        sys.exit(1)


    try:


        logger.info(f"args={args}")

        if check_if_directory_is_a_git_repository(args.input_dir):
            console.print("\t 🏀 Its a git directory 😀")
        else:
            logger.error("Not a git repository")
            sys.exit()

        if not args.releases:

            # Get version tags
            tags = get_git_tags(args.input_dir)
            #print("Version Tags:")
            #for tag in tags:
            #    print(f"- {tag}")

            # Get release branches
            release_branches = get_release_branches(args.input_dir)
            print("\nGetting the release branches:")

            console.print("\t 🏀 Got a list of branches (release branches?) 😀")
            console.print(f"\t release_branches = {release_branches}")


            "Removes the agl/ prefix"
            cleaned_list = [item.replace('agl/', '') for item in release_branches]
            release_branches = cleaned_list

            if args.verbose >= 2:
                console.print(f"\t Cleaned release_branches = {release_branches}")

            "Removes the sandbox release branches"
            cleaned_list = [item for item in release_branches if not item.startswith('sandbox/')]
            release_branches = cleaned_list

            if args.verbose >= 2:
                console.print(f"\t Cleaned release_branches = {release_branches}")



            "Removes the m/icefish"
            cleaned_list = [item for item in release_branches if not item.startswith('m/')]
            release_branches = cleaned_list

            if args.verbose >= 2:
                console.print(f"\t Cleaned release_branches = {release_branches}")


            console.print("\n\t 🏀 Got a clean list of branches (release branches?) 😀")
            console.print(f"\t release_branches = {release_branches}")

            for release in release_branches:
                print_commit_dates(args.input_dir, release)

    except Exception as e:
        # Print the exception traceback using Rich
        console.print(f"[bold yellow]{e} occurred:[/bold yellow]", style="bold red")
        # Print formatted traceback using Rich
        console.print(Traceback(), style="bold red")
        console.print("-" * 40)  # Separator for clarity
        sys.exit(1)


if __name__ == "__main__":
    main()