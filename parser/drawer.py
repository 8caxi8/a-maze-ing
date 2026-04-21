def draw_map(maze: list[list[int]], width: int, height: int) -> None:
    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    # Draw top border
    print("+" + ("---+") * width)

    for y in range(height):
        # Draw west wall and cell
        row = "|"
        for x in range(width):
            # East wall
            if maze[y][x] & (1 << E):
                row += "   |"
            else:
                row += "    "
        print(row)

        # Draw south walls
        bottom = "+"
        for x in range(width):
            if maze[y][x] & (1 << S):
                bottom += "---+"
            else:
                bottom += "   +"
        print(bottom)
