from maze_drawer import MazeDrawer, DrawerError
from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from mazegen import MazeGenerator, MazeGeneratorError


def main() -> None:

    try:
        map: MapConfig = parser()
        gen = MazeGenerator(map.width, map.height, map.entry,
                            map.exit, map.seed, map.algorithm)
        gen.write_to_file(map.output_file)
        drawer = MazeDrawer(gen, start_logo=False)
        drawer.start_engine()
    except (ParserError, MazeGeneratorError, DrawerError) as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
