class MazeDrawer():
    BOLD = "\033[1;97m"
    RESET = RESET = "\033[0m"

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    def __init__(self, maze: list[list[int]], set_i: int = 1):
        self.height = len(maze)
        self.width = len(maze[0])
        self.coded = maze
        self.draw_set = self.choose_drawing_set(set_i)

    def draw_map(self, set: int = 1) -> None:
        print()
        self.print_top_container()
        self.print_mid_cells()
        self.print_last_cell()

    def print_top_container(self) -> None:
        top_row = self.draw_set["up_left_corner"]
        for x in range(self.width):
            if self.coded[0][x] & (1 << self.E):
                top_row += self.draw_set["up_w_wall"]
            else:
                top_row += self.draw_set["up_no_wall"]
        top_row = top_row[:-1] + self.draw_set["up_right_corner"]
        print(self.BOLD + top_row + self.RESET)

    def print_mid_cells(self) -> None:
        for y in range(self.height - 1):
            cells = self.draw_set["cell_left_wall"]
            for x in range(self.width - 1):
                if self.coded[y][x] & (1 << self.E) and \
                   self.coded[y][x] & (1 << self.S) and \
                   self.coded[y][x] & (1 << self.N) and \
                   self.coded[y][x] & (1 << self.W):
                    cells += self.draw_set["cell_clossed"]
                elif self.coded[y][x] & (1 << self.E):
                    cells += self.draw_set["cell_w_wall"]
                else:
                    cells += self.draw_set["cell_no_wall"]
            if self.coded[y][self.width - 1] & (1 << self.E) and \
               self.coded[y][self.width - 1] & (1 << self.S) and \
               self.coded[y][self.width - 1] & (1 << self.N) and \
               self.coded[y][self.width - 1] & (1 << self.W):
                cells += self.draw_set["cell_right_clossed"]
            elif self.coded[y][self.width - 1] & (1 << self.E):
                cells += self.draw_set["cell_right_wall"]
            else:
                cells += self.draw_set["cell_no_wall"]
            print(self.BOLD + cells + self.RESET)

            if self.coded[y][0] & (1 << self.S):
                mid_row = self.draw_set["mid_left_w_wall"]
            else:
                mid_row = self.draw_set["mid_left_no_wall"]

            for x in range(self.width - 1):
                if self.coded[y][x] & (1 << self.S):
                    if self.coded[y][x] & (1 << self.E):
                        if self.coded[y + 1][x] & (1 << self.E):
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_s_ue_de_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_s_ue_de_wall"]
                        else:
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_s_ue_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_s_ue_wall"]
                    else:
                        if self.coded[y + 1][x] & (1 << self.E):
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_s_de_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_s_de_wall"]
                        else:
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_s_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_s_wall"]
                else:
                    if self.coded[y][x] & (1 << self.E):
                        if self.coded[y + 1][x] & (1 << self.E):
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_ue_de_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_ue_de_wall"]
                        else:
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_ue_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_ue_wall"]
                    else:
                        if self.coded[y + 1][x] & (1 << self.E):
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_de_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_de_wall"]
                        else:
                            if self.coded[y][x + 1] & (1 << self.S):
                                mid_row += self.draw_set["mid_se_wall"]
                            else:
                                mid_row += self.draw_set["mid_no_wall"]
            if self.coded[y][self.width - 1] & (1 << self.S):
                mid_row += self.draw_set["mid_right_s_wall"]
            else:
                mid_row += self.draw_set["mid_right_no_wall"]
            print( self.BOLD + mid_row + self.RESET)

    def print_last_cell(self) -> None:
        bot_row = self.draw_set["bot_left_corner"]
        last_cells = self.draw_set["cell_left_wall"]

        for x in range(self.width - 1):
            if self.coded[self.height - 1][self.width - 1] & (1 << self.E) and \
               self.coded[self.height - 1][self.width - 1] & (1 << self.S) and \
               self.coded[self.height - 1][self.width - 1] & (1 << self.N) and \
               self.coded[self.height - 1][self.width - 1] & (1 << self.W):
                last_cells += self.draw_set["cell_clossed"]
            elif self.coded[self.height - 1][x] & (1 << self.E):
                last_cells += self.draw_set["cell_w_wall"]
            else:
                last_cells += self.draw_set["cell_no_wall"]
        if self.coded[self.height - 1][self.width - 1] & (1 << self.E) and \
           self.coded[self.height - 1][self.width - 1] & (1 << self.S) and \
           self.coded[self.height - 1][self.width - 1] & (1 << self.N) and \
           self.coded[self.height - 1][self.width - 1] & (1 << self.W):
            last_cells += self.draw_set["bot_right_clossed"]
        elif self.coded[self.height - 1][self.width - 1] & (1 << self.E):
            last_cells += self.draw_set["bot_right_wall"]
        else:
            last_cells += self.draw_set["bot_right_no_wall"]
        print(self.BOLD + last_cells + self.RESET)

        for x in range(self.width):
            if self.coded[self.height - 1][x] & (1 << self.E):
                bot_row += self.draw_set["bot_w_wall"]
            else:
                bot_row += self.draw_set["bot_no_wall"]
        bot_row = bot_row[:-1] + self.draw_set["bot_right_corner"]
        print(self.BOLD + bot_row + self.RESET)

    @staticmethod
    def choose_drawing_set(set: int) -> dict[str, str]:
        sets = {
            0: {
                "up_left_corner": "+",
                "up_right_corner": "+",
                "up_w_wall": "---+",
                "up_no_wall": "---+",
                "cell_left_wall": "|",
                "cell_right_wall": "   |",
                "cell_w_wall": "   |",
                "cell_no_wall": "    ",
                "cell_clossed": "███|",
                "cell_right_clossed": "███|",
                "mid_s_ue_de_se_wall": "---+",
                "mid_s_ue_de_wall": "---+",
                "mid_s_ue_se_wall": "---+",
                "mid_s_ue_wall": "---+",
                "mid_s_de_se_wall": "---+",
                "mid_s_de_wall": "---+",
                "mid_s_se_wall": "---+",
                "mid_s_wall": "---+",
                "mid_ue_de_se_wall": "   +",
                "mid_ue_de_wall": "   +",
                "mid_ue_se_wall": "   +",
                "mid_ue_wall": "   +",
                "mid_de_se_wall": "   +",
                "mid_de_wall": "   +",
                "mid_se_wall": "   +",
                "mid_no_wall": "    ",
                "mid_left_w_wall": "+",
                "mid_left_no_wall": "+",
                "mid_right_s_wall": "---+",
                "mid_right_no_wall": "   +",
                "bot_left_corner": "+",
                "bot_right_corner": "+",
                "bot_right_wall": "   |",
                "bot_right_clossed": "███|",
                "bot_right_no_wall": "   ",
                "bot_w_wall": "---+",
                "bot_no_wall": "---+",
            },
            1: {
                "up_left_corner": "┌",
                "up_right_corner": "┐",
                "up_w_wall": "───┬",
                "up_no_wall": "────",
                "cell_left_wall": "│",
                "cell_right_wall": "   │",
                "cell_w_wall": "   │",
                "cell_no_wall": "    ",
                "cell_clossed": "███│",
                "cell_right_clossed": "███│",
                "mid_s_ue_de_se_wall": "───┼",
                "mid_s_ue_de_wall": "───┤",
                "mid_s_ue_se_wall": "───┴",
                "mid_s_ue_wall": "───┘",
                "mid_s_de_se_wall": "───┬",
                "mid_s_de_wall": "───┐",
                "mid_s_se_wall": "────",
                "mid_s_wall": "───╴",
                "mid_ue_de_se_wall": "   ├",
                "mid_ue_de_wall": "   │",
                "mid_ue_se_wall": "   └",
                "mid_ue_wall": "   ╵",
                "mid_de_se_wall": "   ┌",
                "mid_de_wall": "   ╷",
                "mid_se_wall": "   ╶",
                "mid_no_wall": "    ",
                "mid_left_w_wall": "├",
                "mid_left_no_wall": "│",
                "mid_right_s_wall": "───┤",
                "mid_right_no_wall": "   │",
                "bot_left_corner": "└",
                "bot_right_corner": "┘",
                "bot_right_wall": "   │",
                "bot_right_clossed": "███│",
                "bot_right_no_wall": "   ",
                "bot_w_wall": "───┴",
                "bot_no_wall": "────",
            },
            2: {
                "up_left_corner": "╔",
                "up_right_corner": "╗",
                "up_w_wall": "═══╦",
                "up_no_wall": "════",
                "cell_left_wall": "║",
                "cell_right_wall": "   ║",
                "cell_w_wall": "   │",
                "cell_no_wall": "    ",
                "cell_clossed": "███│",
                "cell_right_clossed": "███║",
                "mid_s_ue_de_se_wall": "───┼",
                "mid_s_ue_de_wall": "───┤",
                "mid_s_ue_se_wall": "───┴",
                "mid_s_ue_wall": "───┘",
                "mid_s_de_se_wall": "───┬",
                "mid_s_de_wall": "───┐",
                "mid_s_se_wall": "────",
                "mid_s_wall": "───╴",
                "mid_ue_de_se_wall": "   ├",
                "mid_ue_de_wall": "   │",
                "mid_ue_se_wall": "   └",
                "mid_ue_wall": "   ╵",
                "mid_de_se_wall": "   ┌",
                "mid_de_wall": "   ╷",
                "mid_se_wall": "   ╶",
                "mid_no_wall": "    ",
                "mid_left_w_wall": "╠",
                "mid_left_no_wall": "║",
                "mid_right_s_wall": "───╣",
                "mid_right_no_wall": "   ║",
                "bot_left_corner": "╚",
                "bot_right_corner": "╝",
                "bot_right_wall": "   ║",
                "bot_right_clossed": "███║",
                "bot_right_no_wall": "   ",
                "bot_w_wall": "═══╩",
                "bot_no_wall": "════",
            },
            3: {
                "up_left_corner": "┏",
                "up_right_corner": "┓",
                "up_w_wall": "━━━┳",
                "up_no_wall": "━━━━",
                "cell_left_wall": "┃",
                "cell_right_wall": "   ┃",
                "cell_w_wall": "   ┃",
                "cell_no_wall": "    ",
                "cell_clossed": "███┃",
                "cell_right_clossed": "███┃",
                "mid_s_ue_de_se_wall": "━━━╋",
                "mid_s_ue_de_wall": "━━━┫",
                "mid_s_ue_se_wall": "━━━┻",
                "mid_s_ue_wall": "━━━┛",
                "mid_s_de_se_wall": "━━━┳",
                "mid_s_de_wall": "━━━┓",
                "mid_s_se_wall": "━━━━",
                "mid_s_wall": "━━━━",
                "mid_ue_de_se_wall": "   ┣",
                "mid_ue_de_wall": "   ┃",
                "mid_ue_se_wall": "   ┗",
                "mid_ue_wall": "   ┃",
                "mid_de_se_wall": "   ┏",
                "mid_de_wall": "   ┃",
                "mid_se_wall": "    ",
                "mid_no_wall": "    ",
                "mid_left_w_wall": "┣",
                "mid_left_no_wall": "┃",
                "mid_right_s_wall": "━━━┫",
                "mid_right_no_wall": "   ┃",
                "bot_left_corner": "┗",
                "bot_right_corner": "┛",
                "bot_right_wall": "   ┃",
                "bot_right_clossed": "███┃",
                "bot_right_no_wall": "   ",
                "bot_w_wall": "━━━┻",
                "bot_no_wall": "━━━━",

            }
        }

        return sets[set]
