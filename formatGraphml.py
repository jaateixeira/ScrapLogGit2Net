#! /usr/bin/env python3

# formats a graphml file
# calculates centralities
# layout according centralities
# colorize accourding to affiliation atribute

import matplotlib.pyplot as plt
import networkx as nx

G = nx.read_graphml('NetworkFile.graphML')



def printGraph_as_dict_of_dicts(graph):
    print (nx.to_dict_of_dicts(graph))


#printGraph_as_dict_of_dicts(G)

def printGraph_notes_and_its_data(graph):
    
    for node, data in G.nodes(data=True):
        print (node)
        print (data)

#printGraph_notes_and_its_data(G)



print ("Graph imported successfully")
print ("Number_of_nodes="+str(G.number_of_nodes()))
print ("Number_of_edges="+str(G.number_of_edges()))


print ("Calculating centralities")

degree_centrality = nx.centrality.degree_centrality(G)  # sort by de

sorted_degree_centrality=(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))

#print ("degree_centrality")
#print (degree_centrality)
#print ("sorted_degree_centrality")
#print (sorted_degree_centrality)


circular_options = { 
    'node_size': 10,
    'width': 0.1,
    'node-color': 'gray',
}



# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python 
print ("coloring by firm")

org_colors = []

for node, data in G.nodes(data=True):
        #print (node)
    print (data['affiliation'])

    if data['affiliation'] == 'google':
        org_colors.append('red')
    elif data['affiliation'] == 'nvidia':
        org_colors.append('lime')
    elif data['affiliation'] == 'intel':
        org_colors.append('lightblue')
    elif data['affiliation'] == 'amd':
        org_colors.append('black')
    elif data['affiliation'] == 'gmu':
        org_colors.append('yellow')
    elif data['affiliation'] == 'arm':
        org_colors.append('steelblue')
    else:
        org_colors.append('gray')


#print(org_colors)



print ("Saving circular layout")
# Random colors 1-256 
#nx.draw_circular(G,node_color=range(256),**circular_options)
nx.draw_circular(G,node_color=org_colors,**circular_options)
plt.show()
plt.savefig("Uncolored-Circular-Layout.png")



spring_options = { 
    'node_size': 10,
    'width': 0.5,
    'node-color': 'blue',
}


print ("Saving centrality layout")
print ("Position nodes using Fruchterman-Reingold force-directed algorithm.")
nx.draw_spring(G, node_color=org_colors, **spring_options)

plt.show()
plt.savefig("Uncolored-Centrality-Layout.png")


print ("writing formatted NetworkFile.graphML")

nx.write_graphml_lxml(G, "Formatted-NetworkFile.graphML")
