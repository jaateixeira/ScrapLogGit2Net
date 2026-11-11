# ScrapLogGit2Net - nofi_graphml_network_visualizer.py

> The current reference for this tool, with every option, is [docs/tools/nofi_graphml_network_visualizer.md](tools/nofi_graphml_network_visualizer.md). The tool was called `formatFilterAndViz-nofi-GraphML.py` before.

## Documentation of the tool nofi_graphml_network_visualizer.py for visualizing the network of individual software developers

**nofi_graphml_network_visualizer.py** is a shell executable Python script for visualizing GraphML files created with the ScrapLogGit2Net tool for modeling inter-individual networks of software developers that collaborate via Git.

The **nofi_graphml_network_visualizer.py** executable:  
- Formats and visualizes a GraphML file.
- Plots the network with a circular or spring layout (default: spring).
- Colorizes nodes according to the affiliation attribute.
- Sets the size of the nodes according to centralities or all with the same size (default: centralities).
- Can filter what nodes are visualized according to the organizational affiliation of the developers (aka nodes).

The **nofi_graphml_network_visualizer.py** visualization tool was developed by [Jose Apolinário Teixeira](http://users.abo.fi/jteixeir/) in 2024 to speed up the process of modeling and visualizing inter-individual networks created by ScrapLogGit2Net. It is an alternative to importing the GraphML file in network analysis visualization software such as Tulip, Gephi, or Visone. It speeds up the process of obtaining fast network visualizations, bypassing in certain cases the need for specialized network visualization tools.

For more information, see the publication and related websites:

- Teixeira, J., Robles, G., & González-Barahona, J. M. (2015). Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. *Journal of Internet Services and Applications*, 6, 1-27. Available open-access at  [https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2](https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2).
- Website [http://users.abo.fi/jteixeir/OpenStackSNA/](http://users.abo.fi/jteixeir/OpenStackSNA/) with the obtained social networks and visualizations included [in publications by the author on the OpenStack software ecosystem](http://users.abo.fi/jteixeir/#pub).
- Website [http://users.abo.fi/jteixeir/TensorFlowSNA/](http://users.abo.fi/jteixeir/TensorFlowSNA/) with the obtained social networks and visualizations for the TensorFlow open and cooperative project (publication forthcoming).

# Problem statement

Slow to figure out (i.e., visualize) who works with whom in complex software projects.

# Vision

A world where software co-production analytics put social network visualizations at the side of standard quantitative statistical data in a very fast way.

# **nofi_graphml_network_visualizer.py** Inputs

A GraphML file created with ScrapLogGit2Net or another tool. Note that the network needs to be in a specific format that models developers as nodes and associates them with organizations using node attributes.

# **nofi_graphml_network_visualizer.py** Outputs

A social network visualization that captures who codes with whom in a repository (note that developers can be affiliated with firms via an affiliation attribute). The script plots the network using Python NetworkX and Python Matplotlib, and it can then be exported to several formats such as PDF and PNG.

# How **nofi_graphml_network_visualizer.py** works

It simply reads the GraphML file and plots it according to the list of parameters passed via the shell.

With the parameters, you can choose:
- To either have a legend that depicts the organizational affiliation of developers or not have a legend at all.
- To position where the legend is placed or export it to a separate file.
- Filter for developers affiliated with a set of specific firms.
- Filter for developers not affiliated with a set of specific firms.
- Filter for the developers affiliated with the firms with the most developers in the networks.
- Filter for specific firms and their close collaboration partners (i.e., neighboring nodes only) leaving all others out.
- How nodes (i.e., developers) are colored.
- How nodes (i.e., developers) are sized.
- What organizations/affiliations should be displayed in the legend.

# How to use **nofi_graphml_network_visualizer.py**

You need basic skills on how to invoke Python scripts in the shell/terminal.  
Test case scripts are implemented in bash. Knowing the basics of Linux/Unix will help a lot. You do not need to be a programmer to use ScrapLogGit2Net and especially the nofi_graphml_network_visualizer visualizer, but if you are one, and find it useful, please contribute to the project.

# Command line options for filtering and formatting the network visualization

See [Options](tools/nofi_graphml_network_visualizer.md#options) in the tool's reference page, or run `./nofi_graphml_network_visualizer.py --help`.

# Examples

```bash
./nofi_graphml_network_visualizer.py -v -l -ot top5 test-data/5-pentagon-with-star.graphML
```

# Contributing

Please create a new branch for any new feature. Branch or fork, code, test, then pull request. Please follow the basic guide on [https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project).

Jose Teixeira, currently the only maintainer, will review and merge pull requests, update the ChangeLog.txt, acknowledge the contributions, and work on documentation in free time from work.

# Contributors

Jose Teixeira

# Maintainers

Jose Teixeira

# License

GNU General Public License v3.0

