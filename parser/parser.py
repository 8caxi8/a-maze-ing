import sys
from .map_model import Keywords, MapConfig
from pydantic import ValidationError


class ParserError(Exception):
    pass


def import_config(path: str) -> MapConfig:
    """
    Load and validate a maze configuration file.

    Reads a configuration file containing ``KEY=VALUE`` pairs, validates
    that all keys are allowed, ensures no duplicate or missing mandatory
    parameters exist, and converts the values into a validated
    ``MapConfig`` instance using Pydantic.

    Supported keys are defined by the ``Keywords`` enum, and required
    parameters are:

    - width
    - height
    - entry
    - exit
    - output_file
    - perfect

    Args:
        path (str):
            Path to the configuration file.

    Returns:
        MapConfig:
            A validated configuration object.

    Raises:
        ParserError:
            If the file is missing, contains invalid formatting,
            duplicate keys, unsupported keys, missing required keys,
            or values that fail validation.
    """
    config_values: dict[str, str] = {}
    mandatory_params: set[str] = {
        "width",
        "height",
        "entry",
        "exit",
        "output_file",
        "perfect"
    }

    try:
        with open(path) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue

                values = line.split("=", 1)
                if len(values) != 2:
                    raise ParserError("Configuration file must containt one "
                                      f"'KEY=VALUE' per line: {line}")
                try:
                    Keywords(values[0])
                    if values[0].lower() in config_values.keys():
                        raise ParserError(f"Duplicate Key '{values[0]}' "
                                          "found in 'config.txt'")
                except ValueError:
                    available = '\n    - '.join(value.value
                                                for value in Keywords)
                    raise ParserError(f"KEY '{values[0]}' not aceptable, "
                                      "available keys are: "
                                      f"\n    - {available}")
                config_values[values[0].lower()] = values[1].strip()

            missing = [entry for entry in mandatory_params
                       if entry not in set(config_values)]
            if missing:
                raise ParserError(f"Missing keys in 'config.txt': {missing}")

            try:
                parser_config: MapConfig = \
                    MapConfig.model_validate(config_values)
            except ValidationError as e:
                errors = '\n    - '.join(error['msg']
                                         for error in e.errors())
                raise ParserError("Configuration failed: "
                                  f"\n    - {errors}")
    except FileNotFoundError:
        raise ParserError(f"File with path {path} was not found")

    return parser_config


def parser() -> MapConfig:
    """
    Parse command-line arguments and load the configuration file.

    Expects the program to be executed with a configuration file path
    as the first argument:

    ``python3 a_maze_ing.py <config_file>.txt``

    Returns:
        MapConfig:
            A validated configuration object loaded from the given file.

    Raises:
        ParserError:
            If no configuration file path is provided.
    """
    args = sys.argv[1:]

    if len(args) < 1:
        raise ParserError("Program must run with: "
                          "'python3 a_maze_ing.py <config_file>.txt'")

    return import_config(args[0])
