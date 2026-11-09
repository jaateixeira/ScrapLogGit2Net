#!/usr/bin/env python3
"""
solo_contributors.py
────────────────────
For a ScrapLogGit2Net raw git log, counts per study period how many
developers touched ONLY files that no one else touched (i.e. they would
be invisible in a co-editing network).

Also lists every solo-edited file with its sole developer, and can export
results to CSV.

Input log format:
    ==Name;email;timestamp==
    path/to/file1
    path/to/file2
    ==Name2;email2;timestamp==
    ...

Usage:
    # summary counts only
    python solo_contributors.py --log pytorch.log --project PyTorch

    # summary + full Developer – File listing
    python solo_contributors.py --log pytorch.log --project PyTorch --list-files

    # also write CSVs alongside the log file
    python solo_contributors.py --log pytorch.log --project PyTorch --list-files --csv
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

# ── Period boundaries ─────────────────────────────────────────────────────────
PERIODS = {
    "pre":     (datetime(2019,  9,  1, tzinfo=timezone.utc),
                datetime(2022,  8, 31, 23, 59, 59, tzinfo=timezone.utc)),
    "washout": (datetime(2022,  9,  1, tzinfo=timezone.utc),
                datetime(2023,  1, 31, 23, 59, 59, tzinfo=timezone.utc)),
    "post":    (datetime(2023,  2,  1, tzinfo=timezone.utc),
                datetime(2026,  1, 31, 23, 59, 59, tzinfo=timezone.utc)),
}

COMMIT_RE = re.compile(r'^==(.+?);(.+?);(.+?)==\s*$')


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_timestamp(ts_str: str) -> datetime | None:
    try:
        return parsedate_to_datetime(ts_str.strip())
    except Exception:
        pass
    for fmt in ("%a %b %d %H:%M:%S %Y %z", "%Y-%m-%d %H:%M:%S %z"):
        try:
            return datetime.strptime(ts_str.strip(), fmt)
        except ValueError:
            pass
    return None


def assign_period(dt: datetime) -> str | None:
    if dt is None:
        return None
    for name, (start, end) in PERIODS.items():
        if start <= dt <= end:
            return name
    return None


def parse_log(path: str, by_email: bool = False) -> list:
    """
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
                if current_author and current_files:
                    commits.append((current_author, current_period, current_files))
                name, email, ts_str = m.group(1), m.group(2), m.group(3)
                dt = parse_timestamp(ts_str)
                current_period = assign_period(dt)
                current_author = (email.lower() if by_email
                                  else f"{name} <{email.lower()}>")
                current_files = []
            elif line.strip() and current_author is not None:
                current_files.append(line.strip())

        if current_author and current_files:
            commits.append((current_author, current_period, current_files))

    return commits


# ── Analysis ──────────────────────────────────────────────────────────────────

def build_period_data(commits: list, period: str) -> dict:
    """
    Returns a dict with all derived data for one period:
      file_authors   : file  → set of authors
      author_files   : author → set of files
      co_edited      : set of files touched by >1 author
      solo_files     : set of files touched by exactly 1 author
      solo_only_devs : set of authors whose files are ALL solo-edited
      solo_file_dev  : list of (author, file) sorted by author then file
    """
    period_commits = [(a, fs) for a, p, fs in commits if p == period]

    file_authors: dict[str, set] = defaultdict(set)
    author_files: dict[str, set] = defaultdict(set)

    for author, files in period_commits:
        for f in files:
            file_authors[f].add(author)
            author_files[author].add(f)

    co_edited   = {f for f, devs in file_authors.items() if len(devs) > 1}
    solo_files  = {f for f, devs in file_authors.items() if len(devs) == 1}

    solo_only_devs = {a for a, files in author_files.items()
                      if files.isdisjoint(co_edited)}

    # (author, file) pairs where file is solo-edited
    solo_file_dev = sorted(
        ((next(iter(file_authors[f])), f) for f in solo_files),
        key=lambda x: (x[0].lower(), x[1])
    )

    return {
        "file_authors":   file_authors,
        "author_files":   author_files,
        "co_edited":      co_edited,
        "solo_files":     solo_files,
        "solo_only_devs": solo_only_devs,
        "solo_file_dev":  solo_file_dev,
    }


