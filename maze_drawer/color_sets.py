def choose_color_set(param: int) -> dict[str, str]:
    def rgb(r: int, g: int, b: int) -> str:
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
        nonlocal COLOR_SETS
        return {"size": str(len(COLOR_SETS.keys()))}

    if param == -1:
        return return_size()

    return COLOR_SETS.get(param, COLOR_SETS[0])
