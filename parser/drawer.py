# def draw_map(map: list[list[int]]) -> None:
#     mapping_tiles: dict[int, tuple[str, str]] = {
#         0: ("   ", "   "),
#         1: ("───", "   "),
#         2: ("  │", "  │"),
#         3: ("──┐", "  │"),
#         4: ("   ", "───"),
#         5: ("───", "───"),
#         6: ("  │", "──┘"),
#         7: ("──┐", "──┘"),
#         8: ("│  ", "│  "),
#         9: ("┌──", "│  "),
#         10: ("│ │", "│ │"),
#         11: ("┌─┐", "│ │"),
#         12: ("│  ", "│__"),
#         13: ("┌──", "└──"),
#         14: ("│ │", "└─┘"),
#         15: ("┌─┐", "└─┘"),
#     }

#     print("\n"*2)
#     for row in map:
#         line1: str = ""
#         line2: str = ""
#         for cell in row:
#             line1 += mapping_tiles[cell][0]
#             line2 += mapping_tiles[cell][1]
#         print(" "*20, end="")
#         print(line1)
#         print(" "*20, end="")
#         print(line2)
#     print("\n"*2)


def draw_map(grid: list[list[int]]) -> None:
    chars = {
        0b0000: " ",
        0b0001: "╵",
        0b0010: "╶",
        0b0011: "└",
        0b0100: "╷",
        0b0101: "│",
        0b0110: "┌",
        0b0111: "├",
        0b1000: "╴",
        0b1001: "┘",
        0b1010: "─",
        0b1011: "┴",
        0b1100: "┐",
        0b1101: "┤",
        0b1110: "┬",
        0b1111: "┼",
    }

    h = len(grid)
    w = len(grid[0])

    # output grid (2x resolution + borders)
    out_h = h * 2 + 1
    out_w = w * 2 + 1

    canvas = [[0 for _ in range(out_w)] for _ in range(out_h)]

    def add_wall(y: int, x: int, direction: int) -> None:
        canvas[y][x] |= direction

    for y in range(h):
        for x in range(w):
            cell = grid[y][x]

            cy = y * 2 + 1
            cx = x * 2 + 1

            # if NO opening → wall exists
            if not (cell & 1):  # up
                add_wall(cy - 1, cx, 4)
                add_wall(cy, cx, 1)

            if not (cell & 2):  # right
                add_wall(cy, cx + 1, 8)
                add_wall(cy, cx, 2)

            if not (cell & 4):  # down
                add_wall(cy + 1, cx, 1)
                add_wall(cy, cx, 4)

            if not (cell & 8):  # left
                add_wall(cy, cx - 1, 2)
                add_wall(cy, cx, 8)

    # draw
    for row in canvas:
        print("".join(chars[cell] for cell in row))
