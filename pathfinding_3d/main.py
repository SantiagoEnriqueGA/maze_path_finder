import random
from ursina import *
from pathfinding import path_finder_bfs, PathFinder

# random.seed(42)  # Set seed for reproducibility testing

app = Ursina()  # Initialize the app

size = 3        # Size of the cube
maze_size = 25  # Size of the maze

wall_scale = 0.035
path_scale = 0.0125
path_step_scale = 0.05
start_end_scale = 0.1
cube_opacity = 1
grid_lines = False

cube_color = color.azure
line_color = color.white
maze_color = color.gray
start_color = color.green
end_color = color.red
path_color = color.gold
path_step_color = color.magenta
visited_color = color.light_gray

# Function to create the legend
def create_legend(legend_offset_y=0):
    # Vertical spacing between items in the legend
    item_spacing = 0.04
    
    # Add legend items
    legend_items = [
        ('Start', start_color),
        ('End', end_color),
        ('Path', path_color),
        ('Path Step', path_step_color),
        ('Cell Visited', visited_color),
        ('Wall', maze_color),
    ]

    for i, (label, color_) in enumerate(legend_items):
        # Create a small square representing the color
        legend_color_block = Entity(parent=camera.ui, model='quad', scale=(0.02, 0.02), color=color_, position=(-0.8, 0.5 - i * item_spacing + legend_offset_y, 0))
        
        # Create text next to the color block
        legend_text = Text(text=label, parent=camera.ui, origin=(-0.5, 0), scale=1, position=(-0.775, 0.5 - i * item_spacing + legend_offset_y))

# Create the cube entity
cube = Entity(model='cube', color=cube_color, scale=size, alpha=cube_opacity) 

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
    color=line_color,
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
        vline = Entity(parent=lines, model='wireframe_cube', color=line_color)
        vline.scale = (0.002, 1, 0.002)
        vline.x = i * step - 0.5
        
        # Horizontal lines
        hline = Entity(parent=lines, model='wireframe_cube', color=line_color)
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
                wall = Entity(parent=face_entity, model='cube', color=maze_color)   # Attach wall to face_entity
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
    start_wall = Entity(parent=start_entity, model='cube', color=start_color)
    start_wall.scale = (1/maze_size, 1/maze_size, start_end_scale)
    start_wall.x = (start_pos[0] + 0.5) / maze_size - 0.5
    start_wall.y = (start_pos[1] + 0.5) / maze_size - 0.5
    set_face_position(start_entity, start_face)
    
    # Create a parent entity for the end face
    end_entity = Entity(parent=cube)
    end_wall = Entity(parent=end_entity, model='cube', color=end_color)
    end_wall.scale = (1/maze_size, 1/maze_size, start_end_scale)
    end_wall.x = (end_pos[0] + 0.5) / maze_size - 0.5
    end_wall.y = (end_pos[1] + 0.5) / maze_size - 0.5
    set_face_position(end_entity, end_face)
    
    return start_face, start_pos, end_face, end_pos


def place_path(visited, mazes, color=color.gold, alpha=1):
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
            path_wall = Entity(parent=path_entity, model='cube', color=color, alpha=alpha)      # Attach a wall to the path_entity
            path_wall.scale = (1/maze_size -.001, 1/maze_size-.001, path_scale)                 # Scale the wall to fit the grid
            path_wall.x = (pos[0] + 0.5) / maze_size - 0.5                              # Position the wall in the grid, x
            path_wall.y = (pos[1] + 0.5) / maze_size - 0.5                              # Position the wall in the grid, y
            set_face_position(path_entity, face)


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
                path_wall = Entity(parent=path_entity, model='cube', color=path_step_color)   # Attach a red wall to the path_entity
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


