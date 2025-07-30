import argparse
from importlib.metadata import PackageNotFoundError, version

from src.clidoku.enums import Difficulty
from src.clidoku.game import Game
from src.clidoku.grid import Grid
from src.clidoku.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


def get_ascii_logo() -> str:
    """Return the ASCII art logo for clidoku."""
    return """

 ██████╗██╗     ██╗██████╗  ██████╗ ██╗  ██╗██╗   ██╗
██╔════╝██║     ██║██╔══██╗██╔═══██╗██║ ██╔╝██║   ██║
██║     ██║     ██║██║  ██║██║   ██║█████╔╝ ██║   ██║
██║     ██║     ██║██║  ██║██║   ██║██╔═██╗ ██║   ██║
╚██████╗███████╗██║██████╔╝╚██████╔╝██║  ██╗╚██████╔╝
 ╚═════╝╚══════╝╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝

    A simple command-line sudoku game
    https://github.com/barneyjackson/clidoku
"""


def get_credits() -> str:
    return """
    Created by Barney Jackson, 2025
    Licensed under the BSD 3-Clause License
"""


def get_version() -> str:
    """Get the version of the clidoku package."""
    try:
        return version("clidoku")
    except PackageNotFoundError:
        # Fallback for development/testing when package isn't installed
        return "0.1.0"


def get_success_ascii(completion_time: str = "", move_count: int = 0) -> str:
    """Return the ASCII art for successful game completion."""
    base_message = """

 ██████╗ ██████╗ ███╗   ██╗ ██████╗ ██████╗  █████╗ ████████╗███████╗██╗
██╔════╝██╔═══██╗████╗  ██║██╔════╝ ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║
██║     ██║   ██║██╔██╗ ██║██║  ███╗██████╔╝███████║   ██║   ███████╗██║
██║     ██║   ██║██║╚██╗██║██║   ██║██╔══██╗██╔══██║   ██║   ╚════██║╚═╝
╚██████╗╚██████╔╝██║ ╚████║╚██████╔╝██║  ██║██║  ██║   ██║   ███████║██╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝

    🎉 You've completed the game! 🎉"""

    if completion_time and move_count > 0:
        base_message += f"""

    Time to complete:\t{completion_time}
    Moves to complete:\t{move_count}\n"""

    return base_message


def validate_grid_size(value: str) -> int:
    """Validate grid size argument for argparse."""
    try:
        grid_size = int(value)
    except ValueError as err:
        raise argparse.ArgumentTypeError(f"Grid size must be an integer, got '{value}'") from err

    if grid_size < 1:
        raise argparse.ArgumentTypeError(f"Grid size must be positive, got {grid_size}")
    if grid_size > Grid.MAX_GRID_SIZE:
        raise argparse.ArgumentTypeError(f"Grid size {grid_size} exceeds maximum supported size {Grid.MAX_GRID_SIZE}")

    return grid_size


def has_in_progress_game() -> bool:
    """Check if there is an in-progress game save file."""
    save_path = Game.SAVE_PATH / Game.SAVE_FILE
    # Check if file exists and has content (not empty)
    if not save_path.exists():
        return False

    try:
        # Try to read the file and see if it has valid content
        with save_path.open() as f:
            content = f.read().strip()
            return len(content) > 0
    except OSError:
        return False


def handle_new(yes: bool, grid_size: int = 9, difficulty: Difficulty = Difficulty.MEDIUM) -> None:  # noqa: ARG001
    """Create and display a new sudoku game."""
    logger.info(get_ascii_logo() + get_credits())
    game = Game(reset=True, grid_size=grid_size, difficulty=difficulty)
    game.save_game()  # Save the new game so it can be loaded later
    logger.info(f"New {difficulty.value} {grid_size}x{grid_size} game:")
    game.display()


def handle_show() -> None:
    """Load and display the current sudoku game."""
    game = Game()

    # Show info about the most recent move if history exists
    if game.history:
        latest_move = game.history[-1]
        # Format timestamp to be more readable
        timestamp = latest_move.moved_at.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Most recent move at {timestamp}:")

    game.display()


def handle_add(cell: str, val: int) -> None:
    """Add a value to a specific cell in the sudoku grid."""
    game = Game()

    # Check if the cell is fixed (starting cell)
    if game.grid.is_cell_fixed(cell):
        logger.error(f"Cannot add to cell {cell}: it's a starting cell and cannot be changed")
        game.display()
        return

    game.grid[cell] = val
    game.save_game()
    logger.info(f"Added {cell} = {val}:")
    game.display()

    # Check if game is complete after this move
    if game.is_complete():
        completion_time = game.get_completion_time()
        move_count = game.get_move_count()
        logger.info(get_success_ascii(completion_time, move_count))
        logger.info("To start a new game, run: clidoku new")


