from typing import Generator
from .maze_algorithms import MazeAlgorithm, DFSAlgorithm, PRIMSAlgorithm
from .maze_algorithms import logo_42
import random


class MazeGeneratorError(Exception):
    """Exception raised for errors in MazeGenerator operations.

    Raised when invalid parameters are passed to MazeGenerator methods
    or when the maze configuration is invalid.
    """
    pass


class MazeGenerator:
    """Generates and manages mazes using different generation algorithms.

    Provides maze generation, pathfinding, and animation frame generation
    using a strategy pattern to support multiple maze algorithms.

    Attributes:
        available_algos: Mapping of algorithm names to their classes.
        maze: The current maze state as a 2D grid of integers where each
              integer encodes the walls of a cell as bits (N=0, E=1, S=2, W=3).

    """

    available_algos: dict[str, type[MazeAlgorithm]] = {
        "DFS": DFSAlgorithm,
        "PRIM": PRIMSAlgorithm,
        }

    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int], seed: int | None = None,
                 strategy: str = "DFS", perfect: bool = True) -> None:
        """Initialize the MazeGenerator and generate the initial maze.

        Args:
            width: Number of columns in the maze. Must be >= 1.
            height: Number of rows in the maze. Must be >= 1.
            entry: Starting position as (x, y). Must be within bounds
                   and not inside the 42 logo pattern.
            exit: Ending position as (x, y). Must be within bounds,
                  not inside the 42 logo pattern, and different from entry.
            seed: Random seed for reproducible maze generation. If None,
                  a random seed is generated automatically.
            strategy: Name of the maze generation algorithm to use.
                      Must be one of the keys in available_algos.
                      Defaults to "DFS".
            perfect: If True, generates a perfect maze with no loops.
                     If False, also calls make_imperfect() after generation.
                     Defaults to True.

        Raises:
            MazeGeneratorError: If width or height are less than 1.
            MazeGeneratorError: If width and height are both 1.
            MazeGeneratorError: If entry or exit are not valid (int, int)
                                tuples.
            MazeGeneratorError: If entry or exit are out of maze bounds.
            MazeGeneratorError: If entry or exit are inside the 42 logo
                                pattern.
            MazeGeneratorError: If entry and exit are the same position.
            MazeGeneratorError: If strategy is not a valid algorithm name.
            MazeGeneratorError: If seed is not an integer or None.
        """

        self._set_algorithm(strategy)
        self._set_maze_dimensions(width, height)
        if width < 9 or height < 7:
            print("Error: Maze dimensions are too small."
                  " 42 Pattern will be omitted")

        self._set_entry_exit_positions(entry, exit)
        if not isinstance(seed, int | None):
            raise MazeGeneratorError("Seed must be an integer")
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        self._seed = seed
        self._perfect: bool = perfect
        self.maze: list[list[int]] = []
        self.generate_maze()
        if not perfect:
            self.make_imperfect()

    def get_perfect_status(self) -> bool:
        """Return whether the current maze is perfect (no loops).

        Returns:
            True if the maze is perfect, False if it has been made imperfect.
        """
        return self._perfect

    def get_strategy(self) -> str:
        """Return the name of the current maze generation algorithm class.

        Returns:
            The class name of the current strategy (e.g. 'DFSAlgorithm').
        """
        return self._strategy.__class__.__name__

    def get_maze_seed(self) -> int:
        """Return the seed used for maze generation.

        Returns:
            The integer seed used to generate the current maze.
        """
        return self._seed

    def _set_maze_dimensions(self, width: int, height: int) -> None:
        """Validate and set the maze dimensions.

        Args:
            width: Number of columns. Must be a positive integer.
            height: Number of rows. Must be a positive integer.

        Raises:
            MazeGeneratorError: If width or height are less than 1,
                                or if both are equal to 1.
        """
        try:
            if int(width) < 1 or int(height) < 1:
                raise ValueError("Expected maze dimensions to be higher"
                                 f" than 1, got ({width}, {height})")
        except ValueError as e:
            raise MazeGeneratorError(e)

        if width == 1 and height == 1:
            raise MazeGeneratorError("Maze too small")
        self._width = width
        self._height = height

    def _set_entry_exit_positions(self, entry: tuple[int, int],
                                  exit: tuple[int, int]) -> None:
        """Validate and set the entry and exit positions.

        Args:
            entry: Starting position as (x, y).
            exit: Ending position as (x, y).

        Raises:
            MazeGeneratorError: If entry or exit are not (int, int) tuples.
            MazeGeneratorError: If entry or exit are out of maze bounds.
            MazeGeneratorError: If entry or exit are inside the 42 logo
                                pattern.
            MazeGeneratorError: If entry and exit are the same position.
        """
        logo_cells: set[tuple[int, int]] = logo_42(self._width, self._height)

        if not (isinstance(entry, tuple) and
                all(isinstance(v, int) for v in entry)):
            raise MazeGeneratorError("Expected entry point to be"
                                     " (int, int), got"
                                     f" {entry}")

        if not (isinstance(exit, tuple) and
                all(isinstance(v, int) for v in exit)):
            raise MazeGeneratorError("Expected exit point to be"
                                     " (int, int), got"
                                     f" {exit}")

        if entry in logo_cells:
            raise MazeGeneratorError("Entry point must not be inside"
                                     " the 42 pattern")
        elif not ((0 <= entry[0] < self._width) and
                  (0 <= entry[1] < self._height)):
            raise MazeGeneratorError("Entry point is out of maze bounds")

        if exit in logo_cells:
            raise MazeGeneratorError("Exit point must not be inside"
                                     " the 42 pattern")
        elif not ((0 <= exit[0] < self._width) and
                  (0 <= exit[1] < self._height)):
            raise MazeGeneratorError("Exit point is out of maze bounds")

        if entry == exit:
            raise MazeGeneratorError("Entry point must not coincide with"
                                     " Exit point")

        self._entry = entry
        self._exit = exit

    def _set_algorithm(self, strategy: str) -> None:
        """Validate and set the maze generation algorithm.

        Args:
            strategy: Name of the algorithm. Must be a key in available_algos.

        Raises:
            MazeGeneratorError: If strategy is not a valid algorithm name,
                                listing all available strategies in the
                                message.
        """
        availables = ("\n   - ").join(self.available_algos.keys())
        try:
            self._strategy: MazeAlgorithm = self.available_algos[strategy]()
        except KeyError:
            raise MazeGeneratorError(f"Strategy '{strategy}' not found. "
                                     "Available Strategies are:\n   - "
                                     f"{availables}")

    def swap_algorithm(self) -> None:
        """Toggle the maze generation algorithm between DFS and PRIM.

        Switches from DFSAlgorithm to PRIMSAlgorithm or vice versa.
        Does not regenerate the maze automatically.
        """
        if isinstance(self._strategy, DFSAlgorithm):
            self._strategy = PRIMSAlgorithm()
        elif isinstance(self._strategy, PRIMSAlgorithm):
            self._strategy = DFSAlgorithm()

    def generate_maze(self) -> None:
        """Generate a new maze and store it in self.maze.

        Uses the current strategy and seed to generate a deterministic maze.
        Overwrites any existing maze stored in self.maze.
        """
        self.maze = self._strategy.final_maze(self._width, self._height,
                                              self._seed)

    def generate_frame(self) -> Generator[tuple[list[list[int]],
                                          list[tuple[int, int]]], None, None]:
        """Return a generator that yields intermediate maze generation frames.

        Each frame contains the current maze state and the algorithm's
        internal state (stack for DFS, candidates for PRIM) for animation.

        Returns:
            Generator yielding (maze, state) tuples where maze is the current
            2D grid and state is the list of cells being tracked by the
            algorithm.
        """
        return self._strategy.generate(self._width, self._height, self._seed)

    def make_imperfect(self, probability: float = 0.08) -> None:
        """Make the maze imperfect by randomly removing walls to create loops.

        Modifies self.maze in place. Ensures no 3x3 open areas are created
        and no walls inside the 42 logo pattern are removed.

        Args:
            probability: Probability of removing each eligible wall.
                         Must be between 0.0 and 1.0. Defaults to 0.08.

        Raises:
            MazeGeneratorError: If probability is not a number.
            MazeGeneratorError: If probability is not between 0 and 1.
        """
        if not isinstance(probability, (int, float)):
            raise MazeGeneratorError("Expected probability to be of"
                                     " type float")
        if not (0 <= probability <= 1):
            raise MazeGeneratorError("Probability must be between 0 and 1")

        self.maze = self._strategy.make_imperfect(self.maze, probability,
                                                  self._seed)

    def make_imperfect_frames(self, probability: float = 0.08) \
            -> Generator[tuple[tuple[int, int], list[list[int]]], None, None]:
        """Return a generator that yields frames of the make_imperfect process.

        Each frame contains the current cell being processed and the current
        maze state, allowing the caller to animate wall removal in real time.
        Modifies self.maze in place as frames are consumed.

        Args:
            probability: Probability of removing each eligible wall.
                         Must be between 0.0 and 1.0. Defaults to 0.08.

        Returns:
            Generator yielding ((x, y), maze) tuples where (x, y) is the
            cell currently being processed and maze is the current 2D grid.

        Raises:
            MazeGeneratorError: If probability is not a number.
            MazeGeneratorError: If probability is not between 0 and 1.
        """
        if not isinstance(probability, (int, float)):
            raise MazeGeneratorError("Expected probability to be of"
                                     " type float")
        if not (0 <= probability <= 1):
            raise MazeGeneratorError("Probability must be between 0 and 1")
        return self._strategy.make_imperfect_frames(self.maze, probability,
                                                    self._seed)

    def find_shortest_path(self) -> list[tuple[int, int]]:
        """Find the shortest path between entry and exit using BFS.

        Returns:
            List of (x, y) positions from entry to exit representing
            the shortest path. Returns an empty list if no path exists.
        """
        return self._strategy.bfs(self.maze, self._width, self._height,
                                  self._entry, self._exit)

    def path_frames(self) -> Generator[tuple[list[tuple[int, int]],
                                             list[tuple[int, int]]],
                                       None, None]:
        """Return a generator that yields BFS search and path animation frames.

        Yields two phases of animation:
        - Phase 1: BFS search expanding outward from entry, showing cells
                   explored with an empty path list.
        - Phase 2: Path reconstruction from exit back to entry, showing
                   the growing shortest path.

        Returns:
            Generator yielding (searched, path) tuples where searched is the
            list of all cells visited so far and path is the current
            reconstructed path (empty during phase 1).
        """

        return self._strategy.bfs_animate(self.maze, self._width, self._height,
                                          self._entry, self._exit)

    def print_encoded_maze(self) -> None:
        """Print the maze to stdout as a grid of hexadecimal wall encodings.

        Each cell is printed as a single uppercase hex character (0-F)
        representing its wall configuration as a 4-bit integer.
        """
        for row in self.maze:
            for cell in row:
                print(format(cell, 'X'), end="")
            print()

    def get_path_directions(self) -> str:
        """Return the shortest path as a string of cardinal direction
           characters.

        Computes the shortest path from entry to exit and converts each
        step into a direction character.

        Returns:
            String of direction characters (N, S, E, W) representing
            each step of the shortest path. Returns an empty string
            if no path exists.
        """
        path: list[tuple[int, int]] = self.find_shortest_path()
        result: str = ""

        if path:
            for i in range(len(path) - 1):
                if path[i + 1][0] - path[i][0] == 1:
                    result += "E"
                elif path[i + 1][0] - path[i][0] == -1:
                    result += "W"
                elif path[i + 1][1] - path[i][1] == 1:
                    result += "S"
                elif path[i + 1][1] - path[i][1] == -1:
                    result += "N"

        return result

    def get_entry_exit_positions(self) -> list[tuple[int, int]]:
        """Return the entry and exit positions of the maze.

        Returns:
            List containing [entry, exit] as (x, y) tuples.
        """
        return [self._entry, self._exit]

    def write_to_file(self, filename: str) -> None:
        """Write the maze, entry, exit and path directions to a file.

        The file format is:
        - Hex encoded maze grid (one row per line)
        - Blank line
        - Entry position
        - Exit position
        - Path directions string

        Args:
            filename: Path to the output file.

        Raises:
            MazeGeneratorError: If the file cannot be opened or written to.
        """
        try:
            with open(filename, "w") as file:
                for row in self.maze:
                    for cell in row:
                        file.write(format(cell, 'X'))
                    file.write("\n")
                file.write("\n")

                file.write(f"{self._entry}\n")
                file.write(f"{self._exit}\n")
                file.write(f"{self.get_path_directions()}\n")
        except OSError as e:
            raise MazeGeneratorError(f"{e}")
