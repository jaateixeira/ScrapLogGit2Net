# scrapLog.py

`scrapLog.py` is the core tool of ScrapLogGit2Net. It reads a raw Git log and builds a network of developers who co-edited the same files. Developers are identified by their commit email, and their affiliation is inferred from the email domain. Use it as the first step: the other tools work on the GraphML files it writes.

## Run it

From the repository root:

```
./scrapLog.py -r <raw git log> [options]
```

After `pip install -e .` the same tool is available as the console command `scrapLog`:

```
scrapLog -r <raw git log> [options]
```

## Input

A raw Git log made with:

```
git log --pretty=format:"==%an;%ae;%ad==" --name-only > myproject.IN
```

Each commit is a header line followed by the changed files, one per line:

```
==Thai Nguyen;thaink@google.com;Thu Mar 28 04:29:52 2024 -0700==
tensorflow/compiler/mlir/quantization/tensorflow/python/quantize_model.py
```

Details from the parser (`scraplog/parsing.py`):

- The header must match `==name;email;date timezone==`, where the timezone is like `-0700`. Three other header forms are also accepted: `==Name email;;date timezone==`, `==email;;date timezone==`, and a Launchpad bot header `==Launchpad;;date timezone==` (email `launchpad@bot.bot`, affiliation `bot`).
- A header that cannot be parsed is skipped and counted as a skipped block. An email without `@` counts as a validation error.
- Blank lines are ignored. A commit with no files left (empty, merge, or all files filtered out) is skipped.
- If the log starts with a line that is not a header, the tool stops with an error (exit code 1).

The affiliation is taken from the email domain, in lower case. Usually it is the label before the top-level domain (`us.ibm.com` gives `ibm`). If the domain has three or more parts and the second-to-last is `co`, `com`, `ac`, `edu`, `gov`, `net`, `org`, `ltd` or `plc`, the label before that is used (`company.co.uk` gives `company`).

## Output

All output files are written to the current working directory, unless `-o` gives a path.

| Network type (`-t`) | Default output file | Content |
|---|---|---|
| `inter_individual_graph_unweighted` (default) | `<log>.NetworkFile.graphML` | Undirected GraphML. Each node has the attributes `e-mail`, `color` and `affiliation`. |
| `inter_individual_graph_weighted` | `<log>.WeightedNetwork.graphML` | Undirected GraphML, laid out like the unweighted file (each node has `e-mail`, `color` and `affiliation`). Each edge also has a `weight` attribute. |
| `inter_individual_graph_temporal` | `<log>.temporal.graphml.zip` | A zip archive (written with networkx-temporal) holding `<log>.temporal.graphml`. Node IDs are emails. There is one edge per time-stamped co-edit, with a `time` attribute such as `2024-01-06T04:03:16-08:00`. |
| `inter_individual_weighted_LOC_temporal`, `inter_individual_graph_weighted_SUM_LOC` | none | Not exported (see Options). |

`<log>` is the name of the file given with `-r`, without its folder and its last extension. For example, `test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN` gives `tensorFlowGitLog-first-trimester-2024.NetworkFile.graphML`.

The weighted network is derived from the temporal network. In the test log `tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN`, the one developer pair with two time-stamped co-edits gets `weight` 2.

Other output:

- With `-s`, a Python pickle file with the parsed change log (see Options).
- `app.log` in the current directory. The logger writes it on every run (it may stay empty). It rotates at 10 MB.
- A processing summary on the console: lines and commit blocks read, skipped blocks, number of nodes and edges, number of unique affiliations, and similar affiliation strings. A table with the run time and the arguments is printed at exit.

## Options

