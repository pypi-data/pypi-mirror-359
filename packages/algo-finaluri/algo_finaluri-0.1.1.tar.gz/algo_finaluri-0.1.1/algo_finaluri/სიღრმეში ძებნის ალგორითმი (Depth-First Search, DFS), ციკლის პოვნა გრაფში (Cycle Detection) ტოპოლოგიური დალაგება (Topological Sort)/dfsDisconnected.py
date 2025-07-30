# Create an adjacency list for the graph
from collections import defaultdict


def add_edge(adj, s, t):
    adj[s].append(t)
    adj[t].append(s)

# Recursive function for DFS traversal


def dfs_rec(adj, visited, s, res):
    # Mark the current vertex as visited
    visited[s] = True
    res.append(s)

    # Recursively visit all adjacent vertices that are not visited yet
    for i in adj[s]:
        if not visited[i]:
            dfs_rec(adj, visited, i, res)

# Main DFS function to perform DFS for the entire graph


def dfs(adj):
    visited = [False] * len(adj)
    res = []
    # Loop through all vertices to handle disconnected graph
    for i in range(len(adj)):
        if not visited[i]:
            # If vertex i has not been visited,
            # perform DFS from it
            dfs_rec(adj, visited, i, res)
    return res


V = 6
# Create an adjacency list for the graph
adj = defaultdict(list)

# Define the edges of the graph
edges = [[1, 2], [2, 0], [0, 3], [4, 5]]

# Populate the adjacency list with edges
for e in edges:
    add_edge(adj, e[0], e[1])
res = dfs(adj)

print(' '.join(map(str, res)))
