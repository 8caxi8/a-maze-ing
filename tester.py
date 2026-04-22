from maze_drawer import MazeDrawer
from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from mazegen import MazeGenerator


def main() -> None:
    gen = MazeGenerator()

    try:
        map: MapConfig = parser()
        maze = gen.generate_maze(map.width, map.height)
        #maze = gen.make_imperfect(maze, map.width, map.height, probability=1)
        drawer = MazeDrawer(maze)
        drawer.draw_map()
    except ParserError as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
