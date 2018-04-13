from vertex import Vertex

class Graph(object):
    ''' simple unweighted directed acyclic graph class implemented by using vertex names
        as the dictionary keys and the vertex datastructure as the values
    '''

    def __init__(self):
        ''' directed acyclic graph representation using a dictionary of vertices
            identified by a key with a few helper attributes
        '''
        self.graph_dict = {}
        self.vertex_count = 0
        self.edge_count = 0
        self.cyclic = False

    def vertices(self):
        ''' return the vertices of a graph '''
        return list(self.graph_dict.keys())

    def order(self):
        ''' return the number of vertices in the graph '''
        return self.vertex_count

    def edges(self):
        ''' return the edges of a graph '''
        edge_list = []
        for vertex in self.graph_dict:
            for neighbor in self.get_vertex(vertex).neighbors():
                edge_list.append((vertex, neighbor))
        return edge_list

    def size(self):
        ''' return the number of edges in the graph '''
        return self.edge_count

    def cycle_detected(self):
        ''' returns true if the graph contains a cycle '''
        return self.cyclic

    def get_vertex(self,vertex):
        ''' return the vertex object indicated by the key given '''
        if vertex in self.graph_dict:
            return self.graph_dict[vertex]
        else:
            return None

    def add_vertex(self, vertex):
        ''' add vertex to graph, returns true if successful '''
        if vertex not in self.graph_dict:
            new_vertex = Vertex(vertex)
            self.graph_dict[vertex] = new_vertex
            self.vertex_count += 1
            return True
        return False

    def remove_vertex(self, vertex):
        ''' remove a vertex by removing it from adjacency lists and popping from dictionary
            returns true if successful
        '''
        if vertex in self.graph_dict:
            for v in self.graph_dict:
                if self.get_vertex(v).remove_edge(vertex):
                    self.edge_count -= 1
            for neighbor in self.get_vertex(vertex).neighbors():
                self.get_vertex(neighbor).change_indegree(-1)
                self.edge_count -= 1
            self.graph_dict.pop(vertex, None)
            self.vertex_count -= 1
            return True
        return False

    def add_edge(self, vertex, neighbor):
        ''' add an edge to the graph, add vertices if necessary 
            returns true if successful
        '''
        self.add_vertex(vertex)
        self.add_vertex(neighbor)
        success = self.get_vertex(vertex).add_edge(neighbor)
        if success:
            self.get_vertex(neighbor).change_indegree(1)
            self.edge_count += 1
        return success

    def remove_edge(self, vertex, neighbor):
        ''' remove an edge from the graph '''
        if vertex in self.graph_dict:
            success = self.get_vertex(vertex).remove_edge(neighbor)
            self.get_vertex(neighbor).change_indegree(-1)
            self.edge_count -= 1
            return success
        return False

    def indegree(self, vertex):
        ''' returns the indegree of a vertex in the graph '''
        if vertex in self.graph_dict:
            return self.get_vertex(vertex).indegree()

    def is_cyclic_helper(self, i, color):
        ''' the driver of the cycle detector using recursion and a coloring method.
            if during the depth first search a gray vertex is discovered, then there
            is a back-edge, meaning there is a cycle
        '''
        color[i] = "gray"
        for v in self.get_vertex(i).neighbors():
            if color[v] == "gray":
                return True
            if color[v] == "white" and self.is_cyclic_helper(v, color) == True:
                return True
        color[i] = "black"
        return False
 
    def is_cyclic(self):
        ''' modified recursive depth first seach using a coloring method to track
            visited vertices and check for any back-edges that cause cycles. original
            pseudocode algorithm published in introduction to algorithms, rivest pg 604
        '''
        color = {}
        for v in self.vertices():
            color[v] = "white"
        for v in self.vertices():
            if color[v] == "white":
                if self.is_cyclic_helper(v, color) == True:
                    self.cyclic = True
                    return True
        self.cyclic = False
        return False

    def roots(self):
        ''' returns vertices that no other vertex is adjacent to '''
        root = []
        for v in self.vertices():
            if self.get_vertex(v).indegree() == 0:
                root.append(v)
        return root

    def topological_sort_helper(self, v, visited, stack):
        ''' recursive helper function for topological sort using depth first search '''
        visited[v] = True
        for i in self.get_vertex(v).neighbors():
            if visited[i] == False:
                self.topological_sort_helper(i, visited, stack)
        stack.append(v)

    def topological_sort(self):
        ''' recursive depth first search to give an acceptable
            order of resolution of dependencies
        '''
        visited = {}
        for i in self.vertices():
            visited[i] = False
        stack =[]
        for i in self.vertices():
            if visited[i] == False:
                self.topological_sort_helper(i, visited, stack)
        return stack

    def __contains__(self,vertex):
        ''' contains method for graph '''
        return vertex in self.graph_dict

    def __str__(self):
        ''' string representation of the graph '''
        result = "vertices: "
        for i in self.graph_dict:
            result += str(i) + " "
        result += "\nedges: "
        for edge in self.edges():
            result += str(edge) + " "
        return result
