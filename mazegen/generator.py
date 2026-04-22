from typing import Generator
from .maze_algorithms import MazeAlgorithm, DFSAlgorithm
from .maze_algorithms import logo_42


class MazeGeneratorError(Exception):
    pass


class MazeGenerator:

    available_algos: dict[str, type[MazeAlgorithm]] = {
        "DFS": DFSAlgorithm,
        }

    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int], seed: int | None = None,
                 strategy: str = "DFS") -> None:
        self.set_algorithm(strategy)
        self.set_maze_dimensions(width, height)
        self.set_entry_exit_positions(entry, exit)
        if not isinstance(seed, int | None):
            raise MazeGeneratorError("Seed must be an integer")
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

    def set_entry_exit_positions(self, entry: tuple[int, int],
                                 exit: tuple[int, int]) -> None:
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

        self._entry = entry
        self._exit = exit

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

    def generate_frame(self) -> Generator[tuple[list[list[int]],
                                          list[tuple[int, int]]], None, None]:
        return self._strategy.generate(self._width, self._height, self._seed)

    def make_imperfect(self, probability: float = 0.05) -> None:
        if not isinstance(probability, (int, float)):
            raise MazeGeneratorError("Expected probability to be of"
                                     " type float")
        if not (0 <= probability <= 1):
            raise MazeGeneratorError("Probability must be between 0 and 1")

        self.maze = self._strategy.make_imperfect(self.maze, probability,
                                                  self._seed)

    def make_imperfect_frames(self, probability: float = 0.05) \
            -> Generator[list[list[int]], None, None]:
        if not isinstance(probability, (int, float)):
            raise MazeGeneratorError("Expected probability to be of"
                                     " type float")
        if not (0 <= probability <= 1):
            raise MazeGeneratorError("Probability must be between 0 and 1")
        return self._strategy.make_imperfect_frames(self.maze, probability,
                                                    self._seed)

    def find_shortest_path(self) -> list[tuple[int, int]]:
        return self._strategy.bfs(self.maze, self._width, self._height,
                                  self._entry, self._exit)

    def rev_path_frames(self) -> Generator[tuple[tuple[int, int] | None,
                                           list[tuple[int, int]]], None, None]:

        return self._strategy.bfs_animate(self.maze, self._width, self._height,
                                          self._entry, self._exit)

    def print_encoded_maze(self) -> None:
        for row in self.maze:
            for cell in row:
                print(format(cell, 'X'), end="")
            print()

    def get_path_directions(self) -> str:
        path: list[tuple[int, int]] = self.find_shortest_path()
        path_directions: list[str] = []

        if path:
            for i in range(len(path) - 1):
                if path[i + 1][0] - path[i][0] == 1:
                    path_directions.append("E")
                elif path[i + 1][0] - path[i][0] == -1:
                    path_directions.append("W")
                elif path[i + 1][1] - path[i][1] == 1:
                    path_directions.append("S")
                elif path[i + 1][1] - path[i][1] == -1:
                    path_directions.append("N")

        result: str = "".join(path_directions)
        return result

    def write_to_file(self, filename: str) -> None:
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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
