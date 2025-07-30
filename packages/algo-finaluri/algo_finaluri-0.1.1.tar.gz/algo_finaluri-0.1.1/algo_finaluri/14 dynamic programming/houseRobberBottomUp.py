# Python Program to solve House Robber Problem using Tabulation

def maxLoot(hval):
    n = len(hval)
  
    # Create a dp array to store the maximum loot at each house
    dp = [0] * (n + 1)

    # Base cases
    dp[0] = 0
    dp[1] = hval[0]

    # Fill the dp array using the bottom-up approach
    for i in range(2, n + 1):
        dp[i] = max(hval[i - 1] + dp[i - 2], dp[i - 1])

    return dp[n]

hval = [6, 7, 1, 3, 8, 2, 4]
print(maxLoot(hval))