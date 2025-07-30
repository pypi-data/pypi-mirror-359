def isSafe(grid, r, c, visited):
    row = len(grid)
    col = len(grid[0])
    
    return (0 <= r < row) and (0 <= c < col) and (grid[r][c] == 'L' and not visited[r][c])

def dfs(grid, r, c, visited):
    

    rNbr = [-1, -1, -1, 0, 0, 1, 1, 1]
    cNbr = [-1, 0, 1, -1, 1, -1, 0, 1]

    # Mark this cell as visited
    visited[r][c] = True

    # Recur for all connected neighbours
    for k in range(8):
        newR, newC = r + rNbr[k], c + cNbr[k]
        if isSafe(grid, newR, newC, visited):
            dfs(grid, newR, newC, visited)

def countIslands(grid):
    row = len(grid)
    col = len(grid[0])
    
    visited = [[False for _ in range(col)] for _ in range(row)]

    count = 0
    for r in range(row):
        for c in range(col):
            
            # If a cell with value 'L' (land) is not visited yet,
            # then a new island is found
            if grid[r][c] == 'L' and not visited[r][c]:
                
                # Visit all cells in this island.
                dfs(grid, r, c, visited)
                
                # increment the island count
                count += 1
    return count

if __name__ == "__main__":
    grid = [
        ['L', 'L', 'W', 'W', 'W'],
        ['W', 'L', 'W', 'W', 'L'],
        ['L', 'W', 'W', 'L', 'L'],
        ['W', 'W', 'W', 'W', 'W'],
        ['L', 'W', 'L', 'L', 'W']
    ]

    print(countIslands(grid))