#! /usr/bin/env python3

# formats and visualizes a graphml file
# filters by organizational affiliation
# layout can be circular or spring (default)
# colorize accourding to affiliation atribute
# nodesize according centralities 

#Example of use verbose,fitering and only top firms with legend
# ./formatFilterAndViz-nofi-GraphML.py  -svtfl test-data/TensorFlow/icis-2024-wp-networks-graphML/tensorFlowGitLog-2015-git-log-outpuyt-by-Jose.IN.NetworkFile.graphML 


######################### How it works ##########################################
#  
# 1- Loads the networks as a networkX object
# 2- Data-cleasing 
# 3- Filtering by org mode (  --org_list_to_ignore args)
# 4- Removing nodes that are not affiliated with organizations in the given list -- args.org_list_only
# 5- Removing nodes that are not affiliated with organizations in the given list or do not collaborate with them (i.e., neighbours)
# 6- Calculates nodes centralities
# 7- Shows/plots and saves the network

#################################################################################


# For modelling networks 
import networkx as nx

# For visualizing networks 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D



# For logging/debugging 
import logging
import logging.config

# System utils 
import sys
import os

# For getting current time 
from datetime import datetime

# For parsing command line arguments 
import argparse

# For loading config files
import configparser

# For asking user what files to open and what files to save
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile

# For iterating objects with default values 
import numpy as np

# Required for coloring nodes randomly
import turtle, math, random, time

# To be able to load a dictionary key = firm, value = color
import json 



### START ###


##  Sets the logger  ##



def setup_logging():

    timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        encoding='utf-8',
                        #Comment to get logs to stdout 
                        #filename=f'./logs/formatFilterAndViz-nofi-GraphML-{timestamp}.log',
                        filemode='w')


def log_level_example():
    logging.debug("Debugging message")
    logging.info("Informational message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")

# instantiate logger
setup_logging()

# Some log level examples 
log_level_example()


logger = logging.getLogger(__name__)

# Predefined log levels include CRITICAL, ERROR, WARNING, INFO, and DEBUG from highest to lowest severity ### 
logger.setLevel(logging.INFO)


logger.info("Program started")





#logging.basicConfig(filename='', level=logging.INFO)

#logging.info('Started')
        


## Setting the the arguments ## 

# Define a custom argument type for a list of strings
def list_of_strings(arg):
    return arg.split(',')


parser = argparse.ArgumentParser(prog="formatFilterAndViz-nofi-GraphML.py",description="Formats and visualizes a graphML file capturing a unweighted network of individuals affiliated with organizations")

parser.add_argument('--version', action='version', version='%(prog)s Experimental')

parser.add_argument('infile', nargs='?', type=str, help="The network file (created by ScrapLogGit2Net)")


parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity.")

parser.add_argument("-g", "--GitHub", type=str, metavar="GitHubAuthToken",
                    help="Uses GitHub API to retrieve the latest and current affiliation for each node e-mail. Require authentication token.")

parser.add_argument("-p", "--plot", action="store_true",
                    help="Plot the visualization (aka show), otherwise saves to png and pdf.")

parser.add_argument("-nl", "--network_layout",  choices=['circular', 'spring'],  default='spring',
                    help="The type of network visualization layout (i.e., node positioning algorithm). Spring is the default")


parser.add_argument("-oi", "--org_list_to_ignore", type=list_of_strings,
                    help="Filter out developers affiliated with organizations in a given list. Example: -oi microsoft,meta,amazon.")

parser.add_argument("-oo", "--org_list_only", type=list_of_strings ,
                    help="Consider only developers affiliated with organizations in a given list. Example: -oo google,microsoft.")

#Depecrated for simplifing the arguments list 
#parser.add_argument("-to", "--top_org_list_only", choices=['top5','top10','top20','top10+1','top10+n'], default='top10',

parser.add_argument("-ot", "--org_list_top_only", choices=['top5','top10','top20'], default='top10',
                    help="Consider only developers affiliated with the top n organizations with most nodes. TOP 10 by default.")

parser.add_argument("-on","--org_list_and_neighbours_only", type=list_of_strings, help="consider only developers affiliated with organizations in a given list and its neighbours (i.e., people they work with. Example: -on  nokia google.")



parser.add_argument("-c","--org_list_in_config_file", type=str, help="Consider only developers affiliated with organizations in lists provided by a configuration file. Example -c test-configurations/filters.scraplog.conf.")


parser.add_argument("-a","--affiliation_alias_in_config_file", type=str, help="a list of email domain alias (e.g. cn.ibm.com = ibm). Example -c test-configurations/alias.scraplog.config.ini")



parser.add_argument("-nc", "--node_coloring_strategy", choices=['random-color-to-unknown-firms',
                                                                'gray-color-to-unknown-firms',
                                                                'gray-color-to-others-not-in-topn-filter'],
                    default='random-color-to-unknown-firms',
                    help="Some default colors exist in the firm_color dict (e.g., IBM is blue, RedHat is red, Nvidia is green) but how to color others? Set a coloring strategy. Default: random-color-to-unknown-firms.")