def place_path_step_by_step_with_pathfinder(mazes, start_face, start_pos, end_face, end_pos, maze_size):
    """
    Places path steps in a 3D maze step by step using the PathFinder class.
    Args:
        mazes (dict): A dictionary where keys are face identifiers and values are 2D lists representing the maze grid on each face.
        start_face (str): The face identifier where the start position is placed.
        start_pos (tuple): The (row, column) position of the start within the start_face.
        end_face (str): The face identifier where the end position is placed.
        end_pos (tuple): The (row, column) position of the end within the end_face.
        maze_size (int): The size of the maze.
    Returns:
        tuple: A tuple containing:
            - update_vis (function): A function that, when called, places the next step in the path on the maze.
            - path_finder (PathFinder): The PathFinder object used for pathfinding.
    """
    path_finder = PathFinder(mazes, start_face, start_pos, end_face, end_pos, maze_size)        # Create a PathFinder object
    visited = []
        
    # Define the update_path function
    def update_vis():
        if path_finder.current_pos != end_pos:                              # Check if the current position is not the end
            path_finder.advance_step()                                      # Advance to the next step
            
            to_add = []        
            for face, positions in path_finder.visited.items():             # Iterate over the visited positions
                for pos in positions:
                    if (face, pos) not in visited:                          # Check if the position has not been visited
                        visited.append((face, pos))                         # Add the position to the visited list
                        to_add.append((face, pos))                          # Add the position to the to_add list
                    
                place_path(to_add, mazes, color=visited_color, alpha=.75)
            return None
        else:
            return path_finder.path                                         # Return the path if the end has been reached

    return update_vis, path_finder




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

# Find the path and visited
path, visited = path_finder_bfs(mazes, start_face, start_pos, end_face, end_pos, maze_size)

# Place the visited cells step by step using the PathFinder class
update_vis, path_finder = place_path_step_by_step_with_pathfinder(mazes, start_face, start_pos, end_face, end_pos, maze_size)

# Place the path step by step
update_path = place_path_step_by_step(path, mazes)

# Create the legend with an adjustable offset
create_legend(legend_offset_y=-0.1) 

# Add camera instructional text at the center bottom of the screen
instruction_text = Text(
    text="""
            Right-click and move the mouse to move the camera.          
        """,
    parent=camera.ui,
    origin=(0, 0),
    scale=1,
    position=(0, -0.45),  # Adjust position to be at the center bottom
    color=color.white
)

# Add keys instructional text at the bottom left of the screen
keys_text = Text(
    text="""
            [a] to place all visited cells.
            [p] to place the path steps.
            [v] to visualize the pathfinding process.
        """,
    parent=camera.ui,
    origin=(-0.5, 0),
    scale=1,
    position=(-.95, -0.45),  # Adjust position to be at the bottom left
    color=color.white
)

# Set the window
window.color = color.black
window.title = '3D Pathfinding Maze'
window.borderless = False  
window.fullscreen = False  
window.exit_button.visible = False  # Hide exit button

# Set Ursina development mode to False
application.development_mode = False
EditorCamera()

# Logic to handle user input
locked = False
def input(key):
    global locked
    if key == 'v' and not locked:
        locked = True
        invoke(repeat_update_vis, delay=0)      # Start the repeated update_vis process immediately
    elif key == 'p' and not locked:
        locked = True
        invoke(repeat_update_path, delay=0)     # Start the repeated update_path process immediately
    elif key == 'a' and not locked:
        locked = True
        place_path(path, mazes, color=path_color)
        place_path(visited, mazes, color=visited_color, alpha=.75)
        
# Function to repeat the update_vis function
def repeat_update_vis():
    global locked
    result = update_vis()                           # Call the update_vis function
    if result is True:                              # If all path steps have been placed, stop further updates
        print("All visited cells placed!")
        input.update_vis_done = True
        locked = False
        return
    invoke(repeat_update_vis, delay=.1)            # Schedule the next update

# Function to repeat the update_path function
def repeat_update_path():
    global locked
    result = update_path()                          # Call the update_path function
    if result is True:                              # If all path steps have been placed, stop further updates
        print("All path steps placed!")
        input.update_path_done = True
        locked = False
        return
    invoke(repeat_update_path, delay=.25)           # Schedule the next update



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