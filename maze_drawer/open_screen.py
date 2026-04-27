from typing import Generator
import random
import math


def open_gen() -> Generator[list[list[int]], None, None]:
    """
    Generate progressive animation frames for the project logo.

    Starts with an empty 7x9 logo structure and gradually reveals
    the cells that form the final logo by randomly selecting valid
    positions from the predefined ``LOGO`` template.

    Each yielded frame is regenerated so surrounding wall/path
    connections are updated correctly.

    Yields:
        list[list[int]]:
            A 2D matrix representing the current logo frame,
            where each integer encodes wall/path directions.
    """
    LOGO: list[list[int]] = [
        [0,  4,  0,  0,  0,  4,  4,  4,  0],
        [2, 15,  8,  0,  2, 15, 15, 15,  8],
        [2, 15, 12,  4,  0,  5,  7, 15,  8],
        [2, 15, 15, 15, 10, 15, 15, 15,  8],
        [0,  1,  5, 15, 10, 15, 13,  5,  0],
        [0,  0,  2, 15, 10, 15, 15, 15,  8],
        [0,  0,  0,  1,  0,  1,  1,  1,  0],
    ]
    logo_structure: list[list[int]] = [[0 for _ in range(9)] for _ in range(7)]

    positions: list[tuple[int, int]] = get_positions(LOGO)

    while positions:
        x, y = random.choice(positions)
        positions.remove((x, y))

        logo_structure[y][x] = 15

        yield regenerate_logo(logo_structure)


def get_positions(logo: list[list[int]]) -> list[tuple[int, int]]:
    """
    Extract all positions marked as active cells (value 15).

    Scans a 2D logo matrix and returns the coordinates of every
    cell whose value is ``15``.

    Args:
        logo (list[list[int]]):
            A 2D matrix representing the logo structure.

    Returns:
        list[tuple[int, int]]:
            A list of ``(x, y)`` coordinates where the cell value is 15.
    """
    height: int = len(logo)
    width: int = len(logo[0])
    positions: list[tuple[int, int]] = []

    for y in range(height):
        for x in range(width):
            if logo[y][x] == 15:
                positions.append((x, y))

    return positions


def regenerate_logo(logo_structure: list[list[int]]) -> list[list[int]]:
    """
    Recalculate wall/path connections for the current logo frame.

    Resets all non-active cells and rebuilds directional wall values
    around cells marked as ``15``. Bitwise flags are used to represent
    directional connections:

    - North
    - East
    - South
    - West

    Args:
        logo_structure (list[list[int]]):
            Current 2D logo matrix.

    Returns:
        list[list[int]]:
            Updated logo matrix with regenerated directional values.
    """
    N, E, S, W = 0, 1, 2, 3
    height: int = len(logo_structure)
    width: int = len(logo_structure[0])

    for y in range(len(logo_structure)):
        for x in range(len(logo_structure[0])):
            if logo_structure[y][x] != 15:
                logo_structure[y][x] = 0

    for y in range(height):
        for x in range(width):
            if logo_structure[y][x] == 15:
                if y - 1 >= 0 and logo_structure[y-1][x] != 15:
                    logo_structure[y-1][x] |= (1 << S)

                if (y + 1 < len(logo_structure) and
                   logo_structure[y+1][x] != 15):
                    logo_structure[y+1][x] |= (1 << N)

                if x - 1 >= 0 and logo_structure[y][x-1] != 15:
                    logo_structure[y][x-1] |= (1 << E)

                if (x + 1 < len(logo_structure[0]) and
                   logo_structure[y][x+1] != 15):
                    logo_structure[y][x+1] |= (1 << W)

    return logo_structure


def exp() -> Generator[float, None, None]:
    """
    Generate exponentially decreasing values.

    Starts from ``x = 0.1`` and continuously yields:

    ``1 / exp(x)``

    while increasing ``x`` by ``0.2`` each iteration.

    Useful for smooth animation timing or delay scaling.

    Yields:
        float:
            The next exponential decay value.
    """
    x: float = 0.1
    while True:
        yield 1 / math.exp(x)
        x += 0.2


def project_name(color_set: dict[str, str])\
        -> list[str]:
    """
    Build the colored ASCII-art project title.

    Uses ANSI color escape codes provided in ``color_set`` to
    render the stylized project name with terminal colors.

    Expected color keys include:

    - ``last_pos``
    - ``closed``
    - ``wall``
    - ``path``

    Missing keys default to empty strings.

    Args:
        color_set (dict[str, str]):
            Dictionary containing ANSI color codes.

    Returns:
        list[str]:
            A list of strings representing the colored ASCII-art title.
    """
    c1 = color_set.get("last_pos", "")
    c2 = color_set.get("closed", "")
    c3 = color_set.get("wall", "")
    c4 = color_set.get("path", "")
    R = "\033[0m"

    l1 = (c1 + r"""            _    """ + R + c2 +
          r"""     """ + R + c3 +
          r"""  __  __      """ + R + c4 +
          r"""               ___                """ + R)

    l2 = (c1 + r"""           / \   """ + R + c2 +
          r"""     """ + R + c3 +
          r""" |  \/  | __ _ _______  """ + R + c2 +
          r"""    """ + R + c4 +
          r"""|_ _|_ __   __ _    """ + R)

    l3 = (c1 + r"""          / _ \  """ + R + c2 +
          r"""_____""" + R + c3 +
          r""" | |\/| |/ _` |_  / _ \ """ + R + c2 +
          r"""_____""" + R + c4 +
          r"""| || '_ \ / _` |   """ + R)

    l4 = (c1 + r"""         / ___ \ """ + R + c2 +
          r"""_____""" + R + c3 +
          r""" | |  | | (_| |/ /  __/ """ + R + c2 +
          r"""_____""" + R + c4 + r"""| || | | | (_| |   """ + R)

    l5 = (c1 + r"""        /_/   \_\ """ + R + c2 +
          r"""    """ + R + c3 +
          r""" |_|  |_|\__,_/___\___| """ + R + c2 +
          r"""    """ + R + c4 +
          r"""|___|_| |_|\__, |   """ + R)

    l6 = (c4 +
          r"""                             """ +
          r"""                     |______________/    """ + R)

    return [l1, l2, l3, l4, l5, l6]
