#! /usr/bin/env python3

# formats and visualizes a graphml file
# layout can be circular or spring (default)
# colorize accourding to affiliation atribute
# nodesize according centralities 

#Example of use verbose,fitering and only top firms with legend
# ./formatAndViz-nofi-GraphML.py  -svtfl test-data/TensorFlow/icis-2024-wp-networks-graphML/tensorFlowGitLog-2015-git-log-outpuyt-by-Jose.IN.NetworkFile.graphML 


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx

import sys
import os

import argparse


import numpy as np
import turtle, math, random, time

# Define a custom argument type for a list of strings
def list_of_strings(arg):
    return arg.split(',')



parser = argparse.ArgumentParser(prog="formatAndViz-nofi-GraphML.py",description="Formats and visualizes a graphML file capturing a unweighted network of individuals affiliated with organizations")

parser.add_argument("file", type=str, help="the network file (created by ScrapLogGit2Net)")

parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")

parser.add_argument("-g", "--GitHub", type=str, metavar="GitHubAuthToken", help="Uses GitHub API to retrieve the latest and current affiliation for each node e-mail. Require authentication token")

parser.add_argument("-p", "--plot", action="store_true",
                    help="plot the visualization (aka show), otherwises saves to png and pdf")

parser.add_argument("-l", "--legend", action="store_true",
                    help="adds a affiliation attribute legend to the sociogram - by default shows the top 10 org with most nodes")

parser.add_argument("-r", "--outside_legend_right", action="store_true",
                            help="the legend to the sociogram goes outside to the right")

parser.add_argument("-s", "--save_graphML", action="store_true",
                            help="save a new graphML network based on organizations to consider and organizations to filter passed as argument (i.e., -on, -oo, oi)")

parser.add_argument("-nl", "--network_layout",  choices=['circular', 'spring'],  default='spring', help="the type of network visualization layout (i.e., node positioning algorithm)")

parser.add_argument("-oi", "--org_list_to_ignore", type=list_of_strings, 
                    help="filter out developers affiliated with organizations in a given list. Example: -oi microsoft,meta,amazon")

parser.add_argument("-oo", "--org_list_only", type=list_of_strings ,
                    help="consider only developers affiliated with organizations in a given list. Example: -oo google,microsoft")

parser.add_argument("-on","--org_list_and_neighbours_only", type=list_of_strings, help="consider only developers affiliated with organizations in a given list and its neighbours (i.e., people they work with. Example: -on  nokia google")


parser.add_argument("-lt", "--legend_type", choices=['top5','top10','top10+others','top20','top10+1','top10+1+others','top10+n'], default='top10',
                    help="the type of legend to be included  choices=['top5','top10','top10+others','top20','top10+1','top10+1+others','top10+n']. Top10+others is the default")


parser.add_argument("-le", "--legend_extra_organizations", type=list_of_strings,
                    help="adds t othe legend some extra nodes given in list of string. eg. -le mit,ibm." )


parser.add_argument("-lf", "--legend_in_separate_file",
                    help="Saves the legend is two separate files (png and pdf) - might be easier to include it in articles or websites")


parser.add_argument("-to", "--top_org_list_only", choices=['top5','top10','top20','top10+1','top10+n'], default='top10',
                    help="consider only developers affiliated with the top x organizations with most nodes. TOP 10 by default")


parser.add_argument("-c","--org_list_in_config_file", type=str, help="consider only developers affiliated with organizations in lists provided by a configuration file. Example -c test-configurations/filters.scraplog.conf")





args = parser.parse_args()


if args.verbose:
    print("In verbose mode")
    print("Here is the list of arguments")
    print(f"\targs={args}")


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
    print("consider only developers affiliated with organizations in a given list and its neighbours (i.e., people they work with. Example: -on  nokia google")
    print(f'org_list_and_neighbours_only={args.org_list_and_neighbours_only}')
    print()


