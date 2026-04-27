from abc import ABC, abstractmethod
from typing import Generator
import random
from collections import deque


def logo_42(width: int, height: int) -> set[tuple[int, int]]:
    """Generate the set of cells occupied by the 42 logo pattern.

    The logo is centered in the maze and consists of two characters
    ('4' and '2') made up of individual cells. Returns an empty set
    if the maze is too small to fit the pattern.

    Args:
        width: Number of columns in the maze.
        height: Number of rows in the maze.

    Returns:
        Set of (x, y) cell coordinates occupied by the 42 logo.
        Returns an empty set if width < 9 or height < 7.
    """
    logo_cells: set[tuple[int, int]] = set()

    if width < 9 or height < 7:
        return logo_cells

    logo_h = height // 2 - 2
    logo_w = width // 2 - 3

    for h in range(2):
        logo_cells.add((logo_w, logo_h + h))
    for w in range(3):
        logo_cells.add((logo_w + w, logo_h + 2))
    for h in range(1, 3):
        logo_cells.add((logo_w + 2, logo_h + 2 + h))

    for w in range(3):
        logo_cells.add((logo_w + 4 + w, logo_h))
    for h in range(1, 3):
        logo_cells.add((logo_w + 6, logo_h + h))
    for w in range(2):
        logo_cells.add((logo_w + 4 + w, logo_h + 2))
    for h in range(1, 3):
        logo_cells.add((logo_w + 4, logo_h + 2 + h))
    for w in range(1, 3):
        logo_cells.add((logo_w + 4 + w, logo_h + 4))

    return logo_cells


