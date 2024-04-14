# ScrapLogGit2Net
Tools supporting the mining of Git repositories. It creates social networks based on common source-code file edits. 

The tool was first developed by Jose Apolinário Teixeira during his doctoral studies with some guidance from  Software Engineering scholars with expertise in the mining of software repositories. 

Newer features allow you to: 
- Filter developers by email (handy to deal with bots that commit code)
- Support for parallel edges (.e., multiple edges between two nodes) that allow attributing weight to a cooperative relationship between two developers (e.g., the number of times they co-edited a source code file).
- visualize collaborations dynamically using  [NetworkX is a Python package](https://networkx.org/documentation/latest/) and [Matplotlib: Visualization with Python](https://matplotlib.org/). 

The code was also recently made compliant with the [NetworkX is a Python package](https://networkx.org/documentation/latest/) data structures and the [python 3.10 version](https://networkx.org/documentation/latest/) runtime which simplified the original code base. 

For more information, see the publication and related website: 

- Teixeira, J., Robles, G., & González-Barahona, J. M. (2015). Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. *Journal of Internet Services and Applications*, 6, 1-27. for more information. Available open-access at  [https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2](https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2).
- Website [http://users.abo.fi/jteixeir/OpenStackSNA/](http://users.abo.fi/jteixeir/OpenStackSNA/) with the obtained social networks and visualizations included in the publication.
- Website [http://users.abo.fi/jteixeir/TensorFlowSNA/](http://users.abo.fi/jteixeir/TensorFlowSNA/) with the obtained social networks and visualizations for the TensorFlow open and coopetitive project (publication forthcoming). 


# Problem statement # 
Hard to figure out who works with whom in complex software projects. 

# Vision
A world where software co-production analytics put social network visualizations at the side of standard quantitative statistical data.  All towards the improved management and engineering of complex software projects orchestrated on Git. 

# Inputs #

A git repository and its commit logs.


# Outputs #
Social networks that capture who codes who who in a repository (note that a software project can have multiple repositories).

# How it works #

It uses the commit logs of a git repository
```git log --pretty=format:"==%an;%ae;%ad=="  --name-only```

- %an stands for author name
- %ae stands for author email
- %ad stands for author date

Then: 
- It starts by identifying what source-code files were changed by whom at a given point in time. 
- Then associate each file with the developers that co-edited the same source-code file. 
- Then connects developers in a network. Nodes are software developers with a unique email. Edges are established if developers co-edited the same source-code file (i.e., nodes connect by working on the same files). 

Note that:
- Some manual developer's email aggregation might be required as the same developers can use multiple emails.
- Software bots can also commit code, undermining your analysis of human-to-human collaboration. 
- Co-editing some files might not be an indicator of collaboration. It's like some scholars co-authoring articles where little or no cooperation existed as expected.  For example, when  analysing projects in the C programming language, the co-editing of a Makefile might not be an indicator of collaboration, but instead an indicator of coordination. 

  
# How to use it  #

You need basic skills of Git and basic skills on how to invoke python scripts (test case scripts are implemented in bash).  Knowing python code will also help a lot. 
You do not need to be a programmer to use ScrapLogGit2Net, but if you are one, and find it usefull, please contribute to the project. 

## First, clone a Git repository 

Clone the Git repository you wish to mine with Social Network Analysis. Here is the example for TensorFlow: 

```
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
```


## Second, get the Git logs for scraping 


Obtain the commit logs that will be the main input for ScrapLogGit2Net. In this example, they are saved to the tensorFlowGitLog.IN file. 
Note that data scraping is a technique where a computer program extracts data from human-readable output coming from another program. In this case ScrapLogGit2Net will extract data coming from git.

```
git log --pretty=format:"==%an;%ae;%ad=="  --name-only > tensorFlowGitLog.IN`
```

If you are lost by this point, time to learn about Git. 

```
man git
man git log
```

Congratulations you should have your raw data ready for analysis with ScrapLogGit2Net


Look at you INPUT data.  As you can see from the following 4 April 2024 sample data from TensorFlow, you get time.stamped data on who changed what files. 
Note that gardner@tensorflow.org is a bot. Not a developer that directly commits code. 

     A. Unique TensorFlower;gardener@tensorflow.org;Wed Apr 3 22:39:37 2024 -0700
     tensorflow/core/tfrt/saved_model/tests/BUILD
     tensorflow/core/tfrt/saved_model/tests/saved_model_test.cc

     Doyeon Kim;doyeonkim@google.com;Wed Apr 3 20:54:06 2024 -0700
     tensorflow/compiler/mlir/lite/quantization/stablehlo/quantization.cc
     tensorflow/compiler/mlir/quantization/stablehlo/python/integration_test/quantize_model_test.py
     tensorflow/compiler/mlir/quantization/stablehlo/python/quantization.py
     tensorflow/compiler/mlir/quantization/stablehlo/quantization_config.proto

     Jiyoun (Jen) Ha;jiyounha@google.com;Wed Apr 3 18:50:32 2024 -0700
     tensorflow/lite/core/subgraph.cc

     Doyeon Kim;doyeonkim@google.com;Wed Apr 3 17:46:07 2024 -0700
     tensorflow/compiler/mlir/lite/quantization/stablehlo/BUILD
     tensorflow/compiler/mlir/lite/quantization/stablehlo/quantization.cc



What ScrapLogGit2Net does is to parse this time-stamps and associate developers that co-edited the same source-code file in a social network.  If two developers co-edit the same source-code file over time, we can assume that they cooperate with each other. A bit like scietists that co-author papers.  



Note the example year covers almost 10 years of commit logs in the TensorFlow project. It might be wise to narrow down the time window you want to analyse.


```git log --pretty=format:"==%an;%ae;%ad=="  --name-only```

In the following example you are checking commit logs between 1st and 4th of April 2021 

```git log --since='Apr 1 2021' --until='Apr 4 2021' --pretty=format:"==%an;%ae;%ad=="  --name-only```

And this example you check what developers did on 1st of April 2024


```git log --since='Mar 31 2024' --until='Apr 1 2024' --pretty=format:"==%an;%ae;%ad=="  --name-only```

Finally, the last example foes to the tensor flow reposiutory and gets the data to study the  first trimester for 2024

```cd tensorflow && git log --since='Jan 1 2024' --until='Mar 31 2024' --pretty=format:"==%an;%ae;%ad=="  --name-only > tensorFlowGitLog-first-trimester-2024.IN ```


- Now lets analyse some data.

## Scrap the data - Get basic statistics and social networks 
```
./scrapLog.py  --raw  test-data/tensorFlowGitLog-first-trimester-2024.IN
```
or
```
`python3 scrapLog.py  -r test-data/tensorFlowGitLog-first-trimester-2024.IN
```

By default, and all goes well, you get a "NetworkFile.graphML" file prefixed with the data input filename (e.g., tensorFlowGitLog-first-trimester-2024.IN.NetworkFile.graphMK) capturing the social network. 
Congrats. You collected social network data ready for analysis. 


# Command line options for advanced use

- Use serialized changelogs so you don't need to use raw git logs every time (speeds things up)
- Provide a configuration file with emails (aka developers) that should be ignored. Handy for ignoring bots that commit code
- Use verbose mode for debuging and testing 

```
usage: scrapLog.py [-h] [-l LSER] [-r RAW] [-s SSER] [-fe FILTER_EMAILS] [-ff FILTER_FILES] [-v]

Scrap some chagelog to create networks/graphs for research purpses

options:
  -h, --help            show this help message and exit
  -l LSER, --lser LSER  loads and processes an serialized changelog
  -r RAW, --raw RAW     processes from a raw git changelog
  -s SSER, --sser SSER  processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput
  -fe FILTER_EMAILS, --filter_emails FILTER_EMAILS
                        ignores the emails listed in a text file (one email per line)
  -ff FILTER_FILES, --filter_files FILTER_FILES
                        ignores the files listed in a text file (one email per line)
  -v, --verbose         increased output verbosity
```

For example, the following command 

```./scrapLog.py -f test-configurations/TensorFlowBots.txt  -r test-data/tensorFlowGitLog-all-till-12-Apri-2024.IN --verbose`` 

scraps the Git log in the test-data/tensorFlowGitLog-all-till-12-Apri-2024.IN input file, ignores emails listed in the test-configurations/TensorFlowBots.txt file and prints debug information in a verbose way. By default it also creates a
network file in the standard XML based format GraphML. 


# Features 

## Recently implemented features 
- Export to the [GraphML][http://graphml.graphdrawing.org/] format for graphs based on XML. Exports undirected grapths with company affiliation atributes. 
- Verbose debug output
- Use of a serialized changelog, so we dont't need to use RAW git logs every time. Save a lot of time for analysing complext projects.
- Possibiliry of adding an argument pointing with a file with emails to ignore (e.g., bots and spam email addresses).
- Dynamic export of social network visualizations with in the circular and centrality layouts

## To implement (voluntears welcome)
- Possibility to add an argument pointing to a file with REGULAR EXPRESSIONS to capture emails to ignore (e.g., ignoring developers from a given company).
- Possibility to add an argument pointing with a file that aggregates different emails used by a different individual  (e.g., John uses <John@ibm.com> and <John@gmail.com>).
- Possibility to add an argument pointing with a file that aggregates different emails used by different organizations (e.g., @ibm.com, @linux.vnet.ibm.com, @us.ibm.com, @cn.ibm.com all map IBM).
- Possibility to export both networks at the individual and organizational level (networks of individuals affiliated with organizations, and networks of organizations).
- Possibility to limit analysis to n top contributors (organization with most nodes).
- Colorize nodes by company affiliation automatically.
- Report stats on the files connecting people the most (handy for identifying outliers). 
- Support for weighted edges.
- Reporting analysis in latex, Markdown, HTML and text files. Should include quantitative metrics (e.g., n. commits, n. lines of code per dev, most co-edited files) and relational metrics (e.g., centrality, density). 
- Support for other network formats besides graphML (see [https://socnetv.org/docs/formats.html](https://socnetv.org/docs/formats.html)).
- Support for community detection.
- Use a logging system (e.g., [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html) or [https://github.com/gruns/icecream](https://github.com/gruns/icecream)) instead of print statements for debugging.
- Write unit tests for the main functions in scrapLogGit2Net (see [https://docs.python.org/3/library/unittest.html](https://docs.python.org/3/library/unittest.html)).
- Use config files as there are already so many parameters.
- Integrate with the [TNM Tool for Mining of Socio-Technical Data from Git Repositories](https://github.com/JetBrains-Research/tnm)
- Publish as a python package to the community.

# Contributing 
Branch and pull mode. Please follow the basic guide on [https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project). 

Note you should not break the test runner bash script (testScrapLog.sh) that runs ScrapLogGit2Net agains test-data and compares with the expected output. 

Jose Teixeira, currently the only maintainer,  will review and merge pull requests, update the ChangeLog.txt, aknowledge the contribuitions and work on documentation on free-time from work. 

# Contributors 
Jose Teixeira

# Maintainers  
Jose Teixeira

# License 
GNU General Public License v3.0
