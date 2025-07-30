# Python Program to solve House Robber Problem using Memoization

def maxLootRec(hval, n, memo):
    if n <= 0:
        return 0
    if n == 1:
        return hval[0]

    # Check if the result is already computed
    if memo[n] != -1:
        return memo[n]

    pick = hval[n - 1] + maxLootRec(hval, n - 2, memo)
    notPick = maxLootRec(hval, n - 1, memo)

    # Store the max of two choices in the memo array and return it
    memo[n] = max(pick, notPick)
    return memo[n]


def maxLoot(hval):
    n = len(hval)
  
    # Initialize memo array with -1
    memo = [-1] * (n + 1)
    return maxLootRec(hval, n, memo)

if __name__ == "__main__":
    hval = [6, 7, 1, 3, 8, 2, 4]
    print(maxLoot(hval))