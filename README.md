docs/scrapLog-documentation.md 
# ScrapLogGit2Net
A toolset for mining and visualizing [Git](https://git-scm.com/) repositories with [Social Network Analysis](https://en.wikipedia.org/wiki/Social_network_analysis). ScrapLogGit2Net allows its users to scrape, model, and visualize social networks based on common source-code file edits for any given Git repository.

The toolset was first developed by [Jose Apolinário Teixeira](http://users.abo.fi/jteixeir/) during his doctoral studies with some guidance from Software Engineering scholars with expertise in the mining of software repositories. The tool merits by considering both individuals and organizations. The tool maps developers to organizations by the commit email address and external [APIs](https://en.wikipedia.org/wiki/API) such as the [REST](https://docs.github.com/en/rest?apiVersion=2022-11-28) and [GraphQL](https://docs.github.com/en/graphql) ones provided by [GitHub](https://github.com/).

Newer features allow you to:

- Transform a network of individuals/individuals into a network of organizations/firms. The weighted edge between organizations is the sum of developers that worked together (i.e., co-edited the same source-code files).
- Filter developers by email (handy to deal with bots that commit code)
- Support for parallel edges (i.e., multiple edges between two nodes) that allow attributing weight to a cooperative relationship between two developers (e.g., the number of times they co-edited a source code file).
- Visualize collaborations dynamically using [NetworkX is a Python package](https://networkx.org/documentation/latest/) and [Matplotlib: Visualization with Python](https://matplotlib.org/).

The code was also recently (i.e., Spring 2024) made compliant with the [NetworkX is a Python package](https://networkx.org/documentation/latest/) data structures and the [Python 3.10 version](https://networkx.org/documentation/latest/) runtime which simplified the original codebase.

For more information, see the publication and related website:

- Teixeira, J., Robles, G., & González-Barahona, J. M. (2015). Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. *Journal of Internet Services and Applications*, 6, 1-27. Available open-access at  [https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2](https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2).
- Website [http://users.abo.fi/jteixeir/OpenStackSNA/](http://users.abo.fi/jteixeir/OpenStackSNA/) with the obtained social networks and visualizations included [in publications by the author on the OpenStack software ecosystem](http://users.abo.fi/jteixeir/#pub).
- Website [http://users.abo.fi/jteixeir/TensorFlowSNA/](http://users.abo.fi/jteixeir/TensorFlowSNA/) with the obtained social networks and visualizations for the TensorFlow open and coopetitive project (publication forthcoming).

# Problem statement

Hard to figure out who works with whom in complex software projects.

# Vision

A world where software co-production analytics put social network visualizations at the side of standard quantitative statistical data. All towards the improved management and engineering of complex software projects orchestrated on Git.

# # Contributor Guide



Welcome to the project! We're excited to have you contribute to ScrapLogGit2Net. This guide will help you get started and ensure that your contributions are aligned with our project's standards.



\## Table of Contents

1\. [Setting Up Your Development Environment]\(#setting-up-your-development-environment)

2\. [Coding Style]\(#coding-style)

3\. [Architecture]\(#architecture)

4\. [Logging]\(#logging)

5\. [Progress Bars]\(#progress-bars)

6\. [Git Workflow]\(#git-workflow)

7\. [Easy Hacks]\(#easy-hacks)

8\. [Contact]\(#contact)



\## Setting Up Your Development Environment



1\. \*\*Fork the repository\*\* on GitHub.

&#x20;  To fork the ScrapLogGit2Net repository on GitHub, go to [https\://github.com/jaateixeira/ScrapLogGit2Net/]\(https\://github.com/jaateixeira/ScrapLogGit2Net/) . In the top right corner of the page, you will see a "Fork" button. Click on this button, and GitHub will create a copy of the repository under your GitHub account. This forked repository is now independent of the original repository, allowing you to freely make changes without affecting the original project. You can then clone your forked repository to your local machine, make your changes, and push them back to your fork on GitHub.



3\. \*\*Clone your forked repository\*\* to your local machine:

&#x20;  \`\`\`bash

&#x20;  git clone https\://github.com/jaateixeira/ScrapLogGit2Net.git



2\. Install the dependencies

&#x20;  See dependencies.sh



\## Coding Style&#x20;



We adopt the PEP 8 style guide towards writing clean, readable Python code.&#x20;



ScrapLogGit2Net started as quick script for scientific research. Fastly obtaining and processing data for research papers was the main goal. This is not a large, clean, object oriented, test-driven master piece.&#x20;

Still, good principles for Python programming apply:  (1) Follow naming conventions, (2) type check your function parameters, and careful use of global variables. Variables should have descriptive names in snake\_case for readability and consistency. Type hints should be used in function definitions to specify expected input and output types, enhancing code clarity and facilitating debugging. Accessing global variables should be minimized, as it can lead to code that is difficult to understand and maintain. Instead, use function parameters and return values to manage data flow whenever possible, promoting modularity and reducing side effects.





\### PEP 8 Coding Style Guide



PEP 8 is the style guide for Python code. It promotes readability and consistency in Python codebases. Following these guidelines will help improve the readability and maintainability of your code.



For the full PEP 8 documentation, please visit the official page: [PEP 8 -- Style Guide for Python Code]\(https\://peps.python.org/pep-0008/)



\#### Using flake8 for PEP 8 Compliance



\`flake8\` is a tool that checks your Python code against the PEP 8 style guide. It helps identify and fix stylistic issues in your code.



\#### Setting Up flake8



To install \`flake8\`, run the following command:



\`\`\`bash

pip install flake8

\`\`\`

\#### To check your Python files for PEP 8 compliance, navigate to your project directory and run:



\`\`\`bash

flake8 your\_module.py

\`\`\`





\### Allowed global variables&#x20;



The following global variable ex



Please use, the the built-in globals() function to access the global scope’s name table. This signals developers that we are dealing with a imporant global variable that we should not mess up with.&#x20;



TODO Table&#x20;



\| File              | Variable | Type | Description |

\| :---------------- | :------: |  :------: | ----: |

\| scrapLog.py       |   G\_network\_Dev2Dev\_singleEdges   | nx.Graph() | Inter individual network - edges are unweighted  |

\| scrapLog.py       |  G\_network\_Dev2Dev\_multiEdges |  nx.MultiGraph() | Inter individual network - edges can be weighted (using edge-attributes) |&#x20;

\| scrapLog.py       | stats | Dictionary (imutable keys) | Keeps statistics of the scrappping|&#x20;

\| formatFilterAndViz-nofi-GraphML.py   | TODO         |   TODO    | TODO |

\| transform-nofi-2-nofo-GraphML.py    | TODO         |   TODO    | TODO |

\| formatFilterAndViz-nofo-GraphML.py  | TODO         |   TODO    | TODO |















\## Project Architecture



The ScrapLogGit2Net project leverages several powerful Python libraries to achieve its functionality. This section provides an overview of the key libraries used and how they fit into the project's architecture.



![ScrapLogGit2Net Architecture Diagram]\(./ScrapLogGit2Net\_architecture.svg)



\### NumPy



\*\*NumPy\*\* is used for numerical operations, including the creation and manipulation of arrays and matrices. It provides support for large multi-dimensional arrays and matrices, along with a collection of mathematical functions to operate on these arrays efficiently.



\- \*\*Usage\*\*: NumPy is typically used for data manipulation, mathematical calculations, and handling large datasets.

\- \*\*Documentation\*\*: [NumPy Documentation]\(https\://numpy.org/doc/stable/)



\### NetworkX



\*\*NetworkX\*\* is utilized for creating, manipulating, and studying the structure, dynamics, and functions of complex networks. It allows for the creation of both undirected and directed graphs, along with various algorithms to analyze them.



\- \*\*Usage\*\*: NetworkX is used for constructing and analyzing network graphs, which is a core part of the project's functionality.

\- \*\*Documentation\*\*: [NetworkX Documentation]\(https\://networkx.org/documentation/stable/)



\### Matplotlib



\*\*Matplotlib\*\* is a plotting library used for creating static, interactive, and animated visualizations in Python. It is heavily used for generating plots, charts, and other graphical representations of data.



\- \*\*Usage\*\*: Matplotlib is used to visualize data, such as network graphs and other statistical plots.

\- \*\*Documentation\*\*: [Matplotlib Documentation]\(https\://matplotlib.org/stable/contents.html)



\### Argparse&#x20;



\### Rich

&#x20;the ScrapLogGit2Net repository on GitHub, go to https\://github.com/jaateixeira/ScrapLogGit2Net/ . In the top right corner of the page, you will see a "Fork" button. Click on this button, and GitHub will create a copy of the repository under your GitHub account. This forked repository is now independent of the original repository, allowing you to freely make changes without affecting the original project. You can then clone your forked repository to your local machine, make your changes, and push them back to your fork on GitHub.





\*\*Rich\*\* is a library for rich text and beautiful formatting in the terminal. It is used to create aesthetically pleasing and user-friendly command-line interfaces with features like progress bars, tables, and syntax highlighting.



\- \*\*Usage\*\*: Rich is used to enhance the terminal output, making it more informative and visually appealing, especially for progress indicators and formatted output.

\- \*\*Documentation\*\*: [Rich Documentation]\(https\://rich.readthedocs.io/en/stable/)





\*\*Rich\*\* is used for&#x20;



Printing colored text in the console (e.g., debug information)

Printing tex in the MarkDown format for better&#x20;

Priting emojis that reflect feeling in the console&#x20;

Inspect function to help you learn about objects

Colored Logging in integration Loguru&#x20;

Good looking Tables

Progress Bars and Wait Spinners

Better Looking Errors, with colored stacks&#x20;



See (https\://www\.youtube.com/watch?v=JrGFQp9njas)(https\://www\.youtube.com/watch?v=JrGFQp9njas) for a video tutorial&#x20;



\### Loguru



\*\*Loguru\*\* is a library designed for simple and effective logging. It simplifies the process of logging by providing an easy-to-use and powerful logging mechanism.



\- \*\*Usage\*\*: Loguru is used to handle logging throughout the project, ensuring that logs are informative, easy to read, and useful for debugging.

\- \*\*Documentation\*\*: [Loguru Documentation]\(https\://loguru.readthedocs.io/en/stable/)



\### Integration and Workflow



The integration of these libraries follows a well-structured workflow:

1\. \*\*Data Handling\*\*: NumPy is used to preprocess and handle data efficiently.

2\. \*\*Network Construction\*\*: NetworkX is used to construct and manipulate network graphs from the data.

3\. \*\*Visualization\*\*: Matplotlib is used to create visual representations of the network graphs and other data.

4\. \*\*User Interface\*\*: Rich is used to create an enhanced command-line interface for better user interaction.

5\. \*\*Logging\*\*: Loguru is used throughout the project to log important information, errors, and debugging details.



By leveraging these libraries, ScrapLogGit2Net achieves a robust, efficient, and user-friendly architecture that simplifies complex data operations, network analysis, visualization, and interaction.



For more detailed guidelines on how to contribute to the project, please refer to the rest of the \`CONTRIBUTING.md\` file.



Thank you for your contributions and helping improve ScrapLogGit2Net!





















Thank you for your interest in contributing to ScrapLogGit2Net! To ensure a smooth contribution process, please follow the instructions below to submit a pull request with a feature branch.



\## Git Workflow

1\. [Fork the Repository]\(#fork-the-repository)

2\. [Clone the Forked Repository]\(#clone-the-forked-repository)

3\. [Create a Feature Branch]\(#create-a-feature-branch)

4\. [Make Your Changes]\(#make-your-changes)

5\. [Commit Your Changes]\(#commit-your-changes)

6\. [Push Your Feature Branch]\(#push-your-feature-branch)

7\. [Create a Pull Request]\(#create-a-pull-request)

8\. [Respond to Feedback]\(#respond-to-feedback)



\### Fork the Repository



1\. Go to the [ScrapLogGit2Net repository]\(https\://github.com/jaateixeira/ScrapLogGit2Net) on GitHub.

2\. Click the \*\*Fork\*\* button in the upper right corner of the page. This will create a copy of the repository under your GitHub account.



\### Clone the Forked Repository



1\. Open your terminal or command prompt.

2\. Clone your forked repository to your local machine:

&#x20;  \`\`\`bash

&#x20;  git clone https\://github.com/your-username/ScrapLogGit2Net.git





Sync your fork:



bash



git checkout main

git pull upstream main

git push origin main



\### Create a Feature Branch&#x20;

Create a new branch for your feature/bugfix:



bash



git checkout -b feature-branch



Make your changes and commit them:



bash



git add .

git commit -m "Description of your changes"



Push your branch to GitHub:



bash



git push origin feature-branch





\### Submitting a Pull Request



&#x20;   Go to your fork on GitHub.

&#x20;   Click on the "New Pull Request" button.

&#x20;   Select the base fork and branch (our repository's main branch) and compare it with your feature-branch.

&#x20;   Create the pull request with a clear and detailed description of your changes.



\### Code Review Process



Once you submit your pull request, it will be reviewed by the project maintainers. Here’s what to expect:



&#x20;   Initial Review: We will review your code for adherence to the coding standards and overall implementation.

&#x20;   Feedback: You might receive feedback or requests for changes.

&#x20;   Approval: Once your pull request passes review, it will be merged into the main branch.



Please be responsive to feedback and make the necessary changes promptly to expedite the review process.





\## Contact



Jose Teixeira \<jose.teixeira\@abo.fi>&#x20;



\## Easy Hacks&#x20;

TODO&#x20;







**scrapLog.py** - Mines a Git log with SNA (associating developers that co-edit the same source-code files) and outputs a graphML network file (IN Git log -> GraphML).

- formatAndReport-nofi-GraphML.py - Outputs a spreadsheet full of inter-individual network metrics from a given graphML network file created with scrapLog (IN GraphML -> .csv or .xls).
- formatAndReport-nofo-GraphML.py - Outputs a spreadsheet full of inter-organizational network metrics from a given graphML network file created with scrapLog (IN GraphML ->  .csv or .xls).
- formatFilterAndViz-nofi-GraphML.py - Formats, filters, and visualizes a network of individuals from a given graphML network file created with scrapLog (IN GraphML -> pdf or png).
- formatFilterAndViz-nofo-GraphML.py - Formats, filters, and visualizes a network of organizations from a given graphML network file created with scrapLog (IN GraphML -> pdf or png).
- transform-nofi-2-nofo-GraphML.py - Transforms a network into a network of organizations Graphml file (IN graphML, OUT graphML).
- deanonymize\_github\_users.py - Deanonymizes developers' email and affiliation using GitHub REST API

# **scrapLog.py** Inputs

A Git repository and its commit logs.

# **scrapLog.py** Outputs

Social networks that capture who codes with whom in a repository (note that a software project can have multiple repositories).

# How  **scrapLog.py** works

It uses the commit logs of a Git repository
`git log --pretty=format:"==%an;%ae;%ad=="  --name-only`

- %an stands for author name
- %ae stands for author email
- %ad stands for author date

Then:

- It starts by identifying what source-code files were changed by whom at a given point in time.
- Then associates each file with the developers that co-edited the same source-code file.
- Then connects developers in a network. Nodes are software developers with a unique email. Edges are established if developers co-edited the same source-code file (i.e., nodes connect by working on the same files).

Note that:

- Some manual developer email aggregation might be required as the same developers can use multiple emails.

- Software bots can also commit code, undermining your analysis of human-to-human collaboration.

- Co-editing some files might not be an indicator of collaboration. It's like some scholars co-authoring articles where little or no cooperation existed as expected. For example, when analyzing projects in the C programming language, the co-editing of a Makefile might not be an indicator of collaboration, but instead an indicator of coordination.



# How to use **scrapLog.py**

You need basic skills of Git and basic skills on how to invoke Python scripts (test case scripts are implemented in bash). Knowing Python code will also help a lot.
You do not need to be a programmer to use ScrapLogGit2Net, but if you are one, and find it useful, please contribute to the project.

## First, clone a Git repository

Clone the Git repository you wish to mine with Social Network Analysis. Here is the example for TensorFlow:

```
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
```

## Second, get the Git logs for scraping

Obtain the commit logs that will be the main input for ScrapLogGit2Net. In this example, they are saved to the tensorFlowGitLog.IN file.
Note that data scraping is a technique where a computer program extracts data from human-readable output coming from another program. In this case ScrapLogGit2Net will extract data coming from Git.

```
git log --pretty=format:"==%an;%ae;%ad=="  --name-only > tensorFlowGitLog.IN
```

If you are lost by this point, time to learn about Git.

```
man git
man git log
```

Congratulations you should have your raw data ready for analysis with ScrapLogGit2Net

Look at your INPUT data.  As you can see from the following 4 April 2024 sample data from TensorFlow, you get timestamped data on who changed what files.
Note that [gardner@tensorflow.org](mailto\:gardner@tensorflow.org) is a bot, not a developer that directly commits code.

```
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
```

What ScrapLogGit2Net does is to parse these timestamps and associate developers that co-edited the same source-code file in a social network. If two developers co-edit the same source-code file over time, we can assume that they cooperate with each other. A bit like scientists that co-author papers.

Note the example year covers almost 10 years of commit logs in the TensorFlow project. It might be wise to narrow down the time window you want to analyze.

`git log --pretty=format:"==%an;%ae;%ad=="  --name-only`

In the following example, you are checking commit logs between 1st and 4th of April 2021

`git log --since='Apr 1 2021' --until='Apr 4 2021' --pretty=format:"==%an;%ae;%ad=="  --name-only`

And this example you check what developers did on 1st of April 2024

`git log --since='Mar 31 2024' --until='Apr 1 2024' --pretty=format:"==%an;%ae;%ad=="  --name-only`

Finally, the last example goes to the TensorFlow repository and gets the data to study the first trimester for 2024

`cd tensorflow && git log --since='Jan 1 2024' --until='Mar 31 2024' --pretty=format:"==%an;%ae;%ad=="  --name-only > tensorFlowGitLog-first-trimester-2024.IN `

- Now let's analyze some data.

## Scrape the data - Get basic statistics and social networks

```
./scrapLog.py  --raw  test-data/tensorFlowGitLog-first-trimester-2024.IN
```

or

```
`python3 scrapLog.py  -r test-data/tensorFlowGitLog-first-trimester-2024.IN
```

By default, and all goes well, you get a "NetworkFile.graphML" file prefixed with the data input filename (e.g., tensorFlowGitLog-first-trimester-2024.IN.NetworkFile.graphML) capturing the social network.
Congrats. You collected social network data ready for analysis.

# Known issues on mining Git repositories from a network perspective with ScrapLogGit2Net

ScrapLogGit2Net shines at mining Git repositories with Social Network Analysis because it takes a multi-level perspective. It tries to capture and model collaboration in terms of source-code file co-editing in terms of both individuals and organizations. It does that by trying to assign an organization attribute to each developer. An organization should be a firm, research institute, university, etc). However, it does it by looking at the email that developers set when pulling code contributions to the repository.

- If John pulls the code with [john@us.ibm.com](mailto\:john@us.ibm.com), John gets attributed with IBM.
- If Silvia pulls the code with [silvia@amazon.com](mailto\:silvia@amazon.com), Silvia gets attributed Amazon.com
- If Gregor pulls with [gregor@gmail.com](mailto\:gregor@gmail.com), Gregor gets associated with Gmail.

The approach works well, most of the time. But there are known issues that should be mitigated. Often by hard work, where data needs to be "cleaned" manually or using semi-automated approaches whenever possible.

## Getting firm attributes from emails

If a developer has two or more organization emails (e.g., works part-time for two organizations). Should it be treated as two developers!!  Or merged into one? This might require additional investigation on the developer and its contributions to figure out the best way to model the social network.
If a developer changes organization (e.g., changed email), by default ScrapLogGit2Net models him as another developer. You might want to model it in another way.
If a developer contributes with a personal email account (Gmail, Outlook) and with a firm account (e.g., IBM, Amazon) during the same period, what should be done? ScrapLogGit2Net associates the developer with Gmail. But it might make sense to associate him with the firm he also commits. Should contributions submitted with personal use email services (e.g., Gmail, Hotmail, Outlook) be considered as personal contributions that have nothing to do with an organization the developer works with?

When associating emails with developers, and developers with firms, it is a good approach to find suspicious similarities in the strings identifying actors in the network. The Python package [strsimpy](https://pypi.org/project/strsimpy/) implements many algorithms for string similarity. The names 'George Tony' and 'George Toony' have a very high string similarity score, so they are probably the same person. Test for similarity in names and emails to enhance the robustness of the social network model.

### A developer can have several emails!

There are many ways to deal with developers that use several emails. The simplest one is to use the approach by [Augustina Ragwitz (2017)](https://rstudio-pubs-static.s3.amazonaws.com/316662_7181d6efdd584358b935f7e444efb152.html), the
first email address found in the commit log for an author is then the authoritative one. According to her:

> While other methods should be explored and compared for better accuracy, this is sufficient to identify unique authors.

If the Git repository is hosted on GitHub, you can dig and solve this issue with more confidence by assessing the developer's profiles with your favourite programming language using the GitHub GraphQL API  (see  [https://docs.github.com/en/graphql](https://docs.github.com/en/graphql))  or the GitHub  REST API (see [https://docs.github.com/en/rest](https://docs.github.com/en/rest)).  For that, you will need the necessary permission with a GitHub account and an authentication token.  For Python lovers, PyGithub  is readily available  with methods that interface with the GitHub REST API
(see [https://pygithub.readthedocs.io/en/stable/introduction.html](https://pygithub.readthedocs.io/en/stable/introduction.html)).

Note, however, that GitHub GraphQL API was designed in a way that you can retrieve relational graph-oriented data more efficiently from large social networks.

If the Git repository is not hosted on GitHub, you can use the approach by [Teixeira, Leppänen and Hyrynsalmi (2020)](https://arxiv.org/pdf/2106.09329) that used pattern-matching techniques with regular expressions to identify unique names and emails. Note that in their study of code reviews on the Linux Kernel, they adopted a strictly extrarelational approach: individuals are identified by their real names, while all affiliations are based on explicit data extraction from the domain names in individuals’ e-mail addresses. ScrapLogGit2Net gets developers' IDs and their affiliations from e-mail addresses, simply ignoring their names.



### A developer can hide his email!

Most developers do not hide their email from the git logs. Like scientists in their articles, they want to keep their names as authors or contributors. However, they can remain anonymous or simply do not want to be contacted or avoid spam. This is popular since GitHub started allowing the association of pseudo email addresses in the format [8 digit number]+[username]@users.noreply.github.com that are still associated with their GitHub profile. For example, a git commit from Ruslan Inovic [rroinov@gmail.com](mailto\:rroinov@gmail.com) might appear as [608192+rosmanov@users.noreply.github.com](mailto:608192+rosmanov@users.noreply.github.com). See GitHub documentation on the issue at [GitHub Docs](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address#about-commit-email-addresses). Once again using the GitHub GraphQL API  (see  [https://docs.github.com/en/graphql](https://docs.github.com/en/graphql))  or the GitHub  REST API (see [https://docs.github.com/en/rest](https://docs.github.com/en/rest)) would allow mapping the @users.noreply.github.com with developers or other emails used by them. Note that once a developer commits code with an email, it will always be associated with him on GitHub. When a developer sets commits to be signed with a no-reply email, he is only affecting future commits, not the past recorded ones.

## Some collaborative edges are missed with longitudinal segmentation!

As pointed out by [Teixeira et al. (2015)](https://link.springer.com/article/10.1186/s13174-015-0028-2), when studying code-collaboration as a synchronous behaviour happening across different time windows (release after release or year after year), you will miss some collaboration edges between two developers who contributed to the same file that started before the time-window opened for analysis or did not end before the time-window closed. See [https://link.springer.com/article/10.1186/s13174-015-0028-2/figures/3](https://link.springer.com/article/10.1186/s13174-015-0028-2/figures/3).

A way to quantify this issue is to first analyze all the historical data. From day 0 to the last day save the edges. Then conduct the analysis in segments (e.g., year after year, release after release, etc). Then see how many edges there are in the network from all the time that were not captured by the time-limited analysis. 0 is ideal. But expect a few. Given that people tend to drop coding efforts before Xmas and New Year, or before releasing a new version (they as mostly stabilizing over developing new features), the impacts on the model validity are very small.

# Command line options for advanced use

- Use serialized changelogs so you don't need to use raw Git logs every time (speeds things up)
- Provide a configuration file with emails (aka developers) that should be ignored. Handy for ignoring bots that commit code
- Use verbose mode for debugging and testing

```
usage: scrapLog.py [-h] [-l LSER] [-r RAW] [-s SSER] [-fe FILTER_EMAILS] [-ff FILTER_FILES] [-v]

Scrape some changelog to create networks/graphs for research purposes

options:
  -h, --help            show this help message and exit
  -l LSER, --lser LSER  loads and processes a serialized changelog
  -r RAW, --raw RAW     processes from a raw Git changelog
  -s SSER, --sser SSER  processes from a raw Git changelog and saves it into a serialized changelog. Requires -r for input
  -fe FILTER_EMAILS, --filter_emails FILTER_EMAILS
                        ignores the emails listed in a text file (one email per line)
  -ff FILTER_FILES, --filter_files FILTER_FILES
                        ignores the files listed in a text file (one file per line)
  -v, --verbose         increased output verbosity
```

For example, the following command

\`\`\`./scrapLog.py -f test-configurations/TensorFlowBots.txt  -r test-data/tensorFlowGitLog-all-till-12-April-2024.IN --verbose\`\`

scrapes the Git log in the test-data/tensorFlowGitLog-all-till-12-April-2024.IN input file, ignores emails listed in the test-configurations/TensorFlowBots.txt file, and prints debug information in a verbose way. By default, it also creates a
network file in the standard XML-based format GraphML.

# Features

## Recently implemented features

- Export to the [GraphML](http://graphml.graphdrawing.org/) format for graphs based on XML. Exports undirected graphs with company affiliation attributes.
- Optional verbose debug output.
- Use of a serialized changelog, so we don't need to use RAW Git logs every time. Saves a lot of time for analyzing complex projects.
- Possibility of adding an argument pointing to a file with emails to ignore (e.g., bots and spam email addresses).
- Dynamic export of social network visualizations within the circular and centrality layouts.
- Dynamic node size based on degree centrality in the circular and centrality layouts. Highly connected nodes are bigger; less connected nodes are smaller.
- Transformation of unweighted inter-individual networks into weighted inter-organizational networks. The weight is equal to the number of inter-organizational relationships. Intra-organizational relationships are ignored.

## To implement (volunteers welcome)

- Cache the API requests using [https://pypi.org/project/requests-cache/](https://pypi.org/project/requests-cache/) as GitHub REST API replies are limited
- Test the possible integration with the PyGithub API library
- Account for co-authorships made explicit with the 'Co-authored-by:' string on the trailer of the commit's message [see documentation on https://docs.github.com/en/pull-requests](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors). Opens the way for triangulation.
- Account for commits on behalf of organizations using the 'on-behalf-of: @ORG NAME[AT]ORGANIZATION.COM' string on the trailer of the commit's message [see documentation on https://docs.github.com/en/pull-requests](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-on-behalf-of-an-organization).
- Possibility to add an argument pointing to a file with REGULAR EXPRESSIONS to capture emails to ignore (e.g., ignoring developers from a given company).
- Possibility to add an argument pointing to a file that aggregates different emails used by a different individual (e.g., John uses [John@ibm.com](mailto\:John@ibm.com) and [John@gmail.com](mailto\:John@gmail.com)).
- Possibility to add an argument pointing to a file that aggregates different emails used by different organizations (e.g., @ibm.com, @linux.vnet.ibm.com, @us.ibm.com, @cn.ibm.com all map IBM).
- Possibility to export both networks at the individual and organizational level (networks of individuals affiliated with organizations, and networks of organizations) during scraplog execution from Git log data.
- Possibility to limit analysis to n top contributors (organization with most nodes).
- Colorize nodes by company affiliation automatically.
- Report stats on the files connecting people the most (handy for identifying outliers).
- Support for weighted edges.
- Reporting analysis in LaTeX, Markdown, HTML, and text files. Should include quantitative metrics (e.g., n. commits, n. lines of code per dev, most co-edited files) and relational metrics (e.g., centrality, density).
- Support for other network formats besides GraphML (see [https://socnetv.org/docs/formats.html](https://socnetv.org/docs/formats.html)).
- Support for community detection.
- Use a logging system (e.g., [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html) or [https://github.com/gruns/icecream](https://github.com/gruns/icecream)) instead of print statements for debugging.
- Write unit tests for the main functions in ScrapLogGit2Net (see [https://docs.python.org/3/library/unittest.html](https://docs.python.org/3/library/unittest.html)).
- Use config files as there are already so many parameters.
- Integrate with the [TNM Tool for Mining of Socio-Technical Data from Git Repositories](https://github.com/JetBrains-Research/tnm). Cool, advanced, research-based but coded in Java. See [TNM tool presentation at MSR (2021) conference](https://www.youtube.com/watch?v=-NXaY8zTEOU).
- Integrate with the [git2net tool that also facilitates the extraction of co-editing networks from Git repositories.](https://github.com/gotec/git2net). Cool, advanced, research-based and also coded in Python. Has a more sophisticated approach to edges based on entropy and offers disambiguation features.
- Integrate with [https://www.logo.dev](https://www.logo.dev) API for allowing users to use company logos.
- Publish as a Python package to the community.

# Installation

## Linux

Most Linux distributions run ScrapLogGit2Net out of the box. See the file dependencies.sh if something is missing.

## Mac

1. Download a Python development environment such as [PyCharm](https://www.jetbrains.com/pycharm/).
2. Install the necessary packages using pip3 on the console (either on Mac terminal or inside your dev. env. like PyCharm).
3. pip3 install dateutils
4. pip3 install networkx
5. pip3 install colorama
6. pip3 install numpy
7. pip3 install matplotlib
8. pip3 install scipy

## Windows

1. Download a Python development environment such as [PyCharm](https://www.jetbrains.com/pycharm/).
2. Install the necessary packages using pip3 on the console (either on Mac terminal or inside your dev. env. like PyCharm).
3. pip3 install dateutils
4. pip3 install networkx
5. pip3 install colorama
6. pip3 install numpy
7. pip3 install matplotlib
8. pip3 install scipy

Across platforms, you can run test cases by invoking the bash script testScrapLog.sh available in the repository. If those cases run well, i.e., you get green color, you installed ScrapLogGit2Net successfully.

# Contributing

Please create a new branch for any new feature. Branch or fork, code, test, then pull request. Please follow the basic guide on [https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project).

Note you should not break the test runner bash script (testScrapLog.sh) that runs ScrapLogGit2Net against test-data and compares with the expected output. You might need to change the test runner to comply with new developments.

Jose Teixeira, currently the only maintainer, will review and merge pull requests, update the ChangeLog.txt, acknowledge the contributions, and work on documentation in free time from work.

# Contributors

Jose Teixeira

# Maintainers

Jose Teixeira

# License

GNU General Public License v3.0"

