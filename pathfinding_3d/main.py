from ursina import *

app = Ursina()

# Define the size of the cube and the maze
size = 3
maze_size = 10  # A 10x10 maze for each face

# Create a single cube entity with 6 solid colored sides
cube = Entity(model='cube', color=color.azure, scale=size)#, alpha=0.5)

# Add edges using a wireframe
edges = Entity(model=Mesh(vertices=[Vec3(-0.5, -0.5, -0.5), Vec3(0.5, -0.5, -0.5), Vec3(0.5, 0.5, -0.5), Vec3(-0.5, 0.5, -0.5),  # back face
                                    Vec3(-0.5, -0.5, 0.5), Vec3(0.5, -0.5, 0.5), Vec3(0.5, 0.5, 0.5), Vec3(-0.5, 0.5, 0.5)],  # front face
                                    triangles=[
                                            (0, 1, 2), (2, 3, 0),  # back
                                            (4, 5, 6), (6, 7, 4),  # front
                                            (0, 1, 5), (5, 4, 0),  # bottom
                                            (1, 2, 6), (6, 5, 1),  # right
                                            (0, 3, 7), (7, 4, 0)   # left
                                        ],  
                                    mode='line'),  # Display only the edges as lines
                color=color.white,
                scale=size + 0.01)  # Slightly larger to make the edges visible

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
    
    if face == 'front':
        lines.z = 0.5
    elif face == 'back':
        lines.z = -0.5
        lines.rotation_y = 180
    elif face == 'left':
        lines.x = -0.5
        lines.rotation_y = 90
    elif face == 'right':
        lines.x = 0.5
        lines.rotation_y = -90
    elif face == 'top':
        lines.y = 0.5
        lines.rotation_x = 90
    elif face == 'bottom':
        lines.y = -0.5
        lines.rotation_x = -90

# Create grid lines for each face
create_grid_lines('front')
create_grid_lines('back')
create_grid_lines('left')
create_grid_lines('right')
create_grid_lines('top')
create_grid_lines('bottom')

window.color = color.black

EditorCamera()

app.run()