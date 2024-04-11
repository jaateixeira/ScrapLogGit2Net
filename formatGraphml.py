#! /usr/bin/env python3

# formats a graphml file
# calculates centralities
# layout according centralities
# colorize accourding to affiliation atribute

import matplotlib.pyplot as plt
import networkx as nx

G = nx.read_graphml('NetworkFile.graphML')

print ("number_of_nodes="+str(G.number_of_nodes()))
print ("number_of_edges="+str(G.number_of_edges()))

print ()


