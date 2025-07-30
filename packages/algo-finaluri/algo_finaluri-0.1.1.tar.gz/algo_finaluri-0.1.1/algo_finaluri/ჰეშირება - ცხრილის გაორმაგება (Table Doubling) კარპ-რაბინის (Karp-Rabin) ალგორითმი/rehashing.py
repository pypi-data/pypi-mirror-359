class Hash:
    def __init__(self, b):
        self.BUCKET = b  # Number of buckets
        self.numOfElements = 0  # To track the number of elements
        self.table = [[] for _ in range(self.BUCKET)] 

    # Hash function to map values to key
    def hashFunction(self, key):
        return key % self.BUCKET

    # Function to calculate the current load factor
    def getLoadFactor(self):
        return self.numOfElements / self.BUCKET

    # Rehashing function to double the capacity and re-insert elements
    def rehashing(self):
        oldBucket = self.BUCKET
        self.BUCKET = 2 * self.BUCKET  # Double the number of buckets
        oldTable = self.table  # Store current table

        # Initialize new table with doubled size
        self.table = [[] for _ in range(self.BUCKET)]
        self.numOfElements = 0  # Reset the element count

        # Re-insert old values into the new table
        for i in range(oldBucket):
            for key in oldTable[i]:
                self.insertItem(key)

    # Inserts a key into the hash table
    def insertItem(self, key):
        # If load factor exceeds 0.5, rehash
        while self.getLoadFactor() > 0.5:
            self.rehashing()

        index = self.hashFunction(key)
        self.table[index].append(key)
        self.numOfElements += 1

    # Deletes a key from the hash table
    def deleteItem(self, key):
        index = self.hashFunction(key)
        if key in self.table[index]:
            self.table[index].remove(key)
            self.numOfElements -= 1

    # Display the hash table
    def displayHash(self):
        for i in range(self.BUCKET):
            print(f"{i}", end="")
            for x in self.table[i]:
                print(f" --> {x}", end="")
            print()


# Driver program
if __name__ == "__main__":
    # List that contains keys to be mapped
    a = [15, 11, 12]

    # Insert the keys into the hash table
    h = Hash(7)  # 7 is the number of buckets in the hash table
    for key in a:
        h.insertItem(key)
    h.displayHash()
    # Delete 12 from the hash table
    h.deleteItem(12)

    # Display the hash table
    h.displayHash()

    # Insert more items to trigger rehashing
    h.insertItem(33)
    h.insertItem(45)
    h.insertItem(19)

    # Display the hash table after rehashing
    print("\nAfter rehashing:")
    h.displayHash()
