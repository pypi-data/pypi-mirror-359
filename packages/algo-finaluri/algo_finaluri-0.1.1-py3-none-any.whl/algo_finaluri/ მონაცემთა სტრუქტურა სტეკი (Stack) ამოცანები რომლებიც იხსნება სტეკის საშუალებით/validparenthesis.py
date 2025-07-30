def isBalanced(s):
    stack = []
    bracket_map = {')': '(', '}': '{', ']': '['}

    for char in s:
        if char in bracket_map.values():  # Opening brackets
            stack.append(char)
        elif char in bracket_map:  # Closing brackets
            if not stack or stack[-1] != bracket_map[char]:
                return False
            stack.pop()
    return not stack

if __name__ == "__main__":
    s = "{([])})"
    print("true" if isBalanced(s) else "false")