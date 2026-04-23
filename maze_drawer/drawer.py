import sys
import tty
import termios
import time
from mazegen import MazeGenerator
from typing import Generator
from .draw_sets import choose_drawing_set
from .color_sets import choose_color_set


class MazeDrawer():
    BOLD = "\033[1;97m"
    RESET = RESET = "\033[0m"

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    def __init__(self, gen: MazeGenerator, style_param: int = 3, color_param: int = 0):
        self.generator: MazeGenerator = gen
        self.coded: list[list[int]] = gen.maze
        self.path: list[tuple[int, int]] = []
        self.solution: list[tuple[int, int]] = []
        self.height: int = len(self.coded)
        self.width: int = len(self.coded[0])
        self.style_param: int = style_param
        self.color_param: int = color_param
        self.animating: bool = False
        self.frame: Generator[tuple[list[list[int]], list[tuple[int, int]]],
                              None, None] | None = None

        self.define_params()

        self.MAX_COLORS = int(choose_color_set(-1)["size"])
        self.MAX_STYLES = int(choose_drawing_set(-1)["size"])

    def start_engine(self) -> None:
        print("\033[2J\033[H", end="")

        while True:
            print("\033[H", end="")
            if self.animating and self.frame:
                try:
                    self.coded, self.path = next(self.frame)
                except StopIteration:
                    self.frame = None
                    self.animating = False
            self.draw_map()

            if not self.select_command():
                print("\033[2J\033[H", end="")
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
        self.print_last_cells()
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
        for y in range(self.height - 1):
            cells = self.draw_set["cell_left_wall"]
            for x in range(self.width - 1):
                cells += self.render_cell(x, y, is_last_col=False)
            cells += self.render_cell(self.width - 1, y, is_last_col=True)
            print(" "*20, end="")
            print(self.BOLD + self.colors["wall"] + cells + self.RESET)
            print(" "*20, end="")
            print(self.BOLD + self.colors["wall"] + self.render_mid_row(y) +
                  self.RESET)

    def print_last_cells(self) -> None:
        last_cells = self.draw_set["cell_left_wall"]
        for x in range(self.width - 1):
            last_cells += self.render_cell(x, self.height - 1,
                                           is_last_col=False)
        last_cells += self.render_cell(self.width - 1, self.height - 1,
                                       is_last_col=True)
        print(" "*20, end="")
        print(self.BOLD + self.colors["wall"] + last_cells + self.RESET)

        bot_row = self.draw_set["bot_left_corner"]
        for x in range(self.width):
            bot_row += self.draw_set["bot_w_wall"]\
                if self.coded[self.height - 1][x] & (1 << self.E)\
                else self.draw_set["bot_no_wall"]
        bot_row = bot_row[:-1] + self.draw_set["bot_right_corner"]
        print(" "*20, end="")
        print(self.BOLD + self.colors["wall"] + bot_row + self.RESET)

    def render_mid_row(self, y: int) -> str:
        if self.coded[y][0] & (1 << self.S):
            mid_row = self.draw_set["mid_left_w_wall"]
        else:
            mid_row = self.draw_set["mid_left_no_wall"]

        for x in range(self.width - 1):
            s = bool(self.coded[y][x] & (1 << self.S))
            ue = bool(self.coded[y][x] & (1 << self.E))
            de = bool(self.coded[y + 1][x] & (1 << self.E))
            se = bool(self.coded[y][x + 1] & (1 << self.S))

            key = f"mid_{'s_' if s else ''}{'ue_' if ue else ''}{'de_' if de else ''}{'se_' if se else ''}wall"
            key = key.replace("__", "_")

            mid_row += self.draw_set.get(key, self.draw_set["mid_no_wall"])

        if self.coded[y][self.width - 1] & (1 << self.S):
            mid_row += self.draw_set["mid_right_s_wall"]
        else:
            mid_row += self.draw_set["mid_right_no_wall"]

        return mid_row

    def render_cell(self, x: int, y: int, is_last_col: bool) -> str:
        cell = self.coded[y][x]
        has_east = bool(cell & (1 << self.E))
        wall_char = self.draw_set["cell_w_wall"].strip() if has_east else " "
        right_wall = self.draw_set["cell_right_wall"] if is_last_col else ""

        if (x, y) in self.solution:
            if (x, y) == self.solution[-1]:
                color = self.colors["exit_pos"]
            elif (x,y) == self.solution[0]:
                color = self.colors["entry_pos"]
            else:
                color = self.colors["path"]
            content = self.draw_set["cell_path"]
            border = self.draw_set["cell_left_wall"] if is_last_col\
                else wall_char

        elif (x, y) in self.path:
            is_last = (x, y) == self.path[-1]
            color = self.colors["last_pos"] if is_last else self.colors["path"]
            content = self.draw_set["cell_closed"]
            border = self.draw_set["cell_left_wall"] if is_last_col\
                else wall_char

        elif self.is_closed(x, y):
            color = self.colors["closed"]
            content = self.draw_set["cell_right_closed"] if is_last_col\
                else self.draw_set["cell_closed"]
            border = self.draw_set["cell_left_wall"] if is_last_col\
                else self.draw_set["cell_w_wall"].strip()

        else:
            if is_last_col:
                return right_wall if has_east\
                    else self.draw_set["bot_right_no_wall"]
            return self.draw_set["cell_w_wall"] if has_east\
                else self.draw_set["cell_no_wall"]

        return (color + content +
                self.RESET + self.BOLD + self.colors["wall"] + border)

    def is_closed(self, x: int, y: int) -> bool:
        cell = self.coded[y][x]
        return all(cell & (1 << d) for d in [self.N, self.E, self.W, self.S])

    def define_params(self) -> None:
        self.draw_set = choose_drawing_set(self.style_param)
        self.colors = choose_color_set(self.color_param)

    def select_command(self) -> bool:
        self.draw_commands()

        key = None
        if not self.animating:
            key = self.getch()

        if key == "c":
            if self.color_param + 1 < self.MAX_COLORS:
                self.color_param += 1
            else:
                self.color_param = 0
            self.define_params()

        elif key == "p":
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

        elif key == "s":
            if self.style_param + 1 < self.MAX_STYLES:
                self.style_param += 1
            else:
                self.style_param = 0
            self.define_params()

        elif key == "g":
            if self.solution:
                self.solution = []
            self.frame = self.generator.generate_frame()
            self.animating = True
        
        elif key = "o":
            if self.solution:
                self.solution = []
                self.frame = self.generator

        elif key == "i":
            self.generator.make_imperfect()
            self.coded = self.generator.maze

        elif key == "f":
            if not self.solution:
                self.solution = self.generator.find_shortest_path()
            elif len(self.solution) == 2:
                self.solution = self.generator.find_shortest_path()
            else:
                self.solution = []

        elif key == "q":
            return False
        return True

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
