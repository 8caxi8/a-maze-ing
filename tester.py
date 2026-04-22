from maze_drawer import MazeDrawer
from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from mazegen import MazeGenerator


def main() -> None:

    try:
        map: MapConfig = parser()
        gen = MazeGenerator(map.width, map.height)
        drawer = MazeDrawer(gen.maze)
        drawer.draw_map()
    except ParserError as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
