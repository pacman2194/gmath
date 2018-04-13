from node import Node

class Flow(object):
    ''' 
    '''

    def __init__(self):
        ''' initialize flow network with empty dictionary of 
            nodes and node and edge count
        '''
        self.flow_dict = {}
        self.node_count = 0
        self.edge_count = 0

    def nodes(self):
        ''' returns the list of nodes in the flow network '''
        return list(self.flow_dict.keys())

    def order(self):
        ''' return the number of nodes in the graph '''
        return self.node_count

    def edges(self):
        ''' return the edges of a graph '''
        edge_list = []
        for node in self.flow_dict:
            for neighbor in self.get_node(node).neighbors():
                edge_list.append((node, neighbor))
        return edge_list

    def get_node(self,node):
        ''' return the node object indicated by the key given '''
        if node in self.flow_dict:
            return self.flow_dict[node]
        else:
            return None

    def add_node(self, node):
        ''' add node to graph, returns true if successful '''
        if node not in self.flow_dict:
            new_node = Node(node)
            self.flow_dict[node] = new_node
            self.node_count += 1
            return True
        return False
