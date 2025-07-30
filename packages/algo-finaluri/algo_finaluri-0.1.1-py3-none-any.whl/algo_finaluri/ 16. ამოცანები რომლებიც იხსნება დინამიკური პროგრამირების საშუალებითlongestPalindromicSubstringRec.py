def checkPal(str, low, high):
    while low < high:
        if str[low] != str[high]:
            return False
        low += 1
        high -= 1
    return True

def longestPalindrome(s):
    n = len(s)
    maxLen = 1
    start = 0

    for i in range(n):
        for j in range(i, n):
            if checkPal(s, i, j) and (j - i + 1) > maxLen:
                start = i
                maxLen = j - i + 1

    return s[start:start + maxLen]

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
