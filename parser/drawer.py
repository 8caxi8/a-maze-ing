def draw_map(map: list[list[int]]) -> None:
    mapping_tiles: dict[int, tuple[str, str]] = {
        0: ("   ", "   "),
        1: ("───", "   "),
        2: ("  │", "  │"),
        3: ("──┐", "  |"),
        4: ("   ", "───"),
        5: ("───", "───"),
        6: ("  |", "──┘"),
        7: ("──┐", "──┘"),
        8: ("|  ", "|  "),
        9: ("┌──", "|  "),
        10: ("| |", "| |"),
        11: ("┌─┐", "| |"),
        12: ("|  ", "└──"),
        13: ("┌──", "└──"),
        14: ("| |", "└─┘"),
        15: ("┌─┐", "└─┘"),
    }

    for row in map:
        line1: str = ""
        line2: str = ""
        for cell in row:
            line1 += mapping_tiles[cell][0]
            line2 += mapping_tiles[cell][1]
        print(line1)
        print(line2)
