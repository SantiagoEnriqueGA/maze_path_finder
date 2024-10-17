import random
import time
from ursina import *
from collections import deque

# random.seed(42)  # Set seed for reproducibility testing

app = Ursina()  # Initialize the app

size = 3        # Size of the cube
maze_size = 25  # Size of the maze

wall_scale = 0.025
path_scale = 0.025
path_step_scale = 0.05
start_end_scale = 0.1
cube_opacity = 1
grid_lines = False

# Create the cube entity
# cube = Entity(model='cube', color=color.azure, scale=size, alpha=0.75) #for debuging
cube = Entity(model='cube', color=color.azure, scale=size, alpha=cube_opacity) 


# Add edges using a wireframe
edges = Entity(
    model=Mesh(
        vertices=[
            Vec3(-0.5, -0.5, -0.5), Vec3(0.5, -0.5, -0.5), Vec3(0.5, 0.5, -0.5), Vec3(-0.5, 0.5, -0.5),     # back face
            Vec3(-0.5, -0.5, 0.5), Vec3(0.5, -0.5, 0.5), Vec3(0.5, 0.5, 0.5), Vec3(-0.5, 0.5, 0.5)          # front face
        ],
        triangles=[
            (0, 1, 2), (2, 3, 0),  # back
            (4, 5, 6), (6, 7, 4),  # front
            (0, 1, 5), (5, 4, 0),  # bottom
            (1, 2, 6), (6, 5, 1),  # right
            (0, 3, 7), (7, 4, 0)   # left
        ],
        mode='line'
    ),                              # Display only the edges as lines
    color=color.white,
    scale=size + 0.01               # Slightly larger to make the edges visible
)

def set_face_position(entity, face):
    """
    Set the position and rotation of an entity based on the specified face.
    Args:
        entity (object): The entity whose position and rotation are to be set.
        face (str): The face of the entity to set the position and rotation for. 
                    Valid values are 'front', 'back', 'left', 'right', 'top', and 'bottom'.

    The function modifies the following attributes of the entity:
        - For 'front': Sets z to 0.5, rotation_x to 180, and rotation_y to 180.
        - For 'back': Sets z to -0.5 and rotation_x to 180.
        - For 'left': Sets x to 0.5, rotation_y to 90, and rotation_z to -180.
        - For 'right': Sets x to -0.5, rotation_y to -90, and rotation_z to -180.
        - For 'top': Sets y to 0.5, rotation_x to -90, and rotation_y to 180.
        - For 'bottom': Sets y to -0.5, rotation_x to 90, and rotation_y to 180.
    """
    if face == 'front':
        entity.z = 0.5
        entity.rotation_x = 180
        entity.rotation_y = 180
    elif face == 'back':
        entity.z = -0.5
        entity.rotation_x = 180
    elif face == 'left':
        entity.x = 0.5
        entity.rotation_y = 90
        entity.rotation_z = -180
    elif face == 'right':
        entity.x = -0.5
        entity.rotation_y = -90
        entity.rotation_z = -180
    elif face == 'top':
        entity.y = 0.5
        entity.rotation_x = -90
        entity.rotation_y = 180
    elif face == 'bottom':
        entity.y = -0.5
        entity.rotation_x = 90
        entity.rotation_y = 180


def create_grid_lines(face):
    """
    Create grid lines on a specified face of a 3D cube.
    This function generates vertical and horizontal grid lines on a given face of a 3D cube. 
    The grid lines are created using wireframe cubes and are scaled and positioned accordingly.
    Args:
        face (str): The face of the cube where the grid lines will be created. 
                    It should be one of the predefined faces (e.g., 'front', 'back', 'left', 'right', 'top', 'bottom').
    """
    lines = Entity(parent=cube)     # Create a parent entity for the lines
    step = 1 / maze_size            # Calculate the step size for the grid lines
    for i in range(1, maze_size):   # Iterate over the grid lines
        
        # Vertical lines
        vline = Entity(parent=lines, model='wireframe_cube', color=color.white)
        vline.scale = (0.002, 1, 0.002)
        vline.x = i * step - 0.5
        
        # Horizontal lines
        hline = Entity(parent=lines, model='wireframe_cube', color=color.white)
        hline.scale = (1, 0.002, 0.002)
        hline.y = i * step - 0.5
    
    set_face_position(lines, face)  # Set the position and rotation of the lines based on the face


