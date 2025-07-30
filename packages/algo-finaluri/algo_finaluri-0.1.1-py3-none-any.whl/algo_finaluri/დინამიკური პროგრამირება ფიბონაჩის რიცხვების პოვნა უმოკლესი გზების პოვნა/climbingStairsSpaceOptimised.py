# Python program to count number of ways to
# reach nth stair using Space Optimized DP

def countWays(n):
  
    # variable prev1, prev2 - to store the
    # values of last and second last states 
    prev1 = 1
    prev2 = 1
  
    for i in range(2, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
  
    # In last iteration final value
    # of curr is stored in prev.
    return prev1

n = 4
print(countWays(n))

