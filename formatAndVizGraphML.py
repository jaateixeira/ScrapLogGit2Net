#! /usr/bin/env python3

# formats a graphml file
# calculates centralities
# layout according centralities
# colorize accourding to affiliation atribute
# nodesize according centralities 

#Example of use verbose,fitering and only top firms
# ./formatAndVizGraphML.py -svft test-data/icis-2024-wp-networks-graphML/tensorFlowGitLog-2022-git-log-outpuyt-by-Jose.IN.NetworkFile.graphML



import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import sys
import argparse
import os 
global out_file_name
import numpy as np
global prefix_for_figures_filenames 


top_firms_that_matter = ['google','microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_matter = ['microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_do_not_matter = ['users','tensorflow','google']
top_firms_that_do_not_matter = ['users','tensorflow']

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


if args.legend and args.outside_legend_right:
    print()
    print("legend should be outside of plot on the right")
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

isolate_ids=[]
for isolate in nx.isolates(G):
    isolate_ids.append(isolate)

if (isolate_ids != []):
    print("\t Isolates:")
    for node, data in G.nodes(data=True):
        if node in isolate_ids:
            print ("\t",node,data['e-mail'],data['affiliation'])



# We imported the graph and checked for isolates
# Shall we now do some filtering
# Will be implemented as fuction later 

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



for node, data in G.nodes(data=True):
    if node in ids_of_top_10_connected_ind:
        #print (node)
        print (data['e-mail'])
        top_10_connected_ind.append(data['e-mail'])






# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python 
print ("coloring by firm")



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
        org_colors.append('gray')


print(org_colors)



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



# setting size of node according centrality
# see https://stackoverflow.com/questions/16566871/node-size-dependent-on-the-node-degree-on-networkx



circular_options = { 
    'node_size': 10,
    'width': 0.1,
}


fig, ax = plt.subplots(figsize=(6, 4),  facecolor='0.7')

print ("")
print ("Saving circular layout")
# Random colors 1-256 
#nx.draw_circular(G,node_color=range(256),**circular_options)
nx.draw_circular(G,node_color=org_colors,**circular_options)


print ("")
print ("creating labels for top 10 org. with most nodes")

"top 10 org is on the  top_10_org list"
"color should be in top_10_colors otherwise "

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
       # Works but legend get cut
       fig.subplots_adjust(right=0.6)
       fig.legend(bbox_to_anchor=(0.9, 0.5),
                  borderaxespad=0,
                  loc=('center right'),
                  handles=legend_elements,
                  frameon=False,
                  prop={'weight': 'bold', 'size': 14, 'family': 'georgia'},
                  )
       "Comment to save legend in separate file" 
       #plt.gca().set_axis_off()
   else: 
       plt.legend(handles=legend_elements,
                  loc='best',

                  frameon=False,
                  prop={'weight': 'bold', 'size': 14, 'family': 'georgia'})     
       #plt.figtext(0, 0, "Visualization of "+(str(prefix_for_figures_filenames))+"on circular layout",  fontsize = 8) 

if args.show:
    
    plt.show()
else:
    plt.savefig(prefix_for_figures_filenames+"Uncolored-Circular-Layout.png",bbox_inches='tight')
    plt.savefig(prefix_for_figures_filenames+"Uncolored-Circular-Layout.pdf",bbox_inches='tight')

# Clear so graphs do not overlap each other
plt.clf()


exit()

spring_options = { 
#    'node_size': 10,
#   'width': 0.5,
}


print ()
print ("Saving centrality layout")
print ("Position nodes using Fruchterman-Reingold force-directed algorithm.")

"all nodes same size"
# nx.draw_spring(G, node_color=org_colors, **spring_options)
"all nodes size based on centrality"
nx.draw_spring(G, node_color=org_colors,node_size=[v * 100 for v in degree_centrality.values()], **spring_options)


ax = plt.gca()
#ax.legend(handles=legend_elements, loc='upper right')
if args.legend:
    ax.legend(handles=legend_elements, loc='best')

if args.show:
    plt.show()
else:
    plt.savefig(prefix_for_figures_filenames+"Uncolored-Centrality-Layout.png")
    plt.savefig(prefix_for_figures_filenames+"Uncolored-Centrality-Layout.pdf")

#print()
#print ("writing Formatted-NetworkFile.graphML")
#nx.write_graphml_lxml(G, "Formatted-NetworkFile.graphML")

