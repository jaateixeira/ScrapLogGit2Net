# transform_nofi_2_nofo_graphml.py

`transform_nofi_2_nofo_graphml.py` turns a network of individuals (nofi) into a weighted network of organizations (nofo). Two organizations are connected when developers from them are connected. The edge weight is the number of developer-to-developer edges between the two organizations. Edges between developers of the same organization are ignored. Use it on the unweighted or weighted network written by `scrapLog.py`.

## Run it

From the repository root:

```
./transform_nofi_2_nofo_graphml.py <network file> [options]
```

After `pip install -e .` the same tool is available as the console command `transform-nofi-2-nofo`:

```
transform-nofi-2-nofo <network file> [options]
```

## Input

A GraphML network of individuals. Every node must have an `affiliation` attribute. The unweighted (`<log>.NetworkFile.graphML`) and weighted (`<log>.WeightedNetwork.graphML`) networks from `scrapLog.py` both have one.

The developer-level `weight` of a weighted input is not used: each developer pair counts once, so the weighted and unweighted networks of the same log give the same network of organizations.

Isolated nodes are listed in a table and removed before the transformation.

## Output

A GraphML file with one node per organization and an edge attribute `weight` (an integer). Only organizations with at least one inter-organizational edge become nodes. The nodes have no other attributes.

Default file name, written to the current working directory:

- The input file name without its folder, with `.graphML` removed and `-transformed-to-nofo.graphML` added. For example, `test-data/5-pentagon-with-star.graphML` gives `5-pentagon-with-star-transformed-to-nofo.graphML`.
- If that file already exists, a counter is added: `5-pentagon-with-star-transformed-to-nofo(1).graphML`, then `(2)`, and so on. Existing files are not overwritten.
- If the input name already contains `-transformed-to-nofo`, that part is removed first, so it is not repeated.
- The `.graphML` ending is recognised in any case: an input `x.graphml` also gives `x-transformed-to-nofo.graphML`.

The console shows tables with the number of nodes, edges and isolates before and after removing isolates, and the number of organizations and inter-organizational relationships.

## Options

| Option | Meaning | Default |
|---|---|---|
| `file` | The GraphML network of individuals to transform. Required. | none (required) |
| `-h`, `--help` | Show the help message and exit. | |
| `-v`, `--verbose` | Print the input graph, its nodes with their data, each edge being processed, and the nodes and edges of the network of organizations. | off |
| `-t`, `--top-firms-only` | Not implemented. The tool prints "ERROR: Filtering by top firms not implemented yet" and stops with exit code 1. | off |
| `-f`, `--filter-by-org` | Not implemented. The tool prints "ERROR: Filtering by organizations not implemented yet" and stops with exit code 1. | off |
| `-s`, `--show` | After saving, run the organizations visualizer (`python -m scraplog.viz.nofo_visualizer <output file> --show`) on the result. | off |
| `-o OUTFILE`, `--outfile OUTFILE` | Output file name. If it does not end in `.graphML` (in any case), `.graphML` is added: `-o two-orgs` gives `two-orgs.graphML`, and `-o tf-orgs.graphml` is kept as `tf-orgs.graphml`. An existing file with this name is overwritten. | see Output |

## Examples

Transform a small test network. This writes `5-pentagon-with-star-transformed-to-nofo.graphML` (3 organizations, 3 weighted edges) to the current directory:

```
./transform_nofi_2_nofo_graphml.py test-data/5-pentagon-with-star.graphML
```

Transform the network written by `scrapLog.py`. The first command writes `tensorFlowGitLog-first-trimester-2024.NetworkFile.graphML`. The second writes `tensorFlowGitLog-first-trimester-2024.NetworkFile-transformed-to-nofo.graphML` (20 organizations, 63 inter-organizational relationships):

```
./scrapLog.py -r test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN
./transform_nofi_2_nofo_graphml.py tensorFlowGitLog-first-trimester-2024.NetworkFile.graphML
```

Verbose run with a chosen output name. This writes `two-orgs.graphML`:

```
./transform_nofi_2_nofo_graphml.py -v test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML -o two-orgs
```

## Notes and limitations

- The input must have an `affiliation` attribute on every node.
- An organization whose developers only work with each other has no inter-organizational edge, so it is not a node in the output.
- `-t` and `-f` are not implemented and stop the tool.
- With `-s`, the exit code of the visualizer is not checked. The transformation reports success even if the visualizer fails. The visualizer is called with `--show`, which (per its help text) shows the visualization instead of saving it.
- The tool writes `app.log` to the current directory, through the shared logger.

[Back to the README](../../README.md#executable-toolsscripts)