class MazeAlgorithm(ABC):
    """Abstract base class for maze generation algorithms.

    Defines the interface and shared functionality for all maze generation
    strategies. Mazes are represented as 2D grids of integers where each
    cell encodes its walls as a 4-bit integer:
        - Bit 0 (N): North wall
        - Bit 1 (E): East wall
        - Bit 2 (S): South wall
        - Bit 3 (W): West wall

    A bit value of 1 means the wall is closed, 0 means it is open.
    All cells start with value 0xF (all walls closed).

    Class Attributes:
        N: Bit index for the north wall.
        E: Bit index for the east wall.
        S: Bit index for the south wall.
        W: Bit index for the west wall.
        DIRS: List of (dx, dy, direction, opposite) tuples for all
              four cardinal directions.
    """

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    DIRS: list[tuple[int, int, int, int]] = [
            (0, -1, N, S),
            (1, 0, E, W),
            (0, 1, S, N),
            (-1, 0, W, E),
        ]

    @abstractmethod
    def generate(self, width: int, height: int, seed: int | None = None) \
            -> Generator[tuple[list[list[int]],
                               list[tuple[int, int]]], None, None]:
        """Generate a maze step by step, yielding intermediate states.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            seed: Random seed for reproducible generation. If None,
                  generation is non-deterministic.

        Yields:
            Tuples of (maze, state) where maze is the current 2D grid
            and state is the algorithm's internal structure (e.g. stack
            for DFS, candidates for PRIM) as a list of (x, y) positions.
        """
        pass

    @abstractmethod
    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:
        """Generate and return the completed maze.

        Runs the generation algorithm to completion and returns the
        final maze state.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            seed: Random seed for reproducible generation. If None,
                  generation is non-deterministic.

        Returns:
            Completed maze as a 2D list of integers encoding wall states.
        """
        pass

    def make_imperfect_frames(self, maze: list[list[int]],
                              probability: float = 0.08,
                              seed: int | None = None) \
            -> Generator[tuple[tuple[int, int], list[list[int]]], None, None]:
        """Randomly remove walls to create loops, yielding each step as a
           frame.

        Iterates over every eligible cell and independently tries to open
        its east and south walls based on the given probability. Skips cells
        inside the 42 logo pattern and reverts any removal that would create
        a 3x3 open area. Guarantees at least one wall is opened by forcing
        a removal if none occurred naturally. Modifies the maze in place.

        Args:
            maze: The maze to make imperfect, modified in place.
            probability: Probability of opening each eligible wall.
                         Must be between 0.0 and 1.0. Defaults to 0.08.
            seed: Random seed for reproducible results. If None,
                  results are non-deterministic.

        Yields:
            Tuples of ((x, y), maze) where (x, y) is the cell currently
            being processed and maze is the current 2D grid state.
        """

        width: int = len(maze[0])
        height: int = len(maze)
        logo_cells: set[tuple[int, int]] = logo_42(width, height)
        opened_walls: int = 0
        possible_cells: set[tuple[int, int]] = set()

        rng = random.Random(seed)

        def check_open_area(maze: list[list[int]], width: int, height: int) \
                -> bool:
            """Check if any 3x3 block in the maze is fully open.

            Args:
                maze: The current maze state.
                width: Number of columns in the maze.
                height: Number of rows in the maze.

            Returns:
                True if a 3x3 open area exists, False otherwise.
            """

            for sx in range(width - 2):
                for sy in range(height - 2):
                    is_open = True
                    for x in range(sx, sx + 3):
                        for y in range(sy, sy + 3):
                            if x < sx + 2 and (maze[y][x] & (1 << self.E)):
                                is_open = False
                                break

                            if y < sy + 2 and (maze[y][x] & (1 << self.S)):
                                is_open = False
                                break
                        if not is_open:
                            break

                    if is_open:
                        return True
            return False

        for y in range(height):
            for x in range(width):
                if (x, y) in logo_cells:
                    continue

                if x < width - 1:
                    if (maze[y][x] & (1 << self.E) and
                            (x + 1, y) not in logo_cells):
                        possible_cells.add((x, y))
                        if rng.random() < probability:
                            maze[y][x] &= ~(1 << self.E)
                            maze[y][x + 1] &= ~(1 << self.W)
                            opened_walls += 1
                            if check_open_area(maze, width, height):
                                maze[y][x] |= (1 << self.E)
                                maze[y][x + 1] |= (1 << self.W)
                                opened_walls -= 1

                if y < height - 1:
                    if (maze[y][x] & (1 << self.S) and
                            (x, y + 1) not in logo_cells):
                        possible_cells.add((x, y))
                        if rng.random() < probability:
                            maze[y][x] &= ~(1 << self.S)
                            maze[y + 1][x] &= ~(1 << self.N)
                            opened_walls += 1
                            if check_open_area(maze, width, height):
                                maze[y][x] |= (1 << self.S)
                                maze[y + 1][x] |= (1 << self.N)
                                opened_walls -= 1

                yield (x, y), maze

        if opened_walls == 0:
            x, y = rng.choice(list(possible_cells))
            if (maze[y][x] & (1 << self.E)):
                maze[y][x] &= ~(1 << self.E)
                maze[y][x + 1] &= ~(1 << self.W)
            else:
                maze[y][x] &= ~(1 << self.S)
                maze[y + 1][x] &= ~(1 << self.N)

            yield (x, y), maze

    def make_imperfect(self, maze: list[list[int]], probability: float = 0.08,
                       seed: int | None = None) -> list[list[int]]:
        """Randomly remove walls to create loops and return the modified maze.

        Iterates over every eligible cell and independently tries to open
        its east and south walls based on the given probability. Skips cells
        inside the 42 logo pattern and reverts any removal that would create
        a 3x3 open area. Guarantees at least one wall is opened by forcing
        a removal if none occurred naturally. Modifies the maze in place.

        Args:
            maze: The maze to make imperfect, modified in place.
            probability: Probability of opening each eligible wall.
                         Must be between 0.0 and 1.0. Defaults to 0.08.
            seed: Random seed for reproducible results. If None,
                  results are non-deterministic.

        Returns:
            The modified maze with at least one additional passage created.
        """

        width: int = len(maze[0])
        height: int = len(maze)
        logo_cells: set[tuple[int, int]] = logo_42(width, height)
        opened_walls: int = 0
        possible_cells: set[tuple[int, int]] = set()

        rng = random.Random(seed)

        def check_open_area(maze: list[list[int]], width: int, height: int) \
                -> bool:
            """Check if any 3x3 block in the maze is fully open.

            Args:
                maze: The current maze state.
                width: Number of columns in the maze.
                height: Number of rows in the maze.

            Returns:
                True if a 3x3 open area exists, False otherwise.
            """

            for sx in range(width - 2):
                for sy in range(height - 2):
                    is_open = True
                    for x in range(sx, sx + 3):
                        for y in range(sy, sy + 3):
                            if x < sx + 2 and (maze[y][x] & (1 << self.E)):
                                is_open = False
                                break

                            if y < sy + 2 and (maze[y][x] & (1 << self.S)):
                                is_open = False
                                break
                        if not is_open:
                            break

                    if is_open:
                        return True
            return False

        for y in range(height):
            for x in range(width):
                if (x, y) in logo_cells:
                    continue

                if x < width - 1:
                    if (maze[y][x] & (1 << self.E) and
                            (x + 1, y) not in logo_cells):
                        possible_cells.add((x, y))
                        if rng.random() < probability:
                            maze[y][x] &= ~(1 << self.E)
                            maze[y][x + 1] &= ~(1 << self.W)
                            opened_walls += 1
                            if check_open_area(maze, width, height):
                                maze[y][x] |= (1 << self.E)
                                maze[y][x + 1] |= (1 << self.W)
                                opened_walls -= 1

                if y < height - 1:
                    if (maze[y][x] & (1 << self.S) and
                            (x, y + 1) not in logo_cells):
                        possible_cells.add((x, y))
                        if rng.random() < probability:
                            maze[y][x] &= ~(1 << self.S)
                            maze[y + 1][x] &= ~(1 << self.N)
                            opened_walls += 1
                            if check_open_area(maze, width, height):
                                maze[y][x] |= (1 << self.S)
                                maze[y + 1][x] |= (1 << self.N)
                                opened_walls -= 1

        if opened_walls == 0:
            x, y = rng.choice(list(possible_cells))
            if (maze[y][x] & (1 << self.E)):
                maze[y][x] &= ~(1 << self.E)
                maze[y][x + 1] &= ~(1 << self.W)
            else:
                maze[y][x] &= ~(1 << self.S)
                maze[y + 1][x] &= ~(1 << self.N)

        return maze

    def bfs_animate(self, maze: list[list[int]], width: int, height: int,
                    entry: tuple[int, int], exit: tuple[int, int]) \
            -> Generator[tuple[list[tuple[int, int]],
                               list[tuple[int, int]]], None, None]:
        """Animate BFS pathfinding, yielding search progress and path frames.

        Yields two phases of animation:
        - Phase 1 (search): As BFS explores the maze, yields the growing
          list of visited cells with an empty path list each step.
        - Phase 2 (reconstruction): Once the exit is found, yields the
          growing reconstructed path from exit back to entry, one cell
          at a time.

        Args:
            maze: The maze to search as a 2D grid of wall-encoded integers.
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            entry: Starting position as (x, y).
            exit: Target position as (x, y).

        Yields:
            Tuples of (searched, path) where searched is the list of all
            cells visited so far and path is the current reconstructed path.
            During phase 1, path is an empty list. During phase 2, path
            grows from exit toward entry. A final (searched, []) is yielded
            if no path exists.
        """

        queue: deque[tuple[int, int]] = deque([entry])
        searched: list[tuple[int, int]] = []
        visited: set[tuple[int, int]] = set([entry])
        parent: dict[tuple[int, int], tuple[int, int] | None] = {entry: None}

        while queue:
            cell: tuple[int, int] = queue.popleft()
            searched.append(cell)

            if (cell == exit):
                path: list[tuple[int, int]] = []
                current: tuple[int, int] | None = exit
                while current is not None:
                    path.append(current)
                    current = parent[current]
                    yield searched, path[::-1]
                return

            for dx, dy, direction, opposite in self.DIRS:
                nx: int = dx + cell[0]
                ny: int = dy + cell[1]

                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        if not (maze[cell[1]][cell[0]] & 1 << direction):
                            visited.add((nx, ny))
                            parent[(nx, ny)] = cell
                            queue.append((nx, ny))

            yield searched, []

        yield searched, []

    def bfs(self, maze: list[list[int]], width: int, height: int,
            entry: tuple[int, int], exit: tuple[int, int]) \
            -> list[tuple[int, int]]:
        """Find the shortest path between entry and exit using BFS.

        Delegates to bfs_animate and returns only the final path.

        Args:
            maze: The maze to search as a 2D grid of wall-encoded integers.
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            entry: Starting position as (x, y).
            exit: Target position as (x, y).

        Returns:
            List of (x, y) positions from entry to exit representing the
            shortest path. Returns an empty list if no path exists.
        """

        final_path: list[tuple[int, int]] = []
        for searched, path in self.bfs_animate(maze, width, height,
                                               entry, exit):
            final_path = path
        return final_path


