from pydantic import BaseModel, Field, model_validator, field_validator
from pydantic_core import PydanticCustomError as Pe
from enum import Enum


class Keywords(str, Enum):
    WIDTH = "WIDTH"
    HEIGHT = "HEIGHT"
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    OUTPUT_FILE = "OUTPUT_FILE"
    PERFECT = "PERFECT"
    SEED = "SEED"
    ALGORITHM = "ALGORITHM"


class MapConfig(BaseModel):
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = "dfs"

    @model_validator(mode="after")
    def validate_entry_exit(self) -> "MapConfig":
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
        if isinstance(point, tuple):
            return point

        try:
            x, y = point.strip().split(",")
            return int(x), int(y)

        except ValueError:
            raise ValueError("Coordinate must be in 'x,y' format")
