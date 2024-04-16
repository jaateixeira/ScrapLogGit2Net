#! /usr/bin/env python3

# formats a graphml file
# calculates centralities
# layout according centralities
# colorize accourding to affiliation atribute
# nodesize according centralities 


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import sys
import os 
global out_file_name

global prefix_for_figures_filenames 




input_file_name = sys.argv[1] 



G = nx.read_graphml(input_file_name)



prefix_for_figures_filenames= os.path.basename(input_file_name)



#prefix_for_figures_filenames = 


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


print ()
print ("Calculating centralities")

degree_centrality = nx.centrality.degree_centrality(G)  # sort by de

sorted_degree_centrality=(sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True))

#print ("degree_centrality")
#print (degree_centrality)
#print ("sorted_degree_centrality")
#print (sorted_degree_centrality)


top_10_connected_ind = []


print("\nTOP 10 ind. with most edges:")


top_10_connected_indtop_10_connected_ind = sorted_degree_centrality[:10]

ids_of_top_10_connected_ind=(dict(top_10_connected_indtop_10_connected_ind)).keys()

#print(top_10_connected_indtop_10_connected_ind)
#print(ids_of_top_10_connected_ind)



for node, data in G.nodes(data=True):
    if node in ids_of_top_10_connected_ind:
        #print (node)
        print (data['e-mail'])
        top_10_connected_ind.append(data['e-mail'])






# See https://matplotlib.org/stable/gallery/color/named_colors.html for the name of colors in python 
print ("coloring by firm")


# less common goes to gray
top_10_colors = {
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
}

# argument passed to draw functions 
org_colors = []

# list with top 10 org contributors 
top_10 = {}

for node, data in G.nodes(data=True):
        #print (node)
    #print (data['affiliation'])

    affiliation = data['affiliation']
    if data['affiliation'] in list(top_10_colors.keys()):
        org_colors.append(top_10_colors[affiliation])
    else:
        org_colors.append('gray')


#print(org_colors)



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
                                  color=top_10_colors[org],
                                  label=org+" n= ("+str(top_10_org[org])+")",
                                  lw=0,
                                  markerfacecolor=top_10_colors[org],
                                  markersize=5))


ax = plt.gca()
ax.legend(handles=legend_elements, loc='best')
#plt.figtext(0, 0, "Visualization of "+(str(prefix_for_figures_filenames))+"on circular layout",  fontsize = 8) 

#plt.show()
plt.savefig(prefix_for_figures_filenames+"Uncolored-Circular-Layout.png")
plt.clf()



spring_options = { 
#    'node_size': 10,
    'width': 0.5,
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
ax.legend(handles=legend_elements, loc='best')

#plt.show()
plt.savefig(prefix_for_figures_filenames+"Uncolored-Centrality-Layout.png")

print()
print ("writing Formatted-NetworkFile.graphML")


#nx.write_graphml_lxml(G, "Formatted-NetworkFile.graphML")

