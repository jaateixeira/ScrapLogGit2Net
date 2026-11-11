# nofo_graphml_network_visualizer.py

`nofo_graphml_network_visualizer.py` draws a weighted network of organizations (nofo) stored in a GraphML file. Each node is an organization, and the `weight` of an edge counts the collaboration between two organizations. Edge thickness and edge labels show the weight, and node size shows centrality. Use it on a network produced by `transform_nofi_2_nofo_graphml.py` (console command `transform-nofi-2-nofo`) to see which organizations work together.

## Run it

From the repository root:

```bash
./nofo_graphml_network_visualizer.py [options] file
```

After `pip install -e .` the same tool is available as a console command:

```bash
nofo-graphml-network-visualizer [options] file
```

## Input

- `file`: a GraphML file (required), read with NetworkX (`networkx.read_graphml`). Node IDs are used as organization names. Edges may have a numeric `weight` attribute; a missing weight counts as 1. See `test-data/5-pentagon-with-star-transformed-to-nofo.graphML` for an example.
- Optional color map (`-c`): a JSON object that maps a node ID (organization) to a Matplotlib color, for example `{"rijksmuseum": "red", "oodi.fi": "#1f77b4"}`.
- Optional legend data (`--legend-info-data`): a JSON file of this form:

  ```json
  {"organizations": [
    {"organization_id": "rijksmuseum", "organization": "Rijksmuseum Amsterdam", "number_of_contributors": 2}
  ]}
  ```

  `organization_id` must match a node ID. If you do not give this option and a file named `labels.json` exists in the current directory, that file is used.

## Output

The figure files are written to the **same directory as the input file**:

| File | When |
|---|---|
| `<stem>-<layout>-<filters>.png` (300 dpi) | Unless `-s`/`-p` is given without `-w` |
| `<stem>-<layout>-<filters>.pdf` | Same as the PNG |
| `<stem>.html` | With `-w` |

- `<stem>` is the input file name without its last extension.
- `<layout>` is `spring` or `circular`.
- `<filters>` is `all` when no filter is used. Otherwise it joins, with `-`: `top<N>` for `-tf N`, `inc-<count>` for `--include-only` with `<count>` names, and `exc-<count>` for `--exclude` with `<count>` names. `-f` does not change the name.
- Existing files with the same name are overwritten.

For example, `test-data/5-pentagon-with-star-transformed-to-nofo.graphML` with default options gives `test-data/5-pentagon-with-star-transformed-to-nofo-spring-all.png` and `...-spring-all.pdf`. With `--exclude oodi.fi` the names end in `-spring-exc-1.png` and `-spring-exc-1.pdf`.

The HTML page (`-w`) shows the PNG (linked by a relative path) with a caption that lists the command-line arguments as a Python list.

The tool also writes a log file `app.log` (DEBUG level, rotated at 10 MB) in the current working directory, and prints log messages to the terminal.

## Options

