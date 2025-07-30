from collections import deque

def findOrder(n, prerequisites):
    adj = [[] for _ in range(n)]
    inDegree = [0] * n

    for dest, src in prerequisites:
        adj[src].append(dest)
        inDegree[dest] += 1

    q = deque([i for i in range(n) if inDegree[i] == 0])
    order = []

    while q:
        current = q.popleft()
        order.append(current)

        for neighbor in adj[current]:
            inDegree[neighbor] -= 1
            if inDegree[neighbor] == 0:
                q.append(neighbor)

    return order if len(order) == n else []

# Example
if __name__ == "__main__":
    n = 4
    prerequisites = [[1, 0], [2, 0], [3, 1], [3, 2]]
    print("Course order:", findOrder(n, prerequisites))


