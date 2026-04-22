import sys
import tty
import termios
import time
from mazegen import MazeGenerator


class MazeDrawer():
    BOLD = "\033[1;97m"
    RESET = RESET = "\033[0m"

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    def __init__(self, gen: MazeGenerator, style_param: int = 3, color_param: int = 0):
        self.generator = gen
        self.coded: list[list[int]] = gen.maze
        self.path: list[tuple[int, int]] = []
        self.solution: list[tuple[int, int]] = []
        self.height = len(self.coded)
        self.width = len(self.coded[0])
        self.style_param = style_param
        self.color_param = color_param
        self.define_params()

        self.MAX_COLORS = 3
        self.MAX_STYLES = 4

    def start_engine(self) -> None:
        generate_maze = False
        frame = None
        print("\033[2J\033[H", end="")

        while True:
            print("\033[H", end="")
            key = None
            if generate_maze and frame:
                try:
                    self.coded, self.path = next(frame)
                except StopIteration:
                    frame = None
                    generate_maze = False
            self.draw_map()
            self.draw_commands()

            if not generate_maze:
                key = self.getch()

            if key == "c":
                if self.color_param + 1 < self.MAX_COLORS:
                    self.color_param += 1
                else:
                    self.color_param = 0
                self.define_params()
            if key == "p":
                if not self.solution:
                    temp_solution = self.generator.find_shortest_path()
                    self.solution.append(temp_solution[0])
                    self.solution.append(temp_solution[-1])
                elif len(self.solution) == 2:
                    self.solution = []
                else:
                    temp_solution = self.solution
                    self.solution = []
                    self.solution.append(temp_solution[0])
                    self.solution.append(temp_solution[-1])
            if key == "s":
                if self.style_param + 1 < self.MAX_STYLES:
                    self.style_param += 1
                else:
                    self.style_param = 0
                self.define_params()
            if key == "g":
                if self.solution:
                    self.solution = []
                frame = self.generator.generate_frame()
                generate_maze = True
            if key == "i":
                self.generator.make_imperfect()
                self.coded = self.generator.maze
            if key == "f":
                if not self.solution:
                    self.solution = self.generator.find_shortest_path()
                elif len(self.solution) == 2:
                    self.solution = self.generator.find_shortest_path()
                else:
                    self.solution = []
            if key == "q":
                break
            time.sleep(0.005)

    def draw_commands(self) -> None:
        print(" "*9, end="")
        line = self.draw_set["up_left_corner"] +\
            self.draw_set["up_no_wall"] * (self.width + 6) +\
            self.draw_set["up_right_corner"]
        print(line)
        print(" "*10, end="")
        print("c -> Change Color    |    s -> Change Style   |   q -> quit")
        print(" "*9, end="")
        line = self.draw_set["bot_left_corner"] +\
            self.draw_set["up_no_wall"] * (self.width + 6) +\
            self.draw_set["bot_right_corner"]
        print(line)
        print()

    def draw_map(self) -> None:
        print("\n"*2)
        print()
        self.print_top_container()
        self.print_mid_cells()
        self.print_last_cell()
        print()

    def print_top_container(self) -> None:
        top_row = self.draw_set["up_left_corner"]
        for x in range(self.width):
            if self.coded[0][x] & (1 << self.E):
                top_row += self.draw_set["up_w_wall"]
            else:
                top_row += self.draw_set["up_no_wall"]
        top_row = top_row[:-1] + self.draw_set["up_right_corner"]
        print(" "*20, end="")
        print(self.BOLD + self.colors["wall"] + top_row + self.RESET)

    def print_mid_cells(self) -> None:
        assert self.solution is not None
        for y in range(self.height - 1):
            cells = self.draw_set["cell_left_wall"]
            for x in range(self.width - 1):
                if (x, y) in self.path:
                    if (x, y) == self.path[-1]:
                        cells += self.colors["last_pos"] +\
                            self.draw_set["cell_clossed"] +\
                            self.RESET + self.BOLD +\
                            self.colors["wall"]
                        end = self.draw_set["cell_w_wall"].strip()\
                            if self.coded[y][x] & (1 << self.E) else " "
                        cells += end
                    else:
                        cells += self.colors["path"] +\
                            self.draw_set["cell_clossed"] +\
                            self.RESET + self.BOLD +\
                            self.colors["wall"]
                        end = self.draw_set["cell_w_wall"].strip()\
                            if self.coded[y][x] & (1 << self.E) else " "
                        cells += end
                elif (x, y) in self.solution:
                    if (x, y) == self.solution[-1]:
                        cells += self.colors["exit_pos"] +\
                            self.draw_set["cell_path"] +\
                            self.RESET + self.BOLD +\
                            self.colors["wall"]
                        end = self.draw_set["cell_w_wall"].strip()\
                            if self.coded[y][x] & (1 << self.E) else " "
                        cells += end
                    elif (x, y) == self.solution[0]:
                        cells += self.colors["entry_pos"] +\
                            self.draw_set["cell_path"] +\
                            self.RESET + self.BOLD +\
                            self.colors["wall"]
                        end = self.draw_set["cell_w_wall"].strip()\
                            if self.coded[y][x] & (1 << self.E) else " "
                        cells += end
                    else:
                        cells += self.colors["path"] +\
                            self.draw_set["cell_path"] +\
                            self.RESET + self.BOLD +\
                            self.colors["wall"]
                        end = self.draw_set["cell_w_wall"].strip()\
                            if self.coded[y][x] & (1 << self.E) else " "
                        cells += end
                elif self.coded[y][x] & (1 << self.E) and \
                   self.coded[y][x] & (1 << self.S) and \
                   self.coded[y][x] & (1 << self.N) and \
                   self.coded[y][x] & (1 << self.W):
                    cells += self.colors["closed"] +\
                     self.draw_set["cell_clossed"] +\
                     self.RESET + self.BOLD +\
                     self.colors["wall"] + self.draw_set["cell_w_wall"].strip()
                elif self.coded[y][x] & (1 << self.E):
                    cells += self.draw_set["cell_w_wall"]
                else:
                    cells += self.draw_set["cell_no_wall"]
            if (self.width - 1, y) in self.path:
                if (self.width - 1, y) == self.path[-1]:
                    cells += self.colors["last_pos"] +\
                        self.draw_set["cell_clossed"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"] +\
                        self.draw_set["cell_w_wall"].strip()
                else:
                    cells += self.colors["path"] +\
                        self.draw_set["cell_clossed"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"] +\
                        self.draw_set["cell_w_wall"].strip()
            elif (self.width - 1, y) in self.solution:
                if (self.width - 1, y) == self.solution[-1]:
                    cells += self.colors["exit_pos"] +\
                        self.draw_set["cell_path"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[y][x] & (1 << self.E) else " "
                    cells += end
                if (self.width - 1, y) == self.solution[0]:
                    cells += self.colors["entry_pos"] +\
                        self.draw_set["cell_path"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[y][x] & (1 << self.E) else " "
                    cells += end
                else:
                    cells += self.colors["path"] +\
                        self.draw_set["cell_path"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[y][x] & (1 << self.E) else " "
                    cells += end
            elif self.coded[y][self.width - 1] & (1 << self.E) and \
               self.coded[y][self.width - 1] & (1 << self.S) and \
               self.coded[y][self.width - 1] & (1 << self.N) and \
               self.coded[y][self.width - 1] & (1 << self.W):
                cells += self.colors["closed"] +\
                    self.draw_set["cell_right_clossed"] +\
                    self.RESET + self.BOLD +\
                    self.colors["wall"] + self.draw_set["cell_left_wall"]
            elif self.coded[y][self.width - 1] & (1 << self.E):
                cells += self.draw_set["cell_right_wall"]
            else:
                cells += self.draw_set["cell_no_wall"]
            print(" "*20, end="")
            print(self.BOLD + self.colors["wall"] + cells + self.RESET)

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
            print(" "*20, end="")
            print(self.BOLD + self.colors["wall"] + mid_row + self.RESET)

    def print_last_cell(self) -> None:
        assert self.solution is not None
        bot_row = self.draw_set["bot_left_corner"]
        last_cells = self.draw_set["cell_left_wall"]

        for x in range(self.width - 1):
            if (x, self.height - 1) in self.path:
                if (x, self.height - 1) == self.path[-1]:
                    last_cells += self.colors["last_pos"] +\
                        self.draw_set["cell_clossed"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[self.height - 1][x] & (1 << self.E)\
                        else " "
                    last_cells += end
                else:
                    last_cells += self.colors["path"] +\
                        self.draw_set["cell_clossed"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[self.height - 1][x] & (1 << self.E)\
                        else " "
                    last_cells += end
            elif (x, self.height - 1) in self.solution:
                if (x, self.height - 1) == self.solution[-1]:
                    last_cells += self.colors["exit_pos"] +\
                        self.draw_set["cell_path"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[self.height - 1][x] & (1 << self.E) else " "
                    last_cells += end
                elif (x, self.height - 1) == self.solution[0]:
                    last_cells += self.colors["entry_pos"] +\
                        self.draw_set["cell_path"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[self.height - 1][x] & (1 << self.E) else " "
                    last_cells += end
                else:
                    last_cells += self.colors["path"] +\
                        self.draw_set["cell_path"] +\
                        self.RESET + self.BOLD +\
                        self.colors["wall"]
                    end = self.draw_set["cell_w_wall"].strip()\
                        if self.coded[self.height - 1][x] & (1 << self.E) else " "
                    last_cells += end
            elif self.coded[self.height - 1][x] & (1 << self.E) and\
               self.coded[self.height - 1][x] & (1 << self.S) and\
               self.coded[self.height - 1][x] & (1 << self.N) and\
               self.coded[self.height - 1][x] & (1 << self.W):
                last_cells += self.colors["closed"] +\
                    self.draw_set["cell_clossed"] +\
                    self.RESET + self.BOLD +\
                    self.colors["wall"] + self.draw_set["cell_w_wall"].strip()
            elif self.coded[self.height - 1][x] & (1 << self.E):
                last_cells += self.draw_set["cell_w_wall"]
            else:
                last_cells += self.draw_set["cell_no_wall"]
        if (self.width - 1, self.height - 1) in self.path:
            if (self.width - 1, self.height - 1) == self.path[-1]:
                last_cells += self.colors["last_pos"] +\
                    self.draw_set["cell_clossed"] +\
                    self.RESET + self.BOLD +\
                    self.colors["wall"]
                end = self.draw_set["cell_w_wall"].strip()\
                    if self.coded[self.height - 1][self.width - 1] & (1 << self.E)\
                    else " "
                last_cells += end
            else:
                last_cells += self.colors["path"] +\
                    self.draw_set["cell_clossed"] +\
                    self.RESET + self.BOLD +\
                    self.colors["wall"]
                end = self.draw_set["cell_w_wall"].strip()\
                    if self.coded[self.height - 1][self.width - 1] & (1 << self.E)\
                    else " "
                last_cells += end
        elif (self.width - 1, self.height - 1) in self.solution:
            if (self.width - 1, self.height - 1) == self.solution[-1]:
                last_cells += self.colors["exit_pos"] +\
                    self.draw_set["cell_path"] +\
                    self.RESET + self.BOLD +\
                    self.colors["wall"]
                end = self.draw_set["cell_w_wall"].strip()\
                    if self.coded[self.height - 1][self.width - 1] & (1 << self.E) else " "
                last_cells += end
            if (self.width - 1, self.height - 1) == self.solution[0]:
                last_cells += self.colors["entry_pos"] +\
                    self.draw_set["cell_path"] +\
                    self.RESET + self.BOLD +\
                    self.colors["wall"]
                end = self.draw_set["cell_w_wall"].strip()\
                    if self.coded[self.height - 1][self.width - 1] & (1 << self.E) else " "
                last_cells += end
            else:
                last_cells += self.colors["path"] +\
                    self.draw_set["cell_path"] +\
                    self.RESET + self.BOLD +\
                    self.colors["wall"]
                end = self.draw_set["cell_w_wall"].strip()\
                    if self.coded[self.height - 1][self.width - 1] & (1 << self.E) else " "
                last_cells += end
        elif (self.coded[self.height - 1][self.width - 1] & (1 << self.E) and
              self.coded[self.height - 1][self.width - 1] & (1 << self.S) and
              self.coded[self.height - 1][self.width - 1] & (1 << self.N) and
              self.coded[self.height - 1][self.width - 1] & (1 << self.W)):
            last_cells += self.colors["closed"] +\
                self.draw_set["bot_right_clossed"] +\
                self.RESET + self.BOLD +\
                self.colors["wall"] + self.draw_set["cell_left_wall"]
        elif self.coded[self.height - 1][self.width - 1] & (1 << self.E):
            last_cells += self.draw_set["bot_right_wall"]
        else:
            last_cells += self.draw_set["bot_right_no_wall"]
        print(" "*20, end="")
        print(self.BOLD + self.colors["wall"] + last_cells + self.RESET)

        for x in range(self.width):
            if self.coded[self.height - 1][x] & (1 << self.E):
                bot_row += self.draw_set["bot_w_wall"]
            else:
                bot_row += self.draw_set["bot_no_wall"]
        bot_row = bot_row[:-1] + self.draw_set["bot_right_corner"]
        print(" "*20, end="")
        print(self.BOLD + self.colors["wall"] + bot_row + self.RESET)

    def define_params(self) -> None:
        self.draw_set = self.choose_drawing_set(self.style_param)
        self.colors = self.choose_color_set(self.color_param)

    @staticmethod
    def getch() -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    @staticmethod
    def choose_color_set(param: int) -> dict[str, str]:
        def rgb(r: int, g: int, b: int) -> str:
            return f"\033[38;2;{r};{g};{b}m"

        COLOR_SETS = {
            0: {
                "wall": "\033[93m",
                "closed": "\033[91m",
                "path": "\033[33;2m",
                "last_pos": "\033[97m",
                "entry_pos": "\033[92m",
                "exit_pos": "\033[91m",
            },
            1: {
                "wall": "\033[94m",
                "closed": "\033[92m",
                "path": "\033[96m",
                "last_pos": "\033[97m",
                "entry_pos": "\033[92m",
                "exit_pos": "\033[91m",
            },
            2: {
                "wall": rgb(255, 140, 0),
                "closed": "\033[97m",
                "path": "\033[94m",
                "last_pos": "\033[91m",
                "entry_pos": "\033[92m",
                "exit_pos": "\033[91m",
            },
        }

        return COLOR_SETS.get(param, COLOR_SETS[0])

    @staticmethod
    def choose_drawing_set(param: int) -> dict[str, str]:
        SETS = {
            0: {
                "up_left_corner": "+",
                "up_right_corner": "+",
                "up_w_wall": "---+",
                "up_no_wall": "---+",
                "cell_left_wall": "|",
                "cell_right_wall": "   |",
                "cell_w_wall": "   |",
                "cell_no_wall": "    ",
                "cell_clossed": "███",
                "cell_path": " ● ",
                "cell_right_clossed": "███",
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
                "bot_right_clossed": "███",
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
                "cell_clossed": "███",
                "cell_path": " ● ",
                "cell_right_clossed": "███",
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
                "bot_right_clossed": "███",
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
                "cell_clossed": "███",
                "cell_path": " ● ",
                "cell_right_clossed": "███",
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
                "bot_right_clossed": "███",
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
                "cell_clossed": "███",
                "cell_path": " ● ",
                "cell_right_clossed": "███",
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
                "bot_right_clossed": "███",
                "bot_right_no_wall": "   ",
                "bot_w_wall": "━━━┻",
                "bot_no_wall": "━━━━",
            }
        }

        return SETS.get(param, SETS[3])
