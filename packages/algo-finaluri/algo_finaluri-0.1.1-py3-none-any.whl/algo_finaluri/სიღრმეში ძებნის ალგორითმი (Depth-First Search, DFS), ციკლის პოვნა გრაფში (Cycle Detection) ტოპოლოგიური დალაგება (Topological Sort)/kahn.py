from collections import deque

# Function to construct adjacency list from edge list
def constructadj(V, edges):
    adj = [[] for _ in range(V)]  # Initialize empty list for each vertex
    for u, v in edges:
        adj[u].append(v)          # Directed edge from u to v
    return adj

# Function to check for cycle using Kahn's Algorithm (BFS-based Topological Sort)
def isCyclic(V, edges):
    adj = constructadj(V, edges)
    in_degree = [0] * V
    queue = deque()
    visited = 0                       # Count of visited nodes

    #  Calculate in-degree of each node
    for u in range(V):
        for v in adj[u]:
            in_degree[v] += 1

    #  Enqueue nodes with in-degree 0
    for u in range(V):
        if in_degree[u] == 0:
            queue.append(u)

    #  Perform BFS (Topological Sort)
    while queue:
        u = queue.popleft()
        visited += 1

        # Decrease in-degree of adjacent nodes
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    #  If visited != V, graph has a cycle
    return visited != V


# Example usage
V = 4
edges = [[0, 1], [0, 2], [1, 2], [2, 0], [2, 3]]

# Output: true (because there is a cycle: 0 → 2 → 0)
print("true" if isCyclic(V, edges) else "false")
