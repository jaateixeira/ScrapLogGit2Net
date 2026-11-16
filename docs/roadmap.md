# Roadmap: planned next

Features planned next, in this order. Each one changes who the nodes are or how ties are counted, so each starts with its design questions, which are answered before any code is written. Each ships as an option with the current behaviour as the default, is recorded in the output metadata (`scraplog_parameters`), and is tested against a hand-computed network.

The first two change who the nodes are and affect every analysis, which is why they come first.

## 1. Identity merging — done

Implemented as `--mailmap FILE` (README, Q10; [scrapLog page](tools/scrapLog.md)). Decisions:
- Git's `.mailmap` format and matching rules (checked against `git check-mailmap`).
- No automatic merging: `<output>.identities.csv` lists every identity, its mapping and possible duplicates (same name with other e-mails; e-mails differing only in case).
- The mapped e-mail is the node and gives the affiliation.
- `-fe` removes a commit if its original or its mapped e-mail is listed.

## 2. Bot detection and exclusion

**What.** Leave out accounts that are not people: `dependabot[bot]`, renovate, `*[bot]@users.noreply.github.com`, CI accounts.

**Why.** Bots touch many files and become hubs, inflating degree and centrality.

**Design questions.**
- Detection: a known list shipped with the tool, patterns, a user file, or all three.
- Exclude by default, or only with an option.
- Write the excluded accounts and their commit counts to a file next to the output, so reviewers can check them.

## 3. `Co-authored-by` trailers

**What.** Credit the co-authors named in a commit message's `Co-authored-by:` trailers, not only the commit's author.

**Why.** Pair and mob programming leave co-authors only in the message, so these collaborations are missing now.

**Design questions.**
- The input format must include the message trailers. Today's format (`git log --pretty=format:"==%an;%ae;%ad==" --name-only`) has no message. A new format is needed, and the old one must keep working.
- Does a co-author count as having changed every file in the commit? Are the author and co-authors linked to each other directly?
- How it combines with identity merging (item 1).

## 4. Relational-event export (REM / DyNAM)

**What.** A CSV with one row per time-stamped co-edit (`sender, receiver, time, file`), ready for relational event models (`rem`, `goldfish` in R).

**Why.** These are the models the tool's output is meant for. The data already exists in the temporal network, before the files are dropped.

**Design questions.**
- Undirected ties as two rows or one; which developer is the sender (the one who commits later?).
- One row per file, or per commit (files as a list or a count).
- Time format (the log's offset, UTC, or seconds since the epoch).

## 5. Time-sliced snapshots

**What.** One network per period (month, quarter, year or release tag), for longitudinal SNA (ERGM over time, SAOM/RSiena).

**Why.** Longitudinal models need a series of networks over the same set of actors.

**Design questions.**
- Period boundaries: calendar periods (in UTC?) or release tags.
- The same node set in every slice (as RSiena needs), or only active developers.
- Ties per slice only, or cumulative.
- File names and format (one GraphML per slice, or one file with all slices).

## 6. Lines-of-code weights

**What.** Weight ties by lines changed (from `git log --numstat`) instead of the number of co-edits. The network types `inter_individual_weighted_LOC_temporal` and `inter_individual_graph_weighted_SUM_LOC` exist as options but are not exported.

**Why.** A one-line fix and a 2,000-line rewrite count the same now.

**Design questions.**
- The input format must include `--numstat`, as for item 3. Binary files (`-` in numstat) and renames must be handled deliberately.
- Which lines count for a tie: the later developer's, the sum of both, or the smaller of the two.
- Added and deleted lines together or separately.

## Also planned

The developer–file (bipartite), file-dependency and "developer_sequential" networks: see [planned-network-definitions.md](planned-network-definitions.md).
