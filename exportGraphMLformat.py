from datetime import date

graphml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- This file was created by scraplog.py script for OSS SNA research purposes --> 
<!-- For more information contact jose.teixeira@utu.fi and check www.jteixeira.eu for more information on OSS SNA research -->
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
'''

graphml_closer = "</graphml>\n"
graph_opener = '<graph id="G" edgedefault="undirected">\n'
graph_closer = '</graph>\n'

def set_node_attribute_key(attr_id, attr_name, attr_type="string"):
    """Set attributes for a node in GraphML."""
    if attr_type != "string":
        raise ValueError("Only 'string' type is supported for GraphML node attributes.")
    
    return (f'<key id="d{attr_id}" for="node" attr.name="{attr_name}" attr.type="{attr_type}">\n'
            f'\t<default>DEFAULT{attr_name}</default>\n</key>\n')

def add_node(node_id, attributes):
    """Add a node with attributes."""
    attribute_data = ''.join(f'\t<data key="d{attr_id}">{value}</data>\n' for attr_id, value in attributes)
    return f'\t<node id="{node_id}">\n{attribute_data}\t</node>\n'

def add_edge(edge_id, node_id_from, node_id_to):
    """Add an edge connecting two nodes."""
    if not edge_id.startswith('e'):
        raise ValueError("Edge ID must start with 'e', e.g., e0, e12.")
    return f'\t<edge id="{edge_id}" source="{node_id_from}" target="{node_id_to}"/>\n'

def main():
    """Generate and print a sample GraphML file."""
    print(graphml_header)
    print(set_node_attribute_key(0, "e-mail"))
    print(set_node_attribute_key(1, "color"))
    print(set_node_attribute_key(2, "affiliation"))
    print(graph_opener)

    # Add nodes with attributes
    print(add_node(0, [(0, "jose@webkit.org")]))
    print(add_node(1, [(0, "martin@svh.com"), (1, "turquoise"), (2, "San Vicent Health")]))
    print(add_node(2, [(0, "tt@utu.fi"), (1, "red"), (2, "University of Turku")]))

    # Add edges
    print(add_edge("e0", 0, 1))
    print(add_edge("e1", 0, 2))

    print(graph_closer)
    print(graphml_closer)
    print("exportGraphml imported")

if __name__ == "__main__":
    main()
