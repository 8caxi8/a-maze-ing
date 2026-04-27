*This project has been created as part of the 42 curriculum by dansimoe, manferre*

# A-Maze-ing: Maze generation and solving
## Description

This project is divided in two parts:

- Create a `mazegen` module that should implement tools to generate a maze provided its (`width`, `height`) and the pair `Entry` / `Exit`. This generation is made by implementing two algorithms, `DFS` and `PRIM`, and for pathfinding the `BFS` was used. 

- Drawing the maze and some functionalities so show the `mazegen` package working.

## Instructions

### Instalation

```bash
# Install venv and its dependencies
make install
```

### Execution

```bash
# Run the main entry with the default config.txt file
make run

# Run with a specific config.txt
python3 a_maze_ing.py config.txt

# Run with pdb debug tool
make debug

# Run with lint or lint-strict
make lint
make lint-strict
```

### Configuration file format

The `config.txt` file should be in the following format:

|Key    | Description | Example  |
|-------|-------------|----------|
|WIDTH | Maze width | WIDTH=12|
|HEIGHT | Maze height | HEIGHT=15|
|ENTRY | Entry point (x, y) | ENTRY=1,5|
|EXIT | Exit point (x, y) | EXIT=5,5|
|OUTPUT_FILE | output filename | OUTPUT_FILE=maze.txt|
|PERFECT | Is the maze perfect? | PERFECT=TRUE|

Other optional keys are `SEED`(for a special seed number) and `ALGORITHM`(DFS and PRIM are acceptable for maze generation).

### Example `config.txt`:

```text
# Easy configs
WIDTH=25
HEIGHT=20
ENTRY=0,0
EXIT=10,18
SEED=70
ALGORITHM=PRIM
PERFECT=TRUE
OUTPUT_FILE=maze.txt
```

