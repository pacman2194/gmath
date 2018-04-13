class Node(object):
    ''' node object with name, adjacency list represented by a dictionary to store
        capacities, and indegree the adjacency relationship of (a,b) is "a goes to b"
    '''
    def __init__(self, name):
        ''' create base object '''
        self.__name = name
        self.__adj_dict = {}

    def add_edge(self, neighbor, capacity):
        ''' add edge to adjacency list '''
        self.__adj_dict[neighbor] = capacity

    def remove_edge(self, neighbor):
        ''' remove edge from adjacency list '''
        if neighbor in self.__adj_dict:
            self.__adj_dict.pop(neighbor)

    def neighbors(self):
        ''' returns a list of vertices this vertex is adjacent to '''
        return list(self.__adj_dict.keys())

    def __str__(self):
        ''' string representation of this vertex '''
        result = "Vertex: " + self.__name
        edges = []
        for neighbor in self.__adj_dict:
            edges.append(self.__name + " -(" + str(self.__adj_dict[neighbor]) + ")-> " + neighbor)
        if len(self.__adj_dict) > 0:
            result = result + "\nAdjacency List: " + ", ".join(edges)
        return result