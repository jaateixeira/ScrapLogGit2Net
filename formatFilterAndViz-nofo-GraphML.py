#! /usr/bin/env python3

# Formats and visualizes a graphML file capturing a weighted Network of Organizations created by ScrapLog
# Edges thickness maps its weight
# Colorize nodes according to affiliation attribute


# Example of use: 
# ./formatAndViz-nofo-GraphML.py test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML-transformed-to-nofo.graphML 


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import networkx as nx

# SYS and OS utils 
import sys
import os

# For parsing arguments 
import argparse


"needed to assign random colors"
import random

"need for logarithms"
import math

# To be able to load a dictionary key = firm, value = color
import json

from rich import (print as rprint)
# For nicer terminal outputs


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

parser.add_argument("-n", "--network_layout",  choices=['circular', 'spring'],  default='spring', help="the type of network visualization layout (i.e., node positioning algorithm)")

parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")

parser.add_argument("-ns", "--node_sizing_strategy", choices=['all-equal','centrality-score'],
                    default='centrality-score',
                    help="How big the nodes/developers should be? All equal or a function of their centrality?")

parser.add_argument("-nc", "--node_coloring_strategy", choices=['random-color-to-unknown-firms',
                                                                'gray-color-to-unknown-firms',
                                                                'gray-color-to-others-not-in-topn-filter'],
                    default='random-color-to-unknown-firms',
                    help="Some default colors exist in the firm_color dict (e.g., IBM is blue, RedHat is red, Nvidia is green) but how to color others? Set a coloring strategy. Default: random-color-to-unknown-firms.")


parser.add_argument("-t", "--top-firms-only", action="store_true",
                    help="only top_firms_that_matter")

parser.add_argument("-f", "--filter-by-org", action="store_true",
                    help="top_firms_that_do_not_matter")

parser.add_argument("-s", "--show", action="store_true",
                    help="show the visualization, otherwise saves to png and pdf")

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

if args.filter_by_org:
    print()
    print("In filtering by org mode")
    print()

if args.show:
    print()
    print("In snow mode")
    print()

if args.legend:
    print()
    print("Show a legend")
    print()
    
if args.legend and args.outside_legend_right:
    print()
    print("legend should be outside of plot on the right")
    print()


print()
print(f"Chosen network layout: {args.network_layout}")
print()

print (f"Visualizing the {args.file} inter organizational network created with transform-nofi-2-nofo-GraphML.py")

# Reads the GraphML network using NetworkX
input_file_name = args.file

G = nx.read_graphml(input_file_name)
prefix_for_figures_filenames = os.path.basename(input_file_name)

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


print("Inter organizational weighted Graph imported successfully")
print("Number_of_nodes="+str(G.number_of_nodes()))
print("Number_of_edges="+str(G.number_of_edges()))
print("Number_of_isolates="+str(nx.number_of_isolates(G)))


print ()
print ("Calculating centralities")

degree_centrality = nx.eigenvector_centrality(G)  # sort by de
sorted_degree_centrality=(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))



# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python 
print("coloring by firm")


# less common goes to gray
# Convention of black gro research institutes
# Gray for anonymous e-mails
# Yellow for startups

# Loads the firm-color dictionary - Now we know how to map firm to a color
with open('business_firm_color_dictionary_json/firm_color_dict.json', 'r') as file:
    known_org_node_colors = json.load(file)



print()
print("Assigning colors to organizations/nodes")
print()

# Colors to actually be shown - In known_org_node_colors or random color 
org_colors = []

for node in G.nodes:
    if args.verbose:
        print(f"node={node}")
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


if args.network_layout == 'circular':
    pos = nx.circular_layout(G)
elif args.network_layout == 'spring':
    pos = nx.spring_layout(G)
else:
    print("Error - Unknow network layout")
    sys.exit()


print("Drawing inter organizational nodes ... ")


def get_nodes_color(coloring_strategy: str = "random-color-to-unknown-firms") -> list:
    coloring_strategy_possible_choices = ['random-color-to-unknown-firms', 'gray-color-to-unknown-firms',
                                          'gray-color-to-others-not-in-topn-filter']

    if coloring_strategy not in coloring_strategy_possible_choices:
        print("ERROR Invalid coloring_strategy")
        sys.exit()

    if coloring_strategy not in ['random-color-to-unknown-firms', 'gray-color-to-unknown-firms']:
        print(
            "ERROR, Only 'random-color-to-unknown-firms' and 'gray-color-to-unknown-firms' coloring strategies were implemented so far")
        sys.exit()

    # The actual colors to be shown <- depend on top colors
    org_colors = []

    for node in G.nodes(data=False):
        # print (node)
        # print (data['affiliation'])


        if node in list(known_org_node_colors.keys()):
            org_colors.append(known_org_node_colors[node])
        else:
            if coloring_strategy == 'gray-color-to-unknown-firms':
                "Gray for everything not in firm_color"
                org_colors.append('gray')
                known_org_node_colors[node] = 'gray'
            elif coloring_strategy == 'random-color-to-unknown-firms':
                "random color for everyhing not in firm_color"
                r = random.random()
                b = random.random()
                g = random.random()

                color = (r, g, b)
                org_colors.append(color)
                known_org_node_colors[node] = color
            else:
                print(
                    "ERROR, Only 'random-color-to-unknown-firms' and 'gray-color-to-unknown-firms' coloring strategies were implemented so far")
                sys.exit()

    if org_colors == []:
        print("ERROR: How come the list of colors to be shown is empty")
        sys.exit()

    if args.verbose:
        print()
        print("Showing color by organizational affiliation_")
        # print(org_colors)
        for node in G.nodes(data=False):
            print(f"\t color({node}) -->  {known_org_node_colors[node]}")
        print()

    return org_colors


