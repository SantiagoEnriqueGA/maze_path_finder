from calendar import c
import random
from ursina import *
from collections import deque

# random.seed(42)  # Set seed for reproducibility testing

app = Ursina()  # Initialize the app

size = 3        # Size of the cube
maze_size = 10  # Size of the maze

# Create a single cube entity with 6 solid colored sides
cube = Entity(model='cube', color=color.azure, scale=size, alpha=0.8) #for debuging
# cube = Entity(model='cube', color=color.azure, scale=size)

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
        # entity.rotation_x = 180
    elif face == 'top':
        entity.y = 0.5
        entity.rotation_x = -90
        entity.rotation_y = 180
        # entity.rotation_z = 90
    elif face == 'bottom':
        entity.y = -0.5
        entity.rotation_x = 90
        entity.rotation_y = 180

# Function to create grid lines for a face
def create_grid_lines(face):
    lines = Entity(parent=cube)
    step = 1 / maze_size
    for i in range(1, maze_size):
        # Vertical lines
        vline = Entity(parent=lines, model='wireframe_cube', color=color.white)
        vline.scale = (0.002, 1, 0.002)
        vline.x = i * step - 0.5
        # Horizontal lines
        hline = Entity(parent=lines, model='wireframe_cube', color=color.white)
        hline.scale = (1, 0.002, 0.002)
        hline.y = i * step - 0.5
    
    set_face_position(lines, face)


def gen_grid_maze(size, wall_probability=0.3):
    maze = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if random.random() < wall_probability:
                maze[i][j] = 1
    return maze

def create_maze(face):
    maze = gen_grid_maze(maze_size)
       
    face_entity = Entity(parent=cube)  # Create a parent entity for the face

    for i in range(maze_size):
        for j in range(maze_size):
            if maze[i][j] == 1:                                                     # If there is a wall
                wall = Entity(parent=face_entity, model='cube', color=color.gray)   # Attach wall to face_entity
                wall.scale = (1/maze_size -.01, 1/maze_size-.01, 0.01)              # Scale the wall to fit the grid
                wall.x = (i + 0.5) / maze_size - 0.5                                # Position the wall in the grid, x
                wall.y = (j + 0.5) / maze_size - 0.5                                # Position the wall in the grid, y
                                
    set_face_position(face_entity, face)
    
    return maze
    
# Place the start and end points, randomly
def place_start_end(mazes):
    
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
    start_wall.scale = (1/maze_size -.01, 1/maze_size-.01, 0.01)
    start_wall.x = (start_pos[0] + 0.5) / maze_size - 0.5
    start_wall.y = (start_pos[1] + 0.5) / maze_size - 0.5
    
    set_face_position(start_entity, start_face)
    
    # Create a parent entity for the end face
    end_entity = Entity(parent=cube)
    end_wall = Entity(parent=end_entity, model='cube', color=color.red)
    end_wall.scale = (1/maze_size -.01, 1/maze_size-.01, 0.01)
    end_wall.x = (end_pos[0] + 0.5) / maze_size - 0.5
    end_wall.y = (end_pos[1] + 0.5) / maze_size - 0.5
    
    set_face_position(end_entity, end_face)
    
    return start_face, start_pos, end_face, end_pos
    


def get_neighbors(face, pos):
    neighbors = []
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0)  # right, down, left, up
    ]
    for d in directions:
        new_pos = (pos[0] + d[0], pos[1] + d[1])
        if 0 <= new_pos[0] < maze_size and 0 <= new_pos[1] < maze_size:
            neighbors.append((face, new_pos))
        else:
            # Handle edge transitions          
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
                    neighbors.append(('front', (pos[1], maze_size-1)))
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

    queue = deque([(start_face, start_pos)])        # Initialize queue with start position
    visited = {start_face: {start_pos}}             # Initialize visited set with start position
    parent = {start_face: {start_pos: None}}        # Initialize parent dictionary with start position

    while queue:
        current_face, current_pos = queue.popleft()             # Get the current position from the queue
        
        if (current_face, current_pos) == (end_face, end_pos):  # Check if we have reached the end
            path = []                                           
            while current_pos is not None:                      # Reconstruct the path
                path.append((current_face, current_pos))        # Add the current position to the path
                if parent[current_face][current_pos] is not None:
                    current_face, current_pos = parent[current_face][current_pos]   # Move to the parent position
                else:
                    break
            return path[::-1]

        for neighbor_face, neighbor_pos in get_neighbors(current_face, current_pos):
            if neighbor_pos not in visited.get(neighbor_face, set()) and mazes[neighbor_face][neighbor_pos[0]][neighbor_pos[1]] != 1:
                if neighbor_face not in visited:
                    visited[neighbor_face] = set()
                    parent[neighbor_face] = {}
                visited[neighbor_face].add(neighbor_pos)
                parent[neighbor_face][neighbor_pos] = (current_face, current_pos)
                queue.append((neighbor_face, neighbor_pos))

    return []


