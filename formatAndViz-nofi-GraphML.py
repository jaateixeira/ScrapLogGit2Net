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



top_firms_that_matter = ['google','microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_matter = ['microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_do_not_matter = ['users','tensorflow','google']
top_firms_that_do_not_matter = ['users','tensorflow','gmail']

parser = argparse.ArgumentParser(prog="formatAndViz-nofi-GraphML.py",description="Formats and visualizes a graphML file capturing a unweighted network of individuals affiliated with organizations")

parser.add_argument("file", type=str, help="the network file (created by ScrapLogGit2Net)")

parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")

parser.add_argument("-p", "--plot", action="store_true",
                    help="plot the visualization (aka show), otherwises saves to png and pdf")

parser.add_argument("-l", "--legend", action="store_true",
                    help="adds a legend to the sociogram")

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


args = parser.parse_args()


if args.verbose:
    print("In verbose mode")
    print("Here is the list of arguments")
    print(f"\targs={args}")

if  args.org_list_to_ignore:
    print()
    print("In filtering by org mode - ignore given organizations")
    print("filter out developers affiliated with organizations in a given list. Example: -oi microsoft,meta,amazon")
    print(f'org_list_to_ignore={org_list_to_ignore}')
    print()


if args.org_list_only:
    print()
    print("In filtering by org mode - consider only the given organizations")
    print("consider only developers affiliated with organizations in a given list. Example: -oo google,microsoft")
    print(f'org_list_only={org_list_only}')
    print()

if args.org_list_and_neighbours_only:
    print()
    print('We should consider only a list of organizations and its neighbours')
    print("consider only developers affiliated with organizations in a given list and its neighbours (i.e., people they work with. Example: -on  nokia google")
    print(f'org_list_and_neighbours_only={args.org_list_and_neighbours_only}')
    print()


    
if args.plot:
    print()
    print("In show/plot  mode")
    print()


if args.legend and args.outside_legend_right:
    print()
    print("legend should be outside of plot on the right")
    print()

print()
print(f"Chosen network layout: {args.network_layout}")
print()
    



#print (args)
#exit()


input_file_name = args.file



G = nx.read_graphml(input_file_name)



prefix_for_figures_filenames= os.path.basename(input_file_name)



# I want alum to be alum.mit.edu # 
#	<data key="d0">rryan@alum.mit.edu</data>
# Only for ICIS paper 


for node, data in G.nodes(data=True):
    if (data['affiliation'] == 'alum'):
        data['affiliation'] = 'alum.mit.edu'


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



print ("Graph imported successfully")
print ("Number_of_nodes="+str(G.number_of_nodes()))
print ("Number_of_edges="+str(G.number_of_edges()))
print ("Number_of_isolates="+str(nx.number_of_isolates(G)))


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


print()
print("We imported the graph and check for isolates")
print("Let's now filter according the parameters -oi, -oo, -on")
print()


if args.filter_by_org:
    print()
    print("Filtering by org mode")
    print()

    print("\t removing nodes affiliated with", top_firms_that_do_not_matter)

    array_of_nodes_to_be_removed = []

    for node, data in G.nodes(data=True):
                if (data['affiliation'] in  top_firms_that_do_not_matter):
                        array_of_nodes_to_be_removed.append(node)
                        if args.verbose:
                            print ()
                            print ("\t\t Removing node",node,data)

    # Removes everybody affiliated  with top_firms_that_do_not_matter)
    G.remove_nodes_from(array_of_nodes_to_be_removed)



if args.top_firms_only:
    print()
    print("Removing edges not in top_firms_that_matter")
    print()

                        
    array_of_nodes_to_be_removed = []

    for node, data in G.nodes(data=True):
                if (data['affiliation'] not in top_firms_that_matter):
                        array_of_nodes_to_be_removed.append(node)
                        if args.verbose:
                            print ()
                            print ("\t\t Removing node",node,data)

    # Removes everybody affiliated  with top_firms_that_matter)
    G.remove_nodes_from(array_of_nodes_to_be_removed)
                                  

            
print ()
print ("Calculating centralities")

degree_centrality = nx.centrality.degree_centrality(G)  # sort by de

sorted_degree_centrality=(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))

#print ("degree_centrality")
if args.verbose:
    print (degree_centrality)
#print ("sorted_degree_centrality")
#print (sorted_degree_centrality)


top_10_connected_ind = []


print("\nTOP 10 ind. with most edges:")


top_10_connected_ind= sorted_degree_centrality[:10]

ids_of_top_10_connected_ind=(dict(top_10_connected_ind)).keys()


if args.verbose:
    print ("")
    print("Printing list of the most connected firms") 
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
print ()



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
print(f"Drawing network according given layout {args.networklayout} ...")


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



if args.networklayout == 'circular': 
    nx.draw_circular(G,node_color=org_colors,**circular_options)
elif args.networklayout == 'spring':
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
       
if args.show:
    plt.show()
else:
    if args.networklayout == 'circular':
        plt.savefig(prefix_for_figures_filenames+"Uncolored-Circular-Layout.png",bbox_inches='tight')
        print("\t See",prefix_for_figures_filenames+"Uncolored-Circular-Layout.png")
        plt.savefig(prefix_for_figures_filenames+"Uncolored-Circular-Layout.pdf",bbox_inches='tight')
        print("\t See",prefix_for_figures_filenames+"Uncolored-Circular-Layout.pdf")

    elif args.networklayout == 'spring':
            plt.savefig(prefix_for_figures_filenames+"Uncolored-Centrality-Layout.png",bbox_inches='tight')
            print("\t See file",prefix_for_figures_filenames+"Uncolored-Centrality-Layout.png")
            plt.savefig(prefix_for_figures_filenames+"Uncolored-Centrality-Layout.pdf",bbox_inches='tight')
            print("\t See file",prefix_for_figures_filenames+"Uncolored-Centrality-Layout.pdf")
    else:
        print("Error - Unknow network layout")
        sys.exit()


print()
print("DONE")
print("Hope you enjoy the inter-individual network with organizational affiliation atributes")
print()



