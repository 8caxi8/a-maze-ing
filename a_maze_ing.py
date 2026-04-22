from maze_drawer import MazeDrawer
from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from mazegen import MazeGenerator, MazeGeneratorError


def main() -> None:

    try:
        map: MapConfig = parser()
        gen = MazeGenerator(map.width, map.height, map.entry,
                            map.exit, 42, map.algorithm)
        gen.print_encoded_maze()
        drawer = MazeDrawer(gen.maze)
        drawer.draw_map()
        path = gen.find_shortest_path()
        print(path)
        print(gen.get_path_directions())
        gen.write_to_file("output.txt")
    except (ParserError, MazeGeneratorError) as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