class DFSAlgorithm(MazeAlgorithm):
    """Maze generation using iterative Depth First Search.

    Generates mazes with long winding corridors and few dead ends by
    always extending the current path before backtracking. Uses an
    explicit stack instead of recursion to avoid Python's recursion
    limit on large mazes.

    The 42 logo cells are pre-added to visited to prevent the algorithm
    from carving through them, preserving the logo pattern in the maze.
    """
    def generate(self, width: int, height: int, seed: int | None = None) \
            -> Generator[tuple[list[list[int]],
                               list[tuple[int, int]]], None, None]:
        """Generate a maze using iterative DFS, yielding each step.

        Starts at (0, 0) and carves passages by visiting unvisited
        neighbours randomly, backtracking when no unvisited neighbours
        remain. Skips cells inside the 42 logo pattern.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            seed: Random seed for reproducible generation. If None,
                  generation is non-deterministic.

        Yields:
            Tuples of (maze, stack) where maze is the current 2D grid
            and stack is the current DFS path as a list of (x, y) positions.
            The stack shrinks during backtracking and grows during exploration.
        """

        rng = random.Random(seed)

        maze: list[list[int]] = [[0xF for _ in range(width)]
                                 for _ in range(height)]

        stack: list[tuple[int, int]] = [(0, 0)]
        visited: set[tuple[int, int]] = set([(0, 0)])

        for cell in logo_42(width, height):
            visited.add(cell)

        while stack:
            x, y = stack[-1]

            neighbours: list[tuple[int, int, int, int]] = []
            for dx, dy, direction, opposite in self.DIRS:
                nx = x + dx
                ny = y + dy

                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        neighbours.append((nx, ny, direction, opposite))

            if neighbours:
                neighbour = rng.choice(neighbours)

                maze[y][x] &= ~(1 << neighbour[2])
                maze[neighbour[1]][neighbour[0]] &= ~(1 << neighbour[3])

                visited.add((neighbour[0], neighbour[1]))
                stack.append((neighbour[0], neighbour[1]))
            else:
                stack.pop()

            yield maze, stack

    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:
        """Generate and return the completed DFS maze.

        Runs the DFS generator to completion and returns the final state.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            seed: Random seed for reproducible generation. If None,
                  generation is non-deterministic.

        Returns:
            Completed maze as a 2D list of wall-encoded integers.
        """

        final_frame: list[list[int]] = []
        for maze_state, stack in self.generate(width, height, seed):
            final_frame = maze_state
        return final_frame


