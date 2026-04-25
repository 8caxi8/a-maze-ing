import sys
import tty
import termios
import time
import shutil
import select
from mazegen import MazeGenerator
from typing import Generator, Any
from .draw_sets import choose_drawing_set
from .color_sets import choose_color_set
from .open_screen import open_gen, exp, project_name


class DrawerError(Exception):
    pass


class MazeDrawer():
    BOLD = "\033[1;97m"
    RESET = "\033[0m"

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    def __init__(self, gen: MazeGenerator,
                 style_param: int = 3,
                 color_param: int = 2):
        self.generator: MazeGenerator = gen
        self.path: list[tuple[int, int]] = []
        self.solution: list[tuple[int, int]] = []
        self.edge_positions: list[tuple[int, int]] = []

        self.MAX_COLORS = int(choose_color_set(-1)["size"])
        self.MAX_STYLES = int(choose_drawing_set(-1)["size"])
        self.style_param: int = style_param
        self.color_param: int = color_param
        self.define_params()
        self.show_menu: int = 0
        self._starting_screen()

        self.coded: list[list[int]] = gen.maze
        self.height: int = len(self.coded)
        self.width: int = len(self.coded[0])
        self.animating_dfs: bool = False
        self.animating_bfs: bool = False
        self.animating_imp: bool = False
        self.frame: Generator[Any, None, None] | None = None
        self.perfect: bool = gen.get_perfect_status()
        self.draw_speed: float = max(0.001,
                                     min(0.5, 5 / (self.height * self.width)))
        self.show_configs: int = 0
        self.show_menu = 1
        self.pause: str = ""

        self._check_terminal_size()

    def _check_terminal_size(self) -> None:
        MIN_COLS = 69
        cols, rows = shutil.get_terminal_size()
        rendered_maze_width = 20 + self.width * 4 + 1
        render_cols = MIN_COLS if MIN_COLS > rendered_maze_width\
            else rendered_maze_width
        render_rows = 2 + self.height * 2 + 6

        if render_cols > cols or render_rows > rows:
            raise DrawerError("Terminal size too smal to render the maze!")

    def _starting_screen(self) -> None:
        print("\033[2J\033[H", end="")

        self.animate_42()
        self.animate_path()

    def animate_42(self) -> None:
        self.coded = next(open_gen())
        self.height = len(self.coded)
        self.width = len(self.coded[0])
        gen = open_gen()
        e = exp()

        for frame in gen:
            speed_i = next(e)
            self.coded = frame
            print("\033[H", end="")

            self.draw_map()
            time.sleep(speed_i)
            if self.color_param + 1 < self.MAX_COLORS:
                self.color_param += 1
            else:
                self.color_param = 0
            if self.style_param + 1 < self.MAX_STYLES:
                self.style_param += 1
            else:
                self.style_param = 0
            self.define_params()

        for _ in range(self.MAX_STYLES):
            if self.color_param + 1 < self.MAX_COLORS:
                self.color_param += 1
            else:
                self.color_param = 0
            if self.style_param + 1 < self.MAX_STYLES:
                self.style_param += 1
            else:
                self.style_param = 0
            self.define_params()
            print("\033[H", end="")
            self.draw_map()
            time.sleep(0.02)

    def animate_path(self) -> None:
        self.edge_positions = [
                    (4, 0),
                    (4, 6),
                ]
        new_gen = MazeGenerator(9, 7, (4, 0), (4, 6))
        new_gen.maze = self.coded
        frame = new_gen.path_frames()
        title = project_name(choose_color_set(2))
        i = 0

        while True:
            print("\033[H", end="")

            self.draw_map()

            if self.solution:
                if i > len(title):
                    for line in title:
                        print(line)
                else:
                    for j in range(i):
                        print(title[j])
                    i += 1
            try:
                self.path, self.solution = next(frame)
            except StopIteration:
                break
            time.sleep(0.05)

        self.path = []
        print("\033[H", end="")
        self.draw_map()
        time.sleep(1)

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            while True:
                tty.setcbreak(fd)
                key = self.getch()
                if key is not None:
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            self.solution = []
            self.path = []
            self.edge_positions = self.generator.get_entry_exit_positions()

    def start_engine(self) -> None:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            print("\033[2J\033[H", end="")

            while True:
                print("\033[H", end="")

                if self._is_animating():
                    self._next_frame()

                self.draw_map()

                if self._show_menu():
                    continue

                if self._show_configs():
                    continue

                if not self.select_command():
                    break

                time.sleep(self.draw_speed)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _is_animating(self) -> bool:
        return self.animating_bfs or self.animating_dfs or self.animating_imp

    def _next_frame(self) -> None:
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

    def _show_menu(self) -> bool:
        if self.show_menu == 1:
            self.draw_commands()

        elif self.show_menu == 2:
            for _ in range(6):
                print(" "*70)
            self.show_menu = 0
            if self.show_configs == 1:
                for _ in range(7):
                    print(" "*50)
                self.show_configs = 0
            return True

        return False

    def _show_configs(self) -> bool:
        if self.show_configs == 1 and self.show_menu == 1:
            self._draw_configs()

        elif self.show_configs == 2:
            for _ in range(7):
                print(" "*50)
            self.show_configs = 0
            return True

        return False

    def _draw_configs(self) -> None:
        wall = self.draw_set["cell_left_wall"]
        sp = " "*10

        print(f"{sp}{wall} Maze Dimensions: ({self.width}, {self.height})")

        positions = self.generator.get_entry_exit_positions()
        print(f"{sp}{wall} Entry Point: {positions[0]}")

        print(f"{sp}{wall} Exit Point: {positions[1]}")

        print(f"{sp}{wall} SEED: {self.generator._seed}")

        print(f"{sp}{wall} Algorithm used: "
              f"{self.generator._strategy.__class__.__name__}")

        print(f"{sp}{wall} Perfect: {self.perfect} ")

        print(sp + self.draw_set["bot_left_w_s_corner"])

    def draw_commands(self) -> None:
        wall = self.draw_set["cell_w_wall"].strip()
        top = self.draw_set["up_n_wall"][0]
        top_n = self.draw_set["bot_s_e_es_wall"][-1]
        top_s = self.draw_set["up_n_e_ne_wall"][-1]
        s = " "*6
        print(" "*5, end="")
        line = (self.draw_set["up_left_n_w_corner"] +
                (top*4 + top_n + top*6 + top_n) +
                (top*8 + top_s) + (top*20 + top_s)*2)
        print(line[:-1] + self.draw_set["up_right_n_e_corner"])
        print(f"{s}c.Change Color      {wall}  s.Change Style    {wall}"
              "  q.quit")
        print(f"{s}i.Toggle Imperfect  {wall}  f.Toggle Solution {wall}"
              "  p.Toggle Exit/Entry")
        print(f"{s}j.Animate Imperfect {wall}  o.Animate BFS     {wall}"
              "  g.Animate DFS/PRIM")
        print(f"{s}w.Swap Algorithm    {wall}  y.Show Configs    {wall}"
              "  z.Stop Animation")
        print(" "*5, end="")
        line = (self.draw_set["bot_left_w_s_corner"] +
                ((self.draw_set["up_n_ne_wall"] * (5) +
                  self.draw_set["bot_s_e_es_wall"][-1]) * 3)[:-1] +
                self.draw_set["bot_right_e_s_corner"])
        print(line)

    def draw_map(self) -> None:
        self.print_top_container()
        self.print_mid_cells()
        self.print_last_cells()
        print()

    def print_top_container(self) -> None:
        n = bool(self.coded[0][0] & (1 << self.N))
        w = bool(self.coded[0][0] & (1 << self.W))
        if not n and not w:
            key = "up_left_no_corner"
        else:
            key = f"up_left_{'n_' if n else ''}{'w_' if w else ''}corner"
        top_row = self.draw_set.get(key, self.draw_set["up_left_no_corner"])

        for x in range(self.width):
            n = bool(self.coded[0][x] & (1 << self.N))
            e = bool(self.coded[0][x] & (1 << self.E))
            ne = bool(self.coded[0][x + 1] & (1 << self.N)) \
                if x + 1 < self.width else False
            if not n and not e and not ne:
                key = "up_no_wall"
            else:
                key = (f"up_{'n_' if n else ''}{'e_' if e else ''}"
                       f"{'ne_' if ne else ''}wall")
            top_row += self.draw_set.get(key, self.draw_set["up_no_wall"])

        n = bool(self.coded[0][self.width - 1] & (1 << self.N))
        e = bool(self.coded[0][self.width - 1] & (1 << self.E))
        if not n and not e:
            key = "up_right_no_corner"
        else:
            key = f"up_right_{'n_' if n else ''}{'e_' if e else ''}corner"
        top_row = top_row[:-1] + \
            self.draw_set.get(key, self.draw_set["up_right_no_corner"])

        print(" "*20, end="")
        print(self.BOLD + self.colors["wall"] + top_row + self.RESET)

    def print_mid_cells(self) -> None:
        for y in range(self.height - 1):
            w = bool(self.coded[y][0] & (1 << self.W))
            cells = self.draw_set["cell_left_wall"] if w \
                else self.draw_set["cell_left_no_wall"]
            for x in range(self.width - 1):
                cells += self.render_cell(x, y, is_last_col=False)
            cells += self.render_cell(self.width - 1, y, is_last_col=True)
            print(" "*20, end="")
            print(self.BOLD + self.colors["wall"] + cells + self.RESET)
            print(" "*20, end="")
            print(self.BOLD + self.colors["wall"] + self.render_mid_row(y) +
                  self.RESET)

    def render_mid_row(self, y: int) -> str:
        w = bool(self.coded[y][0] & (1 << self.W))
        sw = bool(self.coded[y + 1][0] & (1 << self.W))
        s = bool(self.coded[y][0] & (1 << self.S))
        if not w and not sw and not s:
            key = "mid_left_no_wall"
        else:
            key = (f"mid_left_{'w_' if w else ''}{'sw_' if sw else ''}"
                   f"{'s_' if s else ''}wall")
        mid_row = self.draw_set.get(key, self.draw_set["mid_left_no_wall"])

        for x in range(self.width - 1):
            s = bool(self.coded[y][x] & (1 << self.S))
            ue = bool(self.coded[y][x] & (1 << self.E))
            de = bool(self.coded[y + 1][x] & (1 << self.E))
            se = bool(self.coded[y][x + 1] & (1 << self.S))
            if not s and not ue and not de and not se:
                key = "mid_no_wall"
            else:
                key = (f"mid_{'s_' if s else ''}{'ue_' if ue else ''}"
                       f"{'de_' if de else ''}{'se_' if se else ''}wall")
            mid_row += self.draw_set.get(key, self.draw_set["mid_no_wall"])

        s = bool(self.coded[y][self.width - 1] & (1 << self.S))
        e = bool(self.coded[y][self.width - 1] & (1 << self.E))
        se = bool(self.coded[y + 1][self.width - 1] & (1 << self.E))
        if not s and not e and not se:
            key = "mid_right_no_wall"
        else:
            key = (f"mid_right_{'s_' if s else ''}{'e_' if e else ''}"
                   f"{'se_' if se else ''}wall")
        mid_row += self.draw_set.get(key, self.draw_set["mid_right_no_wall"])

        return mid_row

    def print_last_cells(self) -> None:
        o_wall = self.draw_set["cell_left_wall"]

        w = bool(self.coded[self.height - 1][0] & (1 << self.W))
        last_cells = self.draw_set["cell_left_wall"] if w \
            else self.draw_set["cell_left_no_wall"]

        for x in range(self.width - 1):
            last_cells += self.render_cell(x, self.height - 1,
                                           is_last_col=False, is_last_row=True)
        last_cells += self.render_cell(self.width - 1, self.height - 1,
                                       is_last_col=True, is_last_row=True)

        print(" "*10, end="")
        top_menu = (self.draw_set["up_left_n_w_corner"] +
                    self.draw_set["up_n_ne_wall"] +
                    self.draw_set["up_n_wall"][:2] +
                    self.draw_set["up_right_n_e_corner"] + " " * 2)
        print(top_menu, end="") if self.show_menu == 1\
            else print(" "*10, end="")
        print(self.BOLD + self.colors["wall"] + last_cells + self.RESET)

        s = bool(self.coded[self.height - 1][0] & (1 << self.S))
        w = bool(self.coded[self.height - 1][0] & (1 << self.W))
        if not w and not s:
            key = "bot_left_no_corner"
        else:
            key = f"bot_left_{'w_' if w else ''}{'s_' if s else ''}corner"
        bot_row = self.draw_set.get(key, self.draw_set["bot_left_no_corner"])

        for x in range(self.width):
            s = bool(self.coded[self.height - 1][x] & (1 << self.S))
            e = bool(self.coded[self.height - 1][x] & (1 << self.E))
            es = bool(self.coded[self.height - 1][x + 1] & (1 << self.S)) \
                if x + 1 < self.width else False
            if not s and not e and not es:
                key = "bot_no_wall"
            else:
                key = (f"bot_{'s_' if s else ''}{'e_' if e else ''}"
                       f"{'es_' if es else ''}wall")
            bot_row += self.draw_set.get(key, self.draw_set["bot_no_wall"])

        s = bool(self.coded[self.height - 1][self.width - 1] & (1 << self.S))
        e = bool(self.coded[self.height - 1][self.width - 1] & (1 << self.E))
        if not e and not s:
            key = "bot_right_no_corner"
        else:
            key = f"bot_right_{'e_' if e else ''}{'s_' if s else ''}corner"
        bot_row = bot_row[:-1] + \
            self.draw_set.get(key, self.draw_set["bot_right_no_corner"])

        print(" "*10, end="")
        mid_menu = (o_wall + self.BOLD + " MENU " +
                    self.RESET + o_wall + self.RESET + " " * 2)
        print(mid_menu, end="") if self.show_menu == 1\
            else print(" "*10, end="")
        print(self.BOLD + self.colors["wall"] + bot_row + self.RESET, end="")

    def render_cell(self, x: int, y: int,
                    is_last_col: bool, is_last_row: bool = False) -> str:
        cell = self.coded[y][x]
        has_east = bool(cell & (1 << self.E))
        wall_char = self.draw_set["cell_w_wall"].strip() if has_east else " "

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
            if is_last_col:
                return (color + self.draw_set["cell_closed"] +
                        self.RESET + self.BOLD + self.colors["wall"] +
                        self.draw_set["cell_left_wall"])
            content = self.draw_set["cell_closed"]
            border = self.draw_set["cell_w_wall"].strip() if has_east else " "

        else:
            if is_last_col:
                if has_east:
                    return self.draw_set["cell_right_wall"]
                return self.draw_set["bot_right_no_wall"] if is_last_row \
                    else self.draw_set["cell_no_wall"]
            return self.draw_set["cell_w_wall"] if has_east \
                else self.draw_set["cell_no_wall"]

        return (color + content +
                self.RESET + self.BOLD + self.colors["wall"] + border)

    def is_closed(self, x: int, y: int) -> bool:
        cell = self.coded[y][x]
        return all(cell & (1 << d) for d in [self.N, self.E, self.W, self.S])

    def define_params(self) -> None:
        self.draw_set = choose_drawing_set(self.style_param)
        self.colors = choose_color_set(self.color_param)

    def _stop_animation(self) -> bool:
        self.frame = None
        self.animating_dfs = False
        self.animating_imp = False
        self.animating_bfs = False
        self.path = []
        self.coded = self.generator.maze

        if not self.perfect:
            self.generator.make_imperfect()

        return True

    def handle_key(self, key: str) -> bool:
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
            self.pause = key

        elif key == "o":
            if self.solution:
                self.solution = []
            if not self.edge_positions:
                self.edge_positions =\
                    self.generator.get_entry_exit_positions()
            self.frame = self.generator.path_frames()
            self.animating_bfs = True
            self.pause = key

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
            self.pause = key

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
            if self.show_configs == 0:
                self.show_configs = 1
            elif self.show_configs == 1:
                self.show_configs = 2

        elif key == "h":
            if self.show_menu == 0:
                self.show_menu = 1
            elif self.show_menu == 1:
                self.show_menu = 2

        elif key == "q":
            return False

        return True

    def select_command(self) -> bool:
        if self._is_animating():
            key = self.getch_nonblocking()

            if key == "q":
                return False

            if key == self.pause:
                key = None
                while key != self.pause:
                    key = self.getch()
                    if key == "q":
                        return False

                    elif key == "z":
                        return self._stop_animation()

            elif key == "z":
                return self._stop_animation()

            return True

        key = self.getch()
        if key is not None:
            return self.handle_key(key)
        return True

    def start_logo(self) -> None:
        while True:
            self._draw_start_logo()

    def _draw_start_logo(self) -> None:
        pass

    @staticmethod
    def getch() -> str | None:
        return sys.stdin.read(1)

    @staticmethod
    def getch_nonblocking() -> str | None:
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if ready:
            return sys.stdin.read(1)
        return None
