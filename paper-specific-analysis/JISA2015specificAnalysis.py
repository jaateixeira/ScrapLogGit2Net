from __future__ import absolute_import, print_function
import sys

# Gets connections list among top 10 firms of OpenStack
def getConnectionsAmongTop10Only(con, networked_affiliations, sampled_affiliations): 
    # con is the list of connections 
    # networked_affiliations is the affiliation dictionary (mail -> affiliation)
    # sampled_affiliations to consider only top 10 firms

    top10 = sampled_affiliations
    re = set()  # Using a set to prevent duplicates and improve lookup speed

    for edge in con:
        (a, b) = edge
        if (networked_affiliations.get(a) in top10 and networked_affiliations.get(b) in top10):
            # Add edge only if (b, a) or (a, b) not already in re
            if (b, a) not in re:
                re.add((a, b))
                
    return list(re)  # Convert back to list if needed

# Retrieve unique nodes from a list of connections
def getNodesBetweenDatesInConnList(con):
    # con: list of connections (tuples of nodes)
    
    tmpList = set()  # Using a set to prevent duplicates

    for edge in con:
        (a, b) = edge
        tmpList.add(a)
        tmpList.add(b)
    
    return list(tmpList)  # Convert back to list if needed

# Retrieves nodes between dates for selected firms only
def getNodesBetweenDates4SelectedFirmsDatesInConnList(con, networked_affiliations, firms):
    # Returns unique nodes among connections limited to top 10 firms
    res = getNodesBetweenDatesInConnList(getConnectionsAmongTop10Only(con, networked_affiliations, firms))
    return res

# Placeholder for unimplemented functions
def getNodesBetweenDates(ChangeLongdata, earlier, later):
    print("getNodesBetweenDates not implemented yet")
    sys.exit()

def getNodesBetweenDates4SelectedFirms(ChangeLogData, earlier, later, firms):
    print("getNodesBetweenDates4SelectedFirms not implemented yet")
    sys.exit()

def getEdgesBetweenDates(changeLogData, earlier, later):
    print("getEdgesBetweenDates not implemented yet")
    sys.exit()

def getEdgesBetweenDates4SelectedFirms(changeLogData, earlier, later, firms):
    print("getEdgesBetweenDates4SelectedFirms not implemented yet")
    sys.exit()