parser.add_argument("-ns", "--node_sizing_strategy", choices=['all-equal','centrality-score'],
                    default='centrality-score',
                    help="How big the nodes/developers should be? All equal or a function of their centrality?")


parser.add_argument("-l", "--legend", action="store_true",
                    help="Shows affiliation organizations legend to the sociogram - "
                         "by default shows the top 10 org with most nodes")


parser.add_argument("-ll", "--legend_location",
                    help="Sets where the legend should be displayed",
                    choices=['upper_right','upper_left',
                             'center_right','center_left',
                             'lower_right','lower_left',
                             'outside_center_right',
                             'outside_center_left',
                             'separate_file'], default='outside_center_right')



parser.add_argument("-lt", "--legend_type", choices=['top5','top10','top10+others','top20','top10+1','top10+1+others','top10+extra'],
                    default='top10',
                    help="The type of legend to be included. Top10+others is the default, affiliated with others are counted n.dev. / n.firms. With Top10+1, or top10+extra you need to provided also -le LEGEND_EXTRA_ORGANIZATIONS.")



parser.add_argument("-le", "--legend_extra_organizations", type=list_of_strings,
                    help="adds t othe legend some extra nodes gi. eg. -le mit,ibm." )


parser.add_argument("-s", "--save_graphML", action="store_true",
                            help="save a new graphML network based on organizations to consider and organizations to filter passed as argument (i.e., -on, -oo, -oi, -ot top10 ... top 20)")




logging.info("Parsing aguments")

args = parser.parse_args()


if args.verbose:
    print("In verbose mode")
    print("Here is the list of arguments")
    print(f"\targs={args}")

if not args.infile:
    print("GraphML file encoding network of individuals not provided")
    print("Asking user for a file to fix the issue")

    input_file_name= filedialog.askopenfilename()
else:
    print("\n GraphML file encoding network of individuals was provided")
    print(f"\t args.infile={args.infile}")
    input_file_name = args.infile

if not os.path.isfile(input_file_name):
    print (f"{input_file_name} is not a file as expected")
    print ("ERROR: ScrapLog expects a file")
    sys.exit()

# Not implemented
if args.GitHub:
    print("Before creating the visualization, we use GitHub API to retrieve the latest and current affiliation for each node e-mail")
    print("Require authentication token")
    print("Not implemented in public domain due to privacy, security and spam  issues that might arise with improper us of this feature")
    sys.exit()


if  args.org_list_to_ignore:
    print()
    print("In filtering by org mode - ignore given organizations")
    print("filter out developers affiliated with organizations in a given list. Example: -oi microsoft,meta,amazon")
    print(f'org_list_to_ignore={args.org_list_to_ignore}')
    print()


if args.org_list_only:
    print()
    print("In filtering by org mode - consider only the given organizations")
    print("consider only developers affiliated with organizations in a given list. Example: -oo google,microsoft")
    print(f'org_list_only={args.org_list_only}')
    print()

if args.org_list_and_neighbours_only:
    print()
    print('We should consider only a list of organizations and its neighbours')
    print("consider only developers affiliated with organizations in a given list and its neighbours (i.e., people they work with). Example: -on  nokia google")
    print(f'org_list_and_neighbours_only={args.org_list_and_neighbours_only}')
    print()


if args.org_list_top_only:
    print()
    print('We should consider only top organizations')
    print("consider only developers affiliated with organizations with most n nodes/developers (e.g., top 5, top 10,)")
    print(f"top mode ={args.org_list_top_only}")
    print()

    # Options are top5,top10,top20,top10+1,top10+n
    # But if we are using to10+1 or top10+n, we need to know that others to display and include in legend  --> Depecrated 

    if  args.org_list_top_only  == 'top10+1' and not args.legend_extra_organizations:
        print ("ERROR: If you want to consider only developers affilated with top10 + 1, provide one organization -le LEGEND_EXTRA_ORGANIZATIONS ")
        sys.exit()


    if  args.org_list_top_only == 'top10+n' and not args.legend_extra_organizations:
        print ("ERROR: If you want to consider only developers affilated with top10 + n, provide additional -le LEGEND_EXTRA_ORGANIZATIONS widh comma separated values")
        sys.exit()


    
if args.org_list_in_config_file:
    print("Filter by config files - not implemented yet")
    print("See test-configurations/filters.scraplog.conf")
    sys.exit()

if args.affiliation_alias_in_config_file:
    print("using e-mail domain names alias set in a config files")
    print("See for example test-configurations/alias.scraplog.config.ini")
    print(f"Considering then alias in {args.affiliation_alias_in_config_file}")
    
if args.plot:
    print()
    print("In show/plot  mode")
    print()


if args.legend == 'outside_center_right':
    print()
    print("legend should be outside of plot on the right")
    print()



