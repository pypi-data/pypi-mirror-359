# Python program to implement word break
def wordBreak(s, dictionary):
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True

    # Traverse through the given string
    for i in range(1, n + 1):

        # Traverse through the dictionary words
        for w in dictionary:

            # Check if current word is present
            # the prefix before the word is also
            # breakable
            start = i - len(w)
            if start >= 0 and dp[start] and s[start:start + len(w)] == w:
                dp[i] = True
                break
    return 1 if dp[n] else 0


if __name__ == '__main__':
    s = "ilike"

    dictionary = ["i", "like", "gfg"]

    print("true" if wordBreak(s, dictionary) else "false")