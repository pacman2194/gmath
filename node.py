class Node(object):
    ''' node object with name, adjacency list represented by a dictionary to store
        capacities, and indegree the adjacency relationship of (a,b) is "a goes to b"
    '''
    def __init__(self, name):
        ''' create base object '''
        self.__name = name
        self.__adj_dict = {}
        self.__indegree = 0

    def add_arc(self, neighbor, capacity):
        ''' add arc to adjacency list '''
        self.__adj_dict[neighbor] = capacity

    def remove_arc(self, neighbor):
        ''' remove arc from adjacency list '''
        if neighbor in self.__adj_dict:
            self.__adj_dict.pop(neighbor)
            return True
        return False

    def arc_capacity(self, neighbor):
        ''' returns an arc's capacity '''
        return self.__adj_dict[neighbor]

    def neighbors(self):
        ''' returns a list of nodes this vertex is adjacent to '''
        return list(self.__adj_dict.keys())

    def indegree(self):
        ''' returns the number of nodes adjacent to this vertex '''
        return self.__indegree

    def change_indegree(self, x):
        ''' helper function to change the indegree from the flow datastructure '''
        self.__indegree = self.__indegree + x

    def change_capacity(self, neighbor, inc):
        ''' change capacity for specified edge by inc amount '''
        self.__adj_dict[neighbor] = self.__adj_dict[neighbor] + inc

    def __str__(self):
        ''' string representation of this vertex '''
        result = "Vertex: " + self.__name
        arcs = []
        for neighbor in self.__adj_dict:
            arcs.append(self.__name + " -(" + str(self.__adj_dict[neighbor]) + ")-> " + neighbor)
        if len(self.__adj_dict) > 0:
            result = result + "\nAdjacency List: " + ", ".join(arcs)
        return result