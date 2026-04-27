def choose_color_set(param: int) -> dict[str, str]:
    """
    Return a predefined ANSI color configuration for maze rendering.

    This function provides multiple color themes used for displaying
    the maze, project title, and path visualization inside the terminal.

    Each color set includes ANSI RGB escape codes for:

    - wall
    - closed
    - path
    - last_pos
    - entry_pos
    - exit_pos

    Available styles include:

    - 0: Default warm theme
    - 1: Blue/green theme
    - 2: Orange/blue contrast theme
    - 3: Cyan/purple theme
    - 4: Minimal grayscale theme
    - 5: Strong pink/gold theme

    Special behavior:
        If ``param == -1``, the function returns a dictionary
        containing the total number of available color sets:

        ``{"size": "<number_of_sets>"}``

    Args:
        param (int):
            The color set identifier.

    Returns:
        dict[str, str]:
            A dictionary containing ANSI escape sequences for
            terminal coloring.

            If the provided value does not exist, the default
            color set (style 0) is returned.
    """
    def rgb(r: int, g: int, b: int) -> str:
        """
        Generate an ANSI RGB foreground color escape sequence.

        Uses 24-bit terminal color formatting to create
        custom RGB text colors.

        Args:
            r (int):
                Red channel value (0–255).

            g (int):
                Green channel value (0–255).

            b (int):
                Blue channel value (0–255).

        Returns:
            str:
                ANSI escape sequence for the given RGB color.
        """
        return f"\033[38;2;{r};{g};{b}m"

    COLOR_SETS = {
        0: {
            "wall": rgb(255, 200, 0),
            "closed": rgb(220, 50, 50),
            "path": rgb(180, 130, 0),
            "last_pos": rgb(255, 255, 255),
            "entry_pos": rgb(50, 220, 50),
            "exit_pos": rgb(220, 50, 50),
        },
        1: {
            "wall": rgb(50, 120, 255),
            "closed": rgb(50, 220, 50),
            "path": rgb(50, 200, 220),
            "last_pos": rgb(255, 255, 255),
            "entry_pos": rgb(50, 220, 50),
            "exit_pos": rgb(220, 50, 50),
        },
        2: {
            "wall": rgb(255, 140, 0),
            "closed": rgb(255, 255, 255),
            "path": rgb(50, 120, 255),
            "last_pos": rgb(220, 50, 50),
            "entry_pos": rgb(50, 220, 50),
            "exit_pos": rgb(220, 50, 50),
        },
        3: {
            "wall": rgb(0, 200, 180),
            "closed": rgb(255, 255, 255),
            "path": rgb(180, 50, 220),
            "last_pos": rgb(220, 50, 50),
            "entry_pos": rgb(50, 220, 50),
            "exit_pos": rgb(220, 50, 50),
        },
        4: {
            "wall": rgb(255, 255, 255),
            "closed": rgb(20, 20, 20),
            "path": rgb(211, 211, 211),
            "last_pos": rgb(255, 255, 255),
            "entry_pos": rgb(250, 250, 250),
            "exit_pos": rgb(50, 50, 50),
        },
        5: {
            "wall": rgb(224, 17, 95),
            "closed": rgb(255, 215, 0),
            "path": rgb(105, 20, 13),
            "last_pos": rgb(227, 185, 13),
            "entry_pos": rgb(250, 250, 250),
            "exit_pos": rgb(50, 50, 50),
        },
    }

    def return_size() -> dict[str, str]:
        """
        Return the total number of available color sets.

        Uses the enclosing ``COLOR_SETS`` dictionary to calculate
        how many themes are currently supported.

        Returns:
            dict[str, str]:
                Dictionary containing the number of color sets
                in the format:

                ``{"size": "<count>"}``
        """
        return {"size": str(len(COLOR_SETS.keys()))}

    if param == -1:
        return return_size()

    return COLOR_SETS.get(param, COLOR_SETS[0])
