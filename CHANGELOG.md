# Changelog

## Unreleased

No change to the networks: the same log gives the same GraphML as v1.1-borba.

### Fixes

- `scrapLog.py` writes the unweighted network once. It wrote the same file twice; the content is unchanged.
- **Repeatable figures.** The nofi and nofo visualizers color organizations that are not in the color map by name instead of at random, and the nofi visualizer's spring layout uses a fixed seed. The same input gives byte-identical PNG and PDF files. Organization colors differ from figures made with v1.1-borba.
- `deanonymize_github_users.py` creates its HTTP cache when processing starts, next to the output file, instead of in the current directory on import (even for `--help`). On a rate limit it waits until the reset time GitHub sends, at most 3 times, then stops with exit code 1, instead of sleeping one hour at a time without limit. Cached responses no longer expire after one hour, so a rerun reuses them; delete the cache file or use `--no-cache` to fetch fresh data.
- The reports, the visualizers and the transformer show their current names in usage lines, banners and help (they showed old names such as `formatAndReportGraphML`).
- No hard-coded `/home/apolinex` paths: `compile_all_git_logs_across_branches.sh` finds its log script next to itself, and the AGL study's `config.cfg` uses paths relative to the repository. `run_scrap_log-4_list_of_IN_files.sh` reads the `scrapLogpath` key it could never find before.
- Acceptance scripts call the nofi visualizer by its current name. The color map used by `test-nofo-viz.sh` and the AGL study (`business_firm_color_dictionary_json/firm_color_dict.json`) comes from its own repository, cloned by `dependencies.sh`; the folder is ignored by git, and `test-nofo-viz.sh` says how to get the map if it is missing.
- The README example of a GitHub noreply address uses GitHub's octocat account instead of a real developer's e-mail address.
- nofi visualizer, `-a`: affiliations are matched to the alias keys without regard to case. `configparser` lower-cases the keys, so an affiliation with capitals (e.g. `NVIDIA`) never matched. This changes figures and `-s` output, not scrapLog's networks.

### New

- `--version` in every tool. The version is set once, in `scraplog/_version.py`.
- nofo visualizer: `-nc gray-color-to-others-not-in-topn-filter` is implemented (it colored every node gray and logged an error): the N most central organizations keep their color (N from `-tf`, default 10), the rest are gray.
- `--seed` in both visualizers: seed for the spring layout (default 42).
- `deanonymize_github_users.py`: `--cache-file`, `--no-cache` and `--no-wait`.

### Development

- 299 unit tests. Tk (tkinter), needed by the nofi visualizer, is listed with the system packages in `requirements.txt` and the README.
- The transformer acceptance suite (`test-nofi-2-nofo-transformer.sh`) runs again, in CI too: it validates against a local copy of the GraphML 1.0 schema (`tests/acceptance-test-scripts/graphml-schema/`), because graphml.graphdrawing.org is out of service.

## v1.1-borba (2026-11-10)

### Changes that affect research results

Networks built with v1.0 may differ from networks built with this release in these cases. Rebuild them if they are used in an analysis.

- **`-fe` (filter e-mails) applies to every network type.** In v1.0 the filtered developers stayed in weighted and temporal networks.
- **`-a` (aggregate e-mail domains) works.** In v1.0 a matching key returned the domain unchanged, so `-a` had no effect. Keys now match the organization part of the domain exactly (case-insensitive) and the configured name is used, in lower case.
- **Weighted networks carry affiliations.** Weighted output now has the same layout as unweighted output (numeric node IDs; `e-mail`, `color` and `affiliation` attributes) plus a `weight` on each edge. Nodes, edges and weights are unchanged. The nofi-to-nofo transformer now accepts weighted files.
- **Deterministic output.** The same log gives byte-identical GraphML from scrapLog and from the nofi-to-nofo transformer.

### Fixes

- `deanonymize_github_users.py` no longer prints the GitHub token, and writes the resolved address to `e-mail` (it wrote a separate `email` attribute).
- The nofo reporter works on networks of organizations (organization names, `-f`, `-t`, weighted degree).
- The nofi report shows e-mails (it read `email` instead of `e-mail`).
- An empty graph after filtering stops with a clear error in the nofi visualizer and the nofi report.
- `&`, `<` and `>` in e-mails no longer produce invalid GraphML.
- Fatal errors exit with code 1 instead of 0.
- `-tntr` other than 1 and `-l` stop with an error instead of being ignored; `-s` works with plain file names.
- The transformer accepts `.graphml` in any case for input and `-o`.
- `solo_contributors.py` no longer crashes (missing `--list-developers`).
- Error paths work outside PyCharm.

### New

- `-ff` / `--filter-files`: ignore files by path or wildcard pattern (e.g. `*.md`).
- nofi visualizer: legend locations `upper_left`, `center_left`, `lower_left`; legend type `top10+others`.
- `compare-two-nofi-GraphML-metrics.py --verbose` prints node and edge counts per file.
- A page per tool in `docs/tools/`.

### Removed

- Options that had no effect: `-g` (nofi visualizer), `-lt top10+1`, `-c` (both reports), `--years`, `--output-dir` and `--dry-run` (batch miner).
- Research datasets are no longer in the repository; they are archived on Zenodo (see the README).

### Development

- Code organized as the `scraplog` package; the old script names still work. Python 3.12 or later.
- 269 unit tests and acceptance tests, including the synthetic example of the MSR 2027 paper, run on GitHub Actions. The acceptance tests check for `xmllint` and `unzip` first.

## v1.0-alvarinho (2026-11-04)

First archived release: <https://doi.org/10.5281/zenodo.23964330>.
