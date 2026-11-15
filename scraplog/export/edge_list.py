"""
Edge-list CSV export.

scrapLog writes, next to every network file, a CSV with one row per pair of
developers who co-edited at least one file:

    source, target   the two developers' e-mail addresses, source < target
    weight           number of distinct time-stamped co-edits of the pair (the
                     weight of the weighted network)
    first_ts         earliest co-edit, as in the log (ISO 8601 with the author's
                     UTC offset, as in the temporal network)
    last_ts          latest co-edit, as in the log
    first_ts_utc     first_ts converted to UTC
    last_ts_utc      last_ts converted to UTC

Earliest and latest are decided by the instant, not by the text, so offsets
are compared correctly. Rows are sorted by (source, target), so the same input
gives a byte-identical file. All three network types come from the same
time-stamped co-edits, so the rows are the same for every type; for the
unweighted and weighted networks they are limited to the edges of the
exported network.
"""

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

import networkx as nx

COLUMNS = ("source", "target", "weight", "first_ts", "last_ts", "first_ts_utc", "last_ts_utc")

Row = Tuple[str, str, int, str, str, str, str]


def edge_list_path(network_file: Union[str, Path]) -> Path:
    """t.NetworkFile.graphML -> t.NetworkFile.edges.csv; t.temporal.graphml.zip -> t.temporal.edges.csv."""
    path = Path(network_file)
    name = path.name
    for suffix in (".zip", ".graphml"):
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]
    return path.with_name(name + ".edges.csv")


def _instant(timestamp: str) -> datetime:
    moment = datetime.fromisoformat(timestamp)
    if moment.tzinfo is None:
        raise ValueError(f"Time stamp without UTC offset: {timestamp!r}")
    return moment


def _utc(timestamp: str) -> str:
    return _instant(timestamp).astimezone(timezone.utc).isoformat()


def edge_list_rows(coedits: Iterable[Tuple[str, str, str]],
                   network: Optional[nx.Graph] = None) -> List[Row]:
    """Rows of the edge list.

    coedits: (developer, developer, time stamp) for each time-stamped co-edit, e.g.
        temporal_graph.temporal_edges(data="time"). Repeated triples are counted once.
    network: if given, only its edges are listed, and each must have co-edits.
    """
    times: Dict[Tuple[str, str], set] = {}
    for u, v, timestamp in coedits:
        if u == v:
            continue
        pair = (min(str(u), str(v)), max(str(u), str(v)))
        times.setdefault(pair, set()).add(str(timestamp))

    if network is not None:
        pairs = {(min(str(u), str(v)), max(str(u), str(v))) for u, v in network.edges()}
        missing = sorted(pairs - times.keys())
        if missing:
            raise ValueError(f"{len(missing)} edge(s) of the network have no time-stamped co-edit, e.g. {missing[0]}")
    else:
        pairs = set(times)

    rows: List[Row] = []
    for source, target in sorted(pairs):
        # by instant; equal instants written with different offsets are ordered by their text
        ordered = sorted(times[(source, target)], key=lambda ts: (_instant(ts), ts))
        first, last = ordered[0], ordered[-1]
        rows.append((source, target, len(ordered), first, last, _utc(first), _utc(last)))
    return rows


def write_edge_list_csv(path: Union[str, Path], rows: Iterable[Row]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(rows)
