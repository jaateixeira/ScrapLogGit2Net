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

print ("")
print ("transform-nofi-2-nofo-GraphML.py - transforming unweighted networks of individuals into weighted networks of organizations since June 2024")
print ("Let's go")
print ("")


"we need to handle networks"
import networkx as nx

"Needed to create dictionaries where value default is 0"
from collections import defaultdict

"we need system and operating systems untils"
import sys
import os

"we need to parse arguments" 
import argparse

"To call the visualization script as a subprocess" 
import subprocess 




"filtering of firms is not implemented yet" 
# top_firms_that_matter = ['google','microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
# top_firms_that_matter = ['microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
# top_firms_that_do_not_matter = ['users','tensorflow','google']
# top_firms_that_do_not_matter = ['users','tensorflow','gmail']


def printGraph_as_dict_of_dicts(graph):
    print (nx.to_dict_of_dicts(graph))


def printGraph_nodes_and_its_data(graph):
    
    for node, data in graph.nodes(data=True):
        print (node)
        print (data)

def printGraph_edges_and_its_data(graph):
    
    for edge in graph.edges(data=True):
        print (edge)

        
parser = argparse.ArgumentParser()

parser.add_argument("file", type=str, help="the network file")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")

parser.add_argument("-t", "--top-firms-only", action="store_true",
                    help="only top_firms_that_matter")

parser.add_argument("-f", "--filter-by-org", action="store_true",
                    help="top_firms_that_do_not_matter")

parser.add_argument("-s", "--show", action="store_true",
                    help="Shows/plots the result with formatAndViz-nofo-GraphML.py")


args = parser.parse_args()



if args.verbose:
    print("In verbose mode")


if args.top_firms_only:
    print()
    print("In top-firms only mode")
    print("Not implemented yet")
    sys.exit()

if  args.filter_by_org:
    print()
    print("In filtering by org mode")
    print("Not implemented yet")
    sys.exit()

if  args.show:
    print()
    print("Should display results")


# Lets read the graph then 
input_file_name = args.file

G = nx.read_graphml(input_file_name)


print ("Graph imported successfully")
print ("Number_of_nodes="+str(G.number_of_nodes()))
print ("Number_of_edges="+str(G.number_of_edges()))
print ("Number_of_isolates="+str(nx.number_of_isolates(G)))


if args.verbose:
    print() 
    print("printing graph:")
    printGraph_as_dict_of_dicts(G)
    print() 
    print("printing graph and its data:")
    printGraph_nodes_and_its_data(G)
    print() 


print ("")
print ("Checking for isolates")

    
isolate_ids=[]
for isolate in nx.isolates(G):
    isolate_ids.append(isolate)

if (isolate_ids != []):
    print("\t Isolates:")
    for node, data in G.nodes(data=True):
        if node in isolate_ids:
            print ("\t",node,data['e-mail'],data['affiliation'])

    print ("")
    print ("WARNING: Removing for isolates")
    print ("WARNING: Networks created with scraplog should only capture collaborative relationships (i.e., no isolates)")

    G.remove_nodes_from(isolate_ids)


print ("")
print ("Isolates removed successfully")
print ("Number_of_nodes="+str(G.number_of_nodes()))
print ("Number_of_edges="+str(G.number_of_edges()))
print ("Number_of_isolates="+str(nx.number_of_isolates(G)))

    
print ("")
print ("We have network of individuals")
print ("We don't have isolates")
print ("Lets transform it into a network of organizations")
print ("")


"G is the individual network"
"orgG is the organizational network"
"The edges in orgG have a atribute n equal to number of dev. that collaborated among organizations" 

orgG= nx.Graph()

# 
# TO TRANSFORM the following algorith is applied
# For each edge in G:
# If edge nodes are connected to developer of another companire  then add OrgX with weight 1.0 except if that relation was already modelled
#



# G.add_edge("a", "b", weight=0.6)

print ("")
print ("Iterating over all edges of G (network of individuals)")
print ("")

edges_count_down = G.number_of_edges()

# Creating edges for the organizational network


# Creates a dict with default values as zero.
org_edges = defaultdict(int)


# For every inter organization edge, finds what edges are inter-organizational and add the to org_edges
for edge in G.edges:

    org_affiliation_from = nx.get_node_attributes(G, "affiliation")[edge[0]]
    org_affiliation_to = nx.get_node_attributes(G, "affiliation")[edge[1]]

    print(f"Visiting edge{edge}, {edges_count_down} to go") 
    
    if args.verbose:
        print("")
        print("\t Edge info: "+ str(edge) + " FROM node id" + edge[0] + " TO node id" + edge[1] )
        print(f"\t {org_affiliation_from}  <-->  {org_affiliation_to}.")

        
    if org_affiliation_from == org_affiliation_to:
        if args.verbose:
            print ("\t Intra-firm relationship")
            print("\t\t To IGNORE")
        continue

    elif org_affiliation_from != org_affiliation_to:
        if args.verbose:
            print("\t Inter-firm relationship")
        # ## 
        org_edges[frozenset([org_affiliation_from, org_affiliation_to])] += 1
        if args.verbose:
            print(f"\t\t FOUND NEW orgG relation {org_affiliation_from}  <-->  {org_affiliation_to}. Increasing the weight atribute by 1 (default is 0)")
        
    edges_count_down-=1

# Add nodes and weighted edges to the inter-organizational network
if args.verbose:
    print("\n Adding nodes and weighted edges to the inter-organizational network:")

#for org_edge, weight in org_edges.items():
#    if args.verbose:
#        print(f"\n\t org_edge={org_edge=},weight={weight}")
 #   org_u, org_v = list(org_edge)
 #   if not orgG.has_node(org_u):
 #       orgG.add_node(org_u)
 #   if not orgG.has_node(org_v):
 #       orgG.add_node(org_v)
 #   orgG.add_edge(org_u, org_v, weight=weight)


print()
print("Showing current orgG (network of organizations):")
print()
print("\t The nodes:")
printGraph_nodes_and_its_data(orgG)
print("\t The edges:")
printGraph_edges_and_its_data(orgG)
print()


print()
print("Time to save orgG, the inter organizational network with weighted edges into the graphML format") 


def determine_file_name(name):
    counter = 0
    file_name = '{0}.graphML'.format(name)
    while os.path.exists(file_name):
        counter += 1
        file_name = '{0}({1}).graphML'.format(name, counter)
    return file_name


transformed_file_name = determine_file_name(os.path.basename(args.file[0:-8] + '-transformed-to-nofo'))

nx.write_graphml_lxml(orgG,transformed_file_name)

print(f"File saved at {transformed_file_name}")


if  args.show:
    print()
    print("Displaying the results")

    noo_viz_script="/home/apolinex/rep_clones/own-tools/ScrapLogGit2Net/formatAndViz-nofo-GraphML.py"

    
    # excape caraters to avoid "/bin/sh: 1: Syntax error: "(" unexpected"
                                 
    transformed_file_name= transformed_file_name.replace("(", "\(")
    transformed_file_name= transformed_file_name.replace(")", "\)")
    
    show_cmd = "python3 " + noo_viz_script + " " + transformed_file_name

    print(f"\n Invoking {show_cmd}")
    
    subprocess.call(show_cmd, shell=True)

print("DONE")
