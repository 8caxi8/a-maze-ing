from abc import ABC, abstractmethod
from typing import Generator
import random


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
            -> Generator[tuple[list[list[int]], list[tuple[int, int]]], None, None]:
        pass

    @abstractmethod
    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:
        pass

    def make_imperfect(self, maze: list[list[int]], probability: float = 0.05,
                       seed: int | None = None) -> list[list[int]]:

        width: int = len(maze[0])
        height: int = len(maze)

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


class DFSAlgorithm(MazeAlgorithm):
    def generate(self, width: int, height: int, seed: int | None = None) \
        -> Generator[
            tuple[list[list[int]], list[tuple[int, int]]], None, None]:

        rng = random.Random(seed)

        maze: list[list[int]] = [[0xF for _ in range(width)]
                                 for _ in range(height)]

        stack: list[tuple[int, int]] = [(0, 0)]
        visited: set[tuple[int, int]] = set([(0, 0)])

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

            yield (maze, stack)

    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:

        final_frame: list[list[int]] = []
        for maze_state, stack in self.generate(width, height, seed):
            final_frame = maze_state
        return final_frame
