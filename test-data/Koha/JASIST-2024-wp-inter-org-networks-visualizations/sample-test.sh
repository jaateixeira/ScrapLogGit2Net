
#!/bin/bash

# Considering only top10

VIZ=''../../../formatFilterAndViz-nofo-GraphML.py''
VIZ_ARG=''

KOHA_NET_GraphML_PATH="../JASIST-2024-wp-networks-graphML"

echo TRANSFORMER=$TRANSFORMER
echo FILTER_ARG=$FILTER_ARG
echo KOHA_NET_GraphML_PATH=$KOHA_NET_GraphML_PATH

../../../formatFilterAndViz-nofo-GraphML.py -s -l ../JASIST-2024-wp-inter-org-networks-graphML/Koha-git-log-31-may-2016-31-may2017.NetworkFile-transformed-to-nofo.graphML
