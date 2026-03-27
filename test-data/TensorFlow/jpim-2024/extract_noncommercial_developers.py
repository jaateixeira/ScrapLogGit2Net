#!/usr/bin/env python3
"""
extract_noncommercial_developers.py
─────────────────────────────────────────────────────────────────────────────
Scans one or more ScrapLogGit2Net .IN git log files and extracts all
developers whose email domain matches a list of non-commercial organisations
(universities, research institutes, foundations).

For each matching developer it records:
  - All name strings observed across commits (some contributors use
    different display names over time)
  - Their email address (used as the unique identifier)
  - The inferred organisation (the matched keyword)
  - The email domain
  - The source file(s) in which they were found
  - The number of commits attributed to them in each source file

Output: a CSV file with one row per unique email address.

Usage:
    python3 extract_noncommercial_developers.py logs/*.IN
    python3 extract_noncommercial_developers.py -o results/noncommercial_devs.csv logs/*.IN
    python3 extract_noncommercial_developers.py --targets mit berkeley gatech logs/*.IN

Developed as part of the FOST4DLSNA research project.
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Default target organisations
# Keywords are matched against the full email domain (case-insensitive),
# so @csail.mit.edu matches "mit", @eecs.berkeley.edu matches "berkeley".
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_TARGETS = [
    "naver",       # Naver Corporation (South Korea) — significant ML research
    "mit",         # Massachusetts Institute of Technology
    "snu",         # Seoul National University
    "dfki",        # German Research Center for Artificial Intelligence
    "chromium",    # Chromium open-source project / The Chromium Authors
    "ispras",      # Ivannikov Institute for System Programming (Russia)
    "pku",         # Peking University
    "gatech",      # Georgia Institute of Technology
    "apache",      # Apache Software Foundation
    "kth",         # KTH Royal Institute of Technology (Sweden)
    "berkeley",    # University of California, Berkeley
]

# ─────────────────────────────────────────────────────────────────────────────
# Regex for == header lines
# Captures: name, email, timestamp
# Handles optional trailing whitespace / newline
# ─────────────────────────────────────────────────────────────────────────────
HEADER_RE = re.compile(
    r'^==(?P<name>.+?);(?P<email>.+?);(?P<timestamp>.+?)==\s*$'
)


def extract_domain(email: str) -> str | None:
    """Return the domain portion of an email address, lower-cased."""
    email = email.strip().lower()
    if '@' not in email:
        return None
    return email.split('@', 1)[1]


def match_target(domain: str, targets: list[str]) -> str | None:
    """
    Return the first target keyword found anywhere in the domain string,
    or None if no target matches.

    Matching anywhere in the domain (rather than only at second-level)
    correctly handles subdomains like csail.mit.edu → mit,
    eecs.berkeley.edu → berkeley, cc.gatech.edu → gatech.
    """
    for target in targets:
        if target in domain:
            return target
    return None


def parse_in_file(filepath: Path, targets: list[str], records: dict) -> int:
    """
    Parse a single .IN file and accumulate matching developer records.

    records is a dict keyed by email:
        {
            email: {
                "names":    set of display name strings seen,
                "org":      matched target keyword,
                "domain":   full email domain,
                "sources":  {filename: commit_count},
            }
        }

    Returns the number of matching commit-author lines found in this file.
    """
    matches_in_file = 0
    filename = filepath.name

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
            for line in fh:
                line = line.rstrip('\n')

                if not line.startswith('=='):
                    continue

                m = HEADER_RE.match(line)
                if not m:
                    # Malformed header — skip silently
                    continue

                name  = m.group('name').strip()
                email = m.group('email').strip().lower()

                domain = extract_domain(email)
                if not domain:
                    continue

                org = match_target(domain, targets)
                if not org:
                    continue

                # Accumulate record
                if email not in records:
                    records[email] = {
                        "names":   set(),
                        "org":     org,
                        "domain":  domain,
                        "sources": defaultdict(int),
                    }

                records[email]["names"].add(name)
                records[email]["sources"][filename] += 1
                matches_in_file += 1

    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}", file=sys.stderr)

    return matches_in_file


def write_csv(records: dict, output_path: Path, input_files: list[Path]) -> None:
    """
    Write the deduplicated developer records to a CSV file.

    Columns:
        email           — unique identifier (canonical email address)
        org             — matched target keyword (inferred organisation)
        domain          — full email domain
        names           — pipe-separated list of all display names observed
        total_commits   — total commit count across all source files
        files_found_in  — pipe-separated list of source .IN filenames
        commits_per_file — JSON-style breakdown: file:count|file:count
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Sort rows: first by org (groups universities together), then by email
    sorted_records = sorted(
        records.items(),
        key=lambda kv: (kv[1]["org"], kv[0])
    )

    fieldnames = [
        "email",
        "org",
        "domain",
        "names",
        "total_commits",
        "files_found_in",
        "commits_per_file",
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        for email, rec in sorted_records:
            total = sum(rec["sources"].values())
            files = sorted(rec["sources"].keys())
            per_file = " | ".join(
                f"{f}:{rec['sources'][f]}" for f in files
            )

            writer.writerow({
                "email":           email,
                "org":             rec["org"],
                "domain":          rec["domain"],
                "names":           " | ".join(sorted(rec["names"])),
                "total_commits":   total,
                "files_found_in":  " | ".join(files),
                "commits_per_file": per_file,
            })


def print_summary(records: dict, targets: list[str]) -> None:
    """Print a human-readable summary grouped by organisation."""
    from collections import Counter

    org_counts = Counter(rec["org"] for rec in records.values())

    print("\n" + "=" * 60)
    print("SUMMARY — non-commercial developers found")
    print("=" * 60)
    print(f"  Total unique developers : {len(records)}")
    print()
    print(f"  {'Organisation':<20} {'Unique devs':>12}  {'Total commits':>14}")
    print(f"  {'-'*20} {'-'*12}  {'-'*14}")

    for target in targets:
        count = org_counts.get(target, 0)
        if count == 0:
            continue
        dev_records = [r for r in records.values() if r["org"] == target]
        total_commits = sum(
            sum(r["sources"].values()) for r in dev_records
        )
        print(f"  {target:<20} {count:>12}  {total_commits:>14}")

    print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract non-commercial affiliated developers from "
            "ScrapLogGit2Net .IN git log files."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run over all 12 FOST4DLSNA log files
  python3 extract_noncommercial_developers.py logs/*.IN

  # Custom output path
  python3 extract_noncommercial_developers.py -o results/noncommercial_devs.csv logs/*.IN

  # Override the target list (adds to rather than replaces defaults)
  python3 extract_noncommercial_developers.py --targets nvidia amd logs/*.IN

  # Run over a single file for inspection
  python3 extract_noncommercial_developers.py logs/pytorch-full.IN
        """
    )

    parser.add_argument(
        'input_files',
        nargs='+',
        type=Path,
        metavar='FILE.IN',
        help='One or more ScrapLogGit2Net .IN git log files to scan'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('noncommercial_developers.csv'),
        metavar='OUTPUT.csv',
        help='Path for the output CSV file (default: noncommercial_developers.csv)'
    )
    parser.add_argument(
        '--targets',
        nargs='+',
        metavar='KEYWORD',
        default=None,
        help=(
            'Override the default target keyword list. '
            'Each keyword is matched anywhere in the email domain. '
            f'Default: {" ".join(DEFAULT_TARGETS)}'
        )
    )
    parser.add_argument(
        '--append-targets',
        nargs='+',
        metavar='KEYWORD',
        default=[],
        help='Add keywords to the default list without replacing it'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print progress for each input file'
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Resolve target list
    if args.targets:
        targets = [t.lower() for t in args.targets]
    else:
        targets = list(DEFAULT_TARGETS)
    if args.append_targets:
        targets += [t.lower() for t in args.append_targets]

    print(f"Target organisations : {', '.join(targets)}")
    print(f"Input files          : {len(args.input_files)}")
    print(f"Output CSV           : {args.output}")
    print()

    # Accumulate records across all input files
    # Key: canonical email  Value: record dict (see parse_in_file)
    records: dict = {}
    total_header_lines = 0

    for in_file in sorted(args.input_files):
        n = parse_in_file(in_file, targets, records)
        total_header_lines += n
        if args.verbose or n > 0:
            print(f"  {in_file.name:<45}  {n:>5} matching commit-author lines")

    print()
    print(f"Total matching commit-author lines : {total_header_lines}")
    print(f"Unique matching developers         : {len(records)}")

    if not records:
        print("\n[WARN] No matching developers found. Check your target keywords.")
        sys.exit(0)

    # Write CSV
    write_csv(records, args.output, args.input_files)
    print(f"\nCSV written to: {args.output}")

    # Print grouped summary
    print_summary(records, targets)


if __name__ == '__main__':
    main()