| Option | Meaning | Default |
|---|---|---|
| `file` | The GraphML network file. | required |
| `-h`, `--help` | Show the help message and exit. | |
| `-n {circular,spring}`, `--network_layout {circular,spring}` | Layout algorithm. The spring layout uses the seed from `--seed`, so the same input gives the same positions. | `spring` |
| `--seed SEED` | Seed for the spring layout. Change it to get a different arrangement. | `42` |
| `-v`, `--verbose` | Print debug details (graph contents, centralities, node colors). Also adds the command-line arguments as a title at the top of the figure. | off |
| `-ns {all-equal,centrality-score}`, `--node_sizing_strategy {all-equal,centrality-score}` | `all-equal`: every node has size 100. `centrality-score`: size is centrality × 2000. Centrality is eigenvector centrality; if that fails, degree centrality is used. | `centrality-score` |
| `-nc {random-color-to-unknown-firms,gray-color-to-unknown-firms,gray-color-to-others-not-in-topn-filter}`, `--node_coloring_strategy ...` | How to color nodes that are not in the color map. `random-color-to-unknown-firms`: a color derived from the organization name, the same in every run and in both visualizers (the strategy keeps its old name). `gray-color-to-unknown-firms`: gray. `gray-color-to-others-not-in-topn-filter` is accepted but not implemented: the tool logs "Unknown coloring strategy" for each node and colors it gray. | `random-color-to-unknown-firms` |
| `-c COLOR_MAP`, `--color_map COLOR_MAP` | JSON file that maps node IDs to colors. If the file is missing or not valid JSON, a warning or error is logged and an empty map is used. | none |
| `-ff FOCAL_FIRM`, `--focal_firm FOCAL_FIRM` | Node ID of an organization to highlight with a circle. If the node is not in the (filtered) graph, an error is logged and no circle is drawn. | none |
| `-tf FILTER_BY_N_TOP_CENTRAL_FIRMS_ONLY`, `--filter_by_n_top_central_firms_only FILTER_BY_N_TOP_CENTRAL_FIRMS_ONLY` | Keep only the N most central organizations (integer) and the edges between them. Centrality is computed after the organization filters and computed again after this filter. | none |
| `-f`, `--filter_by_org` | Remove isolated nodes (nodes with no edges), including nodes left isolated by `--include-only` or `--exclude`. | off |
| `--include-only INCLUDE_ONLY` | Comma-separated list of node IDs to keep. All other nodes are removed. | none |
| `--exclude EXCLUDE` | Comma-separated list of node IDs to remove. Applied after `--include-only`. | none |
| `--legend-info-data LEGEND_INFO_DATA` | JSON file with full organization names and contributor counts for the legend (see [Input](#input)). Has a visible effect only with `-l`. | `labels.json` in the current directory, if it exists |
| `-s`, `--show`, `-p`, `--plot` | Show the figure in a window instead of saving it. Combined with `-w`, the figure is shown and also saved. | off (save files) |
| `-w`, `--web-page` | Also save PNG and PDF and write the HTML page `<stem>.html` next to the input file. | off |
| `-l`, `--legend` | Add a legend outside the plot, on the right. Entries are sorted by contributor count. With legend data, an entry reads `<full name> (n=<contributors>)`; without it, the entry is the node ID. | off |

Organization names in `--include-only`, `--exclude` and `-ff` must match node IDs exactly (case-sensitive).

## Examples

All examples below exited with status 0. They were run on a copy of the sample file in a scratch folder, so the outputs were written next to that copy.

Draw the sample network with default settings:

```bash
./nofo_graphml_network_visualizer.py test-data/5-pentagon-with-star-transformed-to-nofo.graphML
```

Use a circular layout, add a legend, and highlight one organization:

```bash
./nofo_graphml_network_visualizer.py -n circular -l -ff rijksmuseum test-data/5-pentagon-with-star-transformed-to-nofo.graphML
```

Remove one organization, remove nodes left isolated, and also write an HTML page:

```bash
./nofo_graphml_network_visualizer.py --exclude oodi.fi -f -w test-data/5-pentagon-with-star-transformed-to-nofo.graphML
```

Keep only the two most central organizations and color them gray:

```bash
./nofo_graphml_network_visualizer.py -tf 2 -nc gray-color-to-unknown-firms test-data/5-pentagon-with-star-transformed-to-nofo.graphML
```

## Notes and limitations

- Output files go next to the input file, not to the current directory. Make sure you can write to that directory.
- If the organization filters remove every node, the tool prints the filters it used and exits with status 1.
- `-nc gray-color-to-others-not-in-topn-filter` is not implemented (see [Options](#options)).
- Edge thickness is `1 + log2(weight)`. A weight below 1 makes the thickness smaller than 1, and a weight of 0 or less causes an error.
- With `-s`/`-p` and no `-w`, nothing is saved. Showing a window needs a Matplotlib backend with a display.
- The same input and options give the same PNG and PDF files: colors come from organization names, the spring layout uses a fixed seed and the PDF has no creation date. Two organizations can get similar colors; use `-c` to choose them.
- `app.log` is created or appended to in the directory where you run the tool.

[Back to the README](../../README.md#executable-toolsscripts)