def gen_grid_maze(size, wall_probability=0.3):
    """
    Generates a 2D grid maze with walls placed randomly based on a given probability.

    Args:
        size (int): The size of the maze (size x size).
        wall_probability (float, optional): The probability of placing a wall at any given cell. Defaults to 0.3.

    Returns:
        list[list[int]]: A 2D list representing the maze, where 0 indicates an open cell and 1 indicates a wall.
    """
    maze = [[0 for _ in range(size)] for _ in range(size)]  # Initialize the maze with all open cells
    for i in range(size):
        for j in range(size):
            if random.random() < wall_probability:          # Place walls based on the probability
                maze[i][j] = 1                              # Set the cell as a wall
    return maze

def create_maze(face):
    """
    Generates a 2D maze on a specified face of a 3D cube and creates corresponding wall entities.
    Args:
        face (str): The face of the cube where the maze will be created.
    Returns:
        list: A 2D list representing the generated maze, where 1 indicates a wall and 0 indicates a path.
    """
    maze = gen_grid_maze(maze_size)     # Generate a random maze
    face_entity = Entity(parent=cube)   # Create a parent entity for the face

    for i in range(maze_size):
        for j in range(maze_size):
            if maze[i][j] == 1:                                                     # If there is a wall
                wall = Entity(parent=face_entity, model='cube', color=color.gray)   # Attach wall to face_entity
                wall.scale = (1/maze_size, 1/maze_size, wall_scale)              # Scale the wall to fit the grid
                wall.x = (i + 0.5) / maze_size - 0.5                                # Position the wall in the grid, x
                wall.y = (j + 0.5) / maze_size - 0.5                                # Position the wall in the grid, y
                                
    set_face_position(face_entity, face)
    return maze
    
# Place the start and end points, randomly
def place_start_end(mazes):
    """
    Places the start ('S') and end ('E') positions randomly on different faces of a 3D maze.
    Args:
        mazes (dict): A dictionary where keys are face identifiers and values are 2D lists representing the maze grid on each face.
    Returns:
        tuple: A tuple containing:
            - start_face (str): The face identifier where the start position is placed.
            - start_pos (tuple): The (row, column) position of the start within the start_face.
            - end_face (str): The face identifier where the end position is placed.
            - end_pos (tuple): The (row, column) position of the end within the end_face.
    """
    
    start_face = random.choice(list(mazes.keys()))                                          # Choose random face for start
    start_pos = (random.randint(0, maze_size - 1), random.randint(0, maze_size - 1))        # Choose non-wall position for start
    while mazes[start_face][start_pos[0]][start_pos[1]] == 1:
        start_pos = (random.randint(0, maze_size - 1), random.randint(0, maze_size - 1))    # Choose non-wall position for start
    mazes[start_face][start_pos[0]][start_pos[1]] = 'S'                                     # Add start to maze as 'S'

    
    end_face = random.choice(list(mazes.keys()))                                            # Choose random face for end
    end_pos = (random.randint(0, maze_size - 1), random.randint(0, maze_size - 1))          # Choose non-wall position for end
    while mazes[end_face][end_pos[0]][end_pos[1]] == 1 or (end_face == start_face and end_pos == start_pos):
        end_pos = (random.randint(0, maze_size - 1), random.randint(0, maze_size - 1))      # Choose non-wall position for end, not the same as start
    mazes[end_face][end_pos[0]][end_pos[1]] = 'E'                                           # Add end to maze as 'E'
    
    # Create a parent entity for the start face
    start_entity = Entity(parent=cube)
    start_wall = Entity(parent=start_entity, model='cube', color=color.green)
    start_wall.scale = (1/maze_size, 1/maze_size, start_end_scale)
    start_wall.x = (start_pos[0] + 0.5) / maze_size - 0.5
    start_wall.y = (start_pos[1] + 0.5) / maze_size - 0.5
    set_face_position(start_entity, start_face)
    
    # Create a parent entity for the end face
    end_entity = Entity(parent=cube)
    end_wall = Entity(parent=end_entity, model='cube', color=color.red)
    end_wall.scale = (1/maze_size, 1/maze_size, start_end_scale)
    end_wall.x = (end_pos[0] + 0.5) / maze_size - 0.5
    end_wall.y = (end_pos[1] + 0.5) / maze_size - 0.5
    set_face_position(end_entity, end_face)
    
    return start_face, start_pos, end_face, end_pos


