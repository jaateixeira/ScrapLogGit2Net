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



print ("Time to calculate centralities")

degree_centrality = nx.centrality.degree_centrality(G)  # sort by de

sorted_degree_centrality=(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))

print ("degree_centrality")
print (degree_centrality)
print ("sorted_degree_centrality")
print (sorted_degree_centrality)




options = { 
    'node_size': 10,
    'width': 1,
    'node-color': 'blue',
}


print ("Saving circular layout")        
nx.draw_circular(G, **options)
plt.show()
plt.savefig("Uncolored-Circular-Layout.png")

print ("Saving centrality layout")        
nx.draw_spring(G, **options)

plt.show()
plt.savefig("Uncolored-Centrality-Layout.png")


print ("writing formatted NetworkFile.graphML")
nx.write_graphml_lxml(G, "Formatted-NetworkFile.graphML")
