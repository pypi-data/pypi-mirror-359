from collections import deque

class MyStack:
    def __init__(self):
        self.q1 = deque()
        self.q2 = deque()

    def push(self, x):
        self.q2.append(x)
        while self.q1:
            self.q2.append(self.q1.popleft())
        self.q1, self.q2 = self.q2, self.q1

    def pop(self):
        return self.q1.popleft()

    def top(self):
        return self.q1[0]

    def empty(self):
        return len(self.q1) == 0
    
    # Driver Code
if __name__ == "__main__":
    stack = MyStack()

    print("Stack is empty?", stack.empty())  # True

    stack.push(10)
    stack.push(20)
    stack.push(30)

    print("Top element:", stack.top())       # 30
    print("Popped element:", stack.pop())    # 30
    print("Top after pop:", stack.top())     # 20
    print("Is stack empty?", stack.empty())  # False

    stack.pop()
    stack.pop()

    print("Is stack empty after popping all?", stack.empty())  # True