| Option | Meaning | Default |
|---|---|---|
| `-h`, `--help` | Show the help message and exit. | |
| `--version` | Show the program name and the ScrapLogGit2Net version, then exit. | |
| `-l LOAD`, `--load LOAD` | Meant to load a change log saved with `-s`. Not implemented: the tool stops with the error "Loading a saved change log (-l) is not implemented yet" and exit code 1. | not set |
| `-r RAW`, `--raw RAW` | The raw Git log to process. Required. | none (required) |
| `-s SAVE`, `--save SAVE` | Also save the parsed change log to this file as a Python pickle. It holds a list of `((email, affiliation), [files], timestamp)` entries, after filtering. A missing parent folder is created. | not set |
| `-fe FILTER_EMAILS`, `--filter-emails FILTER_EMAILS` | Text file with one email per line. Commits by these emails are dropped while parsing, so these developers are absent from every network type. The summary reports how many commits were excluded. If the file cannot be read, the tool stops with an error. | not set |
| `-ff FILTER_FILES`, `--filter-files FILTER_FILES` | Text file with files to ignore, one per line. A line is an exact path as it appears in the log (`src/main.py`) or a wildcard pattern (`*.md`, `docs/*`). `*` also matches `/`, so `*.bzl` matches in every folder. Blank lines and lines starting with `#` are ignored. If the file cannot be read, the tool stops with an error. | not set |
| `-ie EXT [EXT ...]`, `--include-only-with-file-extensions EXT [EXT ...]` | Only keep files with these extensions, for example `-ie .py .cpp .cu`. A missing leading dot is added. | not set |
| `-xe EXT [EXT ...]`, `--exclude-all-with-file-extensions EXT [EXT ...]` | Skip files with these extensions, for example `-xe .json .html .php`. A missing leading dot is added. An extension given to both `-ie` and `-xe` stops the tool with a "Conflicting extension filters" error. | not set |
| `-a AGGREGATE_EMAIL_PREFIXES`, `--aggregate-email-prefixes AGGREGATE_EMAIL_PREFIXES` | JSON file mapping the organization part of email domains to an organization name, for example `{"gmail": "google", "googlemail": "google"}`. A key must equal the organization part exactly (case-insensitive; subdomains are removed first, so `us.gmail.com` gives `gmail`), and the name is written in lower case. A missing file only gives a warning; invalid JSON stops the tool. | not set |
| `-t TYPE`, `--type-of-network TYPE` | Type of network: `inter_individual_graph_unweighted`, `inter_individual_graph_weighted`, `inter_individual_graph_temporal`, `inter_individual_weighted_LOC_temporal` or `inter_individual_graph_weighted_SUM_LOC`. The two LOC types are accepted but not exported: the run ends with an "Unknown network type" error and exit code 1, with or without `-o`. | `inter_individual_graph_unweighted` |
| `-tntr N`, `--temporal-network-time-resolution N` | Time resolution of the temporal network, in seconds. Only `1` is implemented. Any other value stops the tool with "Temporal network time resolution N is not implemented yet" and exit code 1. | `1` |
| `-o OUTPUT_FILE`, `--output-file OUTPUT_FILE` | Write the network to this file name instead of the default name. The name is used as given; no extension is added. For the unweighted and weighted types it must end in `.graphml` (in any case); otherwise the tool stops with "outfilename must finish with .graphml extension", writes no file and exits with code 1. For the temporal type the file is a zip archive whatever its name. | see Output |
| `-v`, `--verbose` | Verbosity. `-v` gives verbose output; `-vv` gives very verbose output. `-vvv` (or more) turns on neither mode, so it prints as much as no `-v`. | off |
| `-d`, `--debug` | Debug mode. The tool stops after each step and asks on the terminal whether to inspect the processing state and whether to continue. Answering no to "continue" ends the run. Do not use it in scripts. | off |
| `-st`, `--strict` | Strict validation. The only check it affects is a block that does not start with a `==` header (text before the first header). With `-st` this raises a `ValueError`; without it, the tool prints a warning and then stops anyway. Both cases end with exit code 1. | off |

## Examples

Build the default unweighted network from the TensorFlow log (January to March 2024). This writes `tensorFlowGitLog-first-trimester-2024.NetworkFile.graphML` (256 nodes, 3363 edges) to the current directory:

```
./scrapLog.py -r test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN
```

Build a weighted network from Python files only. This writes `tensorFlowGitLog-first-trimester-2024.WeightedNetwork.graphML` (61 nodes, 229 edges):

```
./scrapLog.py -r test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN -t inter_individual_graph_weighted -ie .py
```

Ignore bot emails and Bazel build files, and choose the output file name. This writes `filtered.graphML` (223 nodes, 1990 edges) and reports 1432 commits excluded by the email filter:

```
./scrapLog.py -r test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN -fe test-configurations/TensorFlow/TensorFlowBots.txt -ff test-configurations/TensorFlow/TensorFlowIgnoreBuildFiles.txt -o filtered.graphML
```

Build a temporal network from a small test log. This writes `tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.temporal.graphml.zip`:

```
./scrapLog.py -r test-data/TensorFlow/tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN -t inter_individual_graph_temporal
```

## Notes and limitations

- Only developers with at least one co-edit become nodes. A developer whose files nobody else edited is not in the network.
- With the default unweighted type, a log with no co-edits prints "FATAL ERROR: The input did not led to the creation of a valid network", writes no file and exits with code 1 (for example with `test-data/TensorFlow/tensorFlowGitLog-3-commits-0-edges.IN`).
- With the weighted type, a log with no co-edits prints "FATAL ERROR: Network have less than two nodes !", writes no file and exits with code 1.
- With `-fe`, the tool prints the tip "The filtering based on only happen when creating the graphml network output file." In fact the commits are dropped while parsing, for every network type.
- `-l` is not implemented, `-tntr` only accepts `1`, and the two LOC network types are not exported.
- `-d` waits for answers on standard input.
- The tool writes `app.log` to the current directory.

[Back to the README](../../README.md#executable-toolsscripts)
