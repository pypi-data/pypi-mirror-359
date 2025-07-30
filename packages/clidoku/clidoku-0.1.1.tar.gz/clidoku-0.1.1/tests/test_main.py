import io
from unittest.mock import MagicMock, patch

import pytest

from src.clidoku.enums import Difficulty
from src.clidoku.logging_config import setup_logging
from src.clidoku.main import handle_add, handle_check, handle_new, handle_remove, handle_show, main, parser


class TestMain:
    """Test suite for main.py module focusing on CLI parsing and command routing."""

    def test_main_no_command_shows_help_when_no_game(self, capsys):
        """Test that main() shows help when no command is provided and no game exists."""
        # Mock has_in_progress_game to return False (no existing game)
        with patch("src.clidoku.main.has_in_progress_game", return_value=False):
            with patch("sys.argv", ["clidoku"]):
                main()

        captured = capsys.readouterr()
        assert "usage: clidoku" in captured.out
        assert "Available commands" in captured.out

    @patch("src.clidoku.main.Game")
    def test_main_no_command_shows_game_when_exists(self, mock_game):
        """Test that main() shows current game when no command is provided and game exists."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        # Mock has_in_progress_game to return True (existing game)
        with patch("src.clidoku.main.has_in_progress_game", return_value=True):
            with patch("sys.argv", ["clidoku"]):
                main()

        # Should have called Game() and display()
        mock_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_main_with_show_command(self, mock_game):
        """Test that main() routes show command to handle_show correctly."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "show"]):
            main()

        mock_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_main_with_ls_command(self, mock_game):
        """Test that main() routes ls (alias for show) command correctly."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "ls"]):
            main()

        mock_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_main_with_new_command(self, mock_game):
        """Test that main() routes new command to handle_new correctly."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "new"]):
            main()

        mock_game.assert_called_once_with(reset=True, grid_size=9, difficulty=Difficulty.MEDIUM)
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_main_with_new_command_yes_flag(self, mock_game):
        """Test that main() routes new command with -y flag correctly."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "new", "-y"]):
            main()

        mock_game.assert_called_once_with(reset=True, grid_size=9, difficulty=Difficulty.MEDIUM)
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_main_with_add_command(self, mock_game):
        """Test that main() routes add command and modifies game grid."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "add", "a0", "5"]):
            with patch("src.clidoku.main.handle_add") as mock_handle_add:
                main()

        mock_handle_add.assert_called_once_with("a0", 5)

    @patch("src.clidoku.main.Game")
    def test_main_with_remove_command(self, mock_game):
        """Test that main() routes remove command and clears cell."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "remove", "a0"]):
            with patch("src.clidoku.main.handle_remove") as mock_handle_remove:
                main()

        mock_handle_remove.assert_called_once_with("a0")

    @patch("src.clidoku.main.Game")
    def test_main_with_rm_command(self, mock_game):
        """Test that main() routes rm (alias for remove) command and clears cell."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "rm", "a0"]):
            with patch("src.clidoku.main.handle_remove") as mock_handle_remove:
                main()

        mock_handle_remove.assert_called_once_with("a0")

    # Tests for individual handler functions
    @patch("src.clidoku.main.Game")
    def test_handle_new_with_yes_flag(self, mock_game):
        """Test handle_new function with yes=True parameter."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        handle_new(yes=True)

        mock_game.assert_called_once_with(reset=True, grid_size=9, difficulty=Difficulty.MEDIUM)
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_new_without_yes_flag(self, mock_game):
        """Test handle_new function with yes=False parameter."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        handle_new(yes=False)

        mock_game.assert_called_once_with(reset=True, grid_size=9, difficulty=Difficulty.MEDIUM)
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_new_with_custom_difficulty_and_grid_size(self, mock_game):
        """Test handle_new function with custom difficulty and grid size parameters."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        handle_new(yes=False, grid_size=4, difficulty=Difficulty.HARD)

        mock_game.assert_called_once_with(reset=True, grid_size=4, difficulty=Difficulty.HARD)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_new_with_easy_difficulty(self, mock_game):
        """Test handle_new function with easy difficulty."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        handle_new(yes=True, difficulty=Difficulty.EASY)

        mock_game.assert_called_once_with(reset=True, grid_size=9, difficulty=Difficulty.EASY)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_new_displays_logo(self, mock_game):
        """Test handle_new function displays ASCII logo and credits."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        # Capture logging output
        output_stream = io.StringIO()
        setup_logging(output_stream=output_stream)

        handle_new(yes=True)

        output = output_stream.getvalue()
        assert "██████╗██╗     ██╗██████╗  ██████╗ ██╗  ██╗██╗   ██╗" in output
        assert "A simple command-line sudoku game" in output
        assert "github.com" in output

    @patch("src.clidoku.main.Game")
    def test_handle_show(self, mock_game):
        """Test handle_show function creates and displays game."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        handle_show()

        mock_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_add_sets_cell_value(self, mock_game):
        """Test handle_add function loads game, sets cell value, saves and displays."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed (user-added cell)
        mock_grid.is_cell_fixed.return_value = False

        # Mock the game as incomplete (default behavior)
        mock_game_instance.is_complete.return_value = False

        handle_add("a0", 5)

        # Should load existing game, set grid cell, save, and display
        mock_game.assert_called_once()
        mock_grid.__setitem__.assert_called_once_with("a0", 5)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

        # Verify completion methods were not called for incomplete game
        mock_game_instance.get_completion_time.assert_not_called()
        mock_game_instance.get_move_count.assert_not_called()

    @patch("src.clidoku.main.Game")
    def test_handle_add_with_different_parameters(self, mock_game):
        """Test handle_add function with different cell and value parameters."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed (user-added cell)
        mock_grid.is_cell_fixed.return_value = False

        # Mock the game as incomplete (default behavior)
        mock_game_instance.is_complete.return_value = False

        handle_add("b1", 9)

        mock_game.assert_called_once()
        mock_grid.__setitem__.assert_called_once_with("b1", 9)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_add_edge_cases(self, mock_game):
        """Test handle_add function with edge case values."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cells as not fixed (user-added cells)
        mock_grid.is_cell_fixed.return_value = False

        # Mock the game as incomplete (default behavior)
        mock_game_instance.is_complete.return_value = False

        # Test with minimum value
        handle_add("a0", 1)
        mock_grid.__setitem__.assert_called_with("a0", 1)

        # Test with maximum value
        handle_add("i8", 9)
        mock_grid.__setitem__.assert_called_with("i8", 9)

        # Should have been called twice total
        assert mock_game.call_count == 2
        assert mock_game_instance.save_game.call_count == 2
        assert mock_game_instance.display.call_count == 2

    @patch("src.clidoku.main.Game")
    def test_handle_add_via_put_alias(self, mock_game):
        """Test that put alias calls handle_add function correctly."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed (user-added cell)
        mock_grid.is_cell_fixed.return_value = False

        # Mock the game as incomplete (default behavior)
        mock_game_instance.is_complete.return_value = False

        # Test that put command works the same as add
        handle_add("d4", 6)

        mock_game.assert_called_once()
        mock_grid.__setitem__.assert_called_once_with("d4", 6)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_remove_clears_cell_value(self, mock_game):
        """Test handle_remove function loads game, clears cell value, saves and displays."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed (user-added cell)
        mock_grid.is_cell_fixed.return_value = False

        handle_remove("a0")

        # Should load existing game, clear grid cell (set to None), save, and display
        mock_game.assert_called_once()
        mock_grid.__setitem__.assert_called_once_with("a0", None)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_remove_with_different_parameters(self, mock_game):
        """Test handle_remove function with different cell parameters."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed (user-added cell)
        mock_grid.is_cell_fixed.return_value = False

        handle_remove("i8")

        mock_game.assert_called_once()
        mock_grid.__setitem__.assert_called_once_with("i8", None)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_remove_edge_cases(self, mock_game):
        """Test handle_remove function with edge case cell positions."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cells as not fixed (user-added cells)
        mock_grid.is_cell_fixed.return_value = False

        # Test with corner cells
        handle_remove("a0")  # top-left
        mock_grid.__setitem__.assert_called_with("a0", None)

        handle_remove("i8")  # bottom-right
        mock_grid.__setitem__.assert_called_with("i8", None)

        # Should have been called twice total
        assert mock_game.call_count == 2
        assert mock_game_instance.save_game.call_count == 2
        assert mock_game_instance.display.call_count == 2

    # Tests for argument parser configuration and validation
    def test_parser_help_message(self, capsys):
        """Test that parser shows correct help message with all commands."""
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

        captured = capsys.readouterr()
        assert "clidoku" in captured.out
        assert "A simple command-line sudoku game" in captured.out
        assert "new" in captured.out
        assert "show" in captured.out
        assert "add" in captured.out
        assert "put" in captured.out
        assert "remove" in captured.out
        assert "ls" in captured.out
        assert "rm" in captured.out
        assert "check" in captured.out
        assert "validate" in captured.out

    def test_parser_new_command(self):
        """Test parser correctly parses new command with default flag."""
        args = parser.parse_args(["new"])
        assert args.command == "new"
        assert args.y is False
        assert hasattr(args, "func")

    def test_parser_new_command_with_y_flag(self):
        """Test parser correctly parses new command with -y flag."""
        args = parser.parse_args(["new", "-y"])
        assert args.command == "new"
        assert args.y is True
        assert hasattr(args, "func")

    def test_parser_show_command(self):
        """Test parser correctly parses show command."""
        args = parser.parse_args(["show"])
        assert args.command == "show"
        assert hasattr(args, "func")

    def test_parser_ls_command(self):
        """Test parser correctly parses ls command (alias for show)."""
        args = parser.parse_args(["ls"])
        assert args.command == "ls"
        assert hasattr(args, "func")

    def test_parser_add_command(self):
        """Test parser correctly parses add command with cell and value arguments."""
        args = parser.parse_args(["add", "a0", "5"])
        assert args.command == "add"
        assert args.cell == "a0"
        assert args.val == 5
        assert hasattr(args, "func")

    def test_parser_add_command_different_values(self):
        """Test parser correctly parses add command with different valid inputs."""
        args = parser.parse_args(["add", "b1", "9"])
        assert args.command == "add"
        assert args.cell == "b1"
        assert args.val == 9

    def test_parser_put_command(self):
        """Test parser correctly parses put command (alias for add) with cell and value arguments."""
        args = parser.parse_args(["put", "c2", "7"])
        assert args.command == "put"
        assert args.cell == "c2"
        assert args.val == 7
        assert hasattr(args, "func")

    def test_parser_remove_command(self):
        """Test parser correctly parses remove command with cell argument."""
        args = parser.parse_args(["remove", "a0"])
        assert args.command == "remove"
        assert args.cell == "a0"
        assert hasattr(args, "func")

    def test_parser_rm_command(self):
        """Test parser correctly parses rm command (alias for remove) with cell argument."""
        args = parser.parse_args(["rm", "c2"])
        assert args.command == "rm"
        assert args.cell == "c2"
        assert hasattr(args, "func")

    def test_parser_check_command(self):
        """Test parser correctly parses check command."""
        args = parser.parse_args(["check"])
        assert args.command == "check"
        assert hasattr(args, "func")

    def test_parser_validate_command(self):
        """Test parser correctly parses validate command (alias for check)."""
        args = parser.parse_args(["validate"])
        assert args.command == "validate"
        assert hasattr(args, "func")

    def test_parser_invalid_command(self):
        """Test parser raises SystemExit for invalid command."""
        with pytest.raises(SystemExit):
            parser.parse_args(["invalid"])

    def test_parser_add_missing_cell_argument(self):
        """Test parser raises SystemExit when add command missing cell argument."""
        with pytest.raises(SystemExit):
            parser.parse_args(["add"])

    def test_parser_add_missing_value_argument(self):
        """Test parser raises SystemExit when add command missing value argument."""
        with pytest.raises(SystemExit):
            parser.parse_args(["add", "a0"])

    def test_parser_add_invalid_value_type(self):
        """Test parser raises SystemExit when add command has non-integer value."""
        with pytest.raises(SystemExit):
            parser.parse_args(["add", "a0", "not_a_number"])

    def test_parser_remove_missing_cell_argument(self):
        """Test parser raises SystemExit when remove command missing cell argument."""
        with pytest.raises(SystemExit):
            parser.parse_args(["remove"])

    def test_parser_rm_missing_cell_argument(self):
        """Test parser raises SystemExit when rm command missing cell argument."""
        with pytest.raises(SystemExit):
            parser.parse_args(["rm"])

    def test_parser_no_arguments(self):
        """Test parser handles no arguments (should set command to None)."""
        args = parser.parse_args([])
        assert args.command is None

    def test_parser_new_command_with_difficulty_and_grid_size(self):
        """Test parser correctly parses new command with difficulty and grid-size arguments."""
        args = parser.parse_args(["new", "--difficulty", "hard", "--grid-size", "4"])
        assert args.command == "new"
        assert args.y is False
        assert args.difficulty == Difficulty.HARD
        assert args.grid_size == 4
        assert hasattr(args, "func")

    def test_parser_new_command_with_difficulty_only(self):
        """Test parser correctly parses new command with only difficulty argument."""
        args = parser.parse_args(["new", "--difficulty", "easy"])
        assert args.command == "new"
        assert args.difficulty == Difficulty.EASY
        assert args.grid_size == 9  # default
        assert hasattr(args, "func")

    def test_parser_new_command_with_grid_size_only(self):
        """Test parser correctly parses new command with only grid-size argument."""
        args = parser.parse_args(["new", "--grid-size", "4"])
        assert args.command == "new"
        assert args.difficulty == Difficulty.MEDIUM  # default
        assert args.grid_size == 4
        assert hasattr(args, "func")

    def test_parser_new_command_invalid_grid_size_non_integer(self):
        """Test parser raises SystemExit for non-integer grid-size argument."""
        with pytest.raises(SystemExit):
            parser.parse_args(["new", "--grid-size", "not_a_number"])

    def test_parser_new_command_invalid_grid_size_negative(self):
        """Test parser raises SystemExit for negative grid-size argument."""
        with pytest.raises(SystemExit):
            parser.parse_args(["new", "--grid-size", "-1"])

    def test_parser_new_command_invalid_grid_size_zero(self):
        """Test parser raises SystemExit for zero grid-size argument."""
        with pytest.raises(SystemExit):
            parser.parse_args(["new", "--grid-size", "0"])

    def test_parser_new_command_invalid_grid_size_too_large(self):
        """Test parser raises SystemExit for grid-size exceeding maximum."""
        with pytest.raises(SystemExit):
            parser.parse_args(["new", "--grid-size", "16"])  # Assuming max is 9

    @patch("src.clidoku.main.Game")
    def test_handle_add_shows_success_message_when_game_complete(self, mock_game):
        """Test handle_add shows success message when game is completed."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed (user-added cell)
        mock_grid.is_cell_fixed.return_value = False

        # Mock the game as complete
        mock_game_instance.is_complete.return_value = True

        # Mock the new completion methods
        mock_game_instance.get_completion_time.return_value = "2 minutes 30 seconds"
        mock_game_instance.get_move_count.return_value = 15

        # Capture logging output
        output_stream = io.StringIO()
        setup_logging(output_stream=output_stream)

        handle_add("a0", 5)

        # Verify the completion methods were called
        mock_game_instance.get_completion_time.assert_called_once()
        mock_game_instance.get_move_count.assert_called_once()

        # Verify success message appears (without checking exact formatting)
        output = output_stream.getvalue()
        assert "You've completed the game!" in output
        assert "To start a new game" in output

    @patch("src.clidoku.main.Game")
    def test_handle_add_no_success_message_when_game_incomplete(self, mock_game):
        """Test handle_add does not show success message when game is not complete."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed (user-added cell)
        mock_grid.is_cell_fixed.return_value = False

        # Mock the game as incomplete
        mock_game_instance.is_complete.return_value = False

        # Capture logging output
        output_stream = io.StringIO()
        setup_logging(output_stream=output_stream)

        handle_add("a0", 5)

        output = output_stream.getvalue()
        assert "You've completed the game!" not in output
        assert "To start a new game, run: clidoku new" not in output

    @patch("src.clidoku.main.Game")
    def test_handle_remove_prevents_removing_fixed_cells(self, mock_game):
        """Test handle_remove prevents removing fixed (starting) cells."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as fixed
        mock_grid.is_cell_fixed.return_value = True

        # Capture logging output
        output_stream = io.StringIO()
        setup_logging(output_stream=output_stream)

        handle_remove("a0")

        # Should not have set the cell to None or saved the game
        mock_grid.__setitem__.assert_not_called()
        mock_game_instance.save_game.assert_not_called()

        # Should still display the grid to show current state
        mock_game_instance.display.assert_called_once()

        # Should have logged an error message
        output = output_stream.getvalue()
        assert "Cannot remove cell a0: it's a starting cell and cannot be changed" in output

    @patch("src.clidoku.main.Game")
    def test_handle_remove_allows_removing_non_fixed_cells(self, mock_game):
        """Test handle_remove allows removing non-fixed (user-added) cells."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed
        mock_grid.is_cell_fixed.return_value = False

        handle_remove("a0")

        # Should have set the cell to None, saved, and displayed
        mock_grid.__setitem__.assert_called_once_with("a0", None)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_add_prevents_overriding_fixed_cells(self, mock_game):
        """Test handle_add prevents overriding fixed (starting) cells."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as fixed
        mock_grid.is_cell_fixed.return_value = True

        # Capture logging output
        output_stream = io.StringIO()
        setup_logging(output_stream=output_stream)

        handle_add("a0", 5)

        # Should not have set the cell value or saved the game
        mock_grid.__setitem__.assert_not_called()
        mock_game_instance.save_game.assert_not_called()

        # Should still display the grid to show current state
        mock_game_instance.display.assert_called_once()

        # Should have logged an error message
        output = output_stream.getvalue()
        assert "Cannot add to cell a0: it's a starting cell and cannot be changed" in output

    @patch("src.clidoku.main.Game")
    def test_handle_add_allows_overriding_non_fixed_cells(self, mock_game):
        """Test handle_add allows overriding non-fixed (user-added) cells."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_grid = MagicMock()
        mock_game_instance.grid = mock_grid

        # Mock the cell as not fixed
        mock_grid.is_cell_fixed.return_value = False

        # Mock the game as incomplete (default behavior)
        mock_game_instance.is_complete.return_value = False

        handle_add("a0", 5)

        # Should have set the cell value, saved, and displayed
        mock_grid.__setitem__.assert_called_once_with("a0", 5)
        mock_game_instance.save_game.assert_called_once()
        mock_game_instance.display.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_main_with_check_command(self, mock_game):
        """Test that main() routes check command to handle_check correctly."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "check"]):
            with patch("src.clidoku.main.handle_check") as mock_handle_check:
                main()

        mock_handle_check.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_main_with_validate_command(self, mock_game):
        """Test that main() routes validate (alias for check) command correctly."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance

        with patch("sys.argv", ["clidoku", "validate"]):
            with patch("src.clidoku.main.handle_check") as mock_handle_check:
                main()

        mock_handle_check.assert_called_once()

    @patch("src.clidoku.main.Game")
    def test_handle_check_with_valid_grid(self, mock_game):
        """Test handle_check function with a valid grid."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_game_instance.check_game.return_value = True

        # Mock has_in_progress_game to return True
        with patch("src.clidoku.main.has_in_progress_game", return_value=True):
            # Capture logging output
            output_stream = io.StringIO()
            setup_logging(output_stream=output_stream)

            handle_check()

            # Should load game, check validity, and display
            mock_game.assert_called_once()
            mock_game_instance.check_game.assert_called_once()
            mock_game_instance.display.assert_called_once()

            # Should show valid message
            output = output_stream.getvalue()
            assert "✓ Grid is valid - no rule violations detected" in output

    @patch("src.clidoku.main.Game")
    def test_handle_check_with_invalid_grid(self, mock_game):
        """Test handle_check function with an invalid grid."""
        mock_game_instance = MagicMock()
        mock_game.return_value = mock_game_instance
        mock_game_instance.check_game.return_value = False

        # Mock has_in_progress_game to return True
        with patch("src.clidoku.main.has_in_progress_game", return_value=True):
            # Capture logging output
            output_stream = io.StringIO()
            setup_logging(output_stream=output_stream)

            handle_check()

            # Should load game, check validity, and display
            mock_game.assert_called_once()
            mock_game_instance.check_game.assert_called_once()
            mock_game_instance.display.assert_called_once()

            # Should show invalid message
            output = output_stream.getvalue()
            assert "✗ Grid has rule violations - check for duplicate numbers in rows, columns, or boxes" in output

    def test_handle_check_no_game_in_progress(self):
        """Test handle_check function when no game is in progress."""
        # Mock has_in_progress_game to return False
        with patch("src.clidoku.main.has_in_progress_game", return_value=False):
            # Capture logging output
            output_stream = io.StringIO()
            setup_logging(output_stream=output_stream)

            handle_check()

            # Should show error message
            output = output_stream.getvalue()
            assert "No game in progress. Start a new game with: clidoku new" in output

    @staticmethod
    def _parse_version(version: str) -> bool:
        """Parse the version string and return True if valid-ish."""
        return bool(len(version.split(".")) == 3)

    # Tests for version flag functionality
    def test_parser_version_flag(self, capsys):
        """Test that --version flag displays version and exits."""
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        # Should exit with code 0 (success)
        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        # Should display version from pyproject.toml
        assert self._parse_version(captured.out.strip()), "Version output should be in format x.y.z"

    def test_parser_version_short_flag(self, capsys):
        """Test that -v flag displays version and exits."""
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["-v"])

        # Should exit with code 0 (success)
        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        # Should display version from pyproject.toml
        assert self._parse_version(captured.out.strip()), "Version output should be in format x.y.z"

    def test_main_with_version_flag(self, capsys):
        """Test that main() handles --version flag correctly."""
        with pytest.raises(SystemExit) as exc_info:
            with patch("sys.argv", ["clidoku", "--version"]):
                main()

        # Should exit with code 0 (success)
        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        # Should display version from pyproject.toml
        assert self._parse_version(captured.out.strip()), "Version output should be in format x.y.z"
