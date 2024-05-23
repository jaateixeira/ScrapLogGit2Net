#! /usr/bin/env python3


print("Welcome to formatAndReportGraphML")
print("Reporter of GraphML is only now being implemented")
print("")
print("TODO: Should report on companies with more developers")
print("TODO: Should report on centrality of developers and organizations")
print("TODO: Should export in XML, html, latex, MD, CSV and txt files")
print("")




# calculates centralities


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
import turtle, math, random, time

"For writing exel files"
import xlwt

global prefix_for_report_filenames


"This is for filtering results for certain firms - only those" 
top_firms_that_matter = ['google','microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']
#top_firms_that_matter = ['microsoft','ibm','amazon','intel','amd','nvidia','arm','meta','bytedance']

"This is for filtering resultsf for certain firm - not those " 
#top_firms_that_do_not_matter = ['users','tensorflow','google']
top_firms_that_do_not_matter = ['users','tensorflow','gmail']


print("")
print("\tParsing command line arguments")

"This parses the arguments" 
parser = argparse.ArgumentParser()

parser.add_argument("file", type=str, help="the network file")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
parser.add_argument("-t", "--top-firms-only", action="store_true",
                    help="only top_firms_that_matter")

parser.add_argument("-f", "--filter-by-org", action="store_true",
                    help="top_firms_that_do_not_matter")
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



print("")
print("\tReading the required INPUT GraphML file ")
    
input_file_name = args.file



G = nx.read_graphml(input_file_name)



prefix_for_figures_filenames= os.path.basename(input_file_name)



book = xlwt.Workbook(encoding="utf-8")

sheet1 = book.add_sheet("Top contributing firms")




"This manually hacks group email domains that represent same organization"
"alum.mit and .mit should be same"
"cz.ibm.com and us.ibm.com should also be the same" 

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




# list with top 10 org contributors 
top_10 = {}


print("")
print("\tFinding the organizations with most nodes")

"find the top 10 organization contributing"
all_affiliations_freq = {}
for node, data in G.nodes(data=True):
    affiliation = data['affiliation']
    #print (affiliation)
    if affiliation not in all_affiliations_freq.keys():
        all_affiliations_freq[affiliation] = 1
    else:
        all_affiliations_freq[affiliation] += 1
    

print("\n all_affiliations_freq:")
print(dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True)))

top_10_org =  dict(sorted(all_affiliations_freq.items(), key=lambda item: item[1],reverse=True)[:10])



print("\nTOP 10 org. with more nodes:")
for key in top_10_org:
    print (key, top_10_org[key]) 



print ("")
print ("Reporting the most the top 10 org. with most nodes")

"top color org is on the"
"color should be in top_colors otherwise random color "

for org in top_10_org:
    try:
        print (top_colors[org])
    except KeyError:
        print(f"Top firm {org}' color is not defined in top_colors")
        sys.exit()


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






#print()
#print ("writing Formatted-NetworkFile.graphML")
#nx.write_graphml_lxml(G, "Formatted-NetworkFile.graphML")


exit(1)
