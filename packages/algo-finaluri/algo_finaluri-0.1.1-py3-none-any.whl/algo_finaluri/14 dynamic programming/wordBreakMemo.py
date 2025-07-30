def wordBreakRec(ind, s, dict, dp):
    if ind >= len(s):
        return True
    if dp[ind] != -1:
        return dp[ind] == 1
    possible = False
    for temp in dict:
        if len(temp) > len(s) - ind:
            continue
        if s[ind:ind+len(temp)] == temp:
            possible |= wordBreakRec(ind + len(temp), s, dict, dp)
    dp[ind] = 1 if possible else 0
    return possible

def word_break(s, dict):
    n = len(s)
    dp = [-1] * (n + 1)
    return wordBreakRec(0, s, dict, dp)

s = "ilike"
dict = ["i", "like", "gfg"]
print("true" if word_break(s, dict) else "false")