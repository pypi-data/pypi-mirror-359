# Our own Hashnode class
class HashNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value

# Our own Hashmap class
class HashMap:
    # hash element array
    def __init__(self):
        self.capacity = 20
        self.size = 0
        self.arr = [None] * self.capacity
        # dummy node
        self.dummy = HashNode(-1, -1)

    # This implements hash function to find index for a key
    def hashCode(self, key):
        return key % self.capacity

    # Function to add key value pair
    def insertNode(self, key, value):
        temp = HashNode(key, value)
        # Apply hash function to find index for given key
        hashIndex = self.hashCode(key)
        # find next free space
        while self.arr[hashIndex] is not None and self.arr[hashIndex].key != key and self.arr[hashIndex].key != -1:
            hashIndex += 1
            hashIndex %= self.capacity
        # if new node to be inserted, increase the current size
        if self.arr[hashIndex] is None or self.arr[hashIndex].key == -1:
            self.size += 1
        self.arr[hashIndex] = temp

    # Function to delete a key value pair 
    def deleteNode(self, key):
        # Apply hash function to find index for given key
        hashIndex = self.hashCode(key)
        # finding the node with given key
        while self.arr[hashIndex] is not None:
            # if node found
            if self.arr[hashIndex].key == key:
                temp = self.arr[hashIndex]
                # Insert dummy node here for further use
                self.arr[hashIndex] = self.dummy
                # Reduce size
                self.size -= 1
                return temp.value
            hashIndex += 1
            hashIndex %= self.capacity
        # If not found return None
        return None

    # Function to search the value for a given key
    def get(self, key):
        # Apply hash function to find index for given key
        hashIndex = self.hashCode(key)
        counter = 0
        # finding the node with given key
        while self.arr[hashIndex] is not None:
            # If counter is greater than capacity to avoid infinite loop
            if counter > self.capacity:
                return None
            # if node found return its value
            if self.arr[hashIndex].key == key:
                return self.arr[hashIndex].value
            hashIndex += 1
            hashIndex %= self.capacity
            counter += 1
        # If not found return None
        return 0

    # Return current size
    def sizeofMap(self):
        return self.size

    # Return true if size is 0
    def isEmpty(self):
        return self.size == 0

    # Function to display the stored key value pairs
    def display(self):
        for i in range(self.capacity):
            if self.arr[i] is not None and self.arr[i].key != -1:
                print("key = ", self.arr[i].key,
                      " value = ", self.arr[i].value)


# Driver method to test map class
if __name__ == "__main__":
    h = HashMap()
    h.insertNode(1, 1)
    h.insertNode(2, 2)
    h.insertNode(2, 3)
    h.display()
    print(h.sizeofMap())
    print(h.deleteNode(2))
    print(h.sizeofMap())
    print(h.isEmpty())
    print(h.get(2))
