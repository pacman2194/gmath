class Vertex(object):
	''' vertex object with name, adjacency list, and indegree
		the adjacency relationship of (a,b) is "a depends on b"
	'''
	def __init__(self, name):
		''' create base object '''
		self.__name = name
		self.__adj_list = []
		self.__indegree = 0

	def add_edge(self, neighbor):
		''' add edge to this vertex's adjacency list, return true if edge was added '''
		if neighbor not in self.__adj_list:
			self.__adj_list.append(neighbor)
			return True
		return False

	def remove_edge(self, neighbor):
		''' remove edge from this vertex's adjacency list, return true if edge was removed '''
		if neighbor in self.__adj_list:
			self.__adj_list.remove(neighbor)
			return True
		return False

	def neighbors(self):
		''' returns a list of vertices this vertex is adjacent to '''
		return self.__adj_list

	def indegree(self):
		''' returns the number of vertices adjacent to this vertex '''
		return self.__indegree

	def change_indegree(self, x):
		''' helper function to change the indegree from the graph datastructure '''
		self.__indegree = self.__indegree + x

	def __str__(self):
		''' string representation of this vertex '''
		result = "Vertex: " + self.__name + " | In Degree: " + str(self.__indegree)
		if len(self.__adj_list) > 0:
			result = result + "\nAdjacency List: " + ", ".join(self.__adj_list)
		return result
