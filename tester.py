from maze_drawer import MazeDrawer
from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from mazegen import MazeGenerator, MazeGeneratorError


def main() -> None:

    try:
        map: MapConfig = parser()
        gen = MazeGenerator(map.width, map.height, map.entry,
                            map.exit, 42, map.algorithm)
        drawer = MazeDrawer(gen)
        drawer.start_engine()
    except (ParserError, MazeGeneratorError) as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