class PRIMSAlgorithm(MazeAlgorithm):
    """Maze generation using a randomized Prim's algorithm.

    Generates mazes with a more uniform, branchy texture compared to DFS
    by randomly selecting any cell from the frontier rather than always
    extending the current path. Produces a random spanning tree where
    every cell is reachable and there are no loops.

    The 42 logo cells are pre-added to visited to prevent the algorithm
    from carving through them, preserving the logo pattern in the maze.
    """
    def generate(self, width: int, height: int, seed: int | None = None) \
        -> Generator[tuple[list[list[int]],
                           list[tuple[int, int]]], None, None]:
        """Generate a maze using randomized Prim's algorithm, yielding each
        step.

        Starts at (0, 0) and maintains a candidate list of unvisited cells
        adjacent to the visited region. At each step, picks a random candidate,
        connects it to a random visited non-logo neighbour, then adds its
        unvisited non-logo neighbours to the candidates list.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            seed: Random seed for reproducible generation. If None,
                  generation is non-deterministic.

        Yields:
            Tuples of (maze, candidates) where maze is the current 2D grid
            and candidates is the current frontier as a list of (x, y)
            positions. The candidates list grows as new cells are discovered
            and shrinks as cells are connected to the maze.
        """
        rng = random.Random(seed)

        logo_cells: set[tuple[int, int]] = logo_42(width, height)
        maze: list[list[int]] = [[0xF for _ in range(width)]
                                 for _ in range(height)]

        visited: set[tuple[int, int]] = set([(0, 0)])
        candidates: list[tuple[int, int]] = []

        for cell in logo_42(width, height):
            visited.add(cell)

        for dx, dy, direction, opposite in self.DIRS:
            nx = dx
            ny = dy

            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    candidates.append((nx, ny))

        while candidates:
            x, y = rng.choice(candidates)

            visited_neighbours: list[tuple[int, int, int, int]] = []
            for dx, dy, direction, opposite in self.DIRS:
                nx = x + dx
                ny = y + dy

                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) in visited and (nx, ny) not in logo_cells:
                        visited_neighbours.append((nx, ny,
                                                   direction, opposite))

            if visited_neighbours:

                neighbour = rng.choice(visited_neighbours)
                maze[y][x] &= ~(1 << neighbour[2])
                maze[neighbour[1]][neighbour[0]] &= ~(1 << neighbour[3])
                visited.add((x, y))

                for dx, dy, direction, opposite in self.DIRS:
                    nnx = x + dx
                    nny = y + dy
                    if 0 <= nnx < width and 0 <= nny < height:
                        if ((nnx, nny) not in visited
                                and (nnx, nny) not in candidates
                                and (nnx, nny) not in logo_cells):
                            candidates.append((nnx, nny))

                candidates.remove((x, y))

            yield maze, candidates

    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:
        """Generate and return the completed Prim's maze.

        Runs the Prim's generator to completion and returns the final state.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            seed: Random seed for reproducible generation. If None,
                  generation is non-deterministic.

        Returns:
            Completed maze as a 2D list of wall-encoded integers.
        """

        final_frame: list[list[int]] = []
        for maze_state, stack in self.generate(width, height, seed):
            final_frame = maze_state
        return final_frame
