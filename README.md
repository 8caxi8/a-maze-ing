*This project has been created as part of the 42 curriculum by dansimoe, manferre*

# A-Maze-ing

![Maze Demo](assets/intro.gif)

## Description

A-Maze-ing is a maze generator and visualizer built in Python. It generates mazes using two different algorithms — DFS (Depth-First Search) and PRIM — and displays them in the terminal with full ASCII rendering, color themes, and interactive controls.

The project is split into two parts:

- **`mazegen`** — a reusable Python package that handles maze generation, pathfinding via BFS, and file output. It can be installed independently via pip.
- **`maze_drawer`** — a terminal visualization module that renders the maze, animates generation and pathfinding, and handles user interaction.

Every generated maze contains a hidden "42" pattern formed by fully closed cells, visible in the terminal rendering.

## Instructions

### Installation

```bash
make install
```

This will install `uv` if not already present and sync all project dependencies.

### Execution

```bash
# Run with the default config.txt
make run

# Run with a specific config file
uv run python3 a_maze_ing.py my_config.txt

# Run in debug mode (pdb)
make debug

# Lint the project
make lint
make lint-strict
```

### Configuration File Format

The configuration file must contain one `KEY=VALUE` pair per line. Lines starting with `#` are treated as comments and ignored. Blank lines are also ignored.

| Key | Description | Required | Example |
|-----|-------------|----------|---------|
| `WIDTH` | Maze width in cells | Yes | `WIDTH=25` |
| `HEIGHT` | Maze height in cells | Yes | `HEIGHT=20` |
| `ENTRY` | Entry coordinates (x,y) | Yes | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | Yes | `EXIT=10,18` |
| `OUTPUT_FILE` | Output filename | Yes | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect maze (one unique path) | Yes | `PERFECT=True` |
| `SEED` | Random seed for reproducibility | No | `SEED=42` |
| `ALGORITHM` | Generation algorithm (DFS or PRIM) | No | `ALGORITHM=PRIM` |

### Example `config.txt`

```text
# Maze configuration
WIDTH=25
HEIGHT=20
ENTRY=0,0
EXIT=10,18
SEED=70
ALGORITHM=PRIM
PERFECT=True
OUTPUT_FILE=maze.txt
```

### Output File Format

The maze is written to the output file using one hexadecimal digit per cell encoding which walls are closed, where each bit represents a direction:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

After an empty line, the file contains the entry coordinates, exit coordinates, and the shortest path from entry to exit using the letters `N`, `E`, `S`, `W`.

### Interactive Controls

Once the maze is displayed, the following keys are available:

| Key | Action |
|-----|--------|
| `c` | Cycle color theme |
| `s` | Cycle drawing style |
| `f` | Toggle shortest path solution |
| `p` | Toggle entry/exit markers |
| `g` | Animate DFS/PRIM generation |
| `o` | Animate BFS pathfinding |
| `i` | Toggle perfect/imperfect maze |
| `j` | Animate imperfect maze transition |
| `w` | Swap generation algorithm |
| `y` | Toggle maze info display |
| `q` | Quit |

During animations, press the animation key to pause, `z` to stop or `q` to quit.

## Maze Generation Algorithm

Two algorithms are implemented:

**DFS (Depth-First Search) — Recursive Backtracker**
Starts from cell (0,0) and carves passages by randomly exploring unvisited neighbours, backtracking when no unvisited neighbours remain. This produces mazes with long winding corridors and few dead ends.

**PRIM's Algorithm**
Starts from cell (0,0) and maintains a list of candidate frontier cells. At each step it randomly picks one candidate and connects it to an already-visited neighbour. This produces mazes with more branching and shorter corridors than DFS.

We chose DFS as the default because it produces more visually interesting mazes with longer paths, which makes the solution animation more satisfying. PRIM was added as a bonus since it produces a noticeably different maze structure.

For pathfinding, BFS (Breadth-First Search) is used since it guarantees the shortest path between entry and exit.

## Code Reusability — `mazegen` Package

The `mazegen` package is fully self-contained and can be installed independently:

```bash
pip install dist/mazegen*
```

### Basic usage

```python
from mazegen import MazeGenerator

# Create a 20x15 maze with DFS
gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    seed=42,
    strategy="DFS",
    perfect=True
)

# Access the maze grid (list[list[int]])
print(gen.maze)

# Find the shortest path
path = gen.find_shortest_path()
print(path)  # [(0,0), (1,0), ...]

# Get path as direction string
directions = gen.get_path_directions()
print(directions)  # "EESSWW..."

# Write to file
gen.write_to_file("maze.txt")
```

### Custom parameters

```python
# Use PRIM's algorithm with a fixed seed
gen = MazeGenerator(20, 15, (0, 0), (19, 14), seed=123, strategy="PRIM")

# Generate an imperfect maze (removes some walls)
gen.make_imperfect(probability=0.08)

# Swap between DFS and PRIM
gen.swap_algorithm()
gen.generate_maze()
```

### Build the package from source

```bash
pip install build
python -m build
# Output: dist/mazegen-1.0.0-py3-none-any.whl
#         dist/mazegen-1.0.0.tar.gz
```

or

```bash
make build
```

## Team and Project Management

**Roles:**
- **dansimoe** — maze drawer, terminal rendering, animation system, intro screen, config parser
- **manferre** — maze generation algorithms (DFS, PRIM), BFS pathfinding, 42 pattern, file output, mazegen package

**Planning:**
We initially planned to finish generation in the first week and rendering in the second. In practice, the rendering took significantly longer than expected — particularly the dynamic draw sets for different border styles, the animation system, and the terminal input handling. The intro screen and package setup were added in the final days.

**What worked well:**
- The draw set approach using dynamic key building made adding new styles straightforward
- Separating `mazegen` as an independent package from the start made the reusability requirement easy to satisfy
- Using generators for animations kept the generation and rendering logic cleanly decoupled

**What could be improved:**
- The drawer has grown large and could be split further into smaller rendering components
- The config parser could support more flexible value formats
- More algorithms could be added (Kruskal's, Wilson's)

**Tools used:**
- `uv` for dependency management
- `pydantic` for config validation
- `flake8` and `mypy` for linting and type checking
- AI was used for debugging assistance, and documentation

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Pydantic documentation](https://docs.pydantic.dev)
- [Python `termios` and `tty` docs](https://docs.python.org/3/library/termios.html)
- [BFS pathfinding — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Box-drawing characters — Unicode](https://en.wikipedia.org/wiki/Box-drawing_characters)

**AI usage:** AI was used throughout the project for code review and debugging (parser bugs, terminal rendering issues), and generating boilerplate (docstrings, README structure). All generated code was reviewed, tested, and understood before being included.