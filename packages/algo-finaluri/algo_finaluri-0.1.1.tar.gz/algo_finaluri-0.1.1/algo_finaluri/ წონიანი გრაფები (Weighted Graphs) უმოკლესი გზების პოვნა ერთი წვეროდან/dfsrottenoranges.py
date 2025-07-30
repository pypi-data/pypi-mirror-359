# Python Program to find the minimum time
# in which all oranges will get rotten

def is_safe(i, j, n, m):
    return 0 <= i < n and 0 <= j < m

# function to perform dfs and find fresh orange


def dfs(mat, i, j, time):
    n = len(mat)
    m = len(mat[0])

    # update minimum time
    mat[i][j] = time

    # all four directions
    directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]

    # change 4-directionally connected cells
    for dir in directions:
        x = i + dir[0]
        y = j + dir[1]

        # if cell is in the matrix and
        # the orange is fresh
        if is_safe(x, y, n, m) and (mat[x][y] == 1 or mat[x][y] > time + 1):
            dfs(mat, x, y, time + 1)


def oranges_rotting(mat):
    n = len(mat)
    m = len(mat[0])

    # counter of elapsed time
    elapsed_time = 0

    # iterate through all the cells
    for i in range(n):
        for j in range(m):

            # if orange is initially rotten
            if mat[i][j] == 2:
                dfs(mat, i, j, 2)

    # iterate through all the cells
    for i in range(n):
        for j in range(m):

            # if orange is fresh
            if mat[i][j] == 1:
                return -1

            # update the maximum time
            elapsed_time = max(elapsed_time, mat[i][j] - 2)

    return elapsed_time


if __name__ == "__main__":
    mat = [[2, 1, 0, 2, 1],
          [1, 0, 1, 2, 1],
          [1, 0, 0, 2, 1]]

    print(oranges_rotting(mat))