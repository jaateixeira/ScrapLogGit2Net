# Planned network definitions (not implemented)

Six unit tests in `tests/unit/test_extract_temporal_network_from_parsed_change_log_entries.py` describe ways of building networks that ScrapLogGit2Net does not offer yet. They are skipped (`pytest -rs` lists them) and kept as specifications. Each one is a new edge definition, so it would change research results: none will be added without a decision on the open questions below, and the current networks stay the default.

## What scrapLog does now

`extract_temporal_network_from_parsed_change_log_entries` (in `scraplog/networks/temporal.py`) goes through the commits in time order. When a developer changes a file that other developers changed before, at any earlier time, it adds an edge between the developer and each of them, stamped with the commit's time. There is no time window, no minimum number of interactions, and the only nodes are developers. The weighted and unweighted networks are derived from this one (see the README).

The planned tests call the same function with keyword arguments it does not have (`network_type`, `relationship_window`, `min_interactions`), and expect a sequence of snapshot graphs.

## The planned definitions

| Test | Definition | What the test expects |
|---|---|---|
| `test_two_developers_creates_edge` | `network_type="developer_coediting"` with `relationship_window`: an edge only when two developers change the same file within the window. | Alice and Bob change `src/main.py` 30 minutes apart, window 1 hour: one edge, with `file` and `time` attributes; 2 nodes. |
| `test_two_developers_outside_window_no_edge` | The same, outside the window. | 2 hours apart, window 1 hour: no edge, but both developers are nodes. |
| `test_min_interactions_threshold` | `min_interactions`: an edge appears only after this many interactions. | Four alternating edits 5 minutes apart: edges with `min_interactions=2`, and at least as many with `1`. |
| `test_developer_file_bipartite_network` | `network_type="developer_file"`: a bipartite network of developers (`dev_<e-mail>`) and files (`file_<path>`), an edge when a developer changes a file. | Alice changes one file, Bob another: 2 edges. |
| `test_multiple_files_same_commit` | `network_type="file_dependency"`: files are nodes, linked when they change in the same commit. | One commit with 3 files: 3 edges (every pair). |
| `test_with_fixture_different_networks` | All of the above plus `network_type="developer_sequential"`. | Each call returns a network (no further checks). |

## Open questions

1. **Window.** Is the window measured from the earlier edit only (B within *w* after A), or both ways? Is the current definition the same as an infinite window?
2. **Nodes without edges.** The window test expects developers with no edge in the window to be nodes. The current networks leave them out on purpose (README, Q7).
3. **`min_interactions`.** Counted per pair over the whole history, or within the window? Does the edge appear at the *n*-th interaction (and what is its time), or is it dropped from the whole network?
4. **`developer_sequential`.** Not specified by any test: what makes two developers "sequential"?
5. **`file_dependency`.** Are renamed and deleted files, and very large commits (e.g. mass reformatting), treated specially?
6. **Output.** The tests expect snapshot graphs, while the current function returns one multigraph with a `time` attribute per edge. Which form, and how is each written to GraphML and the edge-list CSV?
7. **Interface.** New `-t` network types for `scrapLog.py`, or options such as `--window`?