def get_neighbors(face, pos):
    """
    Given a face of a 3D maze and a position on that face, this function returns a list of neighboring positions.
    The neighbors can be on the same face or on adjacent faces if the position is at the edge of the current face.

    Args:
        face (str): The current face of the 3D maze. Possible values are 'front', 'back', 'left', 'right', 'top', 'bottom'.
        pos (tuple): A tuple (x, y) representing the current position on the face.

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
                elif face == 'top':#todo
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


def path_finder(mazes, start_face, start_pos, end_face, end_pos):
    """
    Finds a path from a start position to an end position in a 3D maze.
    Uses a breadth-first search algorithm to find the shortest path from the start to the end position.
    Args:
        mazes (dict): A dictionary where keys are face identifiers and values are 2D lists representing the maze grid.
                      Each cell in the grid can be 0 (walkable) or 1 (blocked).
        start_face (any): The identifier for the starting face of the maze.
        start_pos (tuple): A tuple (x, y) representing the starting position on the start_face.
        end_face (any): The identifier for the ending face of the maze.
        end_pos (tuple): A tuple (x, y) representing the ending position on the end_face.
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
            return path[::-1]                                                       # Return the reversed path  

        for neighbor_face, neighbor_pos in get_neighbors(current_face, current_pos):    # Iterate over the neighbors
            
            # If the neighbor is not visited and is not a wall
            if neighbor_pos not in visited.get(neighbor_face, set()) and mazes[neighbor_face][neighbor_pos[0]][neighbor_pos[1]] != 1:
                
                if neighbor_face not in visited:                                    # If the neighbor face is not in visited
                    visited[neighbor_face] = set()                                  # Add the face to visited
                    parent[neighbor_face] = {}                                      # Add the face to parent
                visited[neighbor_face].add(neighbor_pos)                            # Add the neighbor to visited
                parent[neighbor_face][neighbor_pos] = (current_face, current_pos)   # Set the parent of the neighbor
                queue.append((neighbor_face, neighbor_pos))                         # Add the neighbor to the queue
    return []


def place_path_step_by_step(path, mazes):
    """
    Creates a function to place path steps in a 3D maze step by step.
    Args:
        path (list of tuples): A list of tuples where each tuple contains a face identifier and a position (x, y) in the maze.
        mazes (dict): A dictionary where keys are face identifiers and values are 2D lists representing the maze grid for each face.
    Returns:
        function: A function that, when called, places the next step in the path on the maze.
    """
    step_index = 0

    def update_path():                      # Define the update_path function
        nonlocal step_index                         # Use the step_index variable from the outer function
        if step_index < len(path):                  # Check if there are more steps in the path
            face, pos = path[step_index]            # Get the face and position for the current step
            if mazes[face][pos[0]][pos[1]] == 0:    # Check if the position is a valid path
                
                # print(f"Step {step_index + 1}: {face}, {pos}")
                
                path_entity = Entity(parent=cube)                                       # Create a parent entity for the path
                path_wall = Entity(parent=path_entity, model='cube', color=color.red)   # Attach a red wall to the path_entity
                path_wall.scale = (1/maze_size, 1/maze_size, path_step_scale)                      # Scale the wall to fit the grid
                path_wall.x = (pos[0] + 0.5) / maze_size - 0.5                          # Position the wall in the grid, x
                path_wall.y = (pos[1] + 0.5) / maze_size - 0.5                          # Position the wall in the grid, y
                set_face_position(path_entity, face)                                    # Set the position and rotation of the path_entity
            step_index += 1 
            
        # Check if the last step has been placed
        if step_index >= len(path):
            return True  # All steps have been placed
        else:
            return None  # There are still more steps to place
    return update_path


