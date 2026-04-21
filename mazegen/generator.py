from typing import Generator
from .maze_algorithms import MazeAlgorithm, DFSAlgorithm


class MazeGenerator:
    def __init__(self, strategy: MazeAlgorithm = DFSAlgorithm()) -> None:
        self._strategy: MazeAlgorithm = strategy

    def set_algorithm(self, strategy: MazeAlgorithm) -> None:
        self._strategy = strategy

    def generate_maze(self, width: int, height: int, seed: int | None = None) \
            -> list[list[int]]:
        return self._strategy.final_maze(width, height, seed)

    def generate_frame(self, width: int, height: int,
                       seed: int | None = None) \
            -> Generator[list[list[int]], None, None]:
        return self._strategy.generate(width, height, seed)

    def make_imperfect(self, maze: list[list[int]], width: int, height: int,
                       probability: float = 0.05, seed: int | None = None) \
            -> list[list[int]]:
        return self._strategy.make_imperfect(maze, width, height,
                                             probability, seed)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
