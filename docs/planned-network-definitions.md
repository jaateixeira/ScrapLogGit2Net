# Planned network definitions

Unit tests in `tests/unit/test_extract_temporal_network_from_parsed_change_log_entries.py` describe ways of building networks that ScrapLogGit2Net does not offer yet (six at first; the co-edit window and the minimum number of co-edits are now implemented, see below, so three remain). They are skipped (`pytest -rs` lists them) and kept as specifications. Each one is a new edge definition, so it would change research results: none will be added without a decision on the open questions below, and the current networks stay the default.

## What scrapLog does now

`extract_temporal_network_from_parsed_change_log_entries` (in `scraplog/networks/temporal.py`) goes through the commits in time order. When a developer changes a file that other developers changed before, at any earlier time, it adds an edge between the developer and each of them, stamped with the commit's time. By default there is no time window and no minimum number of co-edits (see below), and the only nodes are developers. The weighted and unweighted networks are derived from this one (see the README).

The planned tests call the same function with keyword arguments it does not have (`network_type`, `relationship_window`, `min_interactions`), and expect a sequence of snapshot graphs.

## Implemented: the co-edit window (`--coedit-window`)

Decided and implemented (the two window tests are replaced by `tests/unit/test_coedit_window.py`):

- With `--coedit-window w` (e.g. `30d`, `12h`, `90m`, `3600s`), a developer who commits a file is linked to another developer only if that developer's **latest** change to the file is at most *w* earlier (boundary included). The edge has the time of the later commit. Offsets are compared as instants.
- Without the option (the default), there is no limit and the networks are exactly as before.
- Developers with no co-edit inside a window are not nodes, as always (README, Q7).
- It applies to all three network types (the weighted and unweighted networks are derived from the temporal one), and it is recorded in each file's `scraplog_parameters`.

This answers open questions 1, 2 and 7 for the window.

## Implemented: a minimum number of co-edits (`--min-coedits`)

Decided and implemented (the planned `min_interactions` test is replaced by `tests/unit/test_min_coedits.py`):

- With `--min-coedits N`, only developer pairs with at least *N* time-stamped co-edits (their weight in the weighted network) are kept. Pairs below the minimum are removed with all their co-edits, and developers left without co-edits are not nodes. Kept pairs keep every co-edit, so their weight and first and last times are unchanged.
- The count is taken after `--coedit-window`: only co-edits inside the window count.
- Default 1: every pair, as before. It applies to all three network types and is recorded in `scraplog_parameters`.

This answers open question 3.

`--max-coedits N` is the upper bound: pairs with more than *N* co-edits (also counted after the window) are removed the same way, e.g. to leave out bot accounts or very heavy pairs. No upper limit by default; a maximum below `--min-coedits` stops with an error.

## The planned definitions

| Test | Definition | What the test expects |
|---|---|---|
| `test_developer_file_bipartite_network` | `network_type="developer_file"`: a bipartite network of developers (`dev_<e-mail>`) and files (`file_<path>`), an edge when a developer changes a file. | Alice changes one file, Bob another: 2 edges. |
| `test_multiple_files_same_commit` | `network_type="file_dependency"`: files are nodes, linked when they change in the same commit. | One commit with 3 files: 3 edges (every pair). |
| `test_with_fixture_different_networks` | All of the above plus `network_type="developer_sequential"`. | Each call returns a network (no further checks). |

## Open questions

1. **Window.** Decided, see above.
2. **Nodes without edges.** Decided for the window: they are left out (README, Q7). Still open for the other definitions.
3. **`min_interactions`.** Decided, see above (`--min-coedits`).
4. **`developer_sequential`.** Not specified by any test: what makes two developers "sequential"?
5. **`file_dependency`.** Are renamed and deleted files, and very large commits (e.g. mass reformatting), treated specially?
6. **Output.** The tests expect snapshot graphs, while the current function returns one multigraph with a `time` attribute per edge. Which form, and how is each written to GraphML and the edge-list CSV?
7. **Interface.** The window and the minimum are options (`--coedit-window`, `--min-coedits`). Still open for the other definitions: new `-t` network types, or options?
