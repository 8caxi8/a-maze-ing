from abc import ABC, abstractmethod
from typing import Generator
import random
from collections import deque


def logo_42(width: int, height: int) -> set[tuple[int, int]]:
    logo_cells: set[tuple[int, int]] = set()

    if width < 9 or height < 7:
        print("Error: Maze dimensions are too small."
              " 42 Pattern will be omitted")
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
        pass

    @abstractmethod
    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:
        pass

    def make_imperfect_frames(self, maze: list[list[int]],
                              probability: float = 0.05,
                              seed: int | None = None) \
            -> Generator[tuple[tuple[int, int], list[list[int]]], None, None]:

        width: int = len(maze[0])
        height: int = len(maze)
        logo_cells: set[tuple[int, int]] = logo_42(width, height)

        rng = random.Random(seed)

        def check_open_area(maze: list[list[int]], width: int, height: int) \
                -> bool:

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

                if x < width - 1 and rng.random() < probability:
                    if maze[y][x] & (1 << self.E):
                        maze[y][x] &= ~(1 << self.E)
                        maze[y][x + 1] &= ~(1 << self.W)
                        if check_open_area(maze, width, height):
                            maze[y][x] |= (1 << self.E)
                            maze[y][x + 1] |= (1 << self.W)

                if y < height - 1 and rng.random() < probability:
                    if maze[y][x] & (1 << self.S):
                        maze[y][x] &= ~(1 << self.S)
                        maze[y + 1][x] &= ~(1 << self.N)
                        if check_open_area(maze, width, height):
                            maze[y][x] |= (1 << self.S)
                            maze[y + 1][x] |= (1 << self.N)

                yield (x, y), maze

    def make_imperfect(self, maze: list[list[int]], probability: float = 0.05,
                       seed: int | None = None) -> list[list[int]]:

        width: int = len(maze[0])
        height: int = len(maze)
        logo_cells: set[tuple[int, int]] = logo_42(width, height)

        rng = random.Random(seed)

        def check_open_area(maze: list[list[int]], width: int, height: int) \
                -> bool:

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

                if x < width - 1 and rng.random() < probability:
                    if maze[y][x] & (1 << self.E):
                        maze[y][x] &= ~(1 << self.E)
                        maze[y][x + 1] &= ~(1 << self.W)
                        if check_open_area(maze, width, height):
                            maze[y][x] |= (1 << self.E)
                            maze[y][x + 1] |= (1 << self.W)

                if y < height - 1 and rng.random() < probability:
                    if maze[y][x] & (1 << self.S):
                        maze[y][x] &= ~(1 << self.S)
                        maze[y + 1][x] &= ~(1 << self.N)
                        if check_open_area(maze, width, height):
                            maze[y][x] |= (1 << self.S)
                            maze[y + 1][x] |= (1 << self.N)

        return maze

    def bfs_animate(self, maze: list[list[int]], width: int, height: int,
                    entry: tuple[int, int], exit: tuple[int, int]) \
            -> Generator[tuple[list[tuple[int, int]],
                               list[tuple[int, int]]], None, None]:

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

        final_path: list[tuple[int, int]] = []
        for searched, path in self.bfs_animate(maze, width, height,
                                               entry, exit):
            final_path = path
        return final_path


class DFSAlgorithm(MazeAlgorithm):
    def generate(self, width: int, height: int, seed: int | None = None) \
            -> Generator[tuple[list[list[int]],
                               list[tuple[int, int]]], None, None]:

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

        final_frame: list[list[int]] = []
        for maze_state, stack in self.generate(width, height, seed):
            final_frame = maze_state
        return final_frame
