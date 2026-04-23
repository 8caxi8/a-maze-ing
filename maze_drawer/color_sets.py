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

    def return_size() -> dict[str, str]:
        nonlocal COLOR_SETS
        return {"size": str(len(COLOR_SETS.keys()))}

    if param == -1:
        return return_size()

    return COLOR_SETS.get(param, COLOR_SETS[0])
