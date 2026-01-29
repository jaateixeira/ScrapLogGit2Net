
How did we get the networks for the paper we submit ? 

= Get a clone of the TensorFLow repository ==  

The first step is to get a clone of the Tensor Flow repository  

```
$ git clone https://github.com/tensorflow/tensorflow.git
```

Then you need to get the logs with 
```
git log --pretty=format:"==%an;%ae;%ad==" --name-only 
```

We did it using [1-get-raw-inputs-all.sh](1-get-raw-inputs-all.sh)


On 24 Jan, we ran our last analysis 
Output will be saved to: ../raw-inputs/tensorflow_2026-01-24_all.IN.TXT




But then it should be done year by year 
```
git log --since='Jan 1 2021' --until='Dec 12 2021' --pretty=format:"==%an;%ae;%ad==" --name-only
```

We did it using [1-get-raw-inputs-yearly.sh](1-get-raw-inputs-yearly.sh)


We got the networks files 
networks-nofi-graphML/tensorflow_YEAR_network.IN.NetworkFile.graphML
The last being 
networks-nofi-graphML/tensorflow_2025_network.IN.NetworkFile.graphML

Those networks were then visualized to insure accuracy 

Many developer affiliations remain unkown in the networks (aka NetworkFile.graphML) files
 allowing the association of pseudo email addresses in the format [8 digit number]+[username]@users.noreply.github.com that are still associated with their GitHub profile. For example, a git commit from Ruslan Inovic rroinov@gmail.com might appear as 608192+rosmanov@users.noreply.github.com. See GitHub documentation on the issue at GitHub Docs. Once again using the GitHub GraphQL API (see https://docs.github.com/en/graphql) or the GitHub REST API (see https://docs.github.com/en/rest) wo

So the next steep was the to deanonymize  GitHub noreply emails in gramphML files created with ScrapLogGit2Net
ScraplogGit2Net was implemented for it provides  deanonymize_github_users.py

For running this step a GitHub account and a GITHUB_TOKEN is necessary 
It can not be provided, but we invited reproducer to create or use github account
and set the config.ini file with their GUT_HUB_TOJKEN 

The contents of config.ini look something like 
```
ghp_WvDYaPiQvzzsdftQvPBGuyNGxomuI3EDH2IrPsdf
```

See https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens 
for more information 

https://docs.github.com/en/rest/orgs/personal-access-tokens?apiVersion=2022-11-28 

The fastes way to test access to the GitHub REST API using the token is by 
running the following script 
```
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/orgs/ORG/personal-access-token-requests
```


At this point, after (1) retrieving the logs with git log, (2) scrapping them with ScrapLogGit2net and (3) deaninomizing the networks by using the GitHub restapi 

the following folders and files should be created by our scripts:
1-get-raw-inputs-all.sh  1-get-raw-inputs-yearly.sh  2-get-and-viz-networks-noi-graphml.sh   3-deanonymize-noi-graphml.sh


networks-nofi-graphML/:
tensorflow_2015_network.IN.NetworkFile.graphML  tensorflow_2015_network.out.graphML  tensorflow_2025_network.IN.NetworkFile.graphML  tensorflow_2025_network.out.graphML

raw-inputs/:
tensorflow_2026-01-24_all.IN.TXT  yearly_logs  yearly_summary_20260124.txt

raw-inputs/yearly_logs/:
tensorflow_2015_network.IN.TXT  tensorflow_2017_network.IN.TXT  tensorflow_2019_network.IN.TXT  tensorflow_2021_network.IN.TXT  tensorflow_2023_network.IN.TXT  tensorflow_2025_network.IN.TXT
tensorflow_2016_network.IN.TXT  tensorflow_2018_network.IN.TXT  tensorflow_2020_network.IN.TXT  tensorflow_2022_network.IN.TXT  tensorflow_2024_network.IN.TXT  tensorflow_2026_network.IN.TXT
 