def get_nodes_size()->list:
    custom_factor = 20
    # setting size of node according centrality
    # see https://stackoverflow.com/questions/16566871/node-size-dependent-on-the-node-degree-on-networkx
    return [v * custom_factor * 100 for v in degree_centrality.values()]


if args.verbose:
    print("\n Node sizes \n \t")
    rprint(get_nodes_size())

node_circular_options = {
    'node_size': 10,
}


node_spring_options = {
'alpha':0.75
}



print("Drawing inter individual network nodes ... ")

if args.network_layout == 'circular':
    nx.draw_networkx_nodes(G, pos, node_shape='o', node_color=get_nodes_color(args.node_coloring_strategy),
                           **node_circular_options)

elif args.network_layout == 'spring':
    nx.draw_networkx_nodes(G, pos, node_shape='o',
                           node_size=get_nodes_size(),
                           node_color=get_nodes_color(args.node_coloring_strategy),
                           **node_spring_options)
    # nx.draw_networkx_nodes(G, pos, node_shape='s', node_color=get_nodes_color(),node_size=[v * 100 for v in degree_centrality.values()])

else:
    print("Error - Unknow network layout")
    sys.exit()






print("Drawing inter organizational edges ... ")

edge_options = {
'alpha':0.2
}




print("\t Calculating edge thinkness ... ")

edge_thickness = []
for u,v,a in G.edges(data=True):
    if args.verbose:
        print(f"u={u}, v={v}, a={a}")
    "Using weights as they are"
    #edge_thickness.append(a['weight'])
    "Using log base 2"
    edge_thickness.append(1+math.log(a['weight'], 2))


if args.verbose:
    print("\t  edge_thickness:")
    rprint(edge_thickness)

nx.draw_networkx_edges(G, pos, width=edge_thickness, **edge_options)

print("Drawing organizations  node labels") 
nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif",font_weight="bold", font_color='black',alpha=1.0)

print("Drawing inter-organizational edge weight labels") 


print("\t Calculating edge labels based on weight attribute ... ")

weight_labels = nx.get_edge_attributes(G,name='weight')
print("\t  weight_labels = " + str(weight_labels))

#nx.draw_networkx_edge_labels(G, pos, edge_labels)
nx.draw_networkx_edge_labels(G, pos, edge_labels=weight_labels)  


def get_legend_elements(known_org_colors:list)->list:
    print()
    print("Getting the organizational affiliations to be included in the legend")
    print("\t How should a legend look with the following arguments?")
    print()
    
    legend_items = []
    for org  in G.nodes:
        try:
            if args.verbose:
                print(f"Adding legend to organization/node={org}")
            legend_items.append(Line2D([0], [0],
                                       marker='o',
                                       color=known_org_colors[org],
                                       label=org,
                                       lw=0,
                                       markerfacecolor=known_org_colors[org],
                                       markersize=5))
        except KeyError:
            print(f"Dirm {org}' color is not defined in top_colors")
            sys.exit()

        #legend_items_top10_plus_one = legend_items[:10]
        #egend_items_top10_plus_one.append( Line2D([0], [0],
        #                         marker='o',
        #                         color=top_colors[org],
        #                         label=args.legend_extra_organizations[0] +" n=("+str(top_all_org[org])+")",
        #                         lw=0,
        #                         markerfacecolor=top_colors[org],
        #                         markersize=5))
                
    return legend_items



if args.legend:
    print("\t Adding a legend") 

    plt.legend(handles=get_legend_elements(known_org_node_colors),
               loc='right',
               frameon=False,
               prop={'weight': 'bold', 'size': 12, 'family': 'georgia'})






ax = plt.gca()
ax.margins(0.08)

custom_radius= 0.15
Drawing_colored_circle = plt.Circle(pos['chromium'], custom_radius, fill=False, alpha=0.5)


ax.add_artist(Drawing_colored_circle)
#plt.title('Colored Circle')


plt.axis("off")
plt.tight_layout()
plt.show()

rprint(f"The position of cromiuum is:")
rprint(pos['chromium'])



print("")
print("DONE")
print("")