if args.legend_type:

    print()
    print(f"legend type should be {args.legend_type}")
    print()

    # Legend_type must be in choices=['top5','top10','top10+others','top20','top10+1','top10+1+others','top10+n'], default='top10'

    # In the case of 'top10+1': there is one argument dependencie
    if args.legend_type == 'top10+1':
        if args.verbose:
            print ("\n \t With top10+1 as legend type:")
            print ("\t\t Show the 10 organizations with most nodes")
            print ("\t\t And the +1 organization from --org_list_and_neighbours_only")

        if not args.org_list_and_neighbours_only:
            print("\n ERROR: legend_type == 'top10+1+others' requires --org_list_and_neighbours_only ORG_LIST_AND_NEIGHBOURS_ONLY")
            print("\n Explanation: When somebody wants to see the neigbours of IBM, legend would be top 10 + IBM (the + 1).")
            print("\n Provide --org_list_and_neighbours_only and try again")
            sys.exit()

    # In the case of 'top10+1+others': there are two argument dependencies or one argument dependecie
    # if we are looking at neigbours onlythere are two argument dependencies if we are looking at neigbours only 
    # In the case of 'top10+1+others': there are two argument dependencies if we are looking at neigbours only
    if args.legend_type == 'top10+1+others' :
        if args.verbose:
            print ("\n \t With top10+1+others as legend type:")
            print ("\t\t Show the 10 organizations with most nodes")
            print ("\t\t And the +1 organization from --org_list_and_neighbours_only in org_list_and_neighbours_only")
            print ("\t\t And the others organizations are the list of -le LEGEND_EXTRA_ORGANIZATIONS")

    
        if args.org_list_and_neighbours_only and (not args.org_list_and_neighbours_only or not args.legend_extra_organizations):
            print("\n ERROR: legend_type == 'top10+1+others' requires -le LEGEND_EXTRA_ORGANIZATIONS when considering neighbours only (org_list_and_neighbours_only)")
            print("\n Explanation: When somebody wants to see the neigbours of IBM, legend would be top 10 + IBM (the + 1) and optionally list of others that do not make it to top10")
            print("\n Provide --org_list_and_neighbours_only and try again")
            sys.exit()

        if not  args.org_list_and_neighbours_only and not args.legend_extra_organizations:
            print("\n ERROR: legend_type == 'top10+1+others' requires -le LEGEND_EXTRA_ORGANIZATIONS when not considering neighbours only (org_list_and_neighbours_only)")
            print("\n Explanation: When somebody wants to see IBM along the top10 org, legend would be top 10 + IBM (the + 1) an optinally a list of others that do not make it to top10")
            print("\n Provide --org_list_and_neighbours_only and try again")
            sys.exit()

        
    
if args.legend_extra_organizations:
    print()
    print(f"We have some extra organizations to add to the legend {args.legend_extra_organizations}")
    print()


    

if args.save_graphML:
    print()
    print("Should save a new graphML network based on organizations to consider and organizations to filter passed a argument (i.e., -on, -oo, oi)")
    print("Should also consider export only  organization on top if argument -ot {top5,top10,top20} ")
    print("Might be wise to save the smaller inter-individual network")

print()
print(f"Chosen network layout: {args.network_layout}")
print()
    



#print (args)
#exit()





G = nx.read_graphml(input_file_name)

prefix_for_figures_filenames= os.path.basename(input_file_name)


def printGraph_as_dict_of_dicts(graph):
    print (nx.to_dict_of_dicts(graph))


def printGraph_notes_and_its_data(graph):
    
    for node, data in G.nodes(data=True):
        print (node)
        print (data)


if args.verbose:
    print() 
    print("printing graph:")
    printGraph_as_dict_of_dicts(G)
    print() 
    print("printing graph and its data:")
    printGraph_notes_and_its_data(G)
    print() 

    

initial_number_of_nodes= G.number_of_nodes()
initial_number_of_edges= G.number_of_edges()
initial_number_of_isolates= nx.number_of_isolates(G)

print ("Graph imported successfully:")
print (f"\t Initial number_of_nodes={initial_number_of_nodes}")
print (f"\t Initial number_of_edges={initial_number_of_edges}" )
print (f"\t Initial number_of_isolates={initial_number_of_isolates}")


print()
print("Now that graph is imported ...")
print("Let's do some data-cleaning hacks")

# For example I want alum to be alum.mit.edu #
#	<data key="d0">rryan@alum.mit.edu</data>
# I also want us.ibm to be ibm




if args.affiliation_alias_in_config_file:
    config = configparser.ConfigParser()
    config.read(args.affiliation_alias_in_config_file)

    aliases = dict(config['aliases'])
    print("\n\t List of aliases to be applied:")
    print("\t",aliases,"\n")


    for node, data in G.nodes(data=True):
        if (data['affiliation'] in aliases.keys()):

            # Special case for AGL data
            if data['affiliation']  == "jp":
                if "adit" in data['e-mail']:
                    data['affiliation'] = "ADIT"
                    print (f"WARNING: Special affiliation {data['e-mail']} set to ADIT")
                elif "panasonic"  in data['e-mail']:
                    data['affiliation'] = "Panasonic"
                    print(f"WARNING: Special affiliation {data['e-mail']} set to Panasonic")

                elif "fujitsu"  in data['e-mail']:
                    data['affiliation'] = "Fujitsu"
                    print(f"WARNING: Special affiliation {data['e-mail']} set to Panasonic")
                else:
                    print (f"Error: Conflicts with {args.affiliation_alias_in_config_file} conf file")
                    print (f"{data['affiliation']}")
                    print (f"{data['e-mail']}")
                    sys.exit(1)
            else: # DEFAULT us the alias
                data['affiliation'] = aliases[data['affiliation']]

        #print (f"node {node} with data={data} set to be affiliated with {data['affiliation']}")
        #print (node)