def print_summary(project: str, results: dict) -> None:
    print(f"\n{'='*62}")
    print(f"  Project: {project}")
    print(f"{'='*62}")

    for period in ("pre", "washout", "post"):
        d = results[period]
        if d is None:
            print(f"\n  [{period:8s}]  no commits in window")
            continue

        n_total  = len(d["author_files"])
        n_solo   = len(d["solo_only_devs"])
        n_collab = n_total - n_solo
        pct_solo = 100 * n_solo  / n_total if n_total else 0
        pct_co   = 100 * n_collab / n_total if n_total else 0

        n_files_total = len(d["file_authors"])
        n_files_co    = len(d["co_edited"])
        n_files_solo  = len(d["solo_files"])
        pct_fc = 100 * n_files_co   / n_files_total if n_files_total else 0
        pct_fs = 100 * n_files_solo / n_files_total if n_files_total else 0

        start, end = PERIODS[period]
        print(f"\n  [{period:8s}]  {start.date()} – {end.date()}")
        print(f"  {'─'*52}")
        print(f"  Developers total           : {n_total:>6}")
        print(f"  ├─ collaborative (visible) : {n_collab:>6}  ({pct_co:5.1f}%)")
        print(f"  └─ solo-only  (invisible)  : {n_solo:>6}  ({pct_solo:5.1f}%)")
        print(f"  Files total                : {n_files_total:>6}")
        print(f"  ├─ co-edited               : {n_files_co:>6}  ({pct_fc:5.1f}%)")
        print(f"  └─ solo-edited             : {n_files_solo:>6}  ({pct_fs:5.1f}%)")
    print()


def print_developer_listing(results: dict) -> None:
    for period in ("pre", "washout", "post"):
        d = results[period]
        if d is None or not d["solo_only_devs"]:
            continue
        start, end = PERIODS[period]
        devs = sorted(d["solo_only_devs"], key=str.lower)
        print(f"\n  Solo-only developers [{period}]  "
              f"{start.date()} \u2013 {end.date()}  ({len(devs)} developers)")
        print(f"  {chr(8212)*52}")
        for dev in devs:
            print(f"  {dev}")
    print()


def print_file_listing(results: dict) -> None:
    for period in ("pre", "washout", "post"):
        d = results[period]
        if d is None or not d["solo_file_dev"]:
            continue

        start, end = PERIODS[period]
        print(f"\n  Solo-edited files [{period}]  "
              f"{start.date()} – {end.date()}")
        print(f"  {'─'*70}")
        print(f"  {'Developer':<45}  File")
        print(f"  {'─'*70}")

        current_dev = None
        for dev, filepath in d["solo_file_dev"]:
            if dev != current_dev:
                # blank line between developers for readability
                if current_dev is not None:
                    print()
                current_dev = dev
            # truncate long developer names
            dev_display = dev if len(dev) <= 44 else dev[:41] + "..."
            print(f"  {dev_display:<45}  {filepath}")
    print()


# ── CSV export ────────────────────────────────────────────────────────────────

def write_csv(log_path: str, project: str, results: dict) -> None:
    base = Path(log_path).stem
    summary_path = Path(log_path).parent / f"{base}_solo_summary.csv"
    detail_path  = Path(log_path).parent / f"{base}_solo_files.csv"

    # summary CSV
    with open(summary_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["project", "period", "period_start", "period_end",
                    "n_developers", "n_collaborative", "n_solo_only",
                    "pct_solo_only", "n_files", "n_co_edited", "n_solo_edited",
                    "pct_solo_files"])
        for period in ("pre", "washout", "post"):
            d = results[period]
            start, end = PERIODS[period]
            if d is None:
                w.writerow([project, period, start.date(), end.date()] +
                           [""] * 8)
                continue
            n_total  = len(d["author_files"])
            n_solo   = len(d["solo_only_devs"])
            n_collab = n_total - n_solo
            n_ft     = len(d["file_authors"])
            n_fc     = len(d["co_edited"])
            n_fs     = len(d["solo_files"])
            w.writerow([
                project, period, start.date(), end.date(),
                n_total, n_collab, n_solo,
                round(100 * n_solo / n_total, 2) if n_total else 0,
                n_ft, n_fc, n_fs,
                round(100 * n_fs / n_ft, 2) if n_ft else 0,
            ])
    print(f"  Summary CSV  → {summary_path}")

    # detail CSV: developer – file for all solo-edited files
    with open(detail_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["project", "period", "developer", "file"])
        for period in ("pre", "washout", "post"):
            d = results[period]
            if d is None:
                continue
            for dev, filepath in d["solo_file_dev"]:
                w.writerow([project, period, dev, filepath])
    print(f"  Detail CSV   → {detail_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log",        required=True,
                        help="Path to ScrapLogGit2Net raw log file")
    parser.add_argument("--project",    default="",
                        help="Project label (e.g. PyTorch)")
    parser.add_argument("--by-email",   action="store_true",
                        help="Identify authors by email only")
    parser.add_argument("--list-files", action="store_true",
                        help="Print full Developer – File listing")
    parser.add_argument("--csv",        action="store_true",
                        help="Write summary and detail CSVs alongside the log")
    args = parser.parse_args()

    commits = parse_log(args.log, by_email=args.by_email)
    if not commits:
        print(f"ERROR: no commits parsed from {args.log}", file=sys.stderr)
        sys.exit(1)

    project = args.project or Path(args.log).stem

    results = {}
    for period in ("pre", "washout", "post"):
        has_data = any(p == period for _, p, _ in commits)
        results[period] = build_period_data(commits, period) if has_data else None

    print_summary(project, results)

    if args.list_developers:
        print_developer_listing(results)

    if args.list_files:
        print_file_listing(results)

    if args.csv:
        write_csv(args.log, project, results)


if __name__ == "__main__":
    main()