if args.top_org_list_only:
    print()
    print('We should consider only top organizations')
    print("consider only developers affiliated with organizations with most n nodes/developers (e.g., top 5, top 10,)")
    print(f"top mode ={args.top_org_list_only}")
    print()

    
    
if args.org_list_in_config_file:
    print("Filter by config files - not implemented yet")
    print("See test-configurations/filters.scraplog.conf")
    sys.exit()
    
if args.plot:
    print()
    print("In show/plot  mode")
    print()


if args.legend and args.outside_legend_right:
    print()
    print("legend should be outside of plot on the right")
    print()



if args.legend_type:

    print()
    print(f"legend type should be {args.legend_type}")
    print()

if args.legend_extra_organizations:
    print()
    print(f"We have some extra organizations to add to the legend {args.legend_extra_organizations}")
    print()

    

if args.legend_in_separate_file:
    print()
    print("legend_in_separate_file: NOT IMPLEMENTED YET")
    sys.exit()
    print()
    

if args.save_graphML:
    print()
    print("Should save a new graphML network based on organizations to consider and organizations to filter passed a argument (i.e., -on, -oo, oi)")
    print("Might be wise to save the smaller inter-individual network")

print()
print(f"Chosen network layout: {args.network_layout}")
print()
    



#print (args)
#exit()


input_file_name = args.file


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

# I want alum to be alum.mit.edu # 
#	<data key="d0">rryan@alum.mit.edu</data>

# I also want us.ibm to be ibm


for node, data in G.nodes(data=True):
    
    if (data['affiliation'] == 'alum'):
        data['affiliation'] = 'alum.mit.edu'
        print (f"node {node} with data={data} set to be affiliated with alum.mit.edu")
        if 'mit' not in data['e-mail']:
            print ("ERROR - found a alumni account that is not related to MIT")
            sys.exit()
            
    if (data['affiliation'] == 'us'):
        data['affiliation'] = 'ibm'
        print (f"node {node} with data={data} set to be affiliated with ibm")
        if 'ibm' not in data['e-mail']:
            print ("ERROR - found a us affiliation that is not related to IBM")
            sys.exit()
            
print("SUCESS - data cleasing worked nicely")

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



# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python
print()
print("coloring by firm")
print()


# less common goes to gray
# Convention of black gro research institutes
# Gray for anunomous eemails
# Yellow for statups 
top_colors = {
    'google':'red',
    'nvidia':'lime',
    'intel':'lightblue',
    'amd':'black',
    'gmu':'brown',
    'arm':'steelblue',
    'amazon':'orange',
    'ibm':'darkblue',
    'linaro':'pink',
    'gtu':'black',
    'users': 'gray',
    'gmail': 'gray',
    'inailuig': 'gray',
    'bytedance': 'gray',
    'qq': 'gray',
    'hotmail': 'gray',
    'yahoo': 'gray',
    'outlook': 'gray',
    'gmail': 'gray',
    'tensorflow': 'white',
    'fastmail':'gray',
    'ornl':'gray',
    'meta':'blue',
    'polymagelabs':'gray',
    'cern': 'black',
    'nicksweeting': 'gray',
    'borgerding':'gray',
    'apache':'gray',
    'hyperscience':'gray',
    'microsoft': 'darkorange',
    'mit':'black',
    'alum':'gray',
    'us':'white',
    '163':'gray',
    'huawei':'darkred',
    'graphcore':'pink',
    'ispras': 'black',
    'gatech': 'black',
    'alum.mit.edu':'black',
    '126': 'gray',
}

# The actual colors to be shown <- depend on top colors
org_colors = []

# list with top 10 org contributors 
top_10 = {}

