#! /usr/bin/env python3

# Formats and visualizes a graphML file capturing a weighted Network of Organizations created by ScrapLog
# Edges thickness maps its weight
# Colorize nodes according to affiliation attribute

# Example of use: 
# ./formatAndViz-nofo-GraphML.py test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML-transformed-to-nofo.graphML 

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import sys
import os
import argparse
import random
import math
import json
from rich import print as rprint


def print_graph_data(graph):
    print(nx.to_dict_of_dicts(graph))
    for node, data in graph.nodes(data=True):
        print(f"\t{node}\n\t{data}")
    for edge in graph.edges(data=True):
        print(f"\t{edge}")


print("\nformatAndViz-nofo-GraphML.py - visualizing weighted networks of organizations since June 2024\nLet's go\n")

parser = argparse.ArgumentParser(prog="formatAndViz-nofo-GraphML.py", description="Formats and visualizes a graphML file capturing a weighted Network of Organizations")
parser.add_argument("file", type=str, help="the network file")
parser.add_argument("-n", "--network_layout", choices=['circular', 'spring'], default='spring', help="the type of network visualization layout (i.e., node positioning algorithm)")
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
parser.add_argument("-ns", "--node_sizing_strategy", choices=['all-equal', 'centrality-score'], default='centrality-score', help="How big the nodes/developers should be? All equal or a function of their centrality?")
parser.add_argument("-nc", "--node_coloring_strategy", choices=['random-color-to-unknown-firms', 'gray-color-to-unknown-firms', 'gray-color-to-others-not-in-topn-filter'], default='random-color-to-unknown-firms', help="Set a coloring strategy for unknown firms.")
parser.add_argument("-ff", "--focal_firm", required=True, help="the focal firm we want to highlight")
parser.add_argument("-t", "--top_firms_only", action="store_true", help="only top_firms_that_matter")
parser.add_argument("-f", "--filter_by_org", action="store_true", help="top_firms_that_do_not_matter")
parser.add_argument("-s", "--show", action="store_true", help="show the visualization, otherwise saves to png and pdf")
parser.add_argument("-l", "--legend", action="store_true", help="adds a legend to the sociogram")

args = parser.parse_args()

if args.verbose:
    print("In verbose mode")

input_file_name = args.file
G = nx.read_graphml(input_file_name)

if args.verbose:
    print("\nPrinting inter-organizational network:")
    print_graph_data(G)

print("Inter-organizational weighted Graph imported successfully")
print(f"Number_of_nodes={G.number_of_nodes()}")
print(f"Number_of_edges={G.number_of_edges()}")
print(f"Number_of_isolates={nx.number_of_isolates(G)}")

print("\nCalculating centralities")
degree_centrality = nx.eigenvector_centrality(G)
sorted_degree_centrality = sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)

print("Coloring by firm")
with open('business_firm_color_dictionary_json/firm_color_dict.json', 'r') as file:
    known_org_node_colors = json.load(file)

print("\nAssigning colors to organizations/nodes\n")
org_colors = []
for node in G.nodes:
    if node in known_org_node_colors:
        org_colors.append(known_org_node_colors[node])
    else:
        if args.node_coloring_strategy == 'gray-color-to-unknown-firms':
            org_colors.append('gray')
            known_org_node_colors[node] = 'gray'
        else:
            random_color = (random.random(), random.random(), random.random())
            org_colors.append(random_color)
            known_org_node_colors[node] = random_color

print("Colors assigned to organizations/nodes:")
print(org_colors)

print("Drawing inter-organizational network in given layout ...\n")
if args.network_layout == 'circular':
    pos = nx.circular_layout(G)
elif args.network_layout == 'spring':
    pos = nx.spring_layout(G)
else:
    print("Error - Unknown network layout")
    sys.exit()

print("Drawing inter-organizational nodes ... ")
node_sizes = [v * 2000 for v in degree_centrality.values()] if args.node_sizing_strategy == 'centrality-score' else [10] * len(G.nodes)
nx.draw_networkx_nodes(G, pos, node_shape='o', node_size=node_sizes, node_color=org_colors, alpha=0.75)

print("Drawing inter-organizational edges ... ")
edge_thickness = [1 + math.log(a['weight'], 2) for _, _, a in G.edges(data=True)]
nx.draw_networkx_edges(G, pos, width=edge_thickness, alpha=0.2)

print("Drawing organizations node labels")
nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif", font_weight="bold", font_color='black', alpha=1.0)

print("Drawing inter-organizational edge weight labels")
weight_labels = nx.get_edge_attributes(G, name='weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=weight_labels)

if args.legend:
    legend_items = [Line2D([0], [0], marker='o', color=known_org_node_colors[org], label=org, lw=0, markerfacecolor=known_org_node_colors[org], markersize=5) for org in known_org_node_colors]
    plt.legend(handles=legend_items, loc='center left', bbox_to_anchor=(0.95, 0.5), frameon=False, prop={'weight': 'bold', 'size': 12, 'family': 'sans-serif'})

if args.focal_firm in G.nodes():
    custom_radius = 0.10
    focal_circle = plt.Circle(pos[args.focal_firm], custom_radius, fill=False, alpha=0.5)
    plt.gca().add_artist(focal_circle)
else:
    rprint("Error - focal firm is not in G nodes list")
    sys.exit()

plt.axis("off")
plt.tight_layout()
plt.show()

rprint(f"The position of {args.focal_firm} is:")
rprint(pos[args.focal_firm])

print("\nDONE\n")