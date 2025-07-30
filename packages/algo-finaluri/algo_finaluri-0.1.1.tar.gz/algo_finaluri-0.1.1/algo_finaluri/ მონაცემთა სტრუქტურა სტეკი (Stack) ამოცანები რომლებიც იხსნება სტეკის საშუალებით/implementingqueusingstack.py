# Define MyQueue class first
class MyQueue:
    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def push(self, x: int) -> None:
        print(f"Pushing {x} to queue")
        self.in_stack.append(x)

    def pop(self) -> int:
        self._shift_stacks()
        popped = self.out_stack.pop()
        print(f"Popped {popped} from queue")
        return popped

    def peek(self) -> int:
        self._shift_stacks()
        front = self.out_stack[-1]
        print(f"Front element is {front}")
        return front

    def empty(self) -> bool:
        is_empty = not self.in_stack and not self.out_stack
        print(f"Is queue empty? {is_empty}")
        return is_empty

    def _shift_stacks(self):
        if not self.out_stack:
            print("Shifting elements from in_stack to out_stack...")
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())

# -------------------
# 🚀 Driver Code
# -------------------

if __name__ == "__main__":
    q = MyQueue()

    q.push(1)       # Queue: [1]
    q.push(2)       # Queue: [1, 2]
    q.peek()        # Should print 1
    q.pop()         # Removes 1
    q.empty()       # Should print False

    q.pop()         # Removes 2
    q.empty()       # Should print True

    q.push(3)
    q.push(4)
    q.peek()        # Should print 3
    q.pop()         # Should remove 3
    q.peek()        # Should print 4
