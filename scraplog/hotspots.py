"""
Ignoring hotspot files: files changed by very many developers.

A file changed by many developers (a build file, a changelog, a registry of
components) links all of them, which can dominate a co-editing network. After
the log is parsed and before any network is built, scrapLog can leave such
files out:

    --ignore-top-hotspot-files K               the K files (0-20) changed by the most
                                               developers; ties broken by path
    --ignore-files-with-more-than-developers N files changed by more than N developers

A file's count is the number of distinct developers (e-mails) who changed it in
the log, after -fe, -ff and the extension filters. Both options can be used
together; a file is ignored if either selects it. The ignored files are removed
from every commit, so no network type and no edge-list row uses them. They are
printed and written to <output>.ignored-files.csv (see export_results).
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple, Union

from scraplog.core.models import ProcessingState
from scraplog.core.types import ChangeLogEntry

MAX_TOP_HOTSPOT_FILES = 20

# (file, number of developers who changed it, why it is ignored)
IgnoredFile = Tuple[str, int, str]


def developers_per_file(entries: Iterable[ChangeLogEntry]) -> Dict[str, int]:
    """Number of distinct developers (e-mails) who changed each file."""
    developers = defaultdict(set)
    for (email, _affiliation), files, _timestamp in entries:
        for file in files:
            developers[file].add(email)
    return {file: len(emails) for file, emails in developers.items()}


def select_hotspot_files(counts: Dict[str, int], top: int = 0,
                         max_developers: Optional[int] = None) -> List[IgnoredFile]:
    """The files to ignore, most developers first (ties by path).

    top: the `top` files with the most developers (ties broken by path, so exactly `top`
    files, or all files if there are fewer). max_developers: files with more developers.
    The reason is 'top', 'more_than_max' or 'top+more_than_max'.
    """
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    in_top = {file for file, _ in ranked[:top]}
    above_max = {file for file, n in ranked if max_developers is not None and n > max_developers}
    ignored = []
    for file, n in ranked:
        reasons = [name for name, chosen in (("top", file in in_top), ("more_than_max", file in above_max)) if chosen]
        if reasons:
            ignored.append((file, n, "+".join(reasons)))
    return ignored


def drop_files(entries: Iterable[ChangeLogEntry], files: Iterable[str]) -> List[ChangeLogEntry]:
    """The entries with the given files removed from each commit's file list."""
    dropped = set(files)
    return [(developer, [f for f in commit_files if f not in dropped], timestamp)
            for developer, commit_files, timestamp in entries]


def apply_hotspot_filter(state: ProcessingState) -> List[IgnoredFile]:
    """Remove the hotspot files chosen by the options from state.parsed_change_log_entries."""
    ignored = select_hotspot_files(developers_per_file(state.parsed_change_log_entries),
                                   state.ignore_top_hotspot_files, state.max_developers_per_file)
    state.parsed_change_log_entries = drop_files(state.parsed_change_log_entries, (f for f, _, _ in ignored))
    state.ignored_hotspot_files = ignored
    return ignored


def write_ignored_files_csv(path: Union[str, Path], ignored: Iterable[IgnoredFile],
                            metadata: Optional[Mapping[str, str]] = None) -> None:
    """file, developers, reason; after '# name: value' lines for the metadata, as in the edge list."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        for name, value in (metadata or {}).items():
            f.write(f"# {name}: {value}\n")
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(("file", "developers", "reason"))
        writer.writerows(ignored)