# Function to highlight the path step by step
def place_path_step_by_step(path, mazes):
    step_index = 0

    def update_path():
        nonlocal step_index
        if step_index < len(path):
            face, pos = path[step_index]
            if mazes[face][pos[0]][pos[1]] == 0:
                
                print(f"Step {step_index + 1}: {face}, {pos}")
                
                path_entity = Entity(parent=cube)
                path_wall = Entity(parent=path_entity, model='cube', color=color.red)
                path_wall.scale = (1/maze_size -.01, 1/maze_size-.01, 0.05)
                path_wall.x = (pos[0] + 0.5) / maze_size - 0.5
                path_wall.y = (pos[1] + 0.5) / maze_size - 0.5
                set_face_position(path_entity, face)
            step_index += 1

    return update_path

# Function to highlight the path
def place_path(visited, mazes):
    for face, pos in visited:
        if mazes[face][pos[0]][pos[1]] == 0:
            path_entity = Entity(parent=cube)
            path_wall = Entity(parent=path_entity, model='cube', color=color.gold)
            path_wall.scale = (1/maze_size -.01, 1/maze_size-.01, 0.01)
            path_wall.x = (pos[0] + 0.5) / maze_size - 0.5
            path_wall.y = (pos[1] + 0.5) / maze_size - 0.5
            set_face_position(path_entity, face)

def input(key):
    if key == 'space':
        update_path()

# Create grid lines for each face
create_grid_lines('front')
create_grid_lines('back')
create_grid_lines('left')
create_grid_lines('right')
create_grid_lines('top')
create_grid_lines('bottom')

# Create a maze on each face
mazes = {
    'front': create_maze('front'),
    'back': create_maze('back'),
    'left': create_maze('left'),
    'right': create_maze('right'),
    'top': create_maze('top'),
    'bottom': create_maze('bottom')
}

# place point on 2,1 of each face
def create_2x1(face):
    maze = [[0 for _ in range(maze_size)] for _ in range(maze_size)]
    maze[2][1] = 1
       
    face_entity = Entity(parent=cube)  # Create a parent entity for the face

    for i in range(maze_size):
        for j in range(maze_size):
            if maze[i][j] == 1:                                                     # If there is a wall
                wall = Entity(parent=face_entity, model='cube', color=color.blue)   # Attach wall to face_entity
                wall.scale = (1/maze_size -.01, 1/maze_size-.01, 0.01)              # Scale the wall to fit the grid
                wall.x = (i + 0.5) / maze_size - 0.5                                # Position the wall in the grid, x
                wall.y = (j + 0.5) / maze_size - 0.5                                # Position the wall in the grid, y
                                
    set_face_position(face_entity, face)
    
    return maze

create_2x1('front')
create_2x1('back')
create_2x1('left')
create_2x1('right')
create_2x1('top')
create_2x1('bottom')



start_face, start_pos, end_face, end_pos = place_start_end(mazes)
            
path = path_finder(mazes, start_face, start_pos, end_face, end_pos)
place_path(path_finder(mazes, start_face, start_pos, end_face, end_pos), mazes)  

update_path = place_path_step_by_step(path, mazes)

print(mazes)
print(path)
print(f"Start: {start_face}, {start_pos}")
print(f"End: {end_face}, {end_pos}")

window.color = color.black
EditorCamera()
app.run()
