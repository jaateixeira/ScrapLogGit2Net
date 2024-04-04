Tool supporting the mining of GIT repositories
Creates social networks based on common source-code edits

Tool was first created by jose.teixeira@abo.fi


See Teixeira, J., Robles, G., & González-Barahona, J. M. (2015). Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. Journal of Internet Services and Applications, 6, 1-27. for more information. 
publicly available in open-acess as in  https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2


# Inputs #

A git repository


# Outputs #
Social networks capturing who codes who who in software project 

# How it works #

It uses the commit logs of a git repository
git log --pretty=format:"%an;%ae;%ad"  --name-only


# How to use it  #

- First you clone the GIT repository

`$ git clone https://github.com/tensorflow/tensorflow.git`
`$ cd tensorflow`

- Then you get the commit logs that will be used by ScrapLogGit2Net




`git log --pretty=format:"%an;%ae;%ad"  --name-only > tensorFlowGitLog.IN`

If you are lost by this point, time to learn about Git
`$man git`
`$man git log`



Congratulations you should have your raw data ready for analysis with ScrapLogGit2Net






