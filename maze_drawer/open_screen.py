from typing import Generator
import random
import math


def open_gen() -> Generator[list[list[int]], None, None]:
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
    height: int = len(logo)
    width: int = len(logo[0])
    positions: list[tuple[int, int]] = []

    for y in range(height):
        for x in range(width):
            if logo[y][x] == 15:
                positions.append((x, y))

    return positions


def regenerate_logo(logo_structure: list[list[int]]) -> list[list[int]]:
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
    x: float = 0.1
    while True:
        yield 1 / math.exp(x)
        x += 0.2


def project_name(color_set: dict[str, str])\
        -> list[str]:
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
