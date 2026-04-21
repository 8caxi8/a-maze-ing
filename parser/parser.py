import sys
from map_model import Keywords, MapConfig
from drawer import draw_map
from pydantic import ValidationError


class ParserError(Exception):
    pass


def import_config(path: str) -> MapConfig:
    config_values: dict[str, str] = {}

    try:
        with open(path) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue

                values = line.split("=")
                if len(values) != 2:
                    raise ParserError("Configuration file must containt one "
                                      f"'KEY=VALUE' per line: {line}")
                try:
                    Keywords(values[0])
                    if values[0].lower() in config_values.keys():
                        raise ParserError(f"KEY '{values[0]}' can't be "
                                          f"{config_values[values[0].lower()]}"
                                          f" and {values[1]}")
                except ValueError:
                    available = '\n    - '.join(value.value
                                                for value in Keywords)
                    raise ParserError(f"KEY '{values[0]}' not aceptable, "
                                      "available keys are: "
                                      f"\n    - {available}")
                config_values[values[0].lower()] = values[1].strip()
            try:
                parser_config = MapConfig.model_validate(config_values)
            except ValidationError as e:
                errors = '\n    - '.join(error['msg']
                                         for error in e.errors())
                raise ParserError("Configuration failed: "
                                  f"\n    - {errors}")
    except FileNotFoundError:
        raise ParserError(f"File with path {path} was not found")

    return parser_config


def parser() -> MapConfig:
    args = sys.argv[1:]

    if len(args) < 1:
        raise ParserError("Program must run with: "
                          "'python3 a_maze_ing.py <config_file>.txt'")

    return import_config(args[0])


def main() -> None:
    try:
        map: MapConfig = parser()
        draw_map()
    except ParserError as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
