# Python program to find Majority
# element in an array using hashmap

from collections import defaultdict

# Function to find Majority element in a list
# It returns -1 if there is no majority element
def majority_element(arr):
    n = len(arr)
    count_map = defaultdict(int)

    # Traverse the list and count occurrences using the hash map
    for num in arr:
        count_map[num] += 1
        
        # Check if current element count exceeds n / 2
        if count_map[num] > n / 2:
            return num

    # If no majority element is found, return -1
    return -1

if __name__ == "__main__":
    arr = [1, 1, 2, 1, 3, 5, 1]
    print(majority_element(arr))
