# Python program to find minimum number
# of operations to convert s1 to s2

# Recursive function to find number of operations 
# needed to convert s1 into s2.
def editDistRec(s1, s2, m, n, memo):
    
    # If first string is empty, the only option is to
    # insert all characters of second string into first
    if m == 0:
        return n

    # If second string is empty, the only option is to
    # remove all characters of first string
    if n == 0:
        return m

    # If value is memoized
    if memo[m][n] != -1:
        return memo[m][n]

    # If last characters of two strings are same, nothing
    # much to do. Get the count for
    # remaining strings.
    if s1[m - 1] == s2[n - 1]:
        memo[m][n] = editDistRec(s1, s2, m - 1, n - 1, memo)
        return memo[m][n]

    # If last characters are not same, consider all three
    # operations on last character of first string,
    # recursively compute minimum cost for all three
    # operations and take minimum of three values.
    memo[m][n] = 1 + min(
        editDistRec(s1, s2, m, n - 1, memo),
        editDistRec(s1, s2, m - 1, n, memo),
        editDistRec(s1, s2, m - 1, n - 1, memo)
    )
    return memo[m][n]

# Wrapper function to initiate the recursive calculation
def editDistance(s1, s2):
    m, n = len(s1), len(s2)
    memo = [[-1 for _ in range(n + 1)] for _ in range(m + 1)]
    return editDistRec(s1, s2, m, n, memo)

if __name__ == "__main__":
    s1 = "abcd"
    s2 = "bcfe"
    print(editDistance(s1, s2))

    