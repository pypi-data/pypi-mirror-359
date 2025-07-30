# Python program to count number of ways to reach
# nth stair using recursion

def countWays(n):

    # Base cases: If there are 0 or 1 stairs,
    # there is only one way to reach the top.
    if n == 0 or n == 1:
        return 1

    return countWays(n - 1) + countWays(n - 2)

n = 4
print(countWays(n))