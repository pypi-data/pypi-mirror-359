# Python program to find Optimal parenthesization 
# using Memoization

def matrixChainOrderRec(arr, i, j, memo):
  
    # If there is only one matrix
    if i == j:
        temp = chr(ord('A') + i)
        return (temp, 0)

    # if the result for this subproblem is 
    # already computed then return it
    if memo[i][j][1] != -1:
        return memo[i][j]

    res = float('inf')
    str = ""

    # Try all possible split points k between i and j
    for k in range(i + 1, j + 1):
        left = matrixChainOrderRec(arr, i, k - 1, memo)
        right = matrixChainOrderRec(arr, k, j, memo)

        # Calculate the cost of multiplying 
        # matrices from i to k and from k to j
        curr = left[1] + right[1] + arr[i] * arr[k] * arr[j + 1]

        # Update if we find a lower cost
        if res > curr:
            res = curr
            str = "(" + left[0] + right[0] + ")"

    # Return minimum cost and matrix 
    # multiplication order
    memo[i][j] = (str, res)
    return memo[i][j]

def matrixChainOrder(arr):
    n = len(arr)

    # Memoization array to store the results
    memo = [[("", -1) for i in range(n)] for i in range(n)]

    return matrixChainOrderRec(arr, 0, n - 2, memo)[0]

arr = [40, 20, 30, 10, 30]
print(matrixChainOrder(arr))