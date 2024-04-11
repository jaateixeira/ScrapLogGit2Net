# Get some basic network measures 
# Ideal to get number of nodes and edges from agreByConnWSF list that keeps  agregated tuples of connected authors  due to working on a common file [(a-b),file)]

# Validate that the list of connection is on the right format [(a-b),file)]

from __future__ import absolute_import
from __future__ import print_function
import sys


def validateConnectionsFormat(connections):
    # Validate that the list of connections is not empty 
    # Validate that the list of connection is no the write format [(a-b),file)]

    if connections == 0:
        print ("\t Warning - connections list is empty")    
        return False 

    ((author1, author2), fileName ) = connections[0]     
    
    if len(author1)< 5 or  len(author1)< 5 or  len(author1)< 5 :
        print ("\t Warning - connections list is on the wrong format")    
        return False 

    
    return True 



#Get Number of nodes/authors from a list of tuples that worked on thes same file 
#Authors that worked alone are desregarded
def getNumberOfNetworkedNodes(connections):

    contributors = []
    
    #print ("\tGetting number of nodes")
    
    if validateConnectionsFormat(connections) == False : 
        print ("\tERROR trying to get the number of nodes from agregated tuples on empty/wrong format")
        sys.exit()

    for connection in connections:
        contributorsPair = connection[0]
        fileName = connection[1]
        
        #print ("\tContributors " + str (contributorsPair) + " connected by collaborating on file [" + fileName + "]")
    
        (contri1, contri2) = contributorsPair
    
        if contri1 not in contributors:
            contributors.append(contri1)
        if contri2 not in  contributors:
            contributors.append(contri2)

    #print("\tcontributors=[" +str(contributors) + "]")
    #print("\tlen(contributors)=["+str(len(contributors))+"]")
            
    # Validate that the list of connections format
    return len(contributors)
    

# Get the number of nodes/atribute/affiliations
def getNumberOfAffiliations(affiliationsDict):
    #print("getNumberOfAffiliations("+str(affiliationsDict)+")")
    
    uniqueAffiliations = []

    for (author,aff) in affiliationsDict.items():
        if aff not in uniqueAffiliations:
            uniqueAffiliations.append(aff)
    return len(uniqueAffiliations )

# Get print Number of edges/collaborations (include repetitions of the same collaboration) 
def getNumberOfEdges(connections):
    if validateConnectionsFormat(connections) == False : 
        print ("ERROR trying to get the number of nodes from agregated tuples on empty/wrong format")
        sys.exit()

    # Validate that the list of connections format
    return len(connections) 

#Get  Number of unique edges/collaborations (do not include repetitions of the same collaborations)
def getNumberOfUniqueEdges(connections):

    uniqueConnections = []
    
    if validateConnectionsFormat(connections) == False : 
        print ("ERROR trying to get the number of nodes from agregated tuples on empty/wrong format")
        sys.exit()

    # remove duplicates
    for connection in connections:
        ((author1, author2), fileName ) = connection
        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1 
        if (author1, author2) not in uniqueConnections and (author2, author1) not in uniqueConnections :
            uniqueConnections.append (((author1, author2))) 

    # Validate that the list of connections format
    return len(uniqueConnections)


# Get the number of authors/contrinutors/developers that commit code (either alone or collaborating with others)
# Not a network meazure 
def getNumberOfDevelopers():
    print ("TO Implement")
    return -1

# Get the number of authors/contrinutors/developers that commit code in collaboration with others 
def getNumberOfNetworkedDevelopers(connections):
    print ("TO Implement")
    return -1