print("SUCESS - setting emails domain aliases based on conf file worked nicely")


print ("")
print ("Checking for isolates")

isolate_ids=[]
for isolate in nx.isolates(G):
    isolate_ids.append(isolate)

if (isolate_ids != []):
    print("\t Warning - Found isolates")
    print("\t Isolates:")
    for node, data in G.nodes(data=True):
        if node in isolate_ids:
            print ("\t",node,data['e-mail'],data['affiliation'])
elif isolate_ids == []:
    print ("\t No islolates founbd")


# We imported the graph and checked for isolates
# Shall we now do some filtering
# Will be implemented as fuction later 


def print_current_G_stats_after(action:str)-> None:
    print("\n\t\t-----------------------------------------------------")
    print(f"\t\t|     Stat   | Initial  | After {action}|")
    print(f"\t\t| n.  nodes  |\t{initial_number_of_nodes}\t|\t {G.number_of_nodes()}\t\t     |")
    print(f"\t\t| n.  edges  |\t{initial_number_of_edges}\t|\t {G.number_of_edges()}\t\t     |")
    print(f"\t\t| n. isolates|\t{initial_number_of_isolates}\t|\t {nx.number_of_isolates(G)}\t\t     |")
    print("\t\t-----------------------------------------------------")

print()
print("Status:after data-cleasing:")
print_current_G_stats_after("initial data cleasing")

    
print()
print("We imported the graph and check for isolates")
print("Let's now filter according the parameters -oi, -oo, -on")
print()



if args.org_list_to_ignore:
    print()
    print("Filtering by org mode ( -oi --org_list_to_ignore args)")
    print()

    print("\t removing nodes affiliated with", args.org_list_to_ignore,":")

    array_of_nodes_to_be_removed = []

    for node, data in G.nodes(data=True):
                if data['affiliation'] in  args.org_list_to_ignore:
                        array_of_nodes_to_be_removed.append(node)
                        if args.verbose:
                            print ()
                            print ("\t\t Removing node",node,data)

    # Removes everybody affiliated  with top_firms_that_do_not_matter)
    G.remove_nodes_from(array_of_nodes_to_be_removed)


print ()
print (f"SUCESS: filter out developers affiliated with organizations {args.org_list_to_ignore}")



print()
print("Status:after filtering out developers affiliated with organizations:")
print_current_G_stats_after("org_list_to_ignore   ")



if args.org_list_only:
    print()
    print("Removing nodes that are not affiliated with organizations in the given list ")
    print()
    print("\t removing nodes not affiliated with", args.org_list_only,":")

                        
    array_of_nodes_to_be_removed = []

    for node, data in G.nodes(data=True):
                if (data['affiliation'] not in args.org_list_only):
                        array_of_nodes_to_be_removed.append(node)
                        if args.verbose:
                            print ()
                            print ("\t\t Removing node",node,data)

    # Removes everybody affiliated  with top_firms_that_matter)
    G.remove_nodes_from(array_of_nodes_to_be_removed)
                                  


print ()
print (f"SUCESS: considered only developers affiliated with organizations in {args.org_list_only}")


print()
print("Status:after considerign only developers affiliated with organizations in {args.org_list_only}")
print_current_G_stats_after("org_list_only        ")



if args.org_list_and_neighbours_only:
    print()
    print("Removing nodes that are not affiliated with organizations in the given list or do not collaborate with them (i.e., neighbours)")
    print()
    print("\t removing nodes not affiliated with or not collaborating (i.e.,neighbours) with", args.org_list_and_neighbours_only,":")

    array_of_nodes_to_be_removed = []
    array_of_good_neighbours = []

    for node, data in G.nodes(data=True):
        if data['affiliation'] not in args.org_list_and_neighbours_only:
            if args.verbose:
                print ("\tConsidering what to do with" + node,data)
                print ("\tNeighbourhood" , G[node])
                print ("\tNeighbourhood affiliations")

                "Iterates over the neighbours of node"
                for neightbour_node in G[node]:
                    print(f"\t\t neighbour_node_id={neightbour_node}")
                    print(f"\t\t neighbour affiliation -> {nx.get_node_attributes(G, 'affiliation')[neightbour_node]}")

                node_neighbourhood_affiliations = []
                "Iterates over the neighbours of node"
                for neightbour_node in G[node]:
                    node_neighbourhood_affiliations.append(nx.get_node_attributes(G, 'affiliation')[neightbour_node])

                "At list one of the neighbourhood_affiliations needs to be in org_list_and_neighbours_only for the node to survive" 
                toDel = True
                for neightbour_affiliation in node_neighbourhood_affiliations:
                    if neightbour_affiliation in args.org_list_and_neighbours_only:
                        toDel = False
                        if args.verbose:
                            print(f"\t\t Not removing node {node} from {data['affiliation']}, as it have a neighbour from {neightbour_affiliation} that is in args.org_list_and_neighbours_only={args.org_list_and_neighbours_only} ")
                        array_of_good_neighbours.append(node)
                        break 

                if toDel:
                    array_of_nodes_to_be_removed.append(node)
                    if args.verbose:
                        print ("\t\t Removing node",node,data, "no good neighbours found!!")
            
                print ()
                

    # Removes everybody affiliated  with top_firms_that_matter)
    G.remove_nodes_from(array_of_nodes_to_be_removed)

    

