from collections import deque

def get_neighbors(face, pos,maze_size):
    """
    Given a face of a 3D maze and a position on that face, this function returns a list of neighboring positions.
    The neighbors can be on the same face or on adjacent faces if the position is at the edge of the current face.

    Args:
        face (str): The current face of the 3D maze. Possible values are 'front', 'back', 'left', 'right', 'top', 'bottom'.
        pos (tuple): A tuple (x, y) representing the current position on the face.
        maze_size(int): An integer representing the length of a cubical maze.
    Returns:
        list: A list of tuples where each tuple contains a face and a position (face, (x, y)) representing the neighboring positions.
    """
    neighbors = []                          # Initialize the list of neighbors
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0)    # right, down, left, up
    ]
    for d in directions:                                                        # Iterate over the directions
        new_pos = (pos[0] + d[0], pos[1] + d[1])                                # Calculate the new position
        
        if 0 <= new_pos[0] < maze_size and 0 <= new_pos[1] < maze_size:         # Check if the new position is within bounds
            neighbors.append((face, new_pos))                                   # Add the neighbor on the same face
        
        else:                                                                   # Handle edge transitions
            if new_pos[0] < 0:                                                  # If new position is out of bounds on the left
                if face == 'front':
                    neighbors.append(('left', (maze_size - 1, pos[1])))
                elif face == 'back':
                    neighbors.append(('right',(maze_size - 1, pos[1])))
                elif face == 'left':
                    neighbors.append(('back', (maze_size - 1, pos[1])))
                elif face == 'right':
                    neighbors.append(('front',(maze_size - 1, pos[1])))
                elif face == 'top':
                    neighbors.append(('left', (pos[1], 0)))
                elif face == 'bottom':
                    neighbors.append(('left', (maze_size - 1-pos[1], maze_size - 1)))
            elif new_pos[0] >= maze_size:                                       # If new position is out of bounds on the right
                if face == 'front':
                    neighbors.append(('right',(0, pos[1])))
                elif face == 'back':
                    neighbors.append(('left', (0, pos[1])))
                elif face == 'left':
                    neighbors.append(('front',(0, pos[1])))
                elif face == 'right':
                    neighbors.append(('back', (0,pos[1])))
                elif face == 'top':
                    neighbors.append(('right', (maze_size-1-pos[1], 0)))
                elif face == 'bottom':
                    neighbors.append(('right', (pos[1], maze_size - 1)))
            elif new_pos[1] < 0:                                                # If new position is out of bounds on the top
                if face == 'front':
                    neighbors.append(('top', (pos[0], maze_size - 1)))
                elif face == 'back':
                    neighbors.append(('top', (maze_size-1-pos[0], 0)))
                elif face == 'left':
                    neighbors.append(('top', (0, pos[0])))
                elif face == 'right':
                    neighbors.append(('top', ( maze_size - 1, maze_size-1-pos[0])))
                elif face == 'top':
                    neighbors.append(('back', ( maze_size-1-pos[0], 0)))
                elif face == 'bottom':
                    neighbors.append(('front', (pos[0], maze_size-1)))
            elif new_pos[1] >= maze_size:                                       # If new position is out of bounds on the bottom
                if face == 'front':
                    neighbors.append(('bottom', (pos[0], 0)))
                elif face == 'back':
                    neighbors.append(('bottom', (maze_size - 1-pos[0], maze_size - 1)))
                elif face == 'left':
                    neighbors.append(('bottom', (0, maze_size - 1-pos[0])))
                elif face == 'right':
                    neighbors.append(('bottom', (maze_size - 1, pos[0])))
                elif face == 'top':
                    neighbors.append(('front', (pos[0], 0)))
                elif face == 'bottom':
                    neighbors.append(('back', (maze_size - 1-pos[0], maze_size - 1)))
    return neighbors


def path_finder_bfs(mazes, start_face, start_pos, end_face, end_pos, maze_size):
    """
    Uses a breadth-first search algorithm to find the shortest path from the start to the end position.
    Finds a path from a start position to an end position in a 3D maze.
    Args:
        mazes (dict): A dictionary where keys are face identifiers and values are 2D lists representing the maze grid.
                      Each cell in the grid can be 0 (walkable) or 1 (blocked).
        start_face (any): The identifier for the starting face of the maze.
        start_pos (tuple): A tuple (x, y) representing the starting position on the start_face.
        end_face (any): The identifier for the ending face of the maze.
        end_pos (tuple): A tuple (x, y) representing the ending position on the end_face.
        maze_size(int): An integer representing the length of a cubical maze.
    Returns:
        list: A list of tuples representing the path from the start position to the end position.
              Each tuple is of the form (face, (x, y)). If no path is found, returns an empty list.
    """
    queue = deque([(start_face, start_pos)])        # Initialize queue with start position
    visited = {start_face: {start_pos}}             # Initialize visited set with start position
    parent = {start_face: {start_pos: None}}        # Initialize parent dictionary with start position

    while queue:                                                # Continue until the queue is empty
        current_face, current_pos = queue.popleft()             # Get the current position from the queue
        
        if (current_face, current_pos) == (end_face, end_pos):  # Check if we have reached the end
            path = []                                           
            while current_pos is not None:                      # Reconstruct the path
                path.append((current_face, current_pos))        # Add the current position to the path
                
                if parent[current_face][current_pos] is not None:                   # If there is a parent
                    current_face, current_pos = parent[current_face][current_pos]   # Move to the parent position
                
                else:                                                               # If there is no parent, we have reached the start or an isolated point
                    break                                                           # Break out of the loop
            return path[::-1], visited                                              # Return the reversed path  

        for neighbor_face, neighbor_pos in get_neighbors(current_face, current_pos,maze_size):    # Iterate over the neighbors
            
            # If the neighbor is not visited and is not a wall
            if neighbor_pos not in visited.get(neighbor_face, set()) and mazes[neighbor_face][neighbor_pos[0]][neighbor_pos[1]] != 1:
                
                if neighbor_face not in visited:                                    # If the neighbor face is not in visited
                    visited[neighbor_face] = set()                                  # Add the face to visited
                    parent[neighbor_face] = {}                                      # Add the face to parent
                visited[neighbor_face].add(neighbor_pos)                            # Add the neighbor to visited
                parent[neighbor_face][neighbor_pos] = (current_face, current_pos)   # Set the parent of the neighbor
                queue.append((neighbor_face, neighbor_pos))                         # Add the neighbor to the queue
    return [], visited