for node, data in G.nodes(data=True):
        #print (node)
    #print (data['affiliation'])

    affiliation = data['affiliation']
    if data['affiliation'] in list(top_colors.keys()):
        org_colors.append(top_colors[affiliation])
    else:
        "Gray for everything not in top_colors"
        #org_colors.append('gray')
        "random color for everyhing not in top_colors" 
        r = random.random()
        b = random.random()
        g = random.random()

        color = (r, g, b)
        org_colors.append(color)
        top_colors[data['affiliation']]= color


if args.verbose:
    print()
    print("Showing color by organizational affiliation_")
    #print(org_colors)
    for node, data in G.nodes(data=True):
        print(f"\t color({data['affiliation']}) -->  {top_colors[data['affiliation']]}")
    print()


    
"find the top 10 organization contributing"
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

top_10_org =  dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True)[:10])



print("\nTOP 10 org. with more nodes:")
for key in top_10_org:
    print (key, top_10_org[key]) 


print()
print(f"Drawing network according given layout {args.network_layout} ...")


# setting size of node according centrality
# see https://stackoverflow.com/questions/16566871/node-size-dependent-on-the-node-degree-on-networkx


circular_options = { 
    'node_size': 10,
    'width': 0.1,
}


spring_options = { 
#    'node_size': 10,
#   'width': 0.5,
}



print("")
print("Creating a 6 by 4 subplot ...")
fig, ax = plt.subplots(figsize=(6, 4),  facecolor='0.7')
print ("")



if args.network_layout == 'circular': 
    nx.draw_circular(G,node_color=org_colors,**circular_options)
elif args.network_layout == 'spring':
    print ("Position nodes using Fruchterman-Reingold force-directed algorithm.")
    nx.draw_spring(G, node_color=org_colors,node_size=[v * 100 for v in degree_centrality.values()], **spring_options)
else:
    print("Error - Unknow network layout")
    sys.exit()




print ("")
print ("Network is now drawn - not visible yet")
print ("Creating now labels for top 10 org. with most nodes")

"top color org is on the"
"color should be in top_colors otherwise random color "

for org in top_10_org:
    try:
        print (top_colors[org])
    except KeyError:
        print(f"Top firm {org}' color is not defined in top_colors")
        sys.exit()


legend_elements = []

for org in top_10_org:
    print (org)
    legend_elements.append(Line2D([0], [0],
                                  marker='o',
                                  color=top_colors[org],
                                  label=org+" n= ("+str(top_10_org[org])+")",
                                  lw=0,
                                  markerfacecolor=top_colors[org],
                                  markersize=5))


if args.legend:
   if  args.outside_legend_right:
       # Adjusts legend to the right so it does not cut the network 
       fig.subplots_adjust(right=0.6)
       fig.legend(bbox_to_anchor=(1.0, 0.5),
                  borderaxespad=0,
                  loc=('right'),
                  handles=legend_elements,
                  frameon=False,
                  prop={'weight': 'bold', 'size': 12, 'family': 'georgia'},
                  )
       "Comment to save legend in separate file" 
       #plt.gca().set_axis_off()
   else:
       # Just puts it center right without adjusting the figure - legend might cover the nodes 
       fig.legend(handles=legend_elements,
                  loc='center right',
                  frameon=False,
                  prop={'weight': 'bold', 'size': 12, 'family': 'georgia'})     
       #plt.figtext(0, 0, "Visualization of "+(str(prefix_for_figures_filenames))+"on circular layout",  fontsize = 8) 


print()
print("We have now nodes, edges and legend")
print("Let's show or save the inter-individual network")
       
if args.plot:
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
        file_name = '{0} ({1}).graphML'.format(name, counter)
    return file_name

if args.save_graphML:
    print("You should save the filtered network of individuals then ...")
    filtered_file_name = determine_file_name(os.path.basename(args.file[0:-8] + '-filtered'))
    print("Saving filtered network to " + filtered_file_name )

    nx.write_graphml_lxml(G, filtered_file_name)
    print(f"See{ filtered_file_name}")

print()
print("DONE")
print("Hope you enjoy the inter-individual network with organizational affiliation atributes")
print()