print ()
print (f"SUCESS: considered only developers affiliated with organizations in {args.org_list_only} or developers that work with them (e.g, neighbours)")
if args.org_list_and_neighbours_only:
    print (f"\t removed nodes={array_of_nodes_to_be_removed}")
    print (f"\t array_of_good_neighbours={array_of_good_neighbours}")

    




print()
print("Status:after considerign only developers affiliated with organizations in in {args.org_list_only} or developers that work with them (e.g, neighbours)")
print_current_G_stats_after("list_and_neighbours  ")


# Tests that we did not end up with a empty graph
if G.number_of_nodes() == 0 :
    print (f"ERROR: After removing  some many developers, we got an empty network - Time to leave")
    sys.exit()
    



print("Now that we did all the filtering, it is time to calculate centralities at individual and org level")






print ()
print ("Calculating centralities")

degree_centrality = nx.centrality.degree_centrality(G)  # sort by de
sorted_degree_centrality=(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))


if args.verbose:
    print (f"degree_centrality={degree_centrality}")
    print (f"sorted_degree_centrality={sorted_degree_centrality}")


# For getting top5,top10,top20,top10+1,top10+n most connected individuals 
def get_top_n_connected_ind(n:int) -> list:
    return sorted_degree_centrality[:n]


# For getting top5,top10,top20,top10+1,top10+n most connected organizations 
def get_top_n_connected_org(n:int) -> list:
    print ("Not implemented")
    sys.exit()
    return None 

top_10_connected_ind= get_top_n_connected_ind(10)
ids_of_top_10_connected_ind=(dict(top_10_connected_ind)).keys()


top_5_connected_ind= get_top_n_connected_ind(5)
ids_of_top_5_connected_ind=(dict(top_5_connected_ind)).keys()



if args.verbose:
    print ("")
    print("Printing list of the most connected individuals") 
    print("n =", len(top_10_connected_ind))
    print()
    print
    print("top_10_connected_ind=",top_10_connected_ind)
    print("ids_of_top_10_connected_ind=",ids_of_top_10_connected_ind)


    print("\ne-mails of the most connected individuals:")
    for node, data in G.nodes(data=True):
        if node in ids_of_top_10_connected_ind:
            #print (node)
            print (f"\t {data['e-mail']}")
            top_10_connected_ind.append(data['e-mail'])



    
"find the top 5, top 10 and top 20  organization contributing"
all_affiliations_freq = {}
for node, data in G.nodes(data=True):
    affiliation = data['affiliation']
    #print (affiliation)
    if affiliation not in all_affiliations_freq.keys():
        all_affiliations_freq[affiliation] = 1
    else:
        all_affiliations_freq[affiliation] += 1
    

print("\nall_affiliations_freq:")
print(dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True)))


top_5_org =  dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True)[:5])
top_10_org =  dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True)[:10])
top_20_org =  dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True)[:20])
top_all_org  =  dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True))


if args.legend_type == 'top10+1+others':
    print ("\n As the specified legend is top10+1+others, we must calculate the number_of_org_not_intop_10_org and developers not in top10 \n ")
    
    # Counts size top_all_org sorted list after removing the first 10 elements 
    number_of_org_not_intop_10_org = len(list(top_all_org.keys())[10:])
    print(f"\n\t number_of_org_not_intop_10_org={number_of_org_not_intop_10_org}")

    print ("\n As the specified legend is top10+1+others, we must also calculate the number_of_ind_not_intop_10_org and developers not in top10 \n ")

    # First remove the top 10 keys from top_all_org 
    others_dict_org = {key: top_all_org[key] for key in top_all_org if key in top_10_org.keys()}

    # Then sum the keys of the remaining dictionary
    number_of_ind_not_intop_10_org=sum(others_dict_org.values())

    print(f"\n\t number_of_ind_not_intop_10_org ={number_of_ind_not_intop_10_org}")
    


    

print("\nTOP 20 org. with more nodes:")
for key in top_20_org:
    try:
        print (key, top_20_org[key])
    except KeyError:
        print(f"Top firm not in top_20_org dict")
        sys.exit()

print("\nTOP 10 org. with more nodes:")
for key in top_10_org:
    try:
        print (key, top_10_org[key])
    except KeyError:
        print(f"Top firm not in top_20_org dict")
        sys.exit()

print("\nTOP 5 org. with more nodes:")
for key in top_5_org:
    try:
        print (key, top_5_org[key])
    except KeyError:
        print(f"Top firm not in top_20_org dict")
        sys.exit()




    
        
print()
print(f"Drawing network according given layout {args.network_layout} ...")



