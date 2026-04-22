from maze_drawer import MazeDrawer
from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from mazegen import MazeGenerator


def main() -> None:

    try:
        map: MapConfig = parser()
        gen = MazeGenerator(map.width, map.height, 42)
        drawer = MazeDrawer(gen)
        drawer.start_engine()
    except ParserError as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
