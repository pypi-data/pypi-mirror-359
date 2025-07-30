from typing import List

class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        # Map each course to its prerequisite list
        preMap = {i: [] for i in range(numCourses)}
        for crs, pre in prerequisites:
            preMap[crs].append(pre)

        # visitSet = all courses along the current DFS path
        visitSet = set()

        def dfs(crs):
            if crs in visitSet:
                return False
            if preMap[crs] == []:
                return True

            visitSet.add(crs)
            for pre in preMap[crs]:
                if not dfs(pre):
                    return False
            visitSet.remove(crs)
            preMap[crs] = []
            return True

        for crs in range(numCourses):
            if not dfs(crs):
                return False
        return True

# -------------------------------
# Driver code to test the function
# -------------------------------

if __name__ == "__main__":
    sol = Solution()

    # Example 1
    numCourses1 = 2
    prerequisites1 = [[1, 0]]
    print("Example 1 - Can finish:", sol.canFinish(numCourses1, prerequisites1))  # Expected: True

    # Example 2
    numCourses2 = 2
    prerequisites2 = [[1, 0], [0, 1]]
    print("Example 2 - Can finish:", sol.canFinish(numCourses2, prerequisites2))  # Expected: False

    # Example 3
    numCourses3 = 4
    prerequisites3 = [[1, 0], [2, 1], [3, 2]]
    print("Example 3 - Can finish:", sol.canFinish(numCourses3, prerequisites3))  # Expected: True

    # Example 4 (Cycle)
    numCourses4 = 4
    prerequisites4 = [[1, 0], [2, 1], [0, 2], [3, 2]]
    print("Example 4 - Can finish:", sol.canFinish(numCourses4, prerequisites4))  # Expected: False
