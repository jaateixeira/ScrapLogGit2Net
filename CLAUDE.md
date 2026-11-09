# ScrapLogGit2Net

Extracts collaboration networks from `git log` data (who works with whom, via shared files/commits/time windows) for empirical software engineering and OSS research. Output feeds social network analysis (ERGM, REM/DyNAM, QAP) in R/Python.

## Working rules (keep token use low)
- Read only the files needed. Use grep/glob first; never dump whole repos, logs or large CSVs into context.
- Never `cat` data files. Use `head -n 20`, `wc -l`, or `pandas.read_csv(..., nrows=20)`.
- Prefer small, targeted edits over rewriting files. No unrequested refactors.
- Keep replies short: what changed, how verified, next step. No recap of steps.
- Delegate wide searches ("where is X used?") to a cheap subagent (Haiku/Explore).

## Correctness first (research code: wrong networks = wrong papers)
- Parse git with machine-readable formats: `git log --numstat --date=iso-strict --pretty=format:<explicit delimiter format>`. Never parse human-readable output.
- Author identity: normalize name/email (aliases, `noreply` GitHub addresses, bots) in ONE place. Exclude bots explicitly and log what was excluded.
- Handle merge commits, renames, binary files (`-` in numstat), empty commits, and timezone offsets deliberately; document each choice.
- Edge definition (co-edit file, co-commit window, etc.) must be a named, parameterized function, not hard-coded.
- Be deterministic: sorted outputs, fixed seeds, no reliance on dict ordering. Same input must give byte-identical output.
- Record parameters and tool version alongside every output (metadata file or header).

## Verify before saying "done"
- Run the tests (command below). Add a test for any bug fixed.
- Test on a tiny fixture repo (a handful of commits, 3 authors, known expected edges) and compare to a hand-computed network.
- Sanity-check output: node count = distinct normalized authors, no self-loops unless intended, edge weights >= 1, no NaN.
- State what was NOT verified.

## Commands
- Install: `pip install -e ".[test]"` (dependencies are declared in both `pyproject.toml` and `requirements.txt`; keep them in sync)
- Test: `python -m pytest -q` (unit tests in `tests/unit/`)
- Acceptance tests (run from repo root; need `xmllint`): `bash tests/acceptance-test-scripts/testScrapLog.sh`, `testScrapLogTemporalNetworks.sh`, `ExtensionFiltering/test_extension_filtering.sh`
- Lint/format: none configured
- Make input: `git log --pretty=format:"==%an;%ae;%ad==" --name-only > <name>.IN`
- Run: `./scrapLog.py -r <name>.IN [-t <network type>] [-o <out>.graphML]`

## Conventions
- Python 3.12+, type hints, small pure functions; I/O at the edges.
- pandas/networkx for graphs. Export GraphML and edge-list CSV (source, target, weight, first_ts, last_ts).
- Large repos: stream the git log, don't load it all into memory.
- Never commit data dumps, tokens, or cloned repos. Keep these in `.gitignore`.

## Don't
- Don't change edge-definition or identity-merging semantics without asking: it changes research results.
- Don't add dependencies without asking.
- Don't push, tag, or rewrite git history.

## Model use
- Default: Sonnet for implementation, tests, debugging.
- Haiku for subagents: file search, log summarising, boilerplate.
- Escalate to Opus (as advisor) only for: edge-definition design, identity-resolution logic, performance architecture, or when stuck after two failed attempts.
