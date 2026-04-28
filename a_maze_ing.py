from maze_drawer import MazeDrawer, DrawerError
from parser.map_model import MapConfig
from parser.parser import ParserError, parser
from mazegen import MazeGenerator, MazeGeneratorError


def main() -> None:
    """
    Execute the main application workflow.

    This function parses the configuration file, generates the maze,
    writes the encoded maze to the output file, and starts the
    interactive terminal drawer.

    The workflow is:

    1. Read and validate configuration values
    2. Create the maze generator instance
    3. Generate and save the maze output file
    4. Launch the terminal visualization engine

    Handled exceptions include parser errors, maze generation errors,
    and terminal drawing errors.

    Raises:
        Exception:
            Any unexpected exception not explicitly handled here
            is propagated to the outer ``__main__`` block.
    """
    try:
        map: MapConfig = parser()

        gen = MazeGenerator(map.width, map.height, map.entry,
                            map.exit, map.seed, map.algorithm, map.perfect)
        gen.write_to_file(map.output_file)

        drawer = MazeDrawer(gen, start_logo=True)
        drawer.start_engine()
    except (ParserError, MazeGeneratorError, DrawerError) as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
