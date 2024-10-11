# Maze Path Finder

This project, **maze_path_finder**, implements multiple algorithms for maze path finding with visualization using the curses library.

## Project Structure
- **path_finder.py**: The main script that implements the path finding algorithms and visualization.
- **maze.csv**: Contains the maze data in CSV format.
- **requirements.txt**: Packages required (curses)

## Features

- Multiple path finding algorithms.
- Visualization of the maze and the path finding process using the curses library.

## Usage

1. Ensure you have Python installed on your system.  
2. Install the required dependencies:  
**Note**: `curses` is a built-in module in Unix-based systems and does not need to be installed via pip. If you are using Windows, need to install requirements.txt wich includes `windows-curses`.
    ```sh
    pip install -r requirements.txt
    ```
3. Run the path finder script:
    ```sh
    python path_finder.py
    ```

### Command Line Arguments
**Usage**: path_finder.py [-h] [--rows ROWS] [--cols COLS] [--maze_type MAZE_TYPE]  
**Defaults**: [--rows 10] [--cols 10] [--maze_type MAZE_TYPE]
```
-h, --help:             Show this help message and exit
--rows ROWS:            Number of rows in the maze
--cols COLS:            Number of columns in the maze
--maze_type MAZE_TYPE:  Type of maze to generate: Maze type small: 0, Maze type large: 1, Maze type csv: 2, Random grid maze: 3, Random maze: 4
```
**Note**: [--rows ROWS] and [--cols COLS] arguments will only apply to Maze types Random grid maze: 3 and Random maze: 4


## Algorithms Implemented

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- A* Search
- Greedy Best-First Search
- Dijkstra
- Bidirectional Search 


## Visualization
The visualization is done using the curses library, which provides a terminal-based interface to display the maze and the path finding process.

Here are some examples:
### **python path_finder.py --maze_type 0**  
![alt text](https://raw.githubusercontent.com/SantiagoEnriqueGA/maze_path_finder/refs/heads/main/img/maze_type_0.png)


### **python path_finder.py --maze_type 1**    
![alt text](https://raw.githubusercontent.com/SantiagoEnriqueGA/maze_path_finder/refs/heads/main/img/maze_type_1.png)


### **python path_finder.py --maze_type 3 --rows 25 --cols 25**  
![alt text](https://raw.githubusercontent.com/SantiagoEnriqueGA/maze_path_finder/refs/heads/main/img/maze_type_3_r25_c25.png)


### **python path_finder.py --maze_type 4 --rows 20 --cols 20**  
![alt text](https://raw.githubusercontent.com/SantiagoEnriqueGA/maze_path_finder/refs/heads/main/img/maze_type_4_r20_c20.png)


