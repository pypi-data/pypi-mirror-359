# Python program to count number of ways to reach nth stair 
# using memoization

def countWaysRec(n, memo):
  
    # Base cases
    if n == 0 or n == 1:
        return 1

    # if the result for this subproblem is 
    # already computed then return it
    if memo[n] != -1:
        return memo[n]

    memo[n] = countWaysRec(n - 1, memo) + countWaysRec(n - 2, memo)
    return memo[n]

def countWays(n):
  
    # Memoization array to store the results
    memo = [-1] * (n + 1)
    return countWaysRec(n, memo)

if __name__ == "__main__":
    n = 4
    print(countWays(n))
    