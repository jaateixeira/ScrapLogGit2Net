#! /usr/bin/env python3

# formats a graphml file
# calculates centralities
# layout according centralities
# colorize accourding to affiliation atribute


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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
print ("Number_of_isolates="+str(nx.number_of_isolates(G)))

isolate_ids=[]
for isolate in nx.isolates(G):
    isolate_ids.append(isolate)


if (isolate_ids != []):
    print("\t Isolates:")
    for node, data in G.nodes(data=True):
        if node in isolate_ids:
            print ("\t",node,data['e-mail'],data['affiliation'])


#print ("Calculating centralities")

#degree_centrality = nx.centrality.degree_centrality(G)  # sort by de

#sorted_degree_centrality=(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))

#print ("degree_centrality")
#print (degree_centrality)
#print ("sorted_degree_centrality")
#print (sorted_degree_centrality)


circular_options = { 
    'node_size': 10,
    'width': 0.1,
}



# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python 
print ("coloring by firm")


top_10_colors = {
    'google':'red',
    'nvidia':'lime',
    'intel':'lightblue',
    'amd':'black',
    'gmu':'yellow',
    'arm':'steelblue',
    'amazon':'orange',
    'ibm':'darkblue',
    'linaro':'pink',
    'gtu':'brwon'
}

org_colors = []

for node, data in G.nodes(data=True):
        #print (node)
    #print (data['affiliation'])

    affiliation = data['affiliation']
    if data['affiliation'] in list(top_10_colors.keys()):
        org_colors.append(top_10_colors[affiliation])
    else:
        org_colors.append('gray')


#print(org_colors)






print ("Saving circular layout")
# Random colors 1-256 
#nx.draw_circular(G,node_color=range(256),**circular_options)
nx.draw_circular(G,node_color=org_colors,**circular_options)


legend_elements = [Line2D([0], [0], marker='o', color='blue', label='Female', lw=0,
                          markerfacecolor='blue', markersize=10),
                   Line2D([0], [0], marker='o', color='orange', label='Male', lw=0,
                          markerfacecolor='orange', markersize=10)]

ax = plt.gca()
ax.legend(handles=legend_elements, loc='upper right')


plt.show()
plt.savefig("Uncolored-Circular-Layout.png")




spring_options = { 
    'node_size': 10,
    'width': 0.5,
}


print ("Saving centrality layout")
print ("Position nodes using Fruchterman-Reingold force-directed algorithm.")
nx.draw_spring(G, node_color=org_colors, **spring_options)

ax = plt.gca()
ax.legend(handles=legend_elements, loc='upper right')



plt.show()
plt.savefig("Uncolored-Centrality-Layout.png")


print ("writing Formatted-NetworkFile.graphML")

nx.write_graphml_lxml(G, "Formatted-NetworkFile.graphML")

