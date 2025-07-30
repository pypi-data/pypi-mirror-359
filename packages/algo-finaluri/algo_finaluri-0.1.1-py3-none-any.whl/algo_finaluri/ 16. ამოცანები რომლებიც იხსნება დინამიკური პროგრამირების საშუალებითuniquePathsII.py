# Define the Solution class
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: list[list[int]]) -> int:
        m = len(obstacleGrid)
        n = len(obstacleGrid[0])
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        dp[0][1] = 1

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if obstacleGrid[i - 1][j - 1] == 0:
                    dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

        return dp[m][n]

def test_unique_paths_with_obstacles():
    solution = Solution()

    test_cases = [
        {
            "input": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
            "expected": 2
        },
        {
            "input": [[0, 1], [0, 0]],
            "expected": 1
        },
        {
            "input": [[1, 0]],
            "expected": 0
        },
        {
            "input": [[0]],
            "expected": 1
        },
        {
            "input": [[0, 0, 1, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 0]],
            "expected": 0
        }
    ]

    for idx, test in enumerate(test_cases, 1):
        result = solution.uniquePathsWithObstacles(test["input"])
        if result == test["expected"]:
            print(f"Test Case {idx} Passed. Output = {result}")
        else:
            print(f"Test Case {idx} Failed. Output = {result}, Expected = {test['expected']}")

# Run the tests
test_unique_paths_with_obstacles()
