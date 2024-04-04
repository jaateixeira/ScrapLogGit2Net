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
`$git log --pretty=format:"==%an;%ae;%ad=="  --name-only`


# How to use it  #

- First you clone the GIT repository

`$ git clone https://github.com/tensorflow/tensorflow.git`
`$ cd tensorflow`

- Then you get the commit logs that will be used by ScrapLogGit2Net




`git log --pretty=format:"==%an;%ae;%ad=="  --name-only > tensorFlowGitLog.IN`

If you are lost by this point, time to learn about Git
`$man git`
`$man git log`



Congratulations you should have your raw data ready for analysis with ScrapLogGit2Net


Look at you INPUT data.  As you can see from the 4 April 2024 sample from TensorFlow, you get time.stamped data on who changed what files. Note that gardner@tensorflow.org is a bot. Not a developer that directly commits code. 

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


What ScrapLogGit2Net does is to parse this time-stamps and associate developers that co-edited the same source-code file in a social network.

Note the example year covers almost 10 years of commit logs in the TensorFlow project. It might be wise to narrow down the time window you want to analyse.


`$git log --pretty=format:"==%an;%ae;%ad=="  --name-only`

Based on https://stackoverflow.com/questions/37311494/how-to-get-git-to-show-commits-m here is what you need to run instead 

`$git log --pretty=format:"==%an;%ae;%ad=="  --name-only` | \
    awk '$1 >= "<after-date>" && $1 <= "<before-date>" { print $2 }' | \
    git log --no-walk --stdin


Dates must be in strict ISO format (YYYY-MM-DDThh:mm:ss e.g. 2021-04-20T13:30:00)

So to check the logs for first of April 2024 run:

`$git log --pretty=format:"==%an;%ae;%ad=="  --name-only` | awk '$1 >= "2024-05-01T:00:00:00" && $1 <= "2024-05-01T:23:59:59" { print $2 }' | git log --no-walk --stdin



