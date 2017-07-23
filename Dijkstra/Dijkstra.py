import math
from collections import defaultdict
import operator
import copy
import sys

class Node:
    def __init__(self):
        self.id = None
        self.x = None
        self.y = None
        self.neighbors = []
        self.color = "white"
        self.pi = None
        self.d = None
        self.f = None

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = None
        self.weights = None
        self.time = 0

# Function to read the textFile containing the information about the graph
def readTextFile():
    # open the textfile
    txtFile = open("smallTest.txt","r")

    # reads first line of file, to extract number of vertices and edges
    firstLine = txtFile.readline()
    vAnde = map(int, firstLine.split())
    print "\nNumber of vertices: ", vAnde[0]
    print "Number of edges: ", vAnde[1]

    # Read the rest of the file
    lines = txtFile.readlines()

    # Find the first section, which holds the information about the locations
    firstSection = detectSection(lines, 1)

    # Extract ids, x and y coords. Use these info to make an array of nodes.
    # Sort the array, in case the nodes are not given in order in the txt file.
    infos = []
    for i in firstSection:
        if (i != "\n"):
            info = i.split()
            infos.append(info)
    nodes = buildNodes(infos)
    nodes.sort(key=operator.attrgetter('id'))

    # finds second section, which lists the connections
    firstSectionLength = len(firstSection);
    secondSection = detectSection(lines, firstSectionLength + 1)

    # finds the last section
    secondSectionLength = len(secondSection);
    thirdSection = detectSection(lines, secondSectionLength + firstSectionLength + 1)
    print "Test cases: "
    for i in thirdSection:
         print i,

    # get the connections/edges from the text file
    connections = findEdges(secondSection)

    # build the graph, and represent it as an adjacency list
    g = edgesToDict(connections)
    # print "\nGraph: ", g

    # add the neighboring vertices to the node instances
    for item in g:
        nodes[int(item[0])].neighbors = map(int, item[1])

    # build the graph
    graph = buildGraph(nodes)

    # print "Test DFS: "
    finishingTimes = DFS(graph)
    # print finishingTimes

    # find cycle
    cycle = findCycle(graph)
    print "Cycle? ", cycle

    source = 0
    destination = 4
    if source > vAnde[0]:
        print "Source too big"
    if destination > vAnde[0]:
        print "Destination too big"
    else:
        findShortestPath(cycle, graph, source, destination)

    txtFile.close() # To free up any system resources taken up by the open file

# creates an array of nodes, with respective ids and positions
def buildNodes(nodesInfo):
    nodes = []
    for i in range(0, len(nodesInfo)):
        newNode = Node()
        newNode.id = int(nodesInfo[i][0])
        newNode.x = int(nodesInfo[i][1:-1][0])
        newNode.y = int(nodesInfo[i][2])
        nodes.append(newNode)
    return nodes

# function to build the graph of nodes instances
def buildGraph(nodes):
    newGraph = Graph()
    newGraph.nodes = nodes
    return newGraph

# Function to create a list which stores the connections
def findEdges(connectionsList):
    connections = []
    for line in connectionsList:
        if (line != "\n"):
            parts = line.split()
            connections.append((parts[0], parts[1]))
    return connections

# Function to convert the list of connections to an adjacency list.
# This is used to represent the graph.
def edgesToDict(edges):
    graphDict = defaultdict(list)
    for k, v in edges:
        graphDict[k].append(v)
    return sorted(graphDict.items())

# Function to divide the textfile into sections
def detectSection(file, start):
    section = []
    length = len(file)
    for i in range(start, length):
        section.append(file[i])
        if (file[i] == "\n"):
            break
    return section

# Next two functions determine whether the graph has a cycle
def findCycle(graph):
    V = len(graph.nodes)
    visited = [False] * V
    path = [False] * V
    for node in range(0, V):
        if visited[node] == False:
            if isCyclic(graph, node, visited, path) == True:
                return True
    return False

def isCyclic(graph, index, visited, path):
    visited[index] = True
    path[index] = True
    for i in graph.nodes[index].neighbors:
        if visited[i] == False:
            if isCyclic(graph, i, visited, path) == True:
                return True
        elif path[i] == True:
            return True
    path[index] = False
    return False

def DFS(graph):
    for vertex in graph.nodes:
        vertex.color = "white"
        vertex.pi = None
    graph.time = 0
    stack = []
    for vertex in graph.nodes:
        if (vertex.color == "white"):
            DFSvisit(graph, vertex, stack)
    return stack

