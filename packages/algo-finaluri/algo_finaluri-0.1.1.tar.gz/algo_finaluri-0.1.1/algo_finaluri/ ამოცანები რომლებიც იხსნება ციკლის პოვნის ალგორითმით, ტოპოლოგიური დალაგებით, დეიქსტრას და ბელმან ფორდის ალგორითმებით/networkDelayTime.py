import heapq
import collections
from typing import List

class Solution:
    def networkDelayTime(self, times: List[List[int]], n: int, k: int) -> int:
        edges = collections.defaultdict(list)
        for u, v, w in times:
            edges[u].append((v, w))

        minHeap = [(0, k)]
        visit = set()
        t = 0

        while minHeap:
            w1, n1 = heapq.heappop(minHeap)
            if n1 in visit:
                continue
            visit.add(n1)
            t = max(t, w1)

            for n2, w2 in edges[n1]:
                if n2 not in visit:
                    heapq.heappush(minHeap, (w1 + w2, n2))

        return t if len(visit) == n else -1

# -------------------------------
# Driver code to test the function
# -------------------------------
if __name__ == "__main__":
    sol = Solution()

    # Example 1
    times1 = [[2, 1, 1], [2, 3, 1], [3, 4, 1]]
    n1 = 4
    k1 = 2
    print("Example 1 - Network delay time:", sol.networkDelayTime(times1, n1, k1))  
    # Expected: 2

    # Example 2
    times2 = [[1, 2, 1]]
    n2 = 2
    k2 = 1
    print("Example 2 - Network delay time:", sol.networkDelayTime(times2, n2, k2))  
    # Expected: 1

    # Example 3 (Disconnected)
    times3 = [[1, 2, 1]]
    n3 = 2
    k3 = 2
    print("Example 3 - Network delay time:", sol.networkDelayTime(times3, n3, k3))  
    # Expected: -1
