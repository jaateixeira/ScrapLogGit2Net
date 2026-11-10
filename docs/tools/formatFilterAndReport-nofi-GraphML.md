# formatFilterAndReport-nofi-GraphML.py

Reports on a network of individuals (developers) stored in a GraphML file. It prints basic network statistics, the top organizations by number of developers, and the top individuals by degree centrality. It also writes the same analysis, plus a node list and an edge analysis, to an Excel `.xls` file. Use it to get a quick overview of a network produced by `scrapLog.py`, optionally after removing or keeping only developers of some organizations.

## Run it

From the repository root:

```bash
./formatFilterAndReport-nofi-GraphML.py [options] file
```

After `pip install -e .`, the same tool is available as a console command:

```bash
report-nofi [options] file
```

## Input

One GraphML file with a network of individuals, for example a `.graphML` file written by `scrapLog.py`. The tool reads it with `networkx.read_graphml`.

Each node is expected to have an `affiliation` attribute. Nodes without it are not counted in the organization ranking and show as `unknown` in the centrality table.

## Output

- Console: a "Graph Statistics" table (nodes, edges, isolates, density, whether the graph is connected, and the number of connected components when it is not), a list of isolated nodes, a "Top N Organizations by Node Count" table, and a "Top N Individuals by Degree Centrality" table.
- Excel report: `<input file name without extension>_report.xls`, written to the current working directory (not next to the input file). For example, `test-data/5-pentagon-with-star.graphML` gives `5-pentagon-with-star_report.xls`. An existing file with the same name is overwritten. The workbook has these sheets:
  - `Graph Statistics`: the statistics above; when the graph is not connected, also the number and sizes of the connected components.
  - `Top Organizations`: organization, node count and percentage, for the top organizations only (see `-tn`).
  - `Centralities`: node ID, degree centrality and affiliation, for the top individuals only (see `-ti`).
  - `Nodes`: every node left after filtering, with node ID, email and affiliation.
  - `Edge Analysis`: number of intra-organization and inter-organization edges, and the number of intra-organization edges per organization.
- Log file: `app.log` in the current working directory (written by the project's shared logger).

All counts and lists are computed after the organization filters (`-oi`, `-oo`) are applied.

## Options

| Option | Meaning | Default |
|---|---|---|
| `file` | Path to the GraphML network file (required). | none |
| `-h`, `--help` | Show the help message and exit. | |
| `-v`, `--verbose` | Print a debug line for each node removed by `-oi` or `-oo`, and for each `alum` affiliation renamed to `alum.mit.edu`. | off |
| `-oi`, `--org_list_to_ignore` | Comma-separated list of organizations. Developers whose `affiliation` matches one of them are removed. | none |
| `-oo`, `--org_list_only` | Comma-separated list of organizations. Only developers whose `affiliation` matches one of them are kept. | none |
| `-c`, `--color_map` | JSON file mapping firms/organizations to colors. The file is loaded, but the colors are not used anywhere in the report: this option has no effect on the output. | none |
| `-tn`, `--top_n_orgs` | Number of top organizations to report (console table and `Top Organizations` sheet). | 20 |
| `-ti`, `--top_n_inds` | Number of top individuals by degree centrality to report (console table and `Centralities` sheet). | 10 |

## Examples

Report on a small sample network; writes `5-pentagon-with-star_report.xls` in the current directory:

```bash
./formatFilterAndReport-nofi-GraphML.py test-data/5-pentagon-with-star.graphML
```

Remove the developers affiliated with `rijksmuseum` before the analysis:

```bash
./formatFilterAndReport-nofi-GraphML.py test-data/5-pentagon-with-star.graphML -oi rijksmuseum
```

Keep only the developers of two organizations:

```bash
./formatFilterAndReport-nofi-GraphML.py test-data/5-pentagon-with-star.graphML -oo "bywatersolutions,oodi.fi"
```

Limit the report to the top 5 organizations and the top 3 individuals:

```bash
./formatFilterAndReport-nofi-GraphML.py test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML -tn 5 -ti 3
```

## Notes and limitations

- Organization names in `-oi` and `-oo` must match the `affiliation` value exactly, including case. For example, `-oi Rijksmuseum` does not remove nodes with affiliation `rijksmuseum`.
- `-oi` and `-oo` can be combined. `-oi` is applied first, then `-oo`.
- Before filtering, an affiliation of exactly `alum` is renamed to `alum.mit.edu`.
- If the filters remove every node, the tool stops with the error `No graph data to export` and exit code 1. No report is written.
- The tool also accepts a network of organizations (for example a file from `transform_nofi_2_nofo_graphml.py`), but such nodes have no `affiliation`, so the organization ranking is empty and every affiliation shows as `unknown`.
- Degree centrality is the only centrality measure computed.
- The output is written in the legacy Excel 97-2003 `.xls` format (library `xlwt`).

[Back to the README](../../README.md#executable-toolsscripts)
