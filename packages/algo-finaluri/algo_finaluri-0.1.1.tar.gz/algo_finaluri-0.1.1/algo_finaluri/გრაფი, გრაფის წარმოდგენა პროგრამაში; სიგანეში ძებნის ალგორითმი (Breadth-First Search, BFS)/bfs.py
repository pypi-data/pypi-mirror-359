from collections import deque

# Function to find BFS of Graph from given source s
def bfs(adj):
    
    # get number of vertices
    V = len(adj)
    
    # create an array to store the traversal
    res = []
    s = 0
    # Create a queue for BFS
    q = deque()
    
    # Initially mark all the vertices as not visited
    visited = [False] * V
    
    # Mark source node as visited and enqueue it
    visited[s] = True
    q.append(s)
    
    # Iterate over the queue
    while q:
        
        # Dequeue a vertex from queue and store it
        curr = q.popleft()
        res.append(curr)
        
        # Get all adjacent vertices of the dequeued 
        # vertex curr If an adjacent has not been 
        # visited, mark it visited and enqueue it
        for x in adj[curr]:
            if not visited[x]:
                visited[x] = True
                q.append(x)
                
    return res

if __name__ == "__main__":
    
    # create the adjacency list
    # [ [2, 3, 1], [0], [0, 4], [0], [2] ]
    adj = [[1,2], [0,2,3], [0,4], [1,4], [2,3]]
    ans = bfs(adj)
    for i in ans:
        print(i, end=" ")
