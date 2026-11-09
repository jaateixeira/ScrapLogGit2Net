# nofi_graphml_network_visualizer.py

`nofi_graphml_network_visualizer.py` draws a network of individuals (nofi) stored in a GraphML file. In such a network each node is a developer and the `affiliation` node attribute names the developer's organization. The tool colors nodes by affiliation and sizes them by degree centrality. It can also filter developers by organization before drawing. Use it to get a quick picture of who works with whom in a repository, without opening Gephi, Tulip or Visone.

## Run it

From the repository root:

```bash
./nofi_graphml_network_visualizer.py [options] [infile]
```

After `pip install -e .` the same tool is available as a console command:

```bash
nofi-graphml-network-visualizer [options] [infile]
```

The help text still shows the old program name `formatFilterAndViz-nofi-GraphML.py`.

## Input

- One GraphML file, for example one created by `scrapLog.py`. It is read with NetworkX (`networkx.read_graphml`).
- The tool reads these node attributes:
  - `affiliation`: used for coloring, filtering and the legend.
  - `e-mail`: shown in the "Top 10 Most Connected Individuals" list. With `-v`, the part before `@` is drawn as the node label.
- `infile` is optional. If you leave it out, the tool opens a Tk file dialog so you can pick the file. If you cancel the dialog, the tool exits with status 1. If the file does not exist, it exits with status 1.
- Optional color map (`-c`): a JSON object that maps an affiliation to a Matplotlib color, for example `{"rijksmuseum": "red", "oodi.fi": "#1f77b4"}`.
- Optional alias file (`-a`): an INI file with an `[aliases]` section. Each key is an affiliation found in the graph and its value is the affiliation to use instead.

Before filtering, the tool also replaces the affiliation `alum` with `alum.mit.edu`.

## Output

The files are written to the **current working directory**, not next to the input file. `<stem>` is the input file name without its last extension, and `<layout>` is `spring` or `circular`.

| File | When |
|---|---|
| `<stem>_<layout>.png` (300 dpi) | Always, unless `-p` is given |
| `<stem>_<layout>.pdf` | Always, unless `-p` is given |
| `<stem>_filtered.graphml` | With `-s`. If that file already exists, the name becomes `<stem>_filtered_1.graphml`, `<stem>_filtered_2.graphml`, and so on. Existing files are not overwritten. |

The PNG and PDF files are overwritten if they already exist.

The figure title shows the input file name, the layout and the number of nodes and edges after filtering.

The tool also prints to the terminal: the initial node, edge and isolate counts; a table of the top 20 organizations by node count; a before/after filtering table; and the 10 developers with the highest degree centrality.

## Options

