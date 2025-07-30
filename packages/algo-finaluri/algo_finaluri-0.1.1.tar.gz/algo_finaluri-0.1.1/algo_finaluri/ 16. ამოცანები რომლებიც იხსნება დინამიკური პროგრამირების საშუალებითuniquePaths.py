class Solution:
  def uniquePaths(self, m: int, n: int) -> int:
    # dp[i][j] := the number of unique paths from (0, 0) to (i, j)
    dp = [[1] * n for _ in range(m)]

    for i in range(1, m):
      for j in range(1, n):
        dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

    return dp[-1][-1]
  

def test_unique_paths():
    solution = Solution()

    test_cases = [
        {"m": 3, "n": 7, "expected": 28},
        {"m": 3, "n": 2, "expected": 3},
        {"m": 7, "n": 3, "expected": 28},
        {"m": 3, "n": 3, "expected": 6},
        {"m": 1, "n": 1, "expected": 1},
        {"m": 10, "n": 10, "expected": 48620},
    ]

    for i, test in enumerate(test_cases, 1):
        result = solution.uniquePaths(test["m"], test["n"])
        if result == test["expected"]:
            print(f"Test Case {i} Passed: Output = {result}")
        else:
            print(f"Test Case {i} Failed: Output = {result}, Expected = {test['expected']}")

# Run the test
test_unique_paths()
