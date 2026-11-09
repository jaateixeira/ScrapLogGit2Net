# ScrapLogGit2Net

Extracts collaboration networks from `git log` data (who works with whom, via shared files/commits/time windows) for empirical software engineering and OSS research. Output feeds social network analysis (ERGM, REM/DyNAM, QAP) in R/Python.

This file is for any coding agent or LLM (Mistral, DeepSeek, Gemma, Qwen, Llama, or a hosted model). Rules are short and literal on purpose, so small local models can follow them.

## How to work
1. Read the task. If something is unclear, ask ONE short question before changing code.
2. Find the relevant code with `grep -rn "<name>" .` or `ls`. Do not read the whole repo.
3. Open only the files you need. For big files, read a line range, not everything.
4. Make ONE small change at a time. No unrequested refactors, renames or reformatting.
5. Run the tests (see Commands). Fix failures before moving on.
6. Reply briefly: what changed, which command you ran, the result, what was NOT verified.

## Keep context small (important for local models)
- Never print or `cat` data files, `.IN` files, GraphML, or full git logs. Use `head -n 20` or `wc -l`.
- Pipe long command output through `tail -n 30` or `grep`.
- Show diffs or the changed function only, not whole files, in your replies.
- If the context is getting long, summarise the state in 5 lines and continue from that.
- Prefer exact edits (replace this text with that text) over rewriting a whole file.

## Correctness first (research code: wrong networks = wrong papers)
- Parse git with machine-readable formats, e.g. the format in "Make input" below. Never parse human-readable output.
- Author identity: normalise name/email (aliases, `noreply` GitHub addresses, bots) in ONE place. Exclude bots explicitly and log what was excluded.
- Handle merge commits, renames, binary files (`-` in numstat), empty commits and timezone offsets deliberately. Write a comment for each choice.
- The edge definition (co-edit file, co-commit window, etc.) must be a named function with parameters, not hard-coded.
- Be deterministic: sort outputs, fix random seeds, do not depend on dict or set order. The same input must give byte-identical output.
- Write the parameters and tool version next to every output (metadata file or header).

## Verify before saying "done"
- Run all tests listed under Commands.
- When fixing a bug, add a test that fails before the fix and passes after.
- Test on a tiny fixture repo (a few commits, 3 authors, known expected edges) and compare with a hand-computed network.
- Sanity checks on output: node count = number of distinct normalised authors with at least one co-edit (developers who never co-edit are left out by design); no self-loops unless intended; edge weights >= 1; no NaN.
- Say clearly what you did not verify. Never claim a test passed unless you ran it.

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
- Large repos: stream the git log; do not load it all into memory.
- Never commit data dumps, tokens, or cloned repos. Keep them in `.gitignore`.

## Don't
- Don't change edge-definition or identity-merging behaviour without asking: it changes research results.
- Don't add dependencies without asking.
- Don't run `git push`, `git tag`, `git reset --hard`, `git rebase`, or anything that rewrites history.
- Don't invent function names, flags or file paths. Check with `grep` or `ls` first.
- Don't delete files or data without asking.

## Choosing a model (optional guidance for the human)
- Local via Ollama: pick a coding-tuned model that fits your RAM/VRAM. Examples: Qwen2.5-Coder, DeepSeek-Coder(-V2), Codestral or Mistral/Mistral-Nemo, Gemma. Check each model's licence and size on the Ollama library page.
- Context window: Ollama's default context is small. Raise it (`num_ctx`, e.g. 8192-16384, as far as memory allows) or the agent will silently forget the rules in this file.
- Use low temperature (0 to 0.2) for code edits, for reproducible results.
- Small models (up to about 8B): good for single-function edits, tests, docstrings, regex, shell one-liners. Give them one narrow task at a time.
- Larger models or a hosted API: use for edge-definition design, identity-resolution logic, performance design, or when stuck after two failed attempts.
- Always run the tests yourself. Do not trust any model's claim that code works.