| Option | Meaning | Default |
|---|---|---|
| `infile` | The GraphML network file. If omitted, a Tk file dialog opens. | none (file dialog) |
| `-h`, `--help` | Show the help message and exit. | |
| `-v`, `--verbose` | Print more detail (removed nodes, the first 10 node colors, debug log). Also draws the part of each developer's e-mail before `@` as a node label. | off |
| `-c COLOR_MAP_FILE`, `--color-map COLOR_MAP_FILE` | JSON file that maps affiliations to colors. Colors in this file are used first, for every coloring strategy. If the file is missing or is not valid JSON, a warning or error is logged and an empty map is used. | none |
| `-nl {circular,spring}`, `--network-layout {circular,spring}` | Layout algorithm. The spring layout uses no fixed seed, so node positions change from run to run. | `spring` |
| `-ns {all-equal,centrality-score}`, `--node-sizing-strategy {all-equal,centrality-score}` | `all-equal`: every node has size 100. `centrality-score`: size is degree centrality × 100. | `centrality-score` |
| `-nc {random-color-to-unknown-firms,gray-color-to-unknown-firms,gray-color-to-others-not-in-topn-filter}`, `--node-coloring-strategy ...` | How to color affiliations that are not in the color map. `random-color-to-unknown-firms`: a random color per affiliation. `gray-color-to-unknown-firms`: gray. `gray-color-to-others-not-in-topn-filter`: a random color for affiliations among the top N organizations, gray for the rest. N comes from `-ot`, or is 10 if `-ot` is not given. | `random-color-to-unknown-firms` |
| `-oi ORG_LIST_TO_IGNORE`, `--org-list-to-ignore ORG_LIST_TO_IGNORE` | Comma-separated list of affiliations. Developers with these affiliations are removed. | none |
| `-oo ORG_LIST_ONLY`, `--org-list-only ORG_LIST_ONLY` | Comma-separated list of affiliations. Only developers with these affiliations are kept. | none |
| `-on ORG_LIST_AND_NEIGHBOURS_ONLY`, `--org-list-and-neighbours-only ORG_LIST_AND_NEIGHBOURS_ONLY` | Comma-separated list of affiliations. Keeps developers with these affiliations and every developer directly connected to them. | none |
| `-ot {top5,top10,top20}`, `--org-list-top-only {top5,top10,top20}` | Keep only developers from the 5, 10 or 20 organizations with the most developers. The ranking is computed on the graph before any filter is applied. | none (no filter) |
| `-a AFFILIATION_ALIAS_IN_CONFIG_FILE`, `--affiliation-alias-in-config-file AFFILIATION_ALIAS_IN_CONFIG_FILE` | INI file with an `[aliases]` section that renames affiliations (see [Input](#input)). An alias for `jp` is handled specially: the new affiliation is `ADIT`, `Panasonic` or `Fujitsu` depending on the e-mail; other `jp` e-mails are left unchanged with a warning. | none |
| `-p`, `--plot` | Show the figure in a window instead of saving PNG and PDF files. | off (save files) |
| `-l`, `--legend` | Add a legend. Each entry shows an affiliation and its node count after filtering. | off |
| `-ll {upper_right,upper_left,center_right,center_left,lower_right,lower_left,outside_center_right}`, `--legend-location ...` | Legend position. Only `outside_center_right`, `upper_right` and `lower_right` are handled separately. `upper_left`, `center_left`, `lower_left` and `center_right` all place the legend at the center right inside the plot. | `outside_center_right` |
| `-lt {top5,top10,top20,top10+1,top10+others}`, `--legend-type ...` | Which affiliations the legend lists: the top 5, 10 or 20 by node count after filtering. `top10+1` and `top10+others` behave the same: the top 10 plus the organizations given with `-le`. | `top10` |
| `-le LEGEND_EXTRA_ORGANIZATIONS`, `--legend-extra-organizations LEGEND_EXTRA_ORGANIZATIONS` | Comma-separated list of extra affiliations to add to the legend. Used only with `-lt top10+1` or `-lt top10+others`; ignored otherwise. | none |
| `-s`, `--save-graphml` | Also save the filtered graph as a new GraphML file (see [Output](#output)). | off |
| `-g GITHUB_TOKEN`, `--github GITHUB_TOKEN` | Not implemented. The value is accepted and stored but has no effect. | none |

Filters are applied in this order: `-oi`, `-oo`, `-on`, `-ot`. Affiliation names must match exactly (case-sensitive).

## Examples

These examples could not be run as written in the environment used to write this page, because it has no Tk library (see [Notes and limitations](#notes-and-limitations)). They were checked only with the `tkinter` module replaced by an empty stub; with that stub, each one exited with status 0 and wrote the files listed.

Draw a network with the default settings (writes `5-pentagon-with-star_spring.png` and `5-pentagon-with-star_spring.pdf` in the current directory):

```bash
./nofi_graphml_network_visualizer.py test-data/5-pentagon-with-star.graphML
```

Use a circular layout and add a legend:

```bash
./nofi_graphml_network_visualizer.py -nl circular -l test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML
```

Remove developers affiliated with `oodi.fi` and save the filtered network as `5-pentagon-with-star_filtered.graphml`:

```bash
./nofi_graphml_network_visualizer.py -oi oodi.fi -s test-data/5-pentagon-with-star.graphML
```

Keep only the top 5 organizations, gray out the others, and list the top 5 in the legend:

```bash
./nofi_graphml_network_visualizer.py -ot top5 -nc gray-color-to-others-not-in-topn-filter -l -lt top5 test-data/5-pentagon-with-star.graphML
```

## Notes and limitations

- **Tk is required.** The module imports `tkinter` at start-up, even when you pass `infile`. Without a working Tk library the tool fails before parsing any option, including `--help` (for example `ImportError: libtk8.6.so: cannot open shared object file`). On Debian or Ubuntu, Tk usually comes with the `python3-tk` package.
- **Empty result after filtering.** The code is meant to stop with "Graph is empty after filtering!" and status 1. This check does not work: when the filters remove every node, the tool saves no files, still prints "Visualization completed successfully!" and exits with status 0. For example, `-oo nosuch` on the sample file behaves this way. Check the "Filtering Results" table and the saved files.
- With `-ns centrality-score`, a node with no edges has degree centrality 0 and is drawn with size 0, so it is not visible.
- Random colors and the spring layout change on each run. Use `-c` and `-nl circular` for repeatable figures.
- Alias keys in the `-a` file are read with Python `configparser`, which converts keys to lower case. An affiliation that contains upper-case letters will not match any alias.
- If an organization given with `-le` is already in the top 10, it appears twice in the legend.
- `-g/--github` does nothing.
- An older document, `docs/formatAndViz-nofi-GraphML-documentation.md`, describes this tool under its old name.

[Back to the README](../../README.md#executable-toolsscripts)