# Given a coloring strategy passed as argument, returns how a node should be colored 
def get_nodes_color(coloring_strategy:str="random-color-to-unknown-firms")->list:

    coloring_strategy_possible_choices=['random-color-to-unknown-firms','gray-color-to-unknown-firms', 'gray-color-to-others-not-in-topn-filter']

    if coloring_strategy not in coloring_strategy_possible_choices:
        print ("ERROR Invalid coloring_strategy")
        sys.exit()
        

    if coloring_strategy not in ['random-color-to-unknown-firms','gray-color-to-unknown-firms']:
        print ("ERROR, Only 'random-color-to-unknown-firms' and 'gray-color-to-unknown-firms' coloring strategies were implemented so far")
        sys.exit()

    
    # The actual colors to be shown <- depend on top colors
    org_colors = []


    for node, data in G.nodes(data=True):
        #print (node)
        #print (data['affiliation'])

        node_affiliation = data['affiliation']
        if node_affiliation in list(firm_color.keys()):
            org_colors.append(firm_color[node_affiliation])
        else:
            if coloring_strategy == 'gray-color-to-unknown-firms':
                "Gray for everything not in firm_color"
                org_colors.append('gray')
                firm_color[data['affiliation']]= 'gray'
            elif coloring_strategy == 'random-color-to-unknown-firms':
                "random color for everyhing not in firm_color" 
                r = random.random()
                b = random.random()
                g = random.random()

                color = (r, g, b)
                org_colors.append(color)
                firm_color[data['affiliation']]= color
            else:
                print ("ERROR, Only 'random-color-to-unknown-firms' and 'gray-color-to-unknown-firms' coloring strategies were implemented so far")
                sys.exit()

    if org_colors == []:
        print ("ERROR: How come the list of colors to be shown is empty")
        sys.exit()


    if args.verbose:
        print()
        print("Showing color by organizational affiliation_")
        #print(org_colors)
        for node, data in G.nodes(data=True):
            print(f"\t color({data['affiliation']}) -->  {firm_color[data['affiliation']]}")
        print()

    return org_colors

def get_nodes_size()->list:
    # setting size of node according centrality
    # see https://stackoverflow.com/questions/16566871/node-size-dependent-on-the-node-degree-on-networkx
    return [v * 100 for v in degree_centrality.values()]


