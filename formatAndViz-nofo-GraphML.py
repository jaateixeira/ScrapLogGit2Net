#! /usr/bin/env python3

# Formats and visualizes a graphML file capturing a weighted Network of Organizations created by ScrapLog
# Edges thinkness maps its weight 
# Colorize nodes accourding to affiliation atribute


# Example of use: 
# ./formatAndViz-nofo-GraphML.py test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML-transformed-to-nofo.graphML 


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import networkx as nx
import sys
import os 
import argparse

import numpy as np

"needed to assign random colors"
import random

"need for logarithms"
import math 

def printGraph_as_dict_of_dicts(graph):
    print (nx.to_dict_of_dicts(graph))


def printGraph_nodes_and_its_data(graph):
    
    for node, data in graph.nodes(data=True):
        print ("\t"+ str(node))
        print ("\t" + str(data))

def printGraph_edges_and_its_data(graph):
    
    for edge in graph.edges(data=True):
        print ("\t"+str(edge))




print ("")
print ("formatAndViz-nofo-GraphML.py - visualizing weighted networks of organizations since June 2024")
print ("Let's go")
print ("")




#No filtering implemented yet
#top_firms_that_matter = ['google','microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_matter = ['microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_do_not_matter = ['users','tensorflow','google']
#top_firms_that_do_not_matter = ['users','tensorflow','gmail']

parser = argparse.ArgumentParser(prog="formatAndViz-nofo-GraphML.py",description="Formats and visualizes a graphML file capturing a weighted Network of Organizations")
parser.add_argument("file", type=str, help="the network file")

parser.add_argument("-n", "--networklayout",  choices=['circular', 'spring'],  default='spring', help="the type of network visualization layout (i.e., node positioning algorithm)")

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


print()
print(f"Chosen network layout: {args.networklayout}")
print()
    
    

input_file_name = args.file
G = nx.read_graphml(input_file_name)
prefix_for_figures_filenames= os.path.basename(input_file_name)



if args.verbose:
    print() 
    print("Printing inter-organizational network:")
    printGraph_as_dict_of_dicts(G)
    print() 
    print("printing graph notes and its data:")
    printGraph_nodes_and_its_data(G)
    print() 
    print("printing graph notes and its data:")
    printGraph_edges_and_its_data(G)
    print() 



print ("Inter organizational weighted Graph imported successfully")
print ("Number_of_nodes="+str(G.number_of_nodes()))
print ("Number_of_edges="+str(G.number_of_edges()))
print ("Number_of_isolates="+str(nx.number_of_isolates(G)))


# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python 
print ("coloring by firm")


# less common goes to gray
# Convention of black gro research institutes
# Gray for anunomous eemails
# Yellow for statups 
known_org_node_colors = {
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
    'rijksmuseum': 'orange',
}


print()
print("Assigning colors to organizations/nodes")
print()

# Colors to actually be shown - In known_org_node_colors or random color 
org_colors = []

for node  in G.nodes:
    #print (node)

    if node in list(known_org_node_colors.keys()):
        org_colors.append(known_org_node_colors[node])
    else:
        "Gray for everything not in top_colors - not in use"
        #org_colors.append('gray')
        "random color for everyhing not in top_colors" 
        r = random.random()
        b = random.random()
        g = random.random()

        random_color = (r, g, b)
        org_colors.append(random_color)

        "prevents the repetition of random colors"
        known_org_node_colors[node] = random_color


print("Colors assigned to organizations/nodes:")
print(org_colors)
print()



print("Drawing inter organizational network in given layout ...")
print()


if args.networklayout == 'circular': 
    pos=nx.circular_layout(G)
elif args.networklayout == 'spring':
    pos=nx.spring_layout(G)
else:
    print("Error - Unknow network layout")
    sys.exit()


print("Drawing inter organizational nodes ... ")

node_circular_options = { 
    'node_size': 200
}


nx.draw_networkx_nodes(G, pos, node_color=org_colors,**node_circular_options)




print("Drawing inter organizational edges ... ")

edge_circular_options = { 
}




print("\t Calculating edge thinkness ... ")

edge_thinkness=[]
for u,v,a in G.edges(data=True):
    "Using weights as they are"
    #edge_thinkness.append(a['weight'])
    "Using log base 2"
    edge_thinkness.append(1+math.log(a['weight'], 2))

print("\t  edge_thinkness = " + str(edge_thinkness))

nx.draw_networkx_edges(G, pos, width=edge_thinkness)



print("Drawing organizations  node labels") 
nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

print("Drawing inter-organizational edge weight labels") 


print("\t Calculating edge labels based on weight atribute ... ")

weight_labels = nx.get_edge_attributes(G, 'weight')
print("\t  weight_labels = " + str(weight_labels))

#nx.draw_networkx_edge_labels(G, pos, edge_labels)
nx.draw_networkx_edge_labels(G, pos, edge_labels=weight_labels)  


ax = plt.gca()
ax.margins(0.08)
plt.axis("off")
plt.tight_layout()
plt.show()


print("")
print("DONE")
print("")
