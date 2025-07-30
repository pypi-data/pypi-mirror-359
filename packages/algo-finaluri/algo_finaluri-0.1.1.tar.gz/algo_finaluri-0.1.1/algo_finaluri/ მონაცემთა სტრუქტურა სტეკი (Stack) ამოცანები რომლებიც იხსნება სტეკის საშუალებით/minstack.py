class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = [float('inf')]

    def push(self, val: int) -> None:
        self.stack.append(val)
        self.min_stack.append(min(val, self.min_stack[-1]))

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def get_min(self) -> int:
        return self.min_stack[-1]
    

# MinStack კლასის ტესტირება
min_stack = MinStack()

# ელემენტების დამატება
min_stack.push(3)
min_stack.push(5)
print(min_stack.get_min())  # Output: 3

min_stack.push(2)
min_stack.push(8)
print(min_stack.get_min())  # Output: 2

# ბოლო ელემენტის ამოღება
min_stack.pop()
print(min_stack.get_min())  # Output: 2

# ბოლო ელემენტის ამოღება და ტოპის ჩვენება
min_stack.pop()
print(min_stack.top())  # Output: 2

# მინიმუმის მიღება
print(min_stack.get_min())  # Output: 3
