
# Python Program to solve House Robber Problem using 
# Space Optimized Tabulation

# Function to calculate the maximum stolen value
def maxLoot(hval):
    n = len(hval)

    if n == 0:
        return 0
    if n == 1:
        return hval[0]

    # Set previous 2 values
    secondLast = 0
    last = hval[0]

    # Compute current value using previous two values
    # The final current value would be our result
    res = 0
    for i in range(1, n):
        res = max(hval[i] + secondLast, last)
        secondLast = last
        last = res

    return res

hval = [6, 7, 1, 3, 8, 2, 4]
print(maxLoot(hval))