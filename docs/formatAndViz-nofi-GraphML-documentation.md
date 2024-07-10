# ScrapLogGit2Net - formatAndViz-nofi-GraphML.py

## Documentation of the tool formatAndViz-nofi-GraphML.py for visualizing the network of individual software developers 

**formatAndViz-nofi-GraphML.py** is a shell executable python script for visualizing graphML files created with the ScrapLogGit2Net tool for modelling inter-individual networks of software developers that collaborate via Git.

The **formatAndViz-nofi-GraphML.py** excutable:  
- formats and visualizes a graphML file.
- plots the network with a circular or spring layout (default: spring). 
- colourizes nodes according to the affiliation attribute. 
- sets the size of the nodes according to centralities or all with the same size (default: centralities). 
- can filter what nodes are visualized according to the organisational affiliation of the developers (aka nodes). 


The **formatAndViz-nofi-GraphML.py** visualization tool was developed by [Jose Apolinário Teixeira](http://users.abo.fi/jteixeir/) in 2024, to speed up the process of modelling and visualizing inter-individual networks created by ScrapLogGit2Net. It is an alternative to importing the graphML file in a network analysis visualization software such as Tulip, Gephi or Visone. It speeds up the process of obtaining fast network visualizations bypassing in certain case the need for specialized network visualization tools. 
For more information, see the publication and related websites: 

- Teixeira, J., Robles, G., & González-Barahona, J. M. (2015). Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. *Journal of Internet Services and Applications*, 6, 1-27. for more information. Available open-access at  [https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2](https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2).
- Website [http://users.abo.fi/jteixeir/OpenStackSNA/](http://users.abo.fi/jteixeir/OpenStackSNA/) with the obtained social networks and visualizations included [in publications by the author on the OpenStack software ecosystem](http://users.abo.fi/jteixeir/#pub).
- Website [http://users.abo.fi/jteixeir/TensorFlowSNA/](http://users.abo.fi/jteixeir/TensorFlowSNA/) with the obtained social networks and visualizations for the TensorFlow open and coopetitive project (publication forthcoming). 


# Problem statement # 
Slow to figure out (aka visualize) who works with whom in complex software projects. 

# Vision
A world where software co-production analytics put social network visualizations at the side of standard quantitative statistical data in a very fast way. 


# **formatAndViz-nofi-GraphML.py** Inputs #

A graphML file created with the ScrapLogGit2Net or other tool. Note that the network needs to be in a specific format that models developers as nodes, and associates them to organizations using node attributes. 

# **scrapLog.py** Outputs #
A social network visualization that captures who codes with who in a repository (note that developers can be affiliated with firms via an affiliation attribute.). The script plots the network using Python NetworkX and Python MathLibPlot and it can then be exported to several formats such as pdf and png. 

# How  **formatAndViz-nofi-GraphML.py** works #

It simply reads the graphML file and plots it according to the list of parameters passed via the shell. 

With the parameters, you can choose: 
- To either have a legend that depicts the organizational affiliation of developers or not a legend at all.
- To position where the legend is placed or export it to a separate file. 
- Filter for developers affiliated with a set of specific firms.
- Filter for developers not affiliated with a set of specific firms.
- Filter for the developers affiliated with the firms with most developers in the networks. 
- Filter for specific firms and their close collaboration partners (i.e., neighbouring nodes only) leaving all others out. 
- How nodes (aka developers) are coloured.
- How nodes (aka developer)  are sized.
- What organizations/affiliations should be displayed in the legend 
  
# How to use  **formatAndViz-nofi-GraphML.py**#

You need basic skills how to invoke Python scripts in the shell/terminal.  
 (test case scripts are implemented in bash).  Knowing basics of linux/unix will help a lot.  You do not need to be a programmer to use ScrapLogGit2Net and especially the formatAndViz-nofi-GraphML visualizer, but if you are one, and find it useful, please contribute to the project. 


# Command line options for filterign and formatting the network visualization 

TODO: 

```
TODO copy help here 

```

TODO:
Give examples:

./formatAndViz-nofi-GraphML.py  -svtfl test-data/TensorFlow/icis-2024-wp-networks-graphML/tensorFlowGitLog-2015-git-log-outpuyt-by-Jose.IN.NetworkFile.graphML 


# Contributing 
Please create a new branch for any new feature. Branch or fork, code, test, then pull request. Please follow the basic guide on [https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project). 

Jose Teixeira, currently the only maintainer,  will review and merge pull requests, update the ChangeLog.txt, aknowledge the contribuitions and work on documentation on free-time from work. 

# Contributors 
Jose Teixeira

# Maintainers  
Jose Teixeira

# License 
GNU General Public License v3.0
