# file to export VCS (CVS,SVN, GIT) SNA data to the graphml format used by visone and gephi

import sys

graphml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- This file was created by scraplog.py script for OSS SNA research purposes --> \n'  + '<!-- For more information contact jose.teixeira@utu.fi and check www.jteixeira.eu for more information on OSS SNA research -->\n' + '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' + 'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n' 

graphml_closer = "</graphml>\n"

graph_opener= '<graph id="G" edgedefault="undirected">\n'
graph_closer= '</graph>'


# Set atributes that a node can have 
# i.e <key id="d0" for="node" attr.name="color" attr.type="string"> </key>
def setNodeAntributeKey(id, attrName, attrType):

    if attrType != "string":
        print ("Not supported GRAPHML node atribute type")
        sys.exit()
    
    res = '<key id="d'+str(id)+'" for="node" attr.name="'+attrName+'" attr.type="'+attrType+'"> \n' 

    res +='\t<default>DEFAULT'+attrName+'</default>'
    res +='</key>\n' 

    return res

# Add a node with a tuple of atributes
def addNode(nodeId, atributes):
    
    res = '\t<node id="'+ str(nodeId) +'">\n'

    for atribute in atributes:
        key = "d"+str(atribute[0])
        value = atribute[1]

        res += '\t<data key="'+key+'">'+value+'</data>\n'
    
    res+='\t</node>\n' 
    return res 
 
# Add a edge connecting nodes 
def addEdge(edgeId,nodeIdFrom,nodeIdTo):

    if edgeId[0] != 'e':
        print ("edgeid mist start with e: ie. e0, e12")
        sys.exit()
    
    return  '\t<edge id="'+str(edgeId)+'" source="'+ str(nodeIdFrom)+'" target="'+ str(nodeIdTo)+'"/>\n'



# Sample ML file works on Visone and Gephi

def main():
    #prints a smaple graphML file using this file functions  
    print(graphml_header)
    print(setNodeAntributeKey(0,"e-mail","string"))
    print(setNodeAntributeKey(1,"color","string"))
    print(setNodeAntributeKey(2,"affiliation","string"))
    print(graph_opener)

    # Adding a node with email atribute
    print(addNode(0,[(0,"jose@webkit.org")]))

    # Add nodes with email, color and affiliation atribute

    print(addNode(1,[(0,"martin@svh.com"),(1,"turquoise"),(2,"San Vicent Health")]))
    print(addNode(2,[(0,"tt@utu.fi"),(1,"red"),(2,"University of Turku")]))

    print(addEdge("e0",0,1))
    print(addEdge("e1",0,2))
    print(graph_closer)
    print(graphml_closer)


    print "exportGraphml imported"

if __name__ == "__main__":
    main()
