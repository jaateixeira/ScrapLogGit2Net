# formatFilterAndReport-nofo-GraphML.py

Reports on a network of organizations (nofo): for each organization, its degree, its weighted degree and its degree centrality, on the console and in an Excel `.xls` file. It can keep only a list of "top firms" or remove a list of generic organizations before the analysis. It also accepts a network of individuals (nofi), and then reports on developers and their affiliations.

## Run it

From the repository root:

```bash
./formatFilterAndReport-nofo-GraphML.py [options] file
```

After `pip install -e .`, the same tool is available as a console command:

```bash
report-nofo [options] file
```

## Input

One GraphML file, read with `networkx.read_graphml`. This can be:

- a network of organizations, for example a file from `transform_nofi_2_nofo_graphml.py` (node IDs are organization names, nodes have no attributes); or
- a network of individuals from `scrapLog.py` (nodes have `e-mail` and `affiliation` attributes).

The tool prints which kind it found. A file is read as a network of individuals if at least one node has an `e-mail` or `affiliation` attribute. The organization of a node is its `affiliation` attribute when it has one, and otherwise its node ID.

## Output

- Console: a "Graph Statistics" panel (nodes, edges, isolates) and up to 5 isolated nodes. Then:
  - network of organizations: a "Top 10 Most Connected Organizations" table with the organization, its degree (number of partner organizations), its weighted degree (sum of the `weight` of its edges, that is the number of inter-firm co-edits from the transformer) and its degree centrality. Organizations are ranked by degree centrality, then weighted degree, then name.
  - network of individuals: a "Top 10 Most Connected Individuals" table (email, degree centrality, affiliation) and a "Top 10 Organizations by Node Count" table (number of developers per affiliation).
- Excel report: `<prefix>.xls`. The prefix is the value of `-o`; by default it is the input file name without its extension, and the file is written to the current working directory. For example, `test-data/TensorFlow/tensorflow_2025_network.out.nofo.graphML` gives `tensorflow_2025_network.out.nofo.xls`. An existing file with the same name is overwritten. The workbook has these sheets:
  - `Graph Statistics`: number of nodes, edges and isolates.
  - Network of organizations: `Organizations`, with every organization ranked as in the console table (rank, organization, degree, weighted degree, degree centrality). The three sheets below are not written.
  - Network of individuals: the three sheets below.
  - `Organizations by Node Count`: every `affiliation` value with its node count and percentage (not only the top 10).
  - `Nodes (Developers)`: every node with ID, email and affiliation.
  - `Centrality Analysis`: every node with degree centrality, email and affiliation, sorted by centrality.
- Log file: `app.log` in the current working directory (written by the project's shared logger).

All counts and lists are computed after the filters (`-t`, `-f`) are applied, except the "Graph Statistics" panel on the console, which is printed right after loading.

## Options

| Option | Meaning | Default |
|---|---|---|
| `file` | Path to the GraphML network file (required). | none |
| `-h`, `--help` | Show the help message and exit. | |
| `-v`, `--verbose` | Print the configuration, each node removed by a filter, each `alum` affiliation renamed to `alum.mit.edu`, and up to 20 more organizations after the top 10. | off |
| `-t`, `--top-firms-only` | Keep only nodes whose organization is in the top-firms list. | off |
| `-f`, `--filter-by-org` | Remove nodes whose organization is in the filter-firms list. | off |
| `-o`, `--output` | Output file name prefix; `.xls` is appended. It can include a directory. | input file name without extension |
| `--top-firms` | Comma-separated list that replaces the default top-firms list. Only used together with `-t`. | `google,microsoft,ibm,amazon,intel,amd,nvidia,arm,meta,bytedance` |
| `--filter-firms` | Comma-separated list that replaces the default filter-firms list. Only used together with `-f`. | `users,tensorflow,gmail` |

## Examples

Report on a network of organizations; writes `tensorflow_2025_network.out.nofo.xls` in the current directory:

```bash
./formatFilterAndReport-nofo-GraphML.py test-data/TensorFlow/tensorflow_2025_network.out.nofo.graphML
```

Same input, with the generic organizations filter and a chosen output name (`tf2025-filtered.xls`). This removes `users` and `tensorflow` (49 nodes become 47); Google ranks first, with 41 partner organizations and a weighted degree of 3806:

```bash
./formatFilterAndReport-nofo-GraphML.py test-data/TensorFlow/tensorflow_2025_network.out.nofo.graphML -f -o tf2025-filtered
```

Keep only developers of Google and NVIDIA in a network of individuals; writes `tensorFlowGitLog-3-commits-1-edge.NetworkFile.xls`:

```bash
./formatFilterAndReport-nofo-GraphML.py test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML -t --top-firms "google,nvidia"
```

## Notes and limitations

- If the filters remove every node, the tool prints `Error: no nodes left after filtering`, writes no report and exits with code 1.
- Removing organizations with `-f` can leave other organizations without partners; they then show as isolated nodes.
- The filter lists are matched exactly, including case (`google` does not match `Google`).
- `--top-firms` has no effect without `-t`, and `--filter-firms` has no effect without `-f`.
- If both `-f` and `-t` are given, `-f` is applied first, then `-t`.
- The console tables always show at most 10 rows; there is no option to change this.
- Degree centrality counts edges only; the edge weights are shown separately as the weighted degree. An edge without a `weight` attribute counts as 1.
- Renaming the `alum` affiliation to `alum.mit.edu` applies only to the `affiliation` attribute of a network of individuals, not to a node named `alum` in a network of organizations.
- The output is written in the legacy Excel 97-2003 `.xls` format (library `xlwt`).

[Back to the README](../../README.md#executable-toolsscripts)
