# compare-set-nofi-GraphML.py

Compares 2 to 20 networks stored in GraphML files. For each file it computes standard network metrics, prints them as a text table, and draws one figure with nine panels that compare the files. Use it to compare networks of individuals over time, for example one network per year or per release produced by `scrapLog.py`.

## Run it

From the repository root:

```bash
./compare-set-nofi-GraphML.py [options] files [files ...]
```

After `pip install -e .`, the same tool is available as a console command:

```bash
compare-nofi-sets [options] files [files ...]
```

## Input

Between 2 and 20 GraphML files, read with `networkx.read_graphml`. The files are processed in the order given on the command line, and that order is used for the numbering in the table and the plot.

- A file name must end with `.graphml` (any case, so `.graphML` is accepted). Other files, and files that do not exist, are skipped with a warning.
- A file that cannot be read as GraphML is skipped and listed as failed.
- At least 2 files must remain, otherwise the tool exits with code 1.

The tool does not use node attributes, so any GraphML network works, including networks of organizations.

## Output

- Console: a "NETWORK METRICS SUMMARY" table with one row per file (nodes, edges, isolates, average degree, density, average clustering coefficient, number of connected components, largest component as a percentage of nodes, directed, weighted) and a row of averages.
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
| `--version` | Show the program name and the ScrapLogGit2Net version, then exit. | |
| `--save-plot` | Save the plot to this file name, for example `metrics.png` or `metrics.pdf`. | not saved |
| `--output-dir` | Directory for the saved plot. It is created if it does not exist. Only used with `--save-plot`. | current directory |
| `--dpi` | Resolution of the saved plot. | 100 |
| `--verbose` | Print the number of valid files and, for each file, its node and edge counts. | off |
| `--no-show` | Do not open the plot window. The figure is only created when `--save-plot` is also given. | off (window opens) |

## Examples

Compare two networks and show the plot in a window:

```bash
./compare-set-nofi-GraphML.py test-data/5-pentagon-with-star.graphML test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML
```

Compare three networks and save the plot as `metrics.png` without opening a window:

```bash
./compare-set-nofi-GraphML.py test-data/5-pentagon-with-star.graphML test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML --save-plot metrics.png --no-show
```

Save a PDF at 150 DPI in the folder `results` (created if needed), with per-file details on the console:

```bash
./compare-set-nofi-GraphML.py test-data/5-pentagon-with-star.graphML test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML --output-dir results --dpi 150 --save-plot metrics.pdf --no-show --verbose
```

## Notes and limitations

- The plot window needs a graphical display. Without one (for example over SSH, or with `MPLBACKEND=Agg`), no window appears and the tool ends normally; use `--save-plot` to get the figure.
- The file names in the console table are cut to 25 characters, and in the plot to 20 characters, so files with a long common prefix can be hard to tell apart. Use the row numbers.
- Edge weights are not used for any metric; the "Weighted" column only reports whether the graph has weights.
- Directed graphs are handled: their components are weakly connected components, and their clustering coefficient is reported as 0.
- [compare-two-nofi-GraphML-metrics.py](compare-two-nofi-GraphML-metrics.md) computes the same metrics and the same plot, with a different console layout.

[Back to the README](../../README.md#executable-toolsscripts)