def get_legend_elements()->list:
    print ()
    print ("Getting the organizational affiliations to be included in the legend")
    print ("\t How should a legend look with the following arguments?")
    print (f"\t args.legend_type={args.legend_type}")
    print (f"\t args.legend_extra_organizations = {args.legend_extra_organizations}")
    print ()
    
    legend_items = []

    for org in top_20_org:
        try: 
            legend_items.append(Line2D([0], [0],
                                  marker='o',
                                  color=firm_color[org],
                                  label=org+" n=("+str(top_20_org[org])+")",
                                  lw=0,
                                  markerfacecolor=firm_color[org],
                                  markersize=5))
        except KeyError:
            print(f"Top firm {org}' color is not defined in firm_color dict")
            sys.exit()


    if args.legend_type == 'top5':
        print ("With top5 as legend type -> show the 5 organizations with most nodes")
        return legend_items[:5]

    elif args.legend_type == 'top10':
        print ("With to10 as legend type -> show the 10 organizations with most nodes")
        return legend_items[:10]

    elif args.legend_type == 'top20':
        print ("With top20 as legend type -> show the 20 organizations with most nodes")
        return legend_items[:20]

    elif args.legend_type == 'top10+1':
        print ("With top10+1 as legend type -> show the 10 organizations with most nodes")
        print ("And add the extra organization")
        print ("Here the extra organization is the first element of the list of -le LEGEND_EXTRA_ORGANIZATIONS")


        if not args.legend_extra_organizations:
            print("ERROR: requires -le LEGEND_EXTRA_ORGANIZATIONS")
            sys.exit()

        
        legend_items_top10_plus_one = legend_items[:10]
        legend_items_top10_plus_one.append( Line2D([0], [0],
                                  marker='o',
                                  color=firm_color[org],
                                  label=args.legend_extra_organizations[0] +" n=("+str(top_all_org[org])+")",
                                  lw=0,
                                  markerfacecolor=firm_color[org],
                                  markersize=5))
        
        
        return legend_items_top10_plus_one



    elif args.org_list_and_neighbours_only and args.legend_type == 'top10+1+others':
        print ("With top10+1+others as legend type -> show the 10 organizations with most nodes")
        print ("And add the extra organizations")
        print ("And then a count with developers affiliated with others:")
        print ("And then count with all other organizations")
        print ("Here the +1 is the organization passed in --org_list_and_neighbours_only")
        print ("Here the others organizations are the list of -le LEGEND_EXTRA_ORGANIZATIONS")

        print ("Requires -le LEGEND_EXTRA_ORGANIZATIONS and --org_list_and_neighbours_only")

        # Just in case the command line parser is not insuring the dependencies 
        if not args.org_list_and_neighbours_only or not args.legend_extra_organizations:
            print("\n ERROR: legend_type == 'top10+1+others' requires -le LEGEND_EXTRA_ORGANIZATIONS and --org_list_and_neighbours_only ORG_LIST_AND_NEIGHBOURS_ONLY")
            sys.exit()

        
        if args.verbose:
            print("\t Checking if is on the top_all_org")
            print(f"\t top_all_org={top_all_org}")


        legend_items_top10_plus_one = legend_items[:10]
        legend_items_top10_plus_one.append( Line2D([0], [0],
                                  marker='o',
                                  color=firm_color[org],
                                  label=args.legend_extra_organizations[0] +" n= ("+str(top_all_org[org])+")",
                                  lw=0,
                                  markerfacecolor=firm_color[org],markersize=5))
        
        legend_items_top10_plus_one.append( Line2D([0], [0], marker='o', color = 'gray',  label = f"others n.=({number_of_ind_not_intop_10_org})", lw=0, markerfacecolor='gray', markersize=5))
        legend_items_top10_plus_one.append( Line2D([0], [0], marker='o', color = 'gray',  label = f"others org.=({number_of_org_not_intop_10_org})", lw=0, markerfacecolor='gray', markersize=5))
        return legend_items_top10_plus_one


    elif not args.org_list_and_neighbours_only and args.legend_type == 'top10+1+others':
        print ("With top10+1+others as legend type  ouside of the filtering by neighbours -> show the 10 organizations with most nodes")
        print ("And add the extra organizations")
        print ("And then a count with developers affiliated with others:")
        print ("And then count with all other organizations")
        print ("Here the +1  is the first element of LEGEND_EXTRA_ORGANIZATIONS")

        print ("Requires -le LEGEND_EXTRA_ORGANIZATIONS ")


        if not args.legend_extra_organizations:
            print("\n ERROR: legend_type == 'top10+1+others' requires first element of -le LEGEND_EXTRA_ORGANIZATIONS")
            sys.exit()

        
        if args.verbose:
            print("\t Checking if is on the top_all_org")
            print(f"\t top_all_org={top_all_org}")


        legend_items_top10_plus_one = legend_items[:10]
        legend_items_top10_plus_one.append( Line2D([0], [0],
                                  marker='o',
                                  color=firm_color[org],
                                  label=args.legend_extra_organizations[0] +" n= ("+str(top_all_org[org])+")",
                                  lw=0,
                                  markerfacecolor=firm_colors[org],markersize=10))
        
        legend_items_top10_plus_one.append( Line2D([0], [0], marker='o', color = 'gray',  label = f"others n.=({number_of_ind_not_intop_10_org})", lw=0, markerfacecolor='gray', markersize=5))
        legend_items_top10_plus_one.append( Line2D([0], [0], marker='o', color = 'gray',  label = f"others org.={number_of_org_not_intop_10_org})", lw=0, markerfacecolor='gray', markersize=5))
        return legend_items_top10_plus_one


    
    elif args.legend_type == 'top10+n':
        print ("With top10+n as legend type -> show the q0 organizations with most nodes")
        print ("\t\t ERROR, very similar to top10+1 but not implemented yet")
        sys.exit()

    elif args.legend_type == 'top10+others':
        print("With top10+other as legend type -> All the ones not in top10 should be in grapy")
        print("\t\t ERROR, very similar to top10+1 but not implemented yet")
        sys.exit()

    else:
        print ("ERROR: Wrong kind of legend type")
        sys.exit()
    

    
    return legend_items




# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python
print()
print("Coloring by firm")
print()



# Loads the firm-color dictionary - Now we know how to map firm to a color
with open('business_firm_color_dictionary_json/firm_color_dict.json', 'r') as file:
    firm_color = json.load(file)


print()
print("Insuring every company have a color")
print()

get_nodes_color(args.node_coloring_strategy)



print("")
print("Start laying out the network")
print("Creating a 6 by 4 subplot ...")
fig, ax = plt.subplots(figsize=(6, 4),  facecolor='0.7')
print ("")









print("Drawing inter indovidual network in given layout ...")
print()


if args.network_layout == 'circular': 
    pos=nx.circular_layout(G)

    circular_options = { 
    'node_size': 200
    }

    
elif args.network_layout == 'spring':
    print ("Position nodes using Fruchterman-Reingold force-directed algorithm.")
    
    pos=nx.spring_layout(G)

    spring_options = { 
    }


      
else:
    print("Error - Unknow network layout")
    sys.exit()


    
print("Drawing inter individual network nodes ... ")


if args.network_layout == 'circular': 
    nx.draw_networkx_nodes(G, pos, node_shape='o', node_color=get_nodes_color(args.node_coloring_strategy),**circular_options)
    
elif args.network_layout == 'spring':
    nx.draw_networkx_nodes(G, pos, node_shape='o', node_color=get_nodes_color(args.node_coloring_strategy),node_size=get_nodes_size())
    #nx.draw_networkx_nodes(G, pos, node_shape='s', node_color=get_nodes_color(),node_size=[v * 100 for v in degree_centrality.values()])

else:
    print("Error - Unknow network layout")
    sys.exit()



print("Drawing inter individual network edges ... ")

nx.draw_networkx_edges(G, pos, width=1)




print ("")
print ("Network is now drawn - not visible yet")
print ("Creating now labels for the organizations  with most nodes :")

