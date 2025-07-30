# Function to perform DFS and topological sorting
def topologicalSortUtil(v, adj, visited, stack):
    # Mark the current node as visited
    visited[v] = True

    # Recur for all adjacent vertices
    for i in adj[v]:
        if not visited[i]:
            topologicalSortUtil(i, adj, visited, stack)

    # Push current vertex to stack which stores the result
    stack.append(v)

# construct adj list
def constructadj(V, edges):
    adj = [[] for _ in range(V)]

    for it in edges:
        adj[it[0]].append(it[1])

    return adj

# Function to perform Topological Sort
def topologicalSort(V, edges):
    # Stack to store the result
    stack = []
    visited = [False] * V

    adj = constructadj(V, edges)
    # Call the recursive helper function to store
    # Topological Sort starting from all vertices one by one
    for i in range(V):
        if not visited[i]:
            topologicalSortUtil(i, adj, visited, stack)

    # Reverse stack to get the correct topological order
    return stack[::-1]


if __name__ == '__main__':
    # Graph represented as an adjacency list
    v = 6
    edges = [[2, 3], [3, 1], [4, 0], [4, 1], [5, 0], [5, 2]]

    ans = topologicalSort(v, edges)

    print(" ".join(map(str, ans)))
