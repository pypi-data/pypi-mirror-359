# Implementing LRU Cache using a Doubly Linked List + HashMap
class ListNode:
    """Represents a node in a doubly linked list."""
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None

class LinkedList:
    """Doubly Linked List to maintain the order of elements."""
    def __init__(self):
        self.head = None
        self.tail = None
    
    def insert(self, node):
        """Insert a node at the end of the linked list (most recently used)."""
        if self.head is None:
            self.head = node
        else:
            self.tail.next = node
            node.prev = self.tail
        self.tail = node
            
    def delete(self, node):
        """Remove a node from the linked list."""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

class LRUCache:
    """LRU Cache implemented using a Linked List and HashMap."""
    def __init__(self, capacity):
        self.list = LinkedList()
        self.cache = {}
        self.capacity = capacity
        
    def _insert(self, key, val):
        """Helper function to insert a new key-value pair into the cache."""
        node = ListNode(key, val)
        self.list.insert(node)
        self.cache[key] = node

    def get(self, key):
        """Retrieve value if key exists, else return -1. Move key to the end (most recently used)."""
        if key in self.cache:
            val = self.cache[key].val
            self.list.delete(self.cache[key])
            self._insert(key, val)
            return val
        return -1

    def put(self, key, val):
        """Insert a key-value pair into the cache. If full, remove the LRU item."""
        if key in self.cache:
            self.list.delete(self.cache[key])
        elif len(self.cache) == self.capacity:
            # Remove least recently used item
            del self.cache[self.list.head.key]
            self.list.delete(self.list.head)
        self._insert(key, val)

# Example usage:
cache = LRUCache(2)  # Capacity of 2

cache.put(1, 1)  # Cache: {1:1}
cache.put(2, 2)  # Cache: {1:1, 2:2}
print(cache.get(1))  # Returns 1, Cache: {2:2, 1:1}
cache.put(3, 3)  # Removes least recently used (key=2), Cache: {1:1, 3:3}
print(cache.get(2))  # Returns -1 (not found)
cache.put(4, 4)  # Removes least recently used (key=1), Cache: {3:3, 4:4}
print(cache.get(1))  # Returns -1 (not found)
print(cache.get(3))  # Returns 3
print(cache.get(4))  # Returns 4
