# Python program to count number of ways 
# to reach nth stair using Tabulation

def countWays(n):
    dp = [0] * (n + 1)
  
    # Base cases
    dp[0] = 1
    dp[1] = 1

    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]; 
  
    return dp[n]

n = 4
print(countWays(n))
