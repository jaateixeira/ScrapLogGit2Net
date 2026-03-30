#!/usr/bin/env python3
"""
solo_contributors.py
────────────────────
For a ScrapLogGit2Net raw git log, counts per study period how many
developers touched ONLY files that no one else touched (i.e. they would
be invisible in a co-editing network).

Input log format:
    ==Name;email;timestamp==
    path/to/file1
    path/to/file2
    ==Name2;email2;timestamp==
    ...

Usage:
    python solo_contributors.py --log pytorch.log --project PyTorch
    python solo_contributors.py --log pytorch.log --project PyTorch --by-email
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# ── Period boundaries ─────────────────────────────────────────────────────────
PERIODS = {
    "pre":      (datetime(2019,  9,  1, tzinfo=timezone.utc),
                 datetime(2022,  8, 31, 23, 59, 59, tzinfo=timezone.utc)),
    "washout":  (datetime(2022,  9,  1, tzinfo=timezone.utc),
                 datetime(2023,  1, 31, 23, 59, 59, tzinfo=timezone.utc)),
    "post":     (datetime(2023,  2,  1, tzinfo=timezone.utc),
                 datetime(2026,  1, 31, 23, 59, 59, tzinfo=timezone.utc)),
}

COMMIT_RE = re.compile(r'^==(.+?);(.+?);(.+?)==\s*$')


def parse_timestamp(ts_str: str) -> datetime | None:
    """Parse git log timestamp string to timezone-aware datetime."""
    try:
        return parsedate_to_datetime(ts_str.strip())
    except Exception:
        pass
    # fallback: try common git formats
    for fmt in ("%a %b %d %H:%M:%S %Y %z",
                "%Y-%m-%d %H:%M:%S %z"):
        try:
            return datetime.strptime(ts_str.strip(), fmt)
        except ValueError:
            pass
    return None


def assign_period(dt: datetime) -> str | None:
    """Return period name or None if outside all windows."""
    if dt is None:
        return None
    for name, (start, end) in PERIODS.items():
        if start <= dt <= end:
            return name
    return None


def parse_log(path: str, by_email: bool = False):
    """
    Parse the log file.
    Returns list of (author_id, period, files) tuples.
    author_id is email if by_email else 'Name <email>'.
    """
    commits = []
    current_author = None
    current_period = None
    current_files = []

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = COMMIT_RE.match(line)
            if m:
                # flush previous commit
                if current_author and current_files:
                    commits.append((current_author, current_period, current_files))
                name, email, ts_str = m.group(1), m.group(2), m.group(3)
                dt = parse_timestamp(ts_str)
                current_period = assign_period(dt)
                current_author = email.lower() if by_email else f"{name} <{email.lower()}>"
                current_files = []
            elif line.strip() and current_author is not None:
                current_files.append(line.strip())

        # flush last commit
        if current_author and current_files:
            commits.append((current_author, current_period, current_files))

    return commits


def analyse(commits: list, project: str) -> None:
    """
    For each period:
      - Build file → set(authors) mapping
      - A file is "co-edited" if len(authors) > 1
      - A developer is "solo-only" if ALL their files are NOT co-edited
      - Report counts and fraction
    """
    print(f"\n{'='*60}")
    print(f"  Project: {project}")
    print(f"{'='*60}")

    for period in ("pre", "washout", "post"):
        period_commits = [(a, fs) for a, p, fs in commits if p == period]

        if not period_commits:
            print(f"\n  [{period:8s}]  no commits in window")
            continue

        # file → set of authors
        file_authors: dict[str, set] = defaultdict(set)
        # author → set of files
        author_files: dict[str, set] = defaultdict(set)

        for author, files in period_commits:
            for f in files:
                file_authors[f].add(author)
                author_files[author].add(f)

        co_edited_files = {f for f, authors in file_authors.items()
                           if len(authors) > 1}

        all_authors     = set(author_files.keys())
        solo_only       = {a for a, files in author_files.items()
                           if files.isdisjoint(co_edited_files)}
        collab_authors  = all_authors - solo_only

        n_total   = len(all_authors)
        n_solo    = len(solo_only)
        n_collab  = len(collab_authors)
        pct_solo  = 100 * n_solo  / n_total if n_total else 0
        pct_co    = 100 * n_collab / n_total if n_total else 0

        n_files_total  = len(file_authors)
        n_files_co     = len(co_edited_files)
        n_files_solo   = n_files_total - n_files_co
        pct_files_co   = 100 * n_files_co   / n_files_total if n_files_total else 0
        pct_files_solo = 100 * n_files_solo / n_files_total if n_files_total else 0

        start, end = PERIODS[period]
        print(f"\n  [{period:8s}]  {start.date()} – {end.date()}")
        print(f"  {'─'*50}")
        print(f"  Developers total          : {n_total:>6}")
        print(f"  ├─ collaborative (visible): {n_collab:>6}  ({pct_co:5.1f}%)")
        print(f"  └─ solo-only  (invisible) : {n_solo:>6}  ({pct_solo:5.1f}%)")
        print(f"  Files total               : {n_files_total:>6}")
        print(f"  ├─ co-edited              : {n_files_co:>6}  ({pct_files_co:5.1f}%)")
        print(f"  └─ solo-edited            : {n_files_solo:>6}  ({pct_files_solo:5.1f}%)")

    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log",     required=True,
                        help="Path to ScrapLogGit2Net raw log file")
    parser.add_argument("--project", default="",
                        help="Project name for display (e.g. PyTorch)")
    parser.add_argument("--by-email", action="store_true",
                        help="Identify authors by email only (ignores name variants)")
    args = parser.parse_args()

    commits = parse_log(args.log, by_email=args.by_email)

    if not commits:
        print(f"ERROR: no commits parsed from {args.log}", file=sys.stderr)
        sys.exit(1)

    analyse(commits, project=args.project or args.log)


if __name__ == "__main__":
    main()
