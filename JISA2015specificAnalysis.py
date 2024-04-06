# Code specific for the analysis of the JISA 2014/2015 paper 

import sys

# Gets connections list among top 10 firms of open stack 
def getConnectionsAmongTop10Only (con, networked_affiliations, sampled_affiliations): 
    # con is the list of connections 
    # networked_affiliations is the affilation dictionary (mail -> affiliation)
    # sample afffiliation to sondsider onlye 
    # res is a list of connection where both bodes belong to sampled_afiiliations 
    top10 = sampled_affiliations

    re = []
    for edge in con:
        #print "edge=", edge 
        (a,b) = edge
        if (networked_affiliations[a] in top10 and networked_affiliations[b] in top10):
            if ((a,b) not in re and (b,a) not in re):
                re.append((a,b))
    return re 

# from the connections class  

def getNodesBetweenDatesInConnList(con):
    "get a list of nodes from change long data between dates earlier later" 
    #print "getting getNodesBetweenDates", " in ", con 
    
    tmpList= []
    
    for edge in con:
        #print "edge=", edge 
        (a,b) = edge
        if (a not in tmpList):
            tmpList.append(a)
        elif (b not in tmpList):
            tmpList.append (b)
        
    ## TEST 1 
    # if there are duplicates in tmpList, something went wrong  
    if len(tmpList)!=len(set(tmpList)):
        print "error in getting the nodes list from a connections tuples"
        sys.exit()

    return tmpList

def getNodesBetweenDates4SelectedFirmsDatesInConnList(con,  networked_affiliations, firms):
    "get a list of edges  from change long data between dates earlier later" 

    res= getNodesBetweenDatesInConnList(getConnectionsAmongTop10Only(con,networked_affiliations,firms))
    
    ## TEST 1 
    # if there are duplicates in tmpList, something went wrong  
    if len(res)!=len(set(res)):
        print "error in getting the nodes list from a connections tuples"
        sys.exit()

    return res 

# From the scraplog class 


def getNodesBetweenDates(ChangeLongdata, earlier, later):
    "get a list of nodes from change long data between dates earlier later" 
    print "getNodesBetweenDates not implmented yet" 
    sys.exit()

def getNodesBetweenDates4SelectedFirms(ChangeLogData ,earlier, later, firms):
    "get a list of edges  from change long data between dates earlier later" 
    print "getNodesBetweenDates4SelectedFirms not implmented yet" 
    sys.exit()


def getEdgesBetweenDates(changeLogData, earlier, later):
    print "getEdgessBetweenDates not implmented yet" 
    sys.exit()

def getEdgesBetweenDates4SelectedFirms(changeLogData,earlier, later, firms):
    print "getEdgesBetweenDates4SelectedFirms not implmented yet" 
    sys.exit()

    