def DFSvisit(graph, u, stack):
    graph.time = graph.time + 1
    u.d = graph.time
    u.color = "gray"
    for vertexIndex in u.neighbors:
        if (graph.nodes[vertexIndex].color == "white"):
            graph.nodes[vertexIndex].pi = u.id
            DFSvisit(graph, graph.nodes[vertexIndex], stack)
    u.color = "black"
    graph.time = graph.time + 1
    u.f = graph.time
    stack.append(u.id)

def topologicalSort(graph):
    order = DFS(graph)
    return order

def shortestPathDAG(graph, s):
    increasingOrder = topologicalSort(graph)
    initSingleSource(graph, s)
    # for vertexIndex in increasingOrder:
    while increasingOrder:
        vertexIndex = increasingOrder.pop()
        #print "vertexIndex :", vertexIndex
        for vIndex in graph.nodes[vertexIndex].neighbors:
            DAGrelax(graph, vertexIndex, vIndex)

def initSingleSource(graph, s):
    for vertex in graph.nodes:
        vertex.d = float("inf")
        vertex.pi = None
    graph.nodes[s].d = 0

def DAGrelax(graph, u, v):
    if graph.nodes[v].d > graph.nodes[u].d + weightsFromCoords(graph.nodes[u],graph.nodes[v]):
        graph.nodes[v].d = graph.nodes[u].d + weightsFromCoords(graph.nodes[u],graph.nodes[v])
        graph.nodes[v].pi = u

# Function to find the weight of the edges, given the x and y coordinates
def weightsFromCoords(node1, node2):
    weight = math.sqrt((node2.x - node1.x)**2 + (node2.y - node1.y)**2)
    return weight

#Helper functions to determine the left and right child of a node, used in minHeapify.
def left(i):
    return 2*i
def right(i):
    return 2*i + 1

#Function that restores the min-heap property, which states that the value
#held by the children needs to be greater than the value held by the parent.
def minHeapify(A, i):
    size = len(A)
    l = left(i)
    r = right(i)
    if (l < size and A[l].d < A[i].d):
        smallest = l
    else:
        smallest = i
    if (r < size and A[r].d < A[smallest].d):
        smallest = r
    if (smallest != i):
        A[i], A[smallest] = A[smallest], A[i]
        minHeapify(A, smallest)
    return A

#Function that builds a min-heap from a list
#It will be used as a priority queue in Dijkstra algorithm.
def buildMinHeap(A):
    heapSize = len(A)
    i = int(math.floor(heapSize/2))
    while i >= 1:
        minHeapify(A, i)
        i = i - 1
    return A

#It extracts the minimum value in the min-heap.
def extractMin(A):
    size = len(A)-1
    if size < 1:
        return None
    minValue = A[1]
    A[1] = A[-1]
    del A[-1]
    minHeapify(A, 1)
    return minValue

def Dijkstra(graph, s):
    initSingleSource(graph, s)
    S = []
    Q = copy.copy(graph.nodes)
    paddingNode = Node()
    paddingNode.id = -1
    Q.insert(0, paddingNode)
    Q = buildMinHeap(Q)
    while len(Q)>1:
        u = extractMin(Q)
        S.append(u)
        for v in u.neighbors:
            DijkstraRelax(u, graph.nodes[v])

def DijkstraRelax(u, v):
    if v.d > u.d + weightsFromCoords(u,v):
        v.d = u.d + weightsFromCoords(u,v)
        v.pi = u.id

#Call DAG if the graph is acyclic, Dijkstra otherwise
def findShortestPath(cycle, graph, source, destination):
    print "The source vertex is: ", source
    print "The destination vertex is: ", destination
    if cycle == True:
        Dijkstra(graph, source)
    else:
        shortestPathDAG(graph, source)

    pid = destination
    distance = 0
    path = []
    path.append(destination)
    while pid:
        if graph.nodes[pid].pi == None:
            break
        #print "The parent of ", pid, " is ", graph.nodes[pid].pi, ". The distance to parent is ", round(graph.nodes[pid].d, 2)
        distance = distance + graph.nodes[pid].d
        pid = graph.nodes[pid].pi
        path.append(pid)

    print "The total distance of the shortest path is: ", round(distance, 2)
    print "The sequence of vertices that form the shortest path is: ", list(reversed(path))

def main():
    readTextFile()


if __name__ == "__main__":
    main()
