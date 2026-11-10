# compare-two-nofi-GraphML-metrics.py

Compares 2 to 20 networks stored in GraphML files (despite the name, it is not limited to two). For each file it computes standard network metrics, prints them in a formatted console table with a statistics panel, and draws one figure with nine panels that compare the files. It computes the same metrics and the same figure as [compare-set-nofi-GraphML.py](compare-set-nofi-GraphML.md); the difference is the console output.

## Run it

From the repository root:

```bash
./compare-two-nofi-GraphML-metrics.py [options] files [files ...]
```

After `pip install -e .`, the same tool is available as a console command:

```bash
compare-nofi-metrics [options] files [files ...]
```

## Input

Between 2 and 20 GraphML files, read with `networkx.read_graphml`. The files are processed in the order given on the command line, and that order is used for the numbering in the table and the plot.

- A file name must end with `.graphml` (any case, so `.graphML` is accepted). Other files, and files that do not exist, are listed in a warning table and skipped.
- A file that cannot be read as GraphML is skipped and listed with its error.
- At least 2 files must remain, otherwise the tool exits with code 1.

The tool does not use node attributes, so any GraphML network works, including networks of organizations.

## Output

- Console:
  - a "Network Metrics Summary" table with one row per file (nodes, edges, isolates, average degree, density, average clustering coefficient, number of connected components, largest component as a percentage of nodes, directed, weighted) and a row of averages;
  - a "Statistics" panel with minimum, maximum and average numbers of nodes and edges, the density range, and the percentage of directed and weighted graphs;
  - a final "Summary" panel with the number of processed and failed files.
- Plot: one figure titled "Network Metrics Comparison" with nine panels: nodes/edges/isolates, average degree, density, average clustering coefficient, connected components, largest component (% of nodes), nodes vs edges scatter, counts of directed/undirected and weighted/unweighted graphs, and a summary table. File names longer than 20 characters are shortened in the plot.
  - By default the figure opens in a window and the tool waits until you close it.
  - With `--save-plot NAME`, the figure is also saved to `NAME` in the current directory, or to `<output-dir>/NAME` when `--output-dir` is given. The format follows the file extension (for example `.png` or `.pdf`).
  - No plot file is written unless `--save-plot` is given.
- Log file: `app.log` in the current working directory (written by the project's shared logger).

## Options

| Option | Meaning | Default |
|---|---|---|
| `files` | GraphML files to analyze (2 to 20). | none (required) |
| `-h`, `--help` | Show the help message and exit. | |
| `--save-plot` | Save the plot to this file name, for example `metrics.png` or `metrics.pdf`. | not saved |
| `--output-dir` | Directory for the saved plot. It is created if it does not exist. Only used with `--save-plot`. | current directory |
| `--dpi` | Resolution of the saved plot. | 100 |
| `--verbose` | Print each file's node and edge counts as it is read, for example `5-pentagon-with-star.graphML: 5 nodes, 10 edges`. | off |
| `--no-show` | Do not open the plot window. | off (window opens) |
| `--no-table` | Do not print the "Network Metrics Summary" table and the "Statistics" panel. | off (table printed) |

## Examples

Compare two networks, print the table and show the plot in a window:

```bash
./compare-two-nofi-GraphML-metrics.py test-data/5-pentagon-with-star.graphML test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML
```

Save the plot as `metrics.png` without the console table and without opening a window:

```bash
./compare-two-nofi-GraphML-metrics.py test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML --save-plot metrics.png --no-show --no-table
```

Compare three networks and save a PDF at 150 DPI in the folder `results` (created if needed):

```bash
./compare-two-nofi-GraphML-metrics.py test-data/5-pentagon-with-star.graphML test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML --output-dir results --dpi 150 --save-plot metrics.pdf --no-show
```

## Notes and limitations

- The plot window needs a graphical display. Without one (for example over SSH, or with `MPLBACKEND=Agg`), no window appears and the tool ends normally; use `--save-plot` to get the figure.
- The summary table has 12 columns. In a narrow terminal (for example 80 columns) the values are cut and shown as `…`. Use a wide terminal window.
- The file names in the console table are cut to 25 characters, and in the plot to 20 characters. Use the row numbers to tell files apart.
- The final "Summary" panel says `Plot: Displayed` whenever `--save-plot` is not given, even with `--no-show`.
- The tool waits about one second while it shows a progress bar before drawing the plot; this delay does no work.
- Edge weights are not used for any metric; the "Wgt" column only reports whether the graph has weights.
- Directed graphs are handled: their components are weakly connected components, and their clustering coefficient is reported as 0.

[Back to the README](../../README.md#executable-toolsscripts)
