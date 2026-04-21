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
            -> Generator[list[list[int]], None, None]:
        pass

    @abstractmethod
    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:
        pass


class DFSAlgorithm(MazeAlgorithm):
    def generate(self, width: int, height: int, seed: int | None = None) \
            -> Generator[list[list[int]], None, None]:

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

            yield maze

    def final_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:

        final_frame: list[list[int]] = []
        for maze_state in self.generate(width, height, seed):
            final_frame = maze_state
        return final_frame
