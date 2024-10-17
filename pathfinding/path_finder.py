# Curses is a terminal control library for Unix-like systems, enabling the creation of text-based user interfaces.
import curses
from curses import wrapper

# For the maze generation
import math
import random
import time

# For user input
import csv
import argparse

# For the queue and priority queue
import queue
import heapq

def maze_csv(path='pathfinding/maze.csv'): 
    """Reads a maze from a CSV file."""
    with open(path, newline='') as f:
        reader = csv.reader(f)
        maze = list(reader)
    return maze

def maze_small():
    """Small maze for testing."""
    return [
        ["#", "O", "#", "#", "#", "#", "#", "#", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", "#"],
        ["#", " ", "#", "#", " ", "#", "#", " ", "#"],
        ["#", " ", "#", " ", " ", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", "#", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "X", "#"]
    ]

def maze_large():
    """Large maze for testing."""
    return [
        ["#", "O", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        ["#", " ", "#", "#", " ", "#", "#", " ", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", " ", "#"],
        ["#", " ", "#", " ", " ", " ", "#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", "#", "#", "#", "#", "#", "#", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", "#", "#", "#", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "X", "#", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", "#", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", " ", " ", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", "#", "#", "#", "#", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"]
    ]
    
def random_grid_maze(rows, cols):
    """
    Generates a random grid maze.
    
    Parameters:
        - rows (int) - The number of rows in the maze.
        - cols (int) - The number of columns in the maze.
    
    Returns:
        - maze (list) - A 2D list representing the maze, where '#' represents walls and ' ' represents paths.
        The maze also contains a start point 'O' and an end point 'X'.
    """
    # Create an empty maze with walls
    maze = [['#' if i == 0 or i == rows-1 or j == 0 or j == cols-1 else ' ' for j in range(cols)] for i in range(rows)]

    # Add internal walls and paths
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            if i % 2 == 0 and j % 2 == 0:
                maze[i][j] = '#'
            elif i % 4 == 0 and j % 4 == 0:
                maze[i][j] = '#'
            elif i % 6 == 0 and j % 6 == 0:
                maze[i][j] = '#'

    # Place the start and end points, randomly
    maze[random.randint(1, rows-2)][random.randint(1, cols-2)] = 'O'
    maze[random.randint(1, rows-2)][random.randint(1, cols-2)] = 'X'
    
    return maze

def random_maze(rows, cols, p=0.3):
    """
    Generates a random maze with the specified number of rows and columns.
    
    Parameters:
        - rows (int) - The number of rows in the maze.
        - cols (int) - The number of columns in the maze.
        - p (float) - The probability of a cell being a wall ('#'). Default is 0.3.
    
    Returns:
        - maze (list) - A 2D list representing the generated maze, where '#' represents a wall and ' ' represents an empty cell.
    """
    maze = []
    for _ in range(rows):
        row = []
        for _ in range(cols):
            if random.random() < p:
                row.append("#")
            else:
                row.append(" ")
        maze.append(row)
    maze[0][1] = "O"
    maze[-1][-2] = "X"
    
    # Surround the maze with walls
    for row in maze:
        row.insert(0, "#")
        row.append("#")
    maze.insert(0, ["#" for _ in range(len(maze[0]))])
    maze.append(["#" for _ in range(len(maze[0]))])
    
    return maze

def print_maze(maze, stdscr, path=[], start=None, end=None, steps=0, offset=(0, 0), visited=None, path_len=None):
    """
    Prints the maze on the screen using curses library.
    
    Args:
        maze (list) -  The maze represented as a 2D list.
        stdscr: The curses window object.
        path (list, optional) -  The list of positions in the path. Defaults to an empty list.
        start (tuple, optional) -  The start position. Defaults to None.
        end (tuple, optional) -  The end position. Defaults to None.
        steps (int, optional) -  The number of steps taken. Defaults to 0.
        offset (tuple, optional) -  The offset for printing the maze. Defaults to (0, 0).
        visited (set, optional) -  The set of visited positions. Defaults to None.
        path_len (int, optional) -  The length of the path. Defaults to None.
    """
    # Define colors
    BLUE = curses.color_pair(1)
    RED = curses.color_pair(2)
    GREEN = curses.color_pair(3)
    YELLOW = curses.color_pair(4)

    for i, row in enumerate(maze):                                      # For each row in the maze
        for j, value in enumerate(row):                                 # For each column in the row
            if (i, j) == start:                                         # If the current position is the start
                stdscr.addstr(i+offset[0], j*2+offset[1], value, YELLOW)
            elif (i, j) == end:                                         # If the current position is the end
                stdscr.addstr(i+offset[0], j*2+offset[1], value, YELLOW)
            elif (i, j) in path:                                        # If the current position is in the path
                stdscr.addstr(i+offset[0], j*2+offset[1], "X", RED)
            elif visited and (i, j) in visited:                         # If the current position has been visited
                stdscr.addstr(i+offset[0], j*2+offset[1], "X", GREEN) 
            else:                                                       # Otherwise
                stdscr.addstr(i+offset[0], j*2+offset[1], value, BLUE)  # Print the value
    
    # Add markers for start, end, path, steps, and visited count
    stdscr.addstr(len(maze)//2 -1+offset[0], len(maze[0])*2+offset[1]+1, "O-Start", YELLOW)
    stdscr.addstr(len(maze)//2   +offset[0], len(maze[0])*2+offset[1]+1, "X-End", YELLOW)
    stdscr.addstr(len(maze)//2 +1+offset[0], len(maze[0])*2+offset[1]+1, "X-Path", RED)
    stdscr.addstr(len(maze)//2 +2+offset[0], len(maze[0])*2+offset[1]+1, f"Step count: {steps}", RED)
    if visited: 
        stdscr.addstr(len(maze)//2 +3+offset[0], len(maze[0])*2+offset[1]+1, f"Visited count: {len(visited)}", GREEN)
    if path_len:
        stdscr.addstr(len(maze)//2 +4+offset[0], len(maze[0])*2+offset[1]+1, f"Path length: {len(path)-1}", RED)

def find_val(maze, val):
    """
    Finds the position of a given value in a maze.

    Parameters:
        maze (list) - A 2D list representing the maze.
        val - The value to be found in the maze.

    Returns:
        tuple - The position (row, column) of the value in the maze.
        Returns None if the value is not found.
    """
    for i, row in enumerate(maze):          # For each row in the maze
        for j, value in enumerate(row):     # For each column in the row
            if value == val:              # If the value is the start
                return i, j                 # Return the position
    return None

def bfs(maze, stdscr):
    """
    Breadth-First Search algorithm to find the shortest path in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        stdscr - The curses window object.
    
    Returns:
        bool - True if the path is found, False otherwise.
        list - The path from the start to the end position.
        int - The length of the path.
        int - The number of steps taken.
        list - The list of visited positions.
    """
    start = "O"                         # Start position
    end = "X"                           # End position
    start_pos = find_val(maze, start)   # Find the start position
    end_pos = find_val(maze, end)       # Find the end position

    q = queue.Queue()   # Create a queue
    q.put([start_pos])  # Put the start position in the queue
    visited = set()     # Create a set to store visited positions

    steps = 0
    while not q.empty():            # While the queue is not empty
        path = q.get()              # Get the path from the queue
        row, col = path[-1]         # Get the current position

        stdscr.clear()              # Clear the screen
        steps += 1
        print_maze(maze, stdscr, path, start_pos, end_pos, steps, visited=list(visited))  # Print the maze
        # time.sleep(0.1)             # Sleep 
        stdscr.refresh()            # Refresh the screen

        # If the current position is the end position
        if maze[row][col] == end:   
            stdscr.addstr(len(maze), len(maze[0])//2, "Path found!")
            stdscr.addstr(len(maze)+1, len(maze[0])//2, f"Path length: {len(path)-1}")
            return True, path, len(path)-1, steps, list(visited)
        
        # Else, find the neighbors of the current position
        neighbors = find_neighbors(maze, row, col)
        for neighbor in neighbors:      # For each neighbor
            if neighbor in visited:     # If the neighbor has been visited
                continue                # Skip

            r, c = neighbor
            if maze[r][c] == "#":       # If the neighbor is a wall
                continue                # Skip

            new_path = path + [neighbor]    # Add the neighbor to the path
            q.put(new_path)                 # Put the new path in the queue
            visited.add(neighbor)           # Add the neighbor to the visited set
    
    stdscr.addstr(len(maze), len(maze[0])//2, "No path found!")
    return True, path, len(path)-1, steps, list(visited)

def dfs(maze, stdscr):
    """
    Breadth-First Search algorithm to find the shortest path in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        stdscr - The curses window object.
    
    Returns:
        bool - True if the path is found, False otherwise.
        list - The path from the start to the end position.
        int - The length of the path.
        int - The number of steps taken.
        list - The list of visited positions.
    """
    start = "O"                         # Start position
    end = "X"                           # End position
    start_pos = find_val(maze, start)   # Find the start position
    end_pos = find_val(maze, end)       # Find the end position

    # Stack, visited set, and path list
    stack = [start_pos]
    visited = set()
    path = []

    while stack:                        # While the stack is not empty
        current_pos = stack.pop()       # Pop the top position from the stack
        path.append(current_pos)        # Add the position to the path
        row, col = current_pos          # Get the row and column of the position

        # Clear the screen and print the maze
        stdscr.clear()
        print_maze(maze, stdscr, path, start_pos, end_pos, len(path))
        stdscr.refresh()
        
        # If the current position is the end, return the path
        if maze[row][col] == end:
            stdscr.addstr(len(maze), len(maze[0])//2, "Path found!")
            stdscr.addstr(len(maze)+1, len(maze[0])//2, f"Path length: {len(path)-1}")
            return True, path, len(path)-1, len(path), path

        # Else, find the neighbors of the current position
        neighbors = find_neighbors(maze, row, col)
        
        # For each neighbor, if it has not been visited and is not a wall, add it to the stack
        for neighbor in neighbors:
            if neighbor not in visited and maze[neighbor[0]][neighbor[1]] != "#":
                stack.append(neighbor)
                visited.add(neighbor)

    # If no path is found, return False
    stdscr.addstr(len(maze), len(maze[0])//2, "No path found!")
    return False, path, len(path)-1, len(path), path

def a_star(maze, stdscr, heuristic_type="manhattan"):
    """
    A* Search algorithm to find the shortest path in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        stdscr - The curses window object.
        heuristic_type (str) - The heuristic function to use. Default is "manhattan".
    
    Returns:
        bool - True if the path is found, False otherwise.
        list - The path from the start to the end position.
        int - The length of the path.
        int - The number of steps taken.
        list - The list of visited positions.
    """
    start = "O"                         # Start position
    end = "X"                           # End position
    start_pos = find_val(maze, start)   # Find the start position
    end_pos = find_val(maze, end)       # Find the end position

    open_set = queue.PriorityQueue()    # Priority queue
    open_set.put((0, start_pos))        # Put the start position in the queue
    came_from = {}                      # Dictionary to store the path
    g_score = {start_pos: 0}                                # Dictionary to store the g-score, the cost from the start to the current position
    f_score = {start_pos: heuristic(start_pos, end_pos, heuristic_type)}    # Dictionary to store the f-score, the sum of the g-score and the heuristic
    visited = set()                     # Set to store visited positions
    
    # While the open set is not empty
    while not open_set.empty():
        current = open_set.get()[1]     # Get the current position

        # If the current position is the end position
        if current == end_pos:
            path = []
            while current in came_from:         # While the current position is in the path
                path.append(current)            # Add the current position to the path
                current = came_from[current]    # Move to the next position
            path.append(start_pos)              # Add the start position to the path
            path.reverse()                      # Reverse the path
            
            # Print the maze with the path
            stdscr.clear()
            print_maze(maze, stdscr, path=path, start=start_pos, end=end_pos, steps=len(visited),visited=visited)
            stdscr.refresh()

            # Return the path
            return True, path, len(path)-1, len(visited), visited

        visited.add(current)    # Add the current position to the visited set
        row, col = current      # Get the row and column of the current position

        # Clear the screen and print the maze
        stdscr.clear()
        print_maze(maze, stdscr, path=[], start=start_pos, end=end_pos, steps=len(visited),visited=visited)
        stdscr.refresh()

        # Else, find the neighbors of the current position
        neighbors = find_neighbors(maze, row, col)
        
        # For each neighbor, if it has not been visited and is not a wall, calculate the g-score and f-score
        for neighbor in neighbors:
            if neighbor in visited or maze[neighbor[0]][neighbor[1]] == "#":
                continue
            tentative_g_score = g_score[current] + 1

            # If the neighbor is not in the g-score dictionary or the tentative g-score is less than the current g-score
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end_pos, heuristic_type)
                open_set.put((f_score[neighbor], neighbor))

    # If no path is found, return False
    stdscr.addstr(len(maze), len(maze[0])//2, "No path found!")
    return False, [], 0, len(visited), visited

def heuristic(pos1, pos2, type="manhattan"):
    """Calculate the Manhattan distance between two positions."""
    if type == "manhattan":
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    if type == "euclidean":
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    if type == "chebyshev":
        return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))
    if type == "octile":
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

def gbfs(maze, stdscr):
    """
    Greedy Best-First Search algorithm to find the shortest path in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        stdscr - The curses window object.
    
    Returns:
        bool - True if the path is found, False otherwise.
        list - The path from the start to the end position.
        int - The length of the path.
        int - The number of steps taken.
        list - The list of visited positions.
    """
    start = "O"                         # Start position
    end = "X"                           # End position
    start_pos = find_val(maze, start)   # Find the start position
    end_pos = find_val(maze, end)       # Find the end position

    open_set = queue.PriorityQueue()    # Priority queue
    open_set.put((0, start_pos))        # Put the start position in the queue
    came_from = {}                      # Dictionary to store the path
    visited = set()                     # Set to store visited positions

    # While the open set is not empty
    while not open_set.empty():
        current = open_set.get()[1]     # Get the current position

        # If the current position is the end position
        if current == end_pos:
            path = []                   
            while current in came_from:         # While the current position is in the path
                path.append(current)            # Add the current position to the path
                current = came_from[current]    # Move to the next position
            path.append(start_pos)              # Add the start position to the path
            path.reverse()                      # Reverse the path
            
            # Print the maze with the path
            stdscr.clear()
            print_maze(maze, stdscr, path=path, start=start_pos, end=end_pos, steps=len(visited), visited=visited)
            stdscr.refresh()

            # Return the path
            return True, path, len(path)-1, len(visited), visited

        # Else, add the current position to the visited set
        visited.add(current)
        row, col = current

        # Clear the screen and print the maze
        stdscr.clear()
        print_maze(maze, stdscr, path=[], start=start_pos, end=end_pos, steps=len(visited), visited=visited)
        stdscr.refresh()

        # Else, find the neighbors of the current position
        neighbors = find_neighbors(maze, row, col)
        
        # For each neighbor, if it has not been visited and is not a wall, calculate the heuristic
        for neighbor in neighbors:
            if neighbor in visited or maze[neighbor[0]][neighbor[1]] == "#":
                continue

            if neighbor not in visited:
                came_from[neighbor] = current               # Add the current position to the path
                priority = heuristic(neighbor, end_pos)     # Calculate the heuristic
                open_set.put((priority, neighbor))          # Put the neighbor in the queue

    # If no path is found, return False
    stdscr.addstr(len(maze), len(maze[0])//2, "No path found!")
    return False, [], 0, len(visited), visited    

def dijkstra(maze, stdscr):
    """
    Dijkstra's algorithm to find the shortest path in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        stdscr - The curses window object.
    
    Returns:
        bool - True if the path is found, False otherwise.
        list - The path from the start to the end position.
        int - The length of the path.
        int - The number of steps taken.
        list - The list of visited positions.
    """
    start = "O"                         # Start position
    end = "X"                           # End position
    start_pos = find_val(maze, start)   # Find the start position
    end_pos = find_val(maze, end)       # Find the end position

    open_set = []                               # Priority queue
    heapq.heappush(open_set, (0, start_pos))    # Put the start position in the queue
    came_from = {}                              # Dictionary to store the path
    g_score = {start_pos: 0}                    # Dictionary to store the g-score, the cost from the start to the current position
    visited = set()                             # Set to store visited positions

    # While the open set is not empty
    while open_set:
        current_cost, current = heapq.heappop(open_set)     # Get the current position

        # If the current position is the end position
        if current == end_pos:
            path = []
            while current in came_from:         # While the current position is in the path
                path.append(current)            # Add the current position to the path
                current = came_from[current]    # Move to the next position
            path.append(start_pos)              # Add the start position to the path
            path.reverse()                      # Reverse the path
            
            # Print the maze with the path
            stdscr.clear()
            print_maze(maze, stdscr, path=path, start=start_pos, end=end_pos, steps=len(visited), visited=visited)
            stdscr.refresh()

            # Return the path
            return True, path, len(path)-1, len(visited), visited

        # Else, add the current position to the visited set
        visited.add(current)
        row, col = current

        # Print the maze
        stdscr.clear()
        print_maze(maze, stdscr, path=[], start=start_pos, end=end_pos, steps=len(visited), visited=visited)
        stdscr.refresh()

        # Else, find the neighbors of the current position
        neighbors = find_neighbors(maze, row, col)
        
        # For each neighbor, if it has not been visited and is not a wall, calculate the g-score
        for neighbor in neighbors:
            if neighbor in visited or maze[neighbor[0]][neighbor[1]] == "#":
                continue

            tentative_g_score = g_score[current] + 1    # Calculate the g-score

            # If the neighbor is not in the g-score dictionary or the tentative g-score is less than the current g-score
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current                               # Add the current position to the path
                g_score[neighbor] = tentative_g_score                       # Update the g-score
                heapq.heappush(open_set, (tentative_g_score, neighbor))     # Put the neighbor in the queue
    
    # If no path is found, return False
    stdscr.addstr(len(maze), len(maze[0])//2, "No path found!")
    return False, [], 0, len(visited), visited

def bidirectional(maze, stdscr):
    """
    Bidirectional Search algorithm to find the shortest path in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        stdscr - The curses window object.
    
    Returns:
        bool - True if the path is found, False otherwise.
        list - The path from the start to the end position.
        int - The length of the path.
        int - The number of steps taken.
        list - The list of visited positions.
    """
    start = "O"                         # Start position
    end = "X"                           # End position
    start_pos = find_val(maze, start)   # Find the start position
    end_pos = find_val(maze, end)       # Find the end position

    def reconstruct_path(came_from_start, came_from_end, meeting_point):
        """Function to reconstruct the path from the start to the end position."""
        path = []
        
        # Find the path from the start to the meeting point
        current = meeting_point
        while current in came_from_start:
            path.append(current)
            current = came_from_start[current]
        path.reverse()
        
        # Find the path from the meeting point to the end
        current = meeting_point
        while current in came_from_end:
            current = came_from_end[current]
            path.append(current)
            
        return path

    # Queues, dictionaries, and sets, to store the positions, paths, and visited positions
    open_set_start = queue.Queue()  
    open_set_end = queue.Queue()    
    open_set_start.put(start_pos)    
    open_set_end.put(end_pos)            
    came_from_start = {}              
    came_from_end = {}                
    visited_start = set()             
    visited_end = set()               

    # While the queues are not empty
    while not open_set_start.empty() and not open_set_end.empty():
        # Get the current positions, start/end
        current_start = open_set_start.get()
        current_end = open_set_end.get()

        # If start meets end, reconstruct the path
        if current_start in visited_end:
            path = reconstruct_path(came_from_start, came_from_end, current_start)
            
            # Print the maze with the path
            stdscr.clear()
            print_maze(maze, stdscr, path=path, start=start_pos, end=end_pos, steps=len(visited_start) + len(visited_end), visited=visited_start.union(visited_end))
            stdscr.refresh()
            
            # Add the end position to the path, return the path
            path += [current_end]
            return True, path, len(path)-1, len(visited_start) + len(visited_end), visited_start.union(visited_end)
        
        # If end meets start, reconstruct the path
        if current_end in visited_start:
            path = reconstruct_path(came_from_start, came_from_end, current_end)
            
            # Print the maze with the path
            stdscr.clear()
            print_maze(maze, stdscr, path=path, start=start_pos, end=end_pos, steps=len(visited_start) + len(visited_end), visited=visited_start.union(visited_end))
            stdscr.refresh()
            
            # Add the end position to the path, return the path
            path += [current_end]
            return True, path, len(path)-1, len(visited_start) + len(visited_end), visited_start.union(visited_end)

        # Else, add the current positions to the visited sets
        visited_start.add(current_start)
        visited_end.add(current_end)
        row_start, col_start = current_start
        row_end, col_end = current_end

        # Print the maze
        stdscr.clear()
        print_maze(maze, stdscr, path=[], start=start_pos, end=end_pos, steps=len(visited_start) + len(visited_end), visited=visited_start.union(visited_end))
        stdscr.refresh()

        # Find the neighbors of the current positions from the start
        neighbors_start = find_neighbors(maze, row_start, col_start)
        
        # For each neighbor in the start set, if it has not been visited and is not a wall, add it to the queue
        for neighbor in neighbors_start:
            if neighbor not in visited_start and maze[neighbor[0]][neighbor[1]] != "#":
                open_set_start.put(neighbor)
                came_from_start[neighbor] = current_start

        # Find the neighbors of the current positions from the end
        neighbors_end = find_neighbors(maze, row_end, col_end)
        
        # For each neighbor in the end set, if it has not been visited and is not a wall, add it to the queue
        for neighbor in neighbors_end:
            if neighbor not in visited_end and maze[neighbor[0]][neighbor[1]] != "#":
                open_set_end.put(neighbor)
                came_from_end[neighbor] = current_end

    # If no path is found, return False
    stdscr.addstr(len(maze), len(maze[0])//2, "No path found!")
    return False, [], 0, len(visited_start) + len(visited_end), visited_start.union(visited_end)    

def iddfs(maze, stdscr):
    """
    Iterative Deepening Depth-First Search algorithm to find the shortest path in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        stdscr - The curses window object.
    
    Returns:
        bool - True if the path is found, False otherwise.
        list - The path from the start to the end position.
        int - The length of the path.
        int - The number of steps taken.
        list - The list of visited positions.
    """
    start = "O"                         # Start position
    end = "X"                           # End position
    start_pos = find_val(maze, start)   # Find the start position
    end_pos = find_val(maze, end)       # Find the end position

    def DLS(current_pos, depth, path, visited):
        """Function to perform Depth-Limited Search."""
        nonlocal steps
        
        # If the depth is 0 and the current position is the end position, return True
        if depth == 0 and current_pos == end_pos:
            return True
        # Else, if the depth is greater than 0
        if depth > 0:
            row, col = current_pos                      # Get the row and column of the current position
            neighbors = find_neighbors(maze, row, col)  # Find the neighbors of the current position
            
            # For each neighbor, if it has not been visited and is not a wall, add it to the path
            for neighbor in neighbors:
                if neighbor not in visited and maze[neighbor[0]][neighbor[1]] != "#":
                    visited.add(neighbor)   # Add the neighbor to the visited set
                    path.append(neighbor)   # Add the neighbor to the path
                    steps+=1

                    # If the neighbor is the end position, return True
                    if DLS(neighbor, depth - 1, path, visited):
                        return True
                    # Else, remove the neighbor from the path
                    path.pop()  
            
            # Print the maze
            stdscr.clear()
            print_maze(maze, stdscr, path=path, start=start_pos, end=end_pos, steps=steps, visited=visited)
            stdscr.refresh()
        # If the depth is 0, return False    
        return False

    depth = 0               # Initial depth
    visited = set()         # Set to store visited positions
    path = [start_pos]      # List to store the path
    visited.add(start_pos)  # Add the start position to the visited set

    steps=0
    while True: 
        # If the Depth-Limited Search returns True, return the path
        if DLS(start_pos, depth, path, visited):
            return True, path, len(path)-1, steps, visited
        steps += 1
        
        # Else, if the depth is greater than the number of cells in the maze, return False
        if depth > len(maze[1])*len(maze[0]): 
            return False, [], 0, steps, visited
        
        # Increment the depth, clear the visited set, and add the start position to the visited set
        depth +=1
        visited.clear() 
        path = [start_pos]
        visited.add(start_pos)
        
        # Print the maze
        stdscr.clear()
        print_maze(maze, stdscr, path=path, start=start_pos, end=end_pos, steps=steps, visited=visited)
        stdscr.refresh()
               
def find_neighbors(maze, row, col):
    """
    Finds the neighbors of a given position in a maze.
    
    Parameters:
        maze (list) - A 2D list representing the maze.
        row (int) - The row of the position.
        col (int) - The column of the position.
    
    Returns:
        list - A list of neighboring positions.
    """
    neighbors = []  # List to store neighbors

    if row > 0:                             # UP
        neighbors.append((row - 1, col))
    if row + 1 < len(maze):                 # DOWN
        neighbors.append((row + 1, col))
    if col > 0:                             # LEFT
        neighbors.append((row, col - 1))
    if col + 1 < len(maze[0]):              # RIGHT
        neighbors.append((row, col + 1))

    return neighbors

def print_results(stdscr, methods, maze, cols=3):
    """
    Prints the results of the path finding algorithms on the screen.
    
    Parameters:
        stdscr - The curses window object.
        methods (list) - A list of tuples containing the name of the algorithm and the results.
        maze (list) - A 2D list representing the maze
        cols (int) - Number of columns to print the results in
    """
    # Find the start and end positions
    start = find_val(maze, "O")
    end = find_val(maze, "X")
    
    # Clear the screen
    stdscr.clear()
    
    height, width = stdscr.getmaxyx()
    
    # Calculate the width of each column based on the screen width
    col_width = width // cols
    
    # Initialize offsets for each column
    offsets = [(1, col_width * i) for i in range(cols)]
    
    # For each method, print the path
    for i, method in enumerate(methods):
        # Method name and results
        name = method[0]
        path_found, path, path_length, steps, visited = method[1:]
        
        # Determine the current column and offset
        col_index = i % cols
        offset = offsets[col_index]
        
        # Print the path in the current column
        stdscr.addstr(offset[0] - 1, offset[1], f"{name.upper()} Path:")
        print_maze(maze, stdscr, path, start, end, steps, offset=offset, visited=visited, path_len=True)
        
        # Increment the offset for the current column
        offsets[col_index] = tuple(map(sum, zip(offset, (len(maze) + 2, 0))))
    
    # Refresh the screen and wait for a key press
    stdscr.refresh()
    stdscr.getch()
        
def main(stdscr):
    # Define the arguments, and parse them
    parser = argparse.ArgumentParser(description="Maze Path Finder")
    parser.add_argument("--rows", type=int, default=10, help="Number of rows in the maze")
    parser.add_argument("--cols", type=int, default=10, help="Number of columns in the maze")
    parser.add_argument("--maze_type", type=int, default=0, help="Type of maze to generate: Maze type small: 0, Maze type large: 1, Maze type csv: 2, Random grid maze: 3, Random maze: 4")
    args = parser.parse_args()
    
    # Initialize the curses window, set the colors
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    

    # Maze generation
    # -------------------------------------------
    maze_generators = {
        0: maze_small,
        1: maze_large,
        2: maze_csv,
        3: lambda: random_grid_maze(args.rows, args.cols),
        4: lambda: random_maze(args.rows, args.cols)
    }

    maze = maze_generators.get(args.maze_type, lambda: None)()
    if maze is None:
        print(f"Invalid maze type {args.maze_type}, please choose a valid maze type.\nValid maze types are: small:0, large:1, csv:2, random grid maze:3, random maze:4")
        return
    
    # Run the path finding algorithms
    # -------------------------------------------
    bfss = bfs(maze, stdscr)
    bfss = ["bfs"] + list(bfss)
    
    gbfss = gbfs(maze, stdscr)
    gbfss = ["Greedy bfs"] + list(gbfss)
    
    dfss = dfs(maze, stdscr)
    dfss = ["dfs"] + list(dfss)
    
    astar_m = a_star(maze, stdscr, "manhattan")
    astar_m = ["astar-manhattan"] + list(astar_m)
    
    astar_e = a_star(maze, stdscr, "euclidean")
    astar_e = ["astar-euclidean"] + list(astar_e)
    
    astar_c = a_star(maze, stdscr, "chebyshev")
    astar_c = ["astar-chebyshev"] + list(astar_c)
    
    astar_o = a_star(maze, stdscr, "octile")
    astar_o = ["astar-octile"] + list(astar_o)
    
    dijk = dijkstra(maze, stdscr)
    dijk = ["dijkstra"] + list(dijk)
    
    bi = bidirectional(maze, stdscr)
    bi = ["bidirectional"] + list(bi)
    
    # iddfss = iddfs(maze, stdscr)
    # iddfss = ["iddfs"] + list(iddfss)
    # stdscr.getch()
    
    # Print the results, and wait for a key press        
    print_results(stdscr, [bfss,gbfss, dfss, dijk, bi, astar_m, astar_e, astar_c, astar_o] ,maze)
    
if __name__ == "__main__":
    wrapper(main)