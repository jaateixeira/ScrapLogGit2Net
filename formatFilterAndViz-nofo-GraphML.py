#! /usr/bin/env python3

# Formats and visualizes a graphML file capturing a weighted Network of Organizations created by ScrapLog
# Edges thickness maps its weight
# Colorize nodes according to affiliation attribute


# Example of use: 
# ./formatAndViz-nofo-GraphML.py test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML-transformed-to-nofo.graphML 




import sys
import os

import argparse
import networkx as nx

from typing import Tuple

import time
from time import sleep


# Combining loguru with rich provides a powerful logging setup that enhances readability and adds visual appeal to your logs. This integration makes it easier to debug and monitor applications by presenting log messages in a clear, color-coded, and structured format while using loguru's other features, such as log rotation and filtering,
from loguru import logger

# You can then print strings or objects to the terminal in the usual way. Rich will do some basic syntax highlighting and format data structures to make them easier to read.
from rich import print as rprint


# For complete control over terminal formatting, Rich offers a Console class.
# Most applications will require a single Console instance, so you may want to create one at the module level or as an attribute of your top-level object.
from rich.console import Console

# Initialize the console
console = Console()

# JSON gets easier to understand
from rich import print_json
from rich.json import JSON





# Strings may contain Console Markup which can be used to insert color and styles in to the output.
from rich.markdown import Markdown

# Python data structures can be automatically pretty printed with syntax highlighting.
from rich import pretty
from rich.pretty import pprint
pretty.install()

# Rich has an inspect() function which can generate a report on any Python object. It is a fantastic debug aid
from rich import inspect
from rich.color import Color

#Rich supplies a logging handler which will format and colorize text written by Python’s logging module.
from rich.logging import RichHandler

# Add RichHandler to the loguru logger
logger.remove()  # Remove the default logger
logger.add(
    RichHandler(console=console, show_time=True, show_path=True, rich_tracebacks=True),
    format="{message}",  # You can customize this format as needed
    level="DEBUG",  # Set the desired logging level
    #level="INFO",  # Set the desired logging level
)


# Rich’s Table class offers a variety of ways to render tabular data to the terminal.
from rich.table import Table


# Rich provides the Live  class to to animate parts of the terminal
# It's handy to annimate tables that grow row by row
from rich.live import Live

# Rich provides the Align class to align rendable objects
from rich.align import Align

# Rich can display continuously updated information regarding the progress of long running tasks / file copies etc. The information displayed is configurable, the default will display a description of the ‘task’, a progress bar, percentage complete, and estimated time remaining.
from rich.progress import Progress, TaskID

# Rich has a Text class you can use to mark up strings with color and style attributes.
from rich.text import Text


from rich.traceback import Traceback

# For configuring
from rich.traceback import install
# Install the Rich Traceback handler with custom options
install(
    show_locals=True,  # Show local variables in the traceback
    locals_max_length=10, locals_max_string=80, locals_hide_dunder=True, locals_hide_sunder=False,
    indent_guides=True,
    suppress=[__name__],
    # suppress=[your_module],  # Suppress tracebacks from specific modules
    #max_frames=3,  # Limit the number of frames shown
    max_frames=5,  # Limit the number of frames shown
    #width=50,  # Set the width of the traceback display
    width=100,  # Set the width of the traceback display
    extra_lines=3,  # Show extra lines of code around the error
    theme="solarized-dark",  # Use a different color theme
    word_wrap=True,  # Enable word wrapping for long lines
)


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




parser.add_argument("-ff", "--focal_firm",
                    help="the focal firm we want to highlight")

parser.add_argument("-t", "--top_firms_only", action="store_true",
                    help="only top_firms_that_matter")

parser.add_argument("-f", "--filter_by_org", action="store_true",
                    help="top_firms_that_do_not_matter")

parser.add_argument("-s", "--show", action="store_true",
                    help="show the visualization, otherwise saves to png and pdf")

parser.add_argument("-l", "--legend", action="store_true",
                    help="adds a legend to the sociogram")


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

if args.focal_firm:
    print(f"\n\t focal_firm = {args.focal_firm}\n")

    
if args.show:
    rprint("\n In snow mode \n")
else:
    rprint("\n In save png and pdf mode \n")

if args.legend:
    print()
    print("Show a legend")
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
               loc='center left',
               bbox_to_anchor=(0.95, 0.5),
               frameon=False,
               prop={'weight': 'bold', 'size': 12, 'family': 'sans-serif'})




def get_first_half(s):
    """
    Returns the first half of the string.
    If the length of the string is odd, the extra character will be included in the first half.
    
    Parameters:
    s (str): The input string
    
    Returns:
    str: The first half of the input string
    """
    mid_index = (len(s) + 1) // 2  # Middle index, rounded up for odd lengths
    return s[:mid_index]

def get_second_half(s):
    """
    Returns the second half of the string.
    If the length of the string is odd, the extra character will be included in the first half.
    
    Parameters:
    s (str): The input string
    
    Returns:
    str: The second half of the input string
    """
    mid_index = (len(s) + 1) // 2  # Middle index, rounded up for odd lengths
    return s[mid_index:]



first_half = get_first_half(str(args))
second_half = get_second_half(str(args))

print("First Half:", first_half)  # Output: "abcd"
print("Second Half:", second_half)  # Output: "efgh"

    

#plt.title(first_half+"\n"+second_half)
    
ax = plt.gca()
ax.margins(0.08)


if args.focal_firm:

    if args.focal_firm not in G.nodes():
        rprint ("Error- focal firm is on in G nodes list")
        sys.exit()
    
    custom_radius= 0.10
    Drawing_colored_circle = plt.Circle(pos[args.focal_firm], custom_radius, fill=False, alpha=0.5)

    ax.add_artist(Drawing_colored_circle)

plt.axis("off")
plt.tight_layout()

if args.show:
    plt.show()
else:
    # Save the plot as a PDF file
    plt.savefig(f'{args.file}-{args.network_layout}.pdf', format='pdf')

    # Save the plot as a PNG file
    plt.savefig(f'{args.file}-{args.network_layout}'
                f''
                f''
                f'.png', format='png')

"prints the position of the focal firm if any given by the cli"

if args.focal_firm:
    rprint(f"The position of {args.focal_firm } is:")
    rprint(pos[args.focal_firm ])



print("")
print("DONE")
print("")