def place_path(visited, mazes):
    """
    Places a path in the 3D maze based on the visited positions.

    Args:
        visited (list of tuples): A list of tuples where each tuple contains a face index and a position (x, y) 
                                  that has been visited.
        mazes (list of lists of lists): A 3D list representing the maze structure where each face is a 2D grid.

    Returns:
        None
    """
    for face, pos in visited:                                                           # Iterate over the visited positions
        if mazes[face][pos[0]][pos[1]] == 0:                                            # Check if the position is a valid path
            path_entity = Entity(parent=cube)                                           # Create a parent entity for the path
            path_wall = Entity(parent=path_entity, model='cube', color=color.gold)      # Attach a wall to the path_entity
            path_wall.scale = (1/maze_size -.001, 1/maze_size-.001, path_scale)                 # Scale the wall to fit the grid
            path_wall.x = (pos[0] + 0.5) / maze_size - 0.5                              # Position the wall in the grid, x
            path_wall.y = (pos[1] + 0.5) / maze_size - 0.5                              # Position the wall in the grid, y
            set_face_position(path_entity, face)


def input(key):
    if key == 'space':
        invoke(repeat_update, delay=0)  # Start the repeated update process immediately
def repeat_update():
    result = update_path()              # Call the update_path function
    if result is True:                  # If all path steps have been placed, stop further updates
        print("All path steps placed!")
        return
    invoke(repeat_update, delay=1)      # Schedule the next update      

# Create grid lines for each face
if grid_lines:
    create_grid_lines('front')
    create_grid_lines('back')
    create_grid_lines('left')
    create_grid_lines('right')
    create_grid_lines('top')
    create_grid_lines('bottom')

# Create a maze on each face
mazes = {   'front': create_maze('front'),
            'back': create_maze('back'),
            'left': create_maze('left'),
            'right': create_maze('right'),
            'top': create_maze('top'),
            'bottom': create_maze('bottom')}

# Place the start and end points
start_face, start_pos, end_face, end_pos = place_start_end(mazes)

# Find the path and place it in the maze
path = path_finder(mazes, start_face, start_pos, end_face, end_pos)
place_path(path, mazes)  

# Place the path step by step
update_path = place_path_step_by_step(path, mazes)

window.color = color.black
EditorCamera()
app.run()


# --------------------------------------------------------------------------------------------------------------
# Debugging
# --------------------------------------------------------------------------------------------------------------
# print(mazes)
# print(path)
# print(f"Start: {start_face}, {start_pos}")
# print(f"End: {end_face}, {end_pos}")

# place point on 2,1 of each face
# def create_2x1(face):
#     maze = [[0 for _ in range(maze_size)] for _ in range(maze_size)]
#     maze[2][1] = 1
       
#     face_entity = Entity(parent=cube)  # Create a parent entity for the face

#     for i in range(maze_size):
#         for j in range(maze_size):
#             if maze[i][j] == 1:                                                     # If there is a wall
#                 wall = Entity(parent=face_entity, model='cube', color=color.red)    # Attach wall to face_entity
#                 wall.scale = (1/maze_size -.01, 1/maze_size-.01, 0.01)              # Scale the wall to fit the grid
#                 wall.x = (i + 0.5) / maze_size - 0.5                                # Position the wall in the grid, x
#                 wall.y = (j + 0.5) / maze_size - 0.5                                # Position the wall in the grid, y
                                
#     set_face_position(face_entity, face)
    
#     return maze
# create_2x1('front')
# create_2x1('back')
# create_2x1('left')
# create_2x1('right')
# create_2x1('top')
# create_2x1('bottom')