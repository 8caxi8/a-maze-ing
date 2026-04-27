# mazegen

*This project has been created as part of the 42 curriculum by dansimoe, manferre.*

`mazegen` is a reusable Python package for generating, solving, and exporting mazes.

It was developed as part of the **A-Maze-ing** project from the 42 curriculum, where the goal is to generate valid mazes, support perfect and imperfect maze structures, include the required visible **42 pattern**, and provide both terminal visualization and reusable package architecture.

The package exposes a single main class:

```python
from mazegen import MazeGenerator
```

which allows users to generate mazes, retrieve shortest paths, animate generation steps, and export the maze using the hexadecimal format required by the project.

---

# Description

A maze is represented as a 2D grid where each cell stores its walls using a hexadecimal value:

| Bit | Direction |
|---|---|
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

A closed wall sets the bit to `1`, and an open wall sets it to `0`.

Example:

- `3` (`0011`) → North and East closed
- `A` (`1010`) → East and West closed

This format follows the project specification exactly.

The package supports:

- DFS (Recursive Backtracker)
- Prim’s Algorithm
- Perfect mazes
- Imperfect mazes (additional openings)
- Shortest path solving using BFS
- Animated generation frames
- Animated imperfect-maze creation
- Required “42” logo pattern using closed cells

The main reusable module is implemented through the `MazeGenerator` class.

---

# Installation

This package can be install with the command:

```bash
pip install mazegen
```


# Basic Usage

## Create a maze

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    seed=42,
    strategy="DFS",
    perfect=True
)
```

This generates a perfect maze using DFS.

Supported strategies:

- `"DFS"`
- `"PRIM"`

---

# Access Generated Maze

```python
print(maze.maze)
```

This returns:

```python
list[list[int]]
```

where each integer is the hexadecimal wall encoding of a cell.

You can also print the encoded maze:

```python
maze.print_encoded_maze()
```

---

# Access the Shortest Path

```python
path = maze.find_shortest_path()
print(path)
```

Returns:

```python
list[tuple[int, int]]
```

Example:

```python
[(0, 0), (1, 0), (2, 0), ...]
```

You can also get directions:

```python
print(maze.get_path_directions())
```

Example:

```text
EESSWWNN
```

This is generated using BFS internally.

---

# Imperfect Mazes

## Generate directly

```python
maze.make_imperfect()
```

This opens extra walls while ensuring:

- connectivity remains valid
- no forbidden 3x3 open areas are created

The project rules explicitly forbid large open areas wider than 2 cells.

---

# Animation Support

## Animate maze generation

```python
for frame, stack in maze.generate_frame():
    pass
```

## Animate imperfect maze creation

```python
for cell, frame in maze.make_imperfect_frames():
    pass
```

## Animate shortest path solving

```python
for searched, path in maze.path_frames():
    pass
```

These generators are used by the terminal visualizer and allow step-by-step rendering.

---

# Export to File

```python
maze.write_to_file("maze.txt")
```

This creates the required output format:

1. Maze rows using hexadecimal encoding
2. Empty line
3. Entry coordinates
4. Exit coordinates
5. Shortest path directions

Example:

```text
F95A31...
A1BC44...

(0, 0)
(19, 14)
EESSSWWN
```

---


# Why DFS and Prim’s

We chose:

## DFS (Recursive Backtracker)

Because it produces:

- long corridors
- clean structure
- fast execution
- ideal perfect mazes

## Prim’s Algorithm

Because it produces:

- more branching
- more random-looking mazes
- good variation for visualization

Supporting both improves experimentation and satisfies the project bonus for multiple algorithms.

---

# Resources

## Documentation

- Python official documentation
- Python `collections.deque`
- Graph theory references for spanning trees
- DFS / BFS / Prim’s Algorithm references

## AI Usage

AI was used for:

- improving docstrings
- README structure
- debugging edge cases

---

# Final Notes

The goal of this package is not only to generate mazes, but to provide a clean, reusable, and extensible architecture for future projects.

