from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from parser.drawer import draw_map
from mazegen import MazeGenerator


def main() -> None:
    gen = MazeGenerator()

    try:
        map: MapConfig = parser()
        map_tiles = gen.generate_maze(map.width, map.height)
        draw_map(map_tiles)
    except ParserError as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
