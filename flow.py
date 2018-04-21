from node import Node
from copy import deepcopy

class Flow(object):
    ''' this is a flow network datastructure using a dictionary of node names as keys with
        the nodes as the values, using the node datastructure. It's primary purpose to is
        represent a flow network and provide a max flow through the network
    '''

    def __init__(self):
        ''' initialize flow network with empty dictionary of 
            nodes and node and arc count
        '''
        self.flow_dict = {}
        self.node_count = 0
        self.arc_count = 0

    def nodes(self):
        ''' returns the list of nodes in the flow network '''
        return list(self.flow_dict.keys())

    def order(self):
        ''' return the number of nodes in the graph '''
        return self.node_count

    def arcs(self):
        ''' return the arcs of a graph '''
        arc_list = []
        #go through each node and append all its adjacencies and arc capacities
        for node in self.flow_dict:
            n = self.get_node(node)
            for neighbor in n.neighbors():
                arc_list.append((node, neighbor, n.arc_capacity(neighbor)))
        return arc_list

    def size(self):
        ''' return the numbers of arcs in the flow network '''
        return self.arc_count

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

    def remove_node(self, node):
        ''' remove node from graph, returns true if successful '''
        if node in self.flow_dict:
            #remove the node from all adjacency lists of nodes
            for n in self.flow_dict:
                if self.get_node(n).remove_arc(node):
                    self.arc_count -= 1
            #modify all neighbors from this node
            for neighbor in self.get_node(node).neighbors():
                self.get_node(neighbor).change_indegree(-1)
                self.arc_count -= 1
            #remove node from dictionary
            self.flow_dict.pop(node, None)
            self.node_count -= 1
            return True
        return False

    def add_arc(self, node, neighbor, capacity):
        ''' add arc to flow network '''
        #check to see if nodes exist firest, if not then add them
        if node not in self.flow_dict:
            self.add_node(node)
        if neighbor not in self.flow_dict:
            self.add_node(neighbor)
        #if the adjacency didn't already exist create it and update values
        if neighbor not in self.get_node(node).neighbors():
            self.get_node(neighbor).change_indegree(1)
            self.arc_count += 1
            new_node = True
        else:
            new_node = False
        #not a new adjacency, treat as update !!!!! will overwrite without warning
        self.get_node(node).add_arc(neighbor, capacity)
        return new_node

    def remove_arc(self, node, neighbor):
        ''' remove arc from flow network '''
        if node in self.flow_dict and neighbor in self.get_node(node).neighbors():
            capacity = self.get_node(node).arc_capacity(neighbor)
            self.get_node(node).remove_arc(neighbor)
            self.get_node(neighbor).change_indegree(-1)
            self.arc_count -= 1
            return True
        return False

    def max_flow(self):
        ''' returns max flow through the flow network
            implemented using the Ford-Fulkerson algorithm
        '''
        #create a deep copy for manipulating and this copy is a residual graph
        #the residual graph represents the graph with the remaining space until
        #maximum capacity
        g = deepcopy(self)
        #handle if there are back-edges because this algorithm uses back-edges
        #and this datastructure only allows one edge (u,v) for any vertex u and v
        for n in g.nodes():
            for neighbor in g.get_node(n).neighbors():
                if n in g.get_node(neighbor).neighbors():
                    #there is a back-edge, create new in-between node with same capacities
                    #as back-edge and remove original back-edge
                    alt = neighbor + n
                    while alt in g.nodes():
                        alt += "'"
                    g.add_arc(neighbor, alt, g.get_node(neighbor).arc_capacity(n))
                    g.add_arc(alt, n, g.get_node(neighbor).arc_capacity(n))
                    g.remove_arc(neighbor,n)
        #create master source and sink to handle multiple sources and sinks if there are any
        for s in self.sources():
            g.add_arc('master_root', s, float("Inf"))
        for t in self.sinks():
            g.add_arc(t, 'master_sink', float("Inf"))
        parent = {}
        max_flow = 0
        #breadth-first search to make sure there is path from source to sink
        while g.max_flow_bfs('master_root', 'master_sink', parent):
            path_flow = float("Inf")
            s = 'master_sink'
            #backtrack from sink to source and capture minimum available flow
            while s != 'master_root':
                path_flow = min (path_flow, g.get_node(parent[s]).arc_capacity(s))
                s = parent[s]
            #increase flow by the minimal maximum residual capacity
            max_flow += path_flow
            v = 'master_sink'
            #update the residual capacities
            while v != 'master_root':
                u = parent[v]
                g.get_node(u).change_capacity(v, -path_flow)
                if u not in g.get_node(v).neighbors():
                    g.add_arc(v, u, path_flow)
                else:
                    g.get_node(v).change_capacity(u, path_flow)
                v = parent[v]
        return max_flow

    def max_flow_bfs(self, s, t, parent):
        ''' breadth first search helper for max flow function '''
        visited = []
        queue = []
        queue.append(s)
        visited.append(s)
        while queue:
            n = queue.pop(0)
            for neighbor in self.get_node(n).neighbors():
                if neighbor not in visited and self.get_node(n).arc_capacity(neighbor) > 0:
                    queue.append(neighbor)
                    visited.append(neighbor)
                    parent[neighbor] = n
        if t in visited:
            return True
        else:
            return False

    def sources(self):
        ''' returns all the sources in the flow network '''
        src = []
        for n in self.nodes():
            if self.get_node(n).indegree() == 0:
                src.append(n)
        return src

    def sinks(self):
        ''' returns all the sinks in the flow network '''
        snk = []
        for n in self.nodes():
            if not self.get_node(n).neighbors():
                snk.append(n)
        return snk

    def __str__(self):
        ''' return string representation of flow network '''
        result = 'vertices: '
        for node in self.nodes():
            result += str(node) + ' '
        result += '\narcs: '
        for arc in self.arcs():
            result += str(arc) + ' '
        return result
