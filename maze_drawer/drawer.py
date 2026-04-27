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
    """
    Handles terminal-based maze rendering, animations, and user interaction.

    This class is responsible for displaying the maze, animating generation
    and solving algorithms, managing styles and colors, and handling
    keyboard controls during runtime.
    """
    BOLD = "\033[1;97m"
    RESET = "\033[0m"

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    def __init__(self, gen: MazeGenerator,
                 style_param: int = 3,
                 color_param: int = 2,
                 start_logo: bool = True):
        """
        Initialize the maze drawer and prepare the rendering engine.

        Performs terminal size validation, initializes rendering parameters,
        optionally displays the animated startup screen, and prepares
        animation-related state.

        Args:
            gen:
                The maze generator instance containing the maze data.

            style_param:
                Initial drawing style identifier.

            color_param:
                Initial color theme identifier.

            start_logo:
                Whether to display the animated startup screen before
                entering the main interface.

        Raises:
            DrawerError:
                If the terminal is too small to render the maze.
        """
        self._check_terminal_size(gen)
        self._initbasicparams(gen, style_param, color_param)

        if start_logo:
            self._starting_screen(style_param, color_param)

        self._initanimparams(gen)

    def _initbasicparams(self, gen: MazeGenerator,
                         style_param: int,
                         color_param: int) -> None:
        """
        Initialize base rendering configuration and display settings.

        Sets the maze generator reference, prepares path tracking,
        loads available styles and color themes, and initializes
        menu visibility state.

        Args:
            gen:
                Maze generator instance.

            style_param:
                Initial drawing style selection.

            color_param:
                Initial color theme selection.
        """
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

    def _initanimparams(self, gen: MazeGenerator) -> None:
        """
        Initialize animation state variables and maze rendering data.

        Stores the maze structure, dimensions, animation flags,
        animation speed, and runtime interface state.

        Args:
            gen:
                Maze generator containing the current maze.
        """
        self.coded: list[list[int]] = gen.maze
        self.perfect: bool = gen.get_perfect_status()
        self.height: int = len(self.coded)
        self.width: int = len(self.coded[0])

        self.animating_dfs: bool = False
        self.animating_bfs: bool = False
        self.animating_imp: bool = False

        self.frame: Generator[Any, None, None] | None = None
        self.draw_speed: float = max(0.001,
                                     min(0.5, 5 / (self.height * self.width)))

        self.show_configs: int = 0
        self.show_menu = 1
        self.pause: str = ""

    def _check_terminal_size(self, gen: MazeGenerator) -> None:
        """
        Validate that the terminal is large enough to render the maze.

        Calculates the required number of terminal rows and columns
        based on maze dimensions and raises an exception if the
        current terminal size is insufficient.

        Args:
            gen:
                Maze generator containing the maze dimensions.

        Raises:
            DrawerError:
                If the terminal size is too small.
        """
        MIN_COLS = 72
        MIN_ROWS = 20
        cols, rows = shutil.get_terminal_size()
        height, width = len(gen.maze), len(gen.maze[0])

        rendered_maze_width = 20 + width * 4 + 5
        rendered_width = MIN_COLS if MIN_COLS > rendered_maze_width\
            else rendered_maze_width
        rendered_height = height * 2 + 1 + MIN_ROWS

        if rendered_width > cols or rendered_height > rows:
            raise DrawerError(f"Terminal size {cols, rows}too small to render"
                              " the maze! Need at least: "
                              f"{rendered_width, rendered_height}!")

    def _starting_screen(self, style_param: int, color_param: int) -> None:
        print("\033[2J\033[H", end="")
        """
        Display the animated startup screen.

        Plays the opening logo animation and path animation before
        entering the main maze interface.

        Terminal settings are temporarily changed to allow
        non-blocking keyboard interruption.

        Args:
            style_param:
                Drawing style to restore after animation.

            color_param:
                Color theme to restore after animation.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            self._animate_42(fd)
            self._animate_path(fd)

        except DrawerError:
            pass

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            self.solution = []
            self.path = []
            self.edge_positions = self.generator.get_entry_exit_positions()

            self.style_param = style_param
            self.color_param = color_param
            self.define_params()

    def _check_skip(self, fd: int) -> None:
        """
        Interrupt the startup animation if the user presses a key.

        Args:
            fd:
                File descriptor for terminal input.

        Raises:
            DrawerError:
                Raised when input is detected to stop animation.
        """
        if self.getch_nonblocking() is not None:
            raise DrawerError

    def _cycle_style(self) -> None:
        """
        Cycle through available drawing styles and color themes.

        Used during the startup animation to create visual transitions.
        Automatically wraps when reaching the last available style
        or color set.
        """
        if self.color_param + 1 < self.MAX_COLORS:
            self.color_param += 1
        else:
            self.color_param = 0
        if self.style_param + 1 < self.MAX_STYLES:
            self.style_param += 1
        else:
            self.style_param = 0
        self.define_params()

    def _animate_42(self, fd: int) -> None:
        """
        Animate the opening logo frame sequence.

        Gradually reveals the project logo using generated frames
        while cycling through available styles and colors.

        Args:
            fd:
                File descriptor for terminal input.

        Raises:
            DrawerError:
                If the user interrupts the animation.
        """
        gen = open_gen()
        e = exp()

        self.coded = next(open_gen())
        self.height = len(self.coded)
        self.width = len(self.coded[0])

        for frame in gen:
            self.coded = frame
            self._cycle_style()

            print("\033[H", end="")
            self.draw_map()

            time.sleep(next(e))
            self._check_skip(fd)

        for _ in range(self.MAX_STYLES):
            self._cycle_style()

            print("\033[H", end="")
            self.draw_map()

            self._check_skip(fd)
            time.sleep(0.02)

    def _animate_path(self, fd: int) -> None:
        """
        Animate the path traversal over the opening logo.

        Simulates pathfinding across the startup logo and gradually
        reveals the project title before waiting for user input.

        Args:
            fd:
                File descriptor for terminal input.

        Raises:
            DrawerError:
                If the user interrupts the animation.
        """
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
            self._check_skip(fd)
            time.sleep(0.05)

        self.path = []
        print("\033[H", end="")
        self.draw_map()
        time.sleep(1)
        self._check_skip(fd)

        print("\n"*6)
        print(" "*10, end="")
        print("Press any Key to start ", end="", flush=True)

        i = 0
        while True:
            key = self.getch_nonblocking()
            if key is not None:
                break

            if i < 3:
                print(". ", end="", flush=True)
                i += 1
            else:
                print(f"\r{' ' * 40}"
                      f"\r{' ' * 10}Press any key to start ", end="",
                      flush=True)
                i = 0
            time.sleep(0.5)

    def start_engine(self) -> None:
        """
        Start the main interactive rendering loop.

        Continuously redraws the maze, updates active animations,
        renders menus and configuration panels, and processes
        keyboard input until the user exits.
        """
        RENDER_SPEED: float = 0.05
        speed: float = 0.0
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            print("\033[2J\033[H", end="")

            while True:
                print("\033[H", end="")

                if self._is_animating():
                    self._next_frame()
                    speed = self.draw_speed
                else:
                    speed = RENDER_SPEED

                self.draw_map()

                if self._show_menu():
                    continue

                if self._show_configs():
                    continue

                if not self.select_command():
                    break

                time.sleep(speed)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _is_animating(self) -> bool:
        """
        Check whether any animation is currently active.

        Returns:
            bool:
                True if DFS, BFS, or imperfect animation is active,
                otherwise False.
        """
        return self.animating_bfs or self.animating_dfs or self.animating_imp

    def _next_frame(self) -> None:
        """
        Advance the currently active animation by one frame.

        Updates the maze state depending on which animation is active:
        maze generation, shortest-path solving, or imperfect maze creation.

        Stops animation automatically when the frame generator finishes.
        """
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
        """
        Handle menu visibility and rendering state.

        Displays the command menu, hides it, or clears the menu area
        depending on the current menu state.

        Returns:
            bool:
                True if the screen was cleared and requires skipping
                the current loop iteration, otherwise False.
        """
        if self.show_menu == 0:
            self._draw_just_title()

        if self.show_menu == 1:
            self.draw_commands()

        elif self.show_menu == 2:
            for _ in range(8):
                print(" "*70)
            self.show_menu = 0
            if self.show_configs == 1:
                for _ in range(8):
                    print(" "*50)
                self.show_configs = 0
            return True

        return False

    def _show_configs(self) -> bool:
        """
        Handle configuration panel visibility and rendering state.

        Displays the maze configuration panel, hides it, or clears
        the configuration area depending on the current state.

        Returns:
            bool:
                True if the screen was cleared and requires skipping
                the current loop iteration, otherwise False.
        """
        if self.show_configs == 1 and self.show_menu == 1:
            self._draw_configs()

        elif self.show_configs == 2:
            for _ in range(8):
                print(" "*50)
            self.show_configs = 0
            return True

        return False

    def _draw_configs(self) -> None:
        """
        Render the maze configuration details.

        Displays maze size, entry and exit positions, random seed,
        generation algorithm, and whether the maze is perfect.
        """
        wall = self.draw_set["cell_left_wall"]
        sp = " "*6

        print(f"{sp}{self.draw_set['up_left_n_w_corner']}")
        print(f"{sp}{wall} Maze Dimensions: ({self.width}, {self.height})")

        positions = self.generator.get_entry_exit_positions()
        print(f"{sp}{wall} Entry Point: {positions[0]}")

        print(f"{sp}{wall} Exit Point: {positions[1]}")

        print(f"{sp}{wall} SEED: {self.generator._seed}")

        print(f"{sp}{wall} Algorithm used: "
              f"{self.generator._strategy.__class__.__name__}")

        print(f"{sp}{wall} Perfect: {self.perfect} ")

        print(sp + self.draw_set["bot_left_w_s_corner"])

    def _draw_just_title(self) -> None:
        """
        Render only the decorative title container.

        Draws the title frame without displaying the command menu.
        """
        print(" "*5, end="")
        line = (self.draw_set["bot_left_w_s_corner"] +
                ((self.draw_set["up_n_ne_wall"] * (5) +
                  self.draw_set["up_n_ne_wall"][-1]) * 2) +
                self.draw_set["up_n_ne_wall"][:2] +
                self.draw_set["up_n_e_ne_wall"][-1] +
                self.draw_set["up_n_ne_wall"][:2] * 5 +
                self.draw_set["up_n_e_ne_wall"][-1] +
                self.draw_set["up_n_ne_wall"][:2] * 3 +
                self.draw_set["bot_right_e_s_corner"])
        print(line)

        self._print_title()

    def draw_commands(self) -> None:
        """
        Render the command help menu.

        Displays all available keyboard shortcuts and command
        descriptions used during runtime interaction.
        """
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
              "  q.quit" + " "*6)
        print(f"{s}i.Toggle Imperfect  {wall}  f.Toggle Solution {wall}"
              "  p.Toggle Exit/Entry")
        print(f"{s}j.Animate Imperfect {wall}  o.Animate BFS     {wall}"
              "  g.Animate DFS/PRIM")
        print(f"{s}w.Swap Algorithm    {wall}  y.Show Configs    {wall}"
              "  z.Stop Animation")
        print(" "*5, end="")

        line = (self.draw_set["bot_left_w_s_corner"] +
                ((self.draw_set["up_n_ne_wall"] * (5) +
                  self.draw_set["bot_s_e_es_wall"][-1]) * 2) +
                self.draw_set["up_n_ne_wall"][:2] +
                self.draw_set["up_n_e_ne_wall"][-1] +
                self.draw_set["up_n_ne_wall"][:2] * 5 +
                self.draw_set["up_n_e_ne_wall"][-1] +
                self.draw_set["up_n_ne_wall"][:2] * 3 +
                self.draw_set["bot_right_e_s_corner"])
        print(line)

        self._print_title()

    def _print_title(self) -> None:
        """
        Print the project title banner.

        Displays the styled “A-Maze-Ing” title using the current
        wall color theme and active drawing set.
        """
        wall = self.draw_set["cell_w_wall"].strip()

        title = (" "*50 + wall + self.BOLD + self.colors["wall"]
                 + "A-Maze-Ing" + self.RESET + wall)
        print(title)

        line = (" "*50 + self.draw_set["bot_left_w_s_corner"] +
                self.draw_set["up_n_ne_wall"][:2] * (5) +
                self.draw_set["bot_right_e_s_corner"])
        print(line)

    def draw_map(self) -> None:
        """
        Render the complete maze.

        Draws the top border, middle rows, final row, and bottom
        border of the maze.
        """
        self.print_top_container()
        self.print_mid_cells()
        self.print_last_cells()
        print()

    def print_top_container(self) -> None:
        """
        Render the top border of the maze.

        Dynamically determines which wall and corner characters
        should be displayed based on the maze structure.
        """
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
        """
        Render all middle maze rows.

        Prints each cell row together with its separator row
        until reaching the final maze row.
        """
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
        """
        Generate the separator row between two maze rows.

        Builds the connecting walls between row ``y`` and row
        ``y + 1`` using the current drawing set.

        Args:
            y:
                Index of the upper row.

        Returns:
            str:
                The rendered separator row.
        """
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
        """
        Render the final maze row and bottom border.

        Also displays the lower menu section when the command
        menu is enabled.
        """
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
        """
        Render a single maze cell.

        Applies different visual styles depending on whether the cell
        is part of the path, solution, entry/exit points, animation
        state, or a fully closed cell.

        Args:
            x:
                Cell horizontal position.

            y:
                Cell vertical position.

            is_last_col:
                Whether the cell is in the last column.

            is_last_row:
                Whether the cell is in the final row.

        Returns:
            str:
                The fully rendered terminal string for the cell.
        """
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
            border = self.draw_set["cell_left_wall"] if has_east\
                else " "

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
        """
        Check whether a cell is fully enclosed.

        A cell is considered closed when all four directional
        walls are present.

        Args:
            x:
                Cell horizontal position.

            y:
                Cell vertical position.

        Returns:
            bool:
                True if the cell is fully closed, otherwise False.
        """
        cell = self.coded[y][x]
        return all(cell & (1 << d) for d in [self.N, self.E, self.W, self.S])

    def define_params(self) -> None:
        """
        Load the currently selected drawing style and color theme.

        Updates internal references to the active drawing set
        and ANSI color configuration.
        """
        self.draw_set = choose_drawing_set(self.style_param)
        self.colors = choose_color_set(self.color_param)

    def _stop_animation(self) -> bool:
        """
        Stop all active animations and restore the maze state.

        Clears animation generators, disables animation flags,
        resets temporary path rendering, and restores the maze
        to its normal state.

        If the maze is currently imperfect, the imperfect layout
        is restored after stopping the animation.

        Returns:
            bool:
                Always returns True to continue program execution.
        """
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
        """
        Process a keyboard command.

        Applies actions such as changing colors or styles,
        toggling solutions, switching algorithms, starting
        animations, showing configuration panels, and quitting.

        Args:
            key:
                The pressed keyboard key.

        Returns:
            bool:
                False only when the quit command is triggered,
                otherwise True.
        """
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
        """
        Read and process user input.

        Handles different input behavior depending on whether
        an animation is currently running. Supports pausing,
        stopping animations, and standard runtime commands.

        Returns:
            bool:
                False when the program should terminate,
                otherwise True.
        """
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
        return self.handle_key(key)

    @staticmethod
    def getch() -> str:
        """
        Read a single character from standard input.

        This is a blocking input operation and waits until
        the user presses a key.

        Returns:
            str:
                The pressed key.
        """
        return sys.stdin.read(1)

    @staticmethod
    def getch_nonblocking() -> str | None:
        """
        Read a single character without blocking execution.

        Checks whether input is available before attempting
        to read from standard input.

        Returns:
            str | None:
                The pressed key if available, otherwise None.
        """
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if ready:
            return sys.stdin.read(1)
        return None
