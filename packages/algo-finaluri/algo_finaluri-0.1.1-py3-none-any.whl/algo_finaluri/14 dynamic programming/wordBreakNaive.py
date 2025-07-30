def wordBreakRec(i, s, dictionary):
    # If end of string is reached,
    # return true.
    if i == len(s):
        return 1

    n = len(s)
    prefix = ""

    # Try every prefix
    for j in range(i, n):
        prefix += s[j]

        # if the prefix s[i..j] is a dictionary word
        # and rest of the string can also be broken into
        # valid words, return true
        if prefix in dictionary and wordBreakRec(j + 1, s, dictionary) == 1:
            return 1
    return 0


def wordBreak(s, dictionary):
    return wordBreakRec(0, s, dictionary)


if __name__ == "__main__":
    s = "ilike"

    dictionary = {"i", "like", "gfg"}

    print("true" if wordBreak(s, dictionary) else "false")