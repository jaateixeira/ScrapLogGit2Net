# ScrapLogGit2Net
Tool supporting the mining of Git repositories. It creates social networks based on common source-code edits

Tool was first developed by Jose Apolinário Teixeira during his doctoral studies. 

For more information, see publication and related website: 

- Teixeira, J., Robles, G., & González-Barahona, J. M. (2015). Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. *Journal of Internet Services and Applications*, 6, 1-27. for more information. Available open-access at  [https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2](https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2).
- Website [http://users.abo.fi/jteixeir/OpenStackSNA/](http://users.abo.fi/jteixeir/OpenStackSNA/) with the obtained social networks and visualizations included in the publication. 




# Inputs #

A git repository


# Outputs #
Social networks capturing who codes who who in a repository (not a software project can have multiple repositories)

# How it works #

It uses the commit logs of a git repository
`$git log --pretty=format:"==%an;%ae;%ad=="  --name-only`

- %an stands for author name
- %ae stands for author email
- %ad stands for author date

# How to use it  #

You need basic skills of Git and basic skills on how to invoke shell scripts in bash.  Knowing python will also help a lot. 
You don't need to be a programmer to use ScrapLogGit2Net. But if you are one, please contribute by advancing the project. 

## First, clone a Git repository 

Clone the Git repository you wish to mine with Social Network Analysis. Here is the example for TensorFlow: 

```
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow`
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


`$git log --pretty=format:"==%an;%ae;%ad=="  --name-only`

In the following example you are checking commit logs between 1st and 4th of April 2021 

`$git log --since='Apr 1 2021' --until='Apr 4 2021' --pretty=format:"==%an;%ae;%ad=="  --name-only`
q
And this example you check what developers did on 1st of April 2024


`$git log --since='Mar 31 2024' --until='Apr 1 2024' --pretty=format:"==%an;%ae;%ad=="  --name-only`

Finally, the last example foes to the tensor flow reposiutory and gets the data to study the  first trimester for 2024

`cd tensorflow && git log --since='Jan 1 2024' --until='Mar 31 2024' --pretty=format:"==%an;%ae;%ad=="  --name-only > tensorFlowGitLog-first-trimester-2024.IN `


- Now lets analyse some data.

## Scrap the data - Get basic statistics and social networks 
```
./scrapLog.py  --raw  test-data/tensorFlowGitLog-first-trimester-2024.IN
```
or
```
`python3 scrapLog.py  test-data/tensorFlowGitLog-first-trimester-2024.IN`
```

By default, you get a "NetworkFile.graphML" file capturing the social network. 
Congrats. You collected social network data ready for analysis. 


# Command line options for advanced use

- Use serialized changelogs so you don't need to use raw git logs every time (speeds things up)
- Provide a configuration file with emails (aka developers) that should be ignored. Handy for ignoring bots that commit code
- Use verbose mode for debuging and testing 

```
usage: scrapLog.py [-h] [-l LSER] [-r RAW] [-s SSER] [-f FILTER] [-v]

Scrap some chagelog to create networks/graphs for research purpses

options:
  -h, --help            show this help message and exit
  -l LSER, --lser LSER  loads and processes an serialized changelog
  -r RAW, --raw RAW     processes from a raw git changelog
  -s SSER, --sser SSER  processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput
  -f FILTER, --filter FILTER
                        ignores the emails listed in a text file (one email per line)
  -v, --verbose         increased output verbosity
```

# Features 

## Implemented features 
- Export to the [GraphML][http://graphml.graphdrawing.org/] format for graphs based on XML. Exports undirected grapths with company affiliation atributes. 
- Verbose debug output
- Use of a serialized changelog, so we dont't need to use RAW git logs every time. Save a lot of time for analysing complext projects
- - Possibiliry to add a argument pointing with a file with emails to ignore (e.g., bots and spam email addresses)

## To implement (voluntears welcome)
- Possibiliry to add a argument pointing with a file with REGULAR EXPRESSIONS to capture emails to ignore (e.g., bots and spam email addresses)
- Possibiliry to add a argument pointing with a file what agregates different emails used by a different individual  (e.g., John uses <John@ibm.com> and <John@gmail.com>)
- Possibiliry to add a argument pointing with a file what agregates different emails used by a different individual (e.g., @ibm.com, @linux.vnet.ibm.com, @us.ibm.com, @cn.ibm.com)
OA- Possibliity to export both networks at individual and organizational level (networks of individuals affiliated with organizations, and networks of organizations)
- Possiblity to limit analysis to n top contriburors (organization with most nodes)
- Colorize nodes by company affiliation automaticaly 
- export with centrality layout
- automatic circular and centrality analysis using networkX

# Contributing 
Branch and pull mode. Please follow the basic guide on [https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project). 

Note you should not break the test runner bash script (testScrapLog.sh) that runs ScrapLogGit2Net agains test-data and compares with the expected output. 

Jose Teixeira, currently the only maintainer,  will review and merge the code and update the ChangeLog.txt and documentation if needed.  

# Contributors 
Jose Teixeira

# Maintainers  
Jose Teixeira

# License 
GNU General Public License v3.0
