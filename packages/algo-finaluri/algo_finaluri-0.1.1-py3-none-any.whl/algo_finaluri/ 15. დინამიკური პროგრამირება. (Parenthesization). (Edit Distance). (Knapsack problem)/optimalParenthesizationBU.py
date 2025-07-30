# Python program to find Optimal parenthesization 
# using Tabulation

def matrixChainOrder(arr):
    n = len(arr)

    # dp[i][j] stores a pair: matrix order, 
    # minimum cost
    dp = [[("", 0) for i in range(n)] for i in range(n)]

    # Base Case: Initializing diagonal of the dp
    # Cost for multiplying a single matrix is zero
    for i in range(n):
        temp = ""

        # Label the matrices as A, B, C, ...
        temp += chr(ord('A') + i)

        # No cost for multiplying a single matrix
        dp[i][i] = (temp, 0)

    # Fill the DP table for chain lengths 
    # greater than 1
    for length in range(2, n):
        for i in range(n - length):
            j = i + length - 1
            cost = float("inf")
            str = ""

            # Try all possible split points k
            # between i and j
            for k in range(i + 1, j + 1):

                # Calculate the cost of multiplying 
                # matrices from i to k and from k to j
                currCost = (
                    dp[i][k - 1][1] + dp[k][j][1]
                    + arr[i] * arr[k] * arr[j + 1]
                )

                # Update if we find a lower cost
                if currCost < cost:
                    cost = currCost
                    str = "(" + dp[i][k - 1][0] + dp[k][j][0] + ")"

            dp[i][j] = (str, cost)

    # Return the optimal matrix order for
    # the entire chain
    return dp[0][n - 2][0]

arr = [40, 20, 30, 10, 30]
print(matrixChainOrder(arr))