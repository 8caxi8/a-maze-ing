from pydantic import BaseModel, Field, model_validator, field_validator
from pydantic_core import PydanticCustomError as Pe
from enum import Enum


class Keywords(str, Enum):
    """
    Enumeration of all supported configuration keys.

    These values represent the accepted keys that can appear
    in the maze configuration file. They are used to validate
    input and ensure only supported parameters are provided.
    """
    WIDTH = "WIDTH"
    HEIGHT = "HEIGHT"
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    OUTPUT_FILE = "OUTPUT_FILE"
    PERFECT = "PERFECT"
    SEED = "SEED"
    ALGORITHM = "ALGORITHM"


class MapConfig(BaseModel):
    """
    Validated configuration model for maze generation.

    This model stores all parameters required to generate a maze
    and applies validation rules using Pydantic.

    Attributes:
        width (int):
            Width of the maze. Must be greater than or equal to 1.

        height (int):
            Height of the maze. Must be greater than or equal to 1.

        entry (tuple[int, int]):
            Starting coordinate of the maze in ``(x, y)`` format.

        exit (tuple[int, int]):
            Ending coordinate of the maze in ``(x, y)`` format.

        output_file (str):
            Name of the file where the maze will be saved.
            Defaults to ``"maze.txt"``.

        perfect (bool):
            Whether the maze should be a perfect maze
            (only one unique path between any two points).
            Defaults to ``True``.

        seed (int | None):
            Optional random seed for reproducible generation.
            Defaults to ``None``.

        algorithm (str):
            Maze generation algorithm to use.
            Defaults to ``"dfs"``.
    """
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = "maze.txt"
    perfect: bool = True
    seed: int | None = None
    algorithm: str = "dfs"

    @model_validator(mode="after")
    def validate_entry_exit(self) -> "MapConfig":
        """
        Validate that entry and exit coordinates are inside bounds
        and are not the same point.

        Ensures that both ``entry`` and ``exit`` coordinates are
        within the maze dimensions and that they do not overlap.

        Returns:
            MapConfig:
                The validated model instance.

        Raises:
            PydanticCustomError:
                If the entry or exit point is outside maze bounds,
                or if both points are identical.
        """
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        if (entry_x < 0 or entry_x > self.width - 1) or \
           (entry_y < 0 or entry_y > self.height - 1):
            raise Pe("entry_point_error",
                     "Entry point must be a value "
                     "betweem (0,0) and (width, height)!")

        if (exit_x < 0 or exit_x > self.width - 1) or \
           (exit_y < 0 or exit_y > self.height - 1):
            raise Pe("exit_point_error",
                     "Exit point must be a value "
                     "betweem (0,0) and (width, height)!")

        if self.entry == self.exit:
            raise Pe("entry_exit_point_error",
                     "Exit point must be a value "
                     "difernt then the Entry point!")

        return self

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, point: str | tuple[int, int])\
            -> tuple[int, int]:
        """
        Parse coordinate input into a tuple of integers.

        Accepts either an already-formed tuple ``(x, y)``
        or a string in the format ``"x,y"``.

        Args:
            point (str | tuple[int, int]):
                Coordinate value to validate and convert.

        Returns:
            tuple[int, int]:
                Parsed coordinate as a tuple of integers.

        Raises:
            ValueError:
                If the coordinate is not in valid ``"x,y"`` format.
        """
        if isinstance(point, tuple):
            return point

        try:
            x, y = point.strip().split(",")
            return int(x), int(y)

        except ValueError:
            raise ValueError("Coordinate must be in 'x,y' format")