"top color org is on the"
"color should be in top_colors otherwise random color "





if args.legend:
   if  args.legend_location == 'outside_center_right':
       # Adjusts legend to the right so it does not cut the network 
       fig.subplots_adjust(right=0.6)
       fig.legend(bbox_to_anchor=(1.0, 0.5),
                  borderaxespad=0,
                  loc=('right'),
                  handles=get_legend_elements(),
                  frameon=False,
                  prop={'weight': 'bold', 'size': 12, 'family': 'georgia'},
                  )
       "Comment to save legend in separate file" 
       #plt.gca().set_axis_off()
   else:
       # Just puts it center right without adjusting the figure - legend might cover the nodes 
       fig.legend(handles=get_legend_elements(),
                  loc='center right',
                  frameon=False,
                  prop={'weight': 'bold', 'size': 12, 'family': 'georgia'})     
       #plt.figtext(0, 0, "Visualization of "+(str(prefix_for_figures_filenames))+"on circular layout",  fontsize = 8) 


#sys.exit()
       
print()
print("We have now nodes, edges and legend")
print("Let's show or save the inter-individual network")



if args.plot and args.verbose:
    print("In verbose mode:")
    print("\n Showing some debug info on the plot")

    
    plt.figtext(0.0,0.95,f"Visualization of {prefix_for_figures_filenames} on {args.network_layout} layout",  fontsize = 8)

    if args.GitHub:
        print ("\t We are resolving affiliations using GitHub API")
        plt.figtext(0.1, 0.2,f"Affiliations resolved using GitHub API",  fontsize = 8)
        
    if  args.org_list_to_ignore:
        print(f'\t org_list_to_ignore={args.org_list_to_ignore}')
        plt.figtext(0.5, 0.8,f'org_list_to_ignore={args.org_list_to_ignore}', fontsize=8)
    
    if args.org_list_only:
        print(f'\t org_list_only={args.org_list_only}')
        plt.figtext(0.5, 0.05,f'org_list_only={args.org_list_only}', fontsize=8)

    if args.org_list_and_neighbours_only:
        print(f'\t org_list_and_neighbours_only={args.org_list_and_neighbours_only}')
        plt.figtext(0.0, 0.5,f'org_list_and_neighbours_only={args.org_list_and_neighbours_only}',  fontsize=8)

    if args.org_list_top_only :
        print(f'\t top mode={args.org_list_top_only}')
        plt.figtext(0.1, 0.10,f'top mode={args.top_org_list_only} - Should show only developers affiliated with {args.top_org_list_only}',  fontsize=8)

    if args.legend_type:
        print(f'\t legend type={args.legend_type}')
        plt.figtext(0.1, 0.05,f"legend type={args.legend_type}", fontsize=8)

    if args.legend_extra_organizations:
        print(f'\t extra organizations to add to the legend {args.legend_extra_organizations}')
        plt.figtext(0.0, 0.8,f"We have some extra organizations to add to the legend {args.legend_extra_organizations}", fontsize=8)
    

if args.plot:
    fig.set_facecolor('white')
    ax = plt.gca()
    ax.set_facecolor('white')
    ax.margins(0.00)
    plt.axis("off")

    #plt.tight_layout()
    
    plt.show()
else:
    if args.network_layout == 'circular':
        plt.savefig(prefix_for_figures_filenames+"Uncolored-Circular-Layout.png",bbox_inches='tight')
        print("\t See",prefix_for_figures_filenames+"Uncolored-Circular-Layout.png")
        plt.savefig(prefix_for_figures_filenames+"Uncolored-Circular-Layout.pdf",bbox_inches='tight')
        print("\t See",prefix_for_figures_filenames+"Uncolored-Circular-Layout.pdf")

    elif args.network_layout == 'spring':
            plt.savefig(prefix_for_figures_filenames+"Uncolored-Centrality-Layout.png",bbox_inches='tight')
            print("\t See file",prefix_for_figures_filenames+"Uncolored-Centrality-Layout.png")
            plt.savefig(prefix_for_figures_filenames+"Uncolored-Centrality-Layout.pdf",bbox_inches='tight')
            print("\t See file",prefix_for_figures_filenames+"Uncolored-Centrality-Layout.pdf")
    else:
        print("Error - Unknow network layout")
        sys.exit()


print()
print("Everything went fine")

def determine_file_name(name):
    counter = 0
    file_name = '{0}.graphML'.format(name)
    while os.path.exists(file_name):
        counter += 1
        file_name = '{0}({1}).graphML'.format(name, counter)
    return file_name

if args.save_graphML:
    print("You should save the filtered network of individuals then ...")
    filtered_file_name = determine_file_name(os.path.basename(args.infile[0:-8] + '-filtered'))
    print("Saving filtered network to " + filtered_file_name )

    nx.write_graphml_lxml(G, filtered_file_name)
    print(f"See {filtered_file_name}")

    logger.info("Filtered GraphML file saved %s", filtered_file_name)

print()
print("DONE")
print("Hope you enjoy visualizing the inter-individual network with organizational affiliation atributes")
print()

logger.info("Program finished")
### END ### 


