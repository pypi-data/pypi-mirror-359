def longestPalindrome(s):
    n = len(s)
    if n == 0:
        return ""

    # Create a 2D table to store palindrome truth values
    table = [[False] * n for _ in range(n)]

    start = 0  # Starting index of the longest palindrome
    max_len = 1  # At least every single character is a palindrome

    # Every single character is a palindrome
    for i in range(n):
        table[i][i] = True

    # Check for sub-strings of length 2
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            table[i][i + 1] = True
            start = i
            max_len = 2

    # Check for lengths greater than 2
    for length in range(3, n + 1):  # length of the substring
        for i in range(n - length + 1):
            j = i + length - 1  # Ending index

            # Check if substring s[i+1..j-1] is a palindrome
            if s[i] == s[j] and table[i + 1][j - 1]:
                table[i][j] = True
                if length > max_len:
                    start = i
                    max_len = length

    return s[start:start + max_len]


# ----------------------------
# Driver Code to test examples
# ----------------------------

test_cases = [
    {"input": "babad", "expected_outputs": ["bab", "aba"]},
    {"input": "cbbd", "expected_outputs": ["bb"]}
]

for idx, test in enumerate(test_cases, 1):
    result = longestPalindrome(test["input"])
    if result in test["expected_outputs"]:
        print(f"Example {idx} Passed: Output = \"{result}\"")
    else:
        print(f"Example {idx} Failed: Output = \"{result}\", Expected one of {test['expected_outputs']}")
