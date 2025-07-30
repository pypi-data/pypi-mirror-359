def longestPalindrome(s):
    n = len(s)
    memo = {}  # (i, j): is_palindrome

    max_len = 0
    start = 0

    def is_palindrome(i, j):
        if i >= j:
            return True
        if (i, j) in memo:
            return memo[(i, j)]
        if s[i] == s[j] and is_palindrome(i + 1, j - 1):
            memo[(i, j)] = True
        else:
            memo[(i, j)] = False
        return memo[(i, j)]

    for i in range(n):
        for j in range(i, n):
            if is_palindrome(i, j) and (j - i + 1) > max_len:
                start = i
                max_len = j - i + 1

    return s[start:start + max_len]


# ----------------------------
# Driver Code to test examples
# ----------------------------

test_cases = [
    {"input": "babad", "expected_outputs": ["bab", "aba"]},
    {"input": "cbbd", "expected_outputs": ["bb"]},
    {"input": "forgeeksskeegfor", "expected_outputs": ["geeksskeeg"]},
]

for idx, test in enumerate(test_cases, 1):
    result = longestPalindrome(test["input"])
    if result in test["expected_outputs"]:
        print(f"Example {idx} Passed: Output = \"{result}\"")
    else:
        print(f"Example {idx} Failed: Output = \"{result}\", Expected one of {test['expected_outputs']}")
