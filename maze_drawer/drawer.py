import sys
import tty
import termios
import time
import shutil
from mazegen import MazeGenerator
from typing import Generator, Any
from .draw_sets import choose_drawing_set
from .color_sets import choose_color_set


class DrawerError(Exception):
    pass


class MazeDrawer():
    BOLD = "\033[1;97m"
    RESET = RESET = "\033[0m"

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    def __init__(self, gen: MazeGenerator,
                 style_param: int = 3,
                 color_param: int = 2):
        self.generator: MazeGenerator = gen
        self.coded: list[list[int]] = gen.maze
        self.path: list[tuple[int, int]] = []
        self.solution: list[tuple[int, int]] = []
        self.edge_positions: list[tuple[int, int]] =\
            gen.get_entry_exit_positions()
        self.height: int = len(self.coded)
        self.width: int = len(self.coded[0])
        self.style_param: int = style_param
        self.color_param: int = color_param
        self.animating_dfs: bool = False
        self.animating_bfs: bool = False
        self.animating_imp: bool = False
        self.frame: Generator[Any, None, None] | None = None
        self.perfect: bool = gen.get_perfect_status()
        self.draw_speed: float = 5 / (self.height * self.width)
        self.show_configs: bool = False

        self.define_params()

        self.MAX_COLORS = int(choose_color_set(-1)["size"])
        self.MAX_STYLES = int(choose_drawing_set(-1)["size"])

        self.check_terminal_size()

    def check_terminal_size(self) -> None:
        cols, rows = shutil.get_terminal_size()
        rendered_maze_width = 20 + self.width * 4 + 1
        render_cols = 69 if 69 > rendered_maze_width else rendered_maze_width
        render_rows = 2 + self.height * 2 + 6

        if render_cols > cols or render_rows > rows:
            raise DrawerError("Terminal size too smal to render the maze!")

    def start_engine(self) -> None:
        print("Starting Engine ...")
        time.sleep(2)
        print("Loading assets...")
        time.sleep(0.5)
        print("\033[2J\033[H", end="")

        while True:
            print("\033[H", end="")
            if self.animating_dfs and self.frame:
                try:
                    self.coded, self.path = next(self.frame)
                except StopIteration:
                    self.frame = None
                    self.animating_dfs = False
                    if not self.perfect:
                        self.coded = self.generator.maze

            elif self.animating_bfs and self.frame:
                try:
                    self.path, self.solution = next(self.frame)
                except StopIteration:
                    self.frame = None
                    self.animating_bfs = False
                    self.path = []

            elif self.animating_imp and self.frame:
                try:
                    cell, self.coded = next(self.frame)
                    self.path = [cell]
                except StopIteration:
                    self.frame = None
                    self.animating_imp = False
                    self.path = []
                    self.generator.make_imperfect()

            self.draw_map()
            self.draw_commands()
            if self.show_configs:
                self.draw_configs()
            else:
                for _ in range(7):
                    print(" "*50)

            if not self.select_command():
                print("\033[2J\033[H", end="")
                break

            time.sleep(self.draw_speed)

    def draw_configs(self) -> None:
        wall = self.draw_set["cell_left_wall"]
        print(" "*10, end="")
        print(f"{wall} Maze Dimensions: ({self.width}, {self.height})")
        print(" "*10, end="")
        positions = self.generator.get_entry_exit_positions()
        print(f"{wall} Entry Point: {positions[0]}")
        print(" "*10, end="")
        print(f"{wall} Exit Point: {positions[1]}")
        print(" "*10, end="")
        print(f"{wall} SEED: {self.generator._seed}")
        print(" "*10, end="")
        print(f"{wall} Algorithm used: {self.generator._strategy.__class__.__name__}")
        print(" "*10, end="")
        print(f"{wall} Perfect: {self.perfect} ")
        print(" "*10 + self.draw_set["bot_left_corner"])

    def draw_commands(self) -> None:
        wall = self.draw_set["cell_w_wall"].strip()
        top = self.draw_set["up_no_wall"][0]
        top_n = self.draw_set["bot_w_wall"][-1]
        top_s = self.draw_set["up_w_wall"][-1]
        print(" "*5, end="")
        line = (self.draw_set["up_left_corner"] +
                (top*4 + top_n + top*6 + top_n) +
                (top*8 + top_s) + (top*20 + top_s)*2)
        print(line[:-1] + self.draw_set["up_right_corner"])
        print(" "*6, end="")
        print(f"c.Change Color      {wall}  s.Change Style    {wall}  q.quit")
        print(" "*6, end="")
        print(f"i.Toggle Imperfect  {wall}  f.Toggle Solution {wall}"
              "  p.Toggle Exit/Entry")
        print(" "*6, end="")
        print(f"j.Animate Imperfect {wall}  o.Animate BFS     {wall}"
              "  g.Animate DFS/PRIM")
        print(" "*5, end="")
        line = (self.draw_set["bot_left_corner"] +
                ((self.draw_set["up_no_wall"] * (5) +
                  self.draw_set["bot_w_wall"][-1]) * 3)[:-1] +
                self.draw_set["bot_right_corner"])
        print(line)

    def draw_map(self) -> None:
        print("\n"*2)
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
        o_wall = self.draw_set["cell_left_wall"]
        last_cells = self.draw_set["cell_left_wall"]
        for x in range(self.width - 1):
            last_cells += self.render_cell(x, self.height - 1,
                                           is_last_col=False)
        last_cells += self.render_cell(self.width - 1, self.height - 1,
                                       is_last_col=True)
        print(" "*10, end="")
        top_menu = (self.draw_set["up_left_corner"] +
                    self.draw_set["up_no_wall"] +
                    self.draw_set["up_no_wall"][:2] +
                    self.draw_set["up_right_corner"] + " " * 2)
        print(top_menu, end="")
        print(self.BOLD + self.colors["wall"] + last_cells + self.RESET)

        bot_row = self.draw_set["bot_left_corner"]
        for x in range(self.width):
            bot_row += self.draw_set["bot_w_wall"]\
                if self.coded[self.height - 1][x] & (1 << self.E)\
                else self.draw_set["bot_no_wall"]
        bot_row = bot_row[:-1] + self.draw_set["bot_right_corner"]

        print(" "*10, end="")
        mid_menu = (o_wall + self.BOLD + " MENU " +
                    self.RESET + o_wall + self.RESET + " " * 2)
        print(mid_menu, end="")
        print(self.BOLD + self.colors["wall"] + bot_row + self.RESET, end="")

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

            key = (f"mid_{'s_' if s else ''}{'ue_' if ue else ''}"
                   f"{'de_' if de else ''}{'se_' if se else ''}wall")
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

        if (x, y) in self.edge_positions:
            if (x, y) == self.edge_positions[-1]:
                color = self.colors["exit_pos"]
            else:
                color = self.colors["entry_pos"]
            content = self.draw_set["cell_path"]
            border = self.draw_set["cell_left_wall"] if is_last_col\
                else wall_char

        elif (x, y) in self.solution:
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
        key = None
        if (not (self.animating_dfs or
                 self.animating_bfs or
                 self.animating_imp)):
            key = self.getch()

        if key == "c":
            if self.color_param + 1 < self.MAX_COLORS:
                self.color_param += 1
            else:
                self.color_param = 0
            self.define_params()

        elif key == "p":
            if not self.edge_positions:
                self.edge_positions =\
                    self.generator.get_entry_exit_positions()
            else:
                self.edge_positions = []
                self.solution = []

        elif key == "s":
            if self.style_param + 1 < self.MAX_STYLES:
                self.style_param += 1
            else:
                self.style_param = 0
            self.define_params()

        elif key == "g":
            if self.solution:
                self.solution = []
            if self.edge_positions:
                self.edge_positions = []
            self.frame = self.generator.generate_frame()
            self.animating_dfs = True

        elif key == "o":
            if self.solution:
                self.solution = []
            if not self.edge_positions:
                self.edge_positions =\
                    self.generator.get_entry_exit_positions()
            self.frame = self.generator.path_frames()
            self.animating_bfs = True

        elif key == "i":
            if self.perfect:
                self.generator.make_imperfect()
                self.coded = self.generator.maze
                if self.solution:
                    self.solution = self.generator.find_shortest_path()
                self.perfect = False
            else:
                self.generator.generate_maze()
                self.coded = self.generator.maze
                if self.solution:
                    self.solution = self.generator.find_shortest_path()
                self.perfect = True

        elif key == "j":
            if not self.perfect:
                self.generator.generate_maze()
            if self.solution:
                self.solution = []
            if self.edge_positions:
                self.edge_positions = []
            self.frame = self.generator.make_imperfect_frames()
            self.animating_imp = True
            self.perfect = False

        elif key == "f":
            if not self.solution:
                if not self.edge_positions:
                    self.edge_positions =\
                        self.generator.get_entry_exit_positions()
                self.solution = self.generator.find_shortest_path()
            else:
                self.solution = []
                self.edge_positions = []

        elif key == "w":
            self.generator.swap_algorithm()
            self.generator.generate_maze()
            if not self.perfect:
                self.generator.make_imperfect()
            self.coded = self.generator.maze
            if self.solution:
                self.solution = self.generator.find_shortest_path()

        elif key == "y":
            self.show_configs = not self.show_configs

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
