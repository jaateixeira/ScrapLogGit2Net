Tool supporting the mining of GIT repositories
Creates social networks based on common source-code edits

Tool was first created by jose.teixeira@abo.fi


See Teixeira, J., Robles, G., & González-Barahona, J. M. (2015). Lessons learned from applying social network analysis on an industrial Free/Libre/Open Source Software ecosystem. Journal of Internet Services and Applications, 6, 1-27. for more information. 
publicly available in open-acess as in  https://jisajournal.springeropen.com/articles/10.1186/s13174-015-0028-2


# Inputs #

A git repository


# Outputs #
Social networks capturing who codes who who in a repository (not a software project can have multiple repositories) 

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


Look at you INPUT Data 

     A. Unique TensorFlower;gardener@tensorflow.org;Thu Apr 4 02:03:02 2024 -0700
tensorflow/python/compat/compat.py

	A. Unique TensorFlower;gardener@tensorflow.org;Thu Apr 4 02:02:37 2024 -0700
tensorflow/core/public/version.h

	A. Unique TensorFlower;gardener@tensorflow.org;Thu Apr 4 01:44:42 2024 -0700
	third_party/triton/cl617812302.patch
	third_party/triton/cl619146327.patch
	third_party/triton/cl619443019.patch
	third_party/triton/workspace.bzl
	third_party/xla/third_party/triton/cl617812302.patch
	third_party/xla/third_party/triton/cl619146327.patch
	third_party/xla/third_party/triton/cl619443019.patch
	third_party/xla/third_party/triton/workspace.bzl

	Adrian Kuegel;akuegel@google.com;Thu Apr 4 01:33:36 2024 -0700
	third_party/xla/xla/service/gpu/BUILD

