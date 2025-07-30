# Python program to find Optimal parenthesization
# using Recursion

def matrixChainOrderRec(arr, i, j):
    # If there is only one matrix
    if i == j:
        temp = chr(ord('A') + i)
        return (temp, 0)

    res = float('inf')
    str = ""
    # Try all possible split points k between i and j
    for k in range(i + 1, j + 1):
        left = matrixChainOrderRec(arr, i, k - 1)
        right = matrixChainOrderRec(arr, k, j)
        # Calculate the cost of multiplying 
        # matrices from i to k and from k to j
        currCost = left[1] + right[1] + arr[i] * arr[k] * arr[j + 1]
        # Update if we find a lower cost
        if res > currCost:
            res = currCost
            str = "(" + left[0] + right[0] + ")"

    return (str, res)

def matrixChainOrder(arr):
    n = len(arr)
    return matrixChainOrderRec(arr, 0, n - 2)[0]

arr = [40, 20, 30, 10, 30]
print(matrixChainOrder(arr))