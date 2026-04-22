from typing import Generator
from .maze_algorithms import MazeAlgorithm, DFSAlgorithm


class MazeGeneratorError(Exception):
    pass


class MazeGenerator:

    available_algos: dict[str, type[MazeAlgorithm]] = {
        "DFS": DFSAlgorithm,
        }

    def __init__(self, width: int, height: int, seed: int | None = None,
                 strategy: str = "DFS") -> None:
        self.set_algorithm(strategy)
        self.set_maze_dimensions(width, height)
        self._seed = seed
        self.maze: list[list[int]] = self.generate_maze()

    def set_maze_dimensions(self, width: int, height: int) -> None:
        try:
            if int(width) < 1 or int(height) < 1:
                raise ValueError("Expected maze dimensions to be higher" 
                                 f" than 1, got ({width}, {height})")
        except ValueError as e:
            raise MazeGeneratorError(e)
        self._width = width
        self._height = height

    def set_algorithm(self, strategy: str) -> None:
        availables = ("\n   - ").join(self.available_algos.keys())
        try:
            self._strategy: MazeAlgorithm = self.available_algos[strategy]()
        except KeyError:
            raise MazeGeneratorError(f"Strategy '{strategy}' not found. "
                                     "Available Strategies are:\n   - "
                                     f"{availables}")

    def generate_maze(self) -> list[list[int]]:
        return self._strategy.final_maze(self._width, self._height, self._seed)

    def generate_frame(self) -> Generator[list[list[int]], None, None]:
        return self._strategy.generate(self._width, self._height, self._seed)

    def make_imperfect(self, probability: float = 0.05) -> list[list[int]]:
        return self._strategy.make_imperfect(self.maze, probability,
                                             self._seed)

    def print_encoded_maze(self) -> None:
        for row in self.maze:
            for cell in row:
                print(format(cell, 'X'), end="")
            print()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
