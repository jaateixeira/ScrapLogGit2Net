#! /usr/bin/env python3

# Transforms a network of individuals  Graphml File into a network of Organization Graphml file 
# Edge between of org. networks is the sum of developers that worked together
#
#  Example:
#  Nokia and Apple have three developers co-editing the same files
#  Nokia and Apple are then connected with a edge weight of 3 
# 


#Example of use verbose,fitering and only top firms
# ./transform-nofi-2-nofo-GraphML.py -v test-data/icis-2024-wp-networks-graphML/tensorFlowGitLog-2022-git-log-outpuyt-by-Jose.IN.NetworkFile.graphML

print ("transform-nofi-2-nofo-GraphML.py - transforming unweighted networks of individuals into weighted networks of organizations since June 2024")

exit()

import networkx as nx
import sys
import argparse
import os

global out_file_name



top_firms_that_matter = ['google','microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_matter = ['microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_do_not_matter = ['users','tensorflow','google']
top_firms_that_do_not_matter = ['users','tensorflow','gmail']

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="the network file")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
parser.add_argument("-t", "--top-firms-only", action="store_true",
                    help="only top_firms_that_matter")

parser.add_argument("-f", "--filter-by-org", action="store_true",
                    help="top_firms_that_do_not_matter")

parser.add_argument("-s", "--show", action="store_true",
                    help="show the visualization, otherwises saves to png and pdf")

parser.add_argument("-l", "--legend", action="store_true",
                    help="adds a legend to the sociogram")

parser.add_argument("-r", "--outside-legend-right", action="store_true",
                            help="the legend to the sociogram goes outside to the right")


args = parser.parse_args()



if args.verbose:
    print("In verbose mode")


if args.top_firms_only:
    print()
    print("In top-firms only mode")
    print()

if  args.filter_by_org:
    print()
    print("In filtering by org mode")
    print()


if args.show:
    print()
    print("In snow mode")
    print()