def handle_remove(cell: str) -> None:
    """Remove a value from a specific cell in the sudoku grid."""
    game = Game()

    # Check if the cell is fixed (starting cell)
    if game.grid.is_cell_fixed(cell):
        logger.error(f"Cannot remove cell {cell}: it's a starting cell and cannot be changed")
        game.display()
        return

    game.grid[cell] = None
    game.save_game()
    logger.info(f"Cleared cell {cell}:")
    game.display()


def handle_check() -> None:
    """Check if the current grid state is valid according to sudoku rules."""
    if not has_in_progress_game():
        logger.error("No game in progress. Start a new game with: clidoku new")
        return

    game = Game()
    is_valid = game.check_game()

    if is_valid:
        logger.info("✓ Grid is valid - no rule violations detected")
    else:
        logger.info("✗ Grid has rule violations - check for duplicate numbers in rows, columns, or boxes")

    game.display()


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that shows logo only for help, not for errors."""

    def format_help(self) -> str:
        """Format help with ASCII logo at the top."""
        return get_ascii_logo() + get_credits() + "\n" + super().format_help()

    def format_usage(self) -> str:
        """Format usage without ASCII logo for error messages."""
        return super().format_usage()


# Create the top-level parser with custom class
parser = CustomArgumentParser(prog="clidoku", description="A simple command-line sudoku game.")

# Add version argument
parser.add_argument("--version", "-v", action="version", version=f"clidoku {get_version()}")

subparsers = parser.add_subparsers(dest="command", help="Available commands")

# 'new' command with optional '-y' flag and difficulty/grid-size options
new_parser = subparsers.add_parser("new", help="Start a new game")
new_parser.add_argument("-y", action="store_true", help="Confirm automatically")
new_parser.add_argument(
    "--difficulty",
    type=Difficulty,
    choices=list(Difficulty),
    default=Difficulty.MEDIUM,
    help="Difficulty level (default: medium)",
)
new_parser.add_argument(
    "--grid-size", type=validate_grid_size, default=9, help=f"Grid size (default: 9, max: {Grid.MAX_GRID_SIZE})"
)
new_parser.set_defaults(func=lambda args: handle_new(args.y, args.grid_size, args.difficulty))

# 'show' command and 'ls' alias
show_parser = subparsers.add_parser("show", help="Show the current game grid")
show_parser.set_defaults(func=lambda _: handle_show())
subparsers.add_parser("ls", help="Alias for show").set_defaults(func=lambda _: handle_show())

# 'add' command and 'put' alias with 'cell' (string) and 'val' (integer) arguments
add_parser = subparsers.add_parser("add", help="Fill a grid cell with a value")
add_parser.add_argument("cell", type=str, help='Cell, eg "a0" (rows a-i, cols 0-8)')
add_parser.add_argument("val", type=int, help="Value, 1-9")
add_parser.set_defaults(func=lambda args: handle_add(args.cell, args.val))
put_parser = subparsers.add_parser("put", help="Alias for add")
put_parser.add_argument("cell", type=str, help='Cell, eg "a0" (rows a-i, cols 0-8)')
put_parser.add_argument("val", type=int, help="Value, 1-9")
put_parser.set_defaults(func=lambda args: handle_add(args.cell, args.val))

# 'remove' command and 'rm' alias with 'cell' argument
remove_parser = subparsers.add_parser("remove", help="Remove a value from a cell")
remove_parser.add_argument("cell", type=str, help='Cell, eg "a0" (rows a-i, cols 0-8)')
remove_parser.set_defaults(func=lambda args: handle_remove(args.cell))
rm_parser = subparsers.add_parser("rm", help="Remove a value from a cell")
rm_parser.add_argument("cell", type=str, help='Cell, eg "a0" (rows a-i, cols 0-8)')
rm_parser.set_defaults(func=lambda args: handle_remove(args.cell))

# 'check' command and 'validate' alias
check_parser = subparsers.add_parser("check", help="Check if the current grid is valid")
check_parser.set_defaults(func=lambda _: handle_check())
validate_parser = subparsers.add_parser("validate", help="Alias for check")
validate_parser.set_defaults(func=lambda _: handle_check())


def main() -> None:
    """Main entry point for the clidoku CLI application."""
    # Set up logging first
    setup_logging()

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        # Smart default behavior: show game if one exists, otherwise show help
        if has_in_progress_game():
            handle_show()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
