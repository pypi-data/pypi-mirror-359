import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from src.clidoku.enums import Difficulty
from src.clidoku.game import Game, Move
from src.clidoku.grid import Grid


class TestGame:
    SAVE_FILE = "test.savegame.jsonl"

    def test_save_file_path(self):
        """Test save_file_path property and directory creation."""
        game = Game()
        assert isinstance(game.save_file_path, Path)
        assert ".clidoku" in str(game.save_file_path)
        assert str(game.save_file_path).endswith("savegame.jsonl")

        game = Game(save_file="test_tmp.jsonl")
        assert isinstance(game.save_file_path, Path)
        assert ".clidoku" in str(game.save_file_path)
        assert str(game.save_file_path).endswith("test_tmp.jsonl")

    def test_save_file_path_creates_directory(self):
        """Test that save_file_path creates the save directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the SAVE_PATH to point to a non-existent directory
            test_save_path = Path(temp_dir) / "test_clidoku"
            assert not test_save_path.exists()

            with patch.object(Game, "SAVE_PATH", test_save_path):
                game = Game()
                # Accessing save_file_path should create the directory
                save_path = game.save_file_path
                assert test_save_path.exists()
                assert save_path == test_save_path / Game.SAVE_FILE

    def test_init_with_reset_true(self):
        """Test Game initialization with reset=True."""
        game = Game(reset=True)
        assert hasattr(game, "grid")
        assert hasattr(game, "history")
        assert hasattr(game, "started_at")
        assert game.grid.check_grid()  # Should be a valid puzzle

    def test_init_with_existing_save_file(self):
        """Test Game initialization loading from existing save file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
            # Create a proper save file using the Move serialization
            grid = Grid()
            grid[0] = 5  # Add a test value
            move = Move(grid=grid, moved_at=datetime.now(UTC))
            temp_file.write(json.dumps(move.to_dict()))
            temp_file.flush()

            try:
                # Mock the save_file_path property to return our temp file
                with patch.object(
                    Game, "save_file_path", new_callable=lambda: property(lambda _: Path(temp_file.name))
                ):
                    game = Game(reset=False)
                    assert len(game.history) == 1
                    assert game.started_at is not None
                    assert game.grid[0] == 5  # Verify the data was loaded
            finally:
                Path(temp_file.name).unlink()

    def test_gen_game_success(self):
        """Test successful game generation."""
        grid = Grid()
        Game.gen_game(grid)
        assert grid.check_grid()
        # Should have some empty cells after generation
        empty_cells = grid.empty_cells()
        assert len(empty_cells) > 0

    def test_gen_game_failure_raises_runtime_error(self):
        """Test that gen_game raises RuntimeError when generation fails."""
        grid = Grid()
        # Mock _gen_game_simple to always return False (failure)
        with patch.object(Game, "_gen_game_simple", return_value=False):
            with pytest.raises(RuntimeError, match="Couldn't generate game"):
                Game.gen_game(grid)

    def test_load_game_from_file(self):
        """Test loading a game from a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
            # Create multiple moves using proper serialization
            grid1 = Grid()
            grid1[0] = 5
            move1 = Move(grid=grid1, moved_at=datetime.now(UTC))

            grid2 = Grid()
            grid2[0] = 5
            grid2[1] = 7
            move2 = Move(grid=grid2, moved_at=datetime.now(UTC))

            # Write both moves to file
            temp_file.write(json.dumps(move1.to_dict()) + "\n")
            temp_file.write(json.dumps(move2.to_dict()))
            temp_file.flush()

            try:
                game = Game(reset=True)
                game.load_game(Path(temp_file.name))

                # Should have loaded both moves
                assert len(game.history) == 2
                assert game.started_at is not None
                # The grid should be from the last move
                assert game.grid[0] == 5
                assert game.grid[1] == 7
            finally:
                Path(temp_file.name).unlink()

    def test_load_game_empty_file_restarts(self):
        """Test that loading from empty file triggers restart."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
            # Create empty file
            temp_file.flush()

            try:
                game = Game(reset=True)  # Start with a game
                with patch.object(game, "restart") as mock_restart:
                    game.load_game(Path(temp_file.name))
                    mock_restart.assert_called_once()
            finally:
                Path(temp_file.name).unlink()

    def test_save_game_to_file(self):
        """Test saving a game to a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
            try:
                game = Game(reset=True)
                game.grid[0] = 5  # Make a test move
                game.save_game(Path(temp_file.name))

                # Verify file was written and has content
                assert Path(temp_file.name).exists()
                with Path(temp_file.name).open() as f:
                    content = f.read().strip()
                    assert content  # Should have content
                    data = json.loads(content)
                    assert "grid" in data
                    assert "moved_at" in data
                    assert data["grid"]["data"][0] == 5
            finally:
                Path(temp_file.name).unlink()

    def test_save_game_default_path(self):
        """Test saving a game to default path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the save path to use our temp directory
            test_save_path = Path(temp_dir) / ".clidoku"
            with patch.object(Game, "SAVE_PATH", test_save_path):
                game = Game(reset=True)
                game.grid[0] = 5  # Make a test move
                game.save_game()  # No file_path argument - should use default

                # Verify file was created at default location
                expected_file = test_save_path / Game.SAVE_FILE
                assert expected_file.exists()

                # Verify content
                with expected_file.open() as f:
                    content = f.read().strip()
                    data = json.loads(content)
                    assert data["grid"]["data"][0] == 5

    def test_save_load_roundtrip(self):
        """Test complete save/load roundtrip functionality."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
            try:
                # Create a game with specific state
                game1 = Game(reset=True)
                game1.grid[0] = 5
                game1.grid[10] = 7
                game1.grid[20] = 3
                original_grid_size = game1.grid.grid_size

                # Save the game
                game1.save_game(Path(temp_file.name))

                # Create a new game and load the saved state
                game2 = Game(reset=True)  # Start with different state
                game2.load_game(Path(temp_file.name))

                # Verify the state was restored correctly
                assert game2.grid[0] == 5
                assert game2.grid[10] == 7
                assert game2.grid[20] == 3
                assert game2.grid.grid_size == original_grid_size
                assert len(game2.history) == 1
                assert game2.started_at is not None

                # Verify the grids are equivalent
                assert list(game2.grid) == list(game1.grid)
            finally:
                Path(temp_file.name).unlink()

    def test_save_load_multiple_moves(self):
        """Test saving and loading multiple moves in sequence."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
            try:
                # Create initial game state
                game = Game(reset=True)
                game.grid[0] = 5
                game.save_game(Path(temp_file.name))

                # Make another move and append to file
                game.grid[1] = 7
                move2 = Move(grid=game.grid, moved_at=datetime.now(UTC))
                with Path(temp_file.name).open("a") as f:
                    f.write("\n" + json.dumps(move2.to_dict()))

                # Load the game and verify both moves
                new_game = Game(reset=True)
                new_game.load_game(Path(temp_file.name))

                assert len(new_game.history) == 2
                assert new_game.grid[0] == 5
                assert new_game.grid[1] == 7
                assert new_game.started_at is not None
            finally:
                Path(temp_file.name).unlink()

    def test_restart_creates_new_game(self):
        """Test that restart creates a new valid game."""
        game = Game(reset=True)
        original_started_at = game.started_at

        # Wait a tiny bit to ensure different timestamp
        import time

        time.sleep(0.001)

        game.restart(grid_size=9)  # Explicitly pass grid_size to avoid None issue
        assert game.started_at != original_started_at
        assert game.grid.check_grid()
        assert len(game.history) == 0

    def test_restart_with_custom_grid_size(self):
        """Test restart with custom grid size."""
        game = Game(reset=True)
        game.restart(grid_size=4)
        assert game.grid.grid_size == 4
        assert game.grid.check_grid()

    def test_clear_resets_state(self):
        """Test that clear resets game state."""
        game = Game(reset=True)
        # Add some history
        game.history.append(Move(grid=Grid(), moved_at=datetime.now(UTC)))

        game.clear(grid_size=9)  # Explicitly pass grid_size to avoid None issue
        assert len(game.history) == 0
        assert game.grid.grid_size == 9

    def test_clear_with_custom_grid_size(self):
        """Test clear with custom grid size."""
        game = Game(reset=True)
        game.clear(grid_size=4)
        assert game.grid.grid_size == 4
        assert len(game.history) == 0

    def test_check_game_delegates_to_grid(self):
        """Test that check_game delegates to grid.check_grid()."""
        game = Game(reset=True)
        with patch.object(game.grid, "check_grid", return_value=True) as mock_check:
            result = game.check_game()
            assert result is True
            mock_check.assert_called_once()

    def test_is_complete_with_complete_valid_game(self, valid_complete_sudoku):
        """Test is_complete returns True for a complete, valid sudoku."""
        game = Game(reset=True)
        game.grid = valid_complete_sudoku

        assert game.is_complete() is True

    def test_is_complete_with_incomplete_game(self, valid_incomplete_sudoku):
        """Test is_complete returns False for an incomplete sudoku."""
        game = Game(reset=True)
        game.grid = valid_incomplete_sudoku

        assert game.is_complete() is False

    def test_is_complete_with_invalid_complete_game(self, invalid_row_conflict):
        """Test is_complete returns False for a complete but invalid sudoku."""
        game = Game(reset=True)
        game.grid = invalid_row_conflict

        assert game.is_complete() is False

    def test_is_complete_with_empty_grid(self, empty_grid):
        """Test is_complete returns False for an empty grid."""
        game = Game(reset=True)
        game.grid = empty_grid

        assert game.is_complete() is False

    def test_get_completion_time_with_recent_start(self):
        """Test get_completion_time returns formatted time for recent game start."""
        game = Game(reset=True)
        # Set started_at to a few seconds ago
        game.started_at = datetime.now(UTC) - timedelta(seconds=30)

        completion_time = game.get_completion_time()
        assert "30 seconds" in completion_time

    def test_get_completion_time_with_minutes(self):
        """Test get_completion_time returns formatted time with minutes."""
        game = Game(reset=True)
        # Set started_at to 2 minutes 30 seconds ago
        game.started_at = datetime.now(UTC) - timedelta(minutes=2, seconds=30)

        completion_time = game.get_completion_time()
        assert "2 minutes 30 seconds" in completion_time

    def test_get_completion_time_with_hours(self):
        """Test get_completion_time returns formatted time with hours."""
        game = Game(reset=True)
        # Set started_at to 1 hour 30 minutes 45 seconds ago
        game.started_at = datetime.now(UTC) - timedelta(hours=1, minutes=30, seconds=45)

        completion_time = game.get_completion_time()
        assert "1 hours 30 minutes 45 seconds" in completion_time

    def test_get_completion_time_no_start_time(self):
        """Test get_completion_time returns 'Unknown' when started_at is None."""
        game = Game(reset=True)
        game.started_at = None

        completion_time = game.get_completion_time()
        assert completion_time == "Unknown"

    def test_get_move_count_new_game(self):
        """Test get_move_count returns 0 for a new game with only initial state."""
        game = Game(reset=True)
        # Simulate saving the initial game state (like handle_new does)
        game.save_game()
        # New game should have 1 move in history (initial state) = 0 user moves
        assert game.get_move_count() == 0

    def test_get_move_count_with_user_moves(self):
        """Test get_move_count returns correct count after user moves."""
        game = Game(reset=True)

        # Simulate saving the initial game state (like handle_new does)
        game.save_game()

        # Simulate user moves by modifying grid and saving (like handle_add does)
        game.grid[0] = 1
        game.save_game()  # First user move

        game.grid[1] = 2
        game.save_game()  # Second user move

        # Should have 2 user moves (total 3 moves - 1 initial = 2)
        assert game.get_move_count() == 2

    def test_get_move_count_empty_history(self):
        """Test get_move_count returns 0 when history is empty."""
        game = Game(reset=True)
        game.history = []

        assert game.get_move_count() == 0

    def test_display_prints_grid(self):
        """Test that display prints the grid."""
        import io

        from src.clidoku.logging_config import setup_logging

        # Capture logging output
        output_stream = io.StringIO()
        setup_logging(output_stream=output_stream)

        game = Game(reset=True)
        game.display()

        output = output_stream.getvalue()
        assert output  # Should have logged something
        # The output should contain grid representation
        assert len(output.strip()) > 0

    def test_remove_cells_reduces_filled_cells(self, valid_complete_sudoku):
        """Test that remove_cells reduces the number of filled cells in the grid."""
        # Count initial filled cells
        initial_filled = sum(1 for cell in valid_complete_sudoku if cell is not None)
        assert initial_filled == 81  # Complete 9x9 grid should have all cells filled

        # Remove cells
        Game.remove_cells(valid_complete_sudoku)

        # Count remaining filled cells
        final_filled = sum(1 for cell in valid_complete_sudoku if cell is not None)
        assert final_filled < initial_filled
        assert final_filled > 0  # Should not remove all cells

    def test_remove_cells_maintains_valid_sudoku_constraints(self, valid_complete_sudoku):
        """Test that remove_cells maintains valid sudoku constraints in remaining cells."""
        # Remove cells
        Game.remove_cells(valid_complete_sudoku)

        # Verify the remaining filled cells still form a valid partial sudoku
        assert valid_complete_sudoku.check_grid() is True

    def test_remove_cells_easy_difficulty(self, valid_complete_sudoku):
        """Test that easy difficulty removes fewer cells (easier puzzle)."""
        Game.remove_cells(valid_complete_sudoku, difficulty=Difficulty.EASY)

        filled_cells = sum(1 for cell in valid_complete_sudoku if cell is not None)
        # Easy puzzles should have more filled cells (typically 45-55 for 9x9)
        assert filled_cells >= 45
        assert filled_cells <= 55

    def test_remove_cells_medium_difficulty(self, valid_complete_sudoku):
        """Test that medium difficulty removes moderate number of cells."""
        Game.remove_cells(valid_complete_sudoku, difficulty=Difficulty.MEDIUM)

        filled_cells = sum(1 for cell in valid_complete_sudoku if cell is not None)
        # Medium puzzles should have moderate filled cells (typically 35-45 for 9x9)
        assert filled_cells >= 35
        assert filled_cells <= 45

    def test_remove_cells_hard_difficulty(self, valid_complete_sudoku):
        """Test that hard difficulty removes more cells (harder puzzle)."""
        Game.remove_cells(valid_complete_sudoku, difficulty=Difficulty.HARD)

        filled_cells = sum(1 for cell in valid_complete_sudoku if cell is not None)
        # Hard puzzles should have fewer filled cells (typically 25-35 for 9x9)
        assert filled_cells >= 25
        assert filled_cells <= 35

    def test_remove_cells_invalid_difficulty_raises_error(self, valid_complete_sudoku):
        """Test that invalid difficulty parameter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid difficulty 'invalid'"):
            Game.remove_cells(valid_complete_sudoku, difficulty="invalid")

    def test_remove_cells_string_difficulty_conversion(self, valid_complete_sudoku):
        """Test that string difficulty values are properly converted to enum."""
        Game.remove_cells(valid_complete_sudoku, difficulty="easy")

        filled_cells = sum(1 for cell in valid_complete_sudoku if cell is not None)
        # Should behave like Difficulty.EASY
        assert filled_cells >= 45
        assert filled_cells <= 55

    def test_remove_cells_preserves_grid_structure(self, valid_complete_sudoku):
        """Test that remove_cells preserves the grid structure and size."""
        original_length = len(valid_complete_sudoku)
        original_grid_size = valid_complete_sudoku.grid_size

        Game.remove_cells(valid_complete_sudoku)

        # Grid structure should remain unchanged
        assert len(valid_complete_sudoku) == original_length
        assert valid_complete_sudoku.grid_size == original_grid_size

    def test_remove_cells_4x4_grid(self):
        """Test remove_cells works with smaller 4x4 grids."""
        from src.clidoku.grid import Grid

        # Create a valid 4x4 sudoku solution
        grid_data = [1, 2, 3, 4, 3, 4, 1, 2, 2, 1, 4, 3, 4, 3, 2, 1]
        grid = Grid(grid=grid_data)

        Game.remove_cells(grid, difficulty=Difficulty.MEDIUM)

        filled_cells = sum(1 for cell in grid if cell is not None)
        # Should remove some but not all cells (medium difficulty: 8-10 for 4x4)
        assert filled_cells < 16  # Less than complete
        assert filled_cells >= 8  # At least 8 cells remain
        assert filled_cells <= 10  # At most 10 cells remain
        assert grid.check_grid() is True  # Still valid

    def test_gen_game_marks_starting_cells_as_fixed(self):
        """Test that gen_game marks all starting cells as fixed."""
        from src.clidoku.grid import Grid

        grid = Grid(grid_size=4)
        Game.gen_game(grid, difficulty=Difficulty.EASY)

        # Check all cells and verify filled ones are marked as fixed
        for row_idx, row in enumerate(grid.ROWS):
            for col in grid.COLS:
                cell_position = f"{row}{col}"
                cell_idx = row_idx * grid.grid_size + col

                if grid[cell_idx] is not None:
                    # Filled cells should be marked as fixed
                    assert grid.is_cell_fixed(cell_position) is True
                else:
                    # Empty cells should not be marked as fixed
                    assert grid.is_cell_fixed(cell_position) is False

    def test_move_serialization_includes_fixed_cells(self):
        """Test that Move serialization includes fixed cells information."""
        from src.clidoku.grid import Grid

        # Create a grid with some fixed cells
        grid = Grid(grid_size=4)
        grid["a0"] = 1
        grid["a1"] = 2
        grid.mark_cell_as_fixed("a0")
        grid.mark_cell_as_fixed("a1")

        # Create a move and serialize it
        move = Move(grid=grid, moved_at=datetime.now(UTC))
        move_dict = move.to_dict()

        # Check that fixed cells are included in serialization
        assert "fixed_cells" in move_dict["grid"]
        assert "a0" in move_dict["grid"]["fixed_cells"]
        assert "a1" in move_dict["grid"]["fixed_cells"]

        # Test deserialization preserves fixed cells
        restored_move = Move.from_dict(move_dict)
        assert restored_move.grid.is_cell_fixed("a0") is True
        assert restored_move.grid.is_cell_fixed("a1") is True
        assert restored_move.grid.is_cell_fixed("a2") is False

    def test_remove_cells_minimum_cells_constraint(self, valid_complete_sudoku):
        """Test that remove_cells respects minimum cells needed for solvability."""
        Game.remove_cells(valid_complete_sudoku, difficulty=Difficulty.HARD)

        filled_cells = sum(1 for cell in valid_complete_sudoku if cell is not None)
        # Should never remove so many cells that puzzle becomes unsolvable
        # Minimum for 9x9 sudoku is typically around 17-25 cells
        assert filled_cells >= 17

    def test_remove_cells_distribution_across_boxes(self, valid_complete_sudoku):
        """Test that remove_cells distributes removals across all 3x3 boxes."""
        Game.remove_cells(valid_complete_sudoku)

        # Check that each 3x3 box has at least one filled cell
        for box_row in range(3):
            for box_col in range(3):
                box_has_filled_cell = False
                for row in range(box_row * 3, (box_row + 1) * 3):
                    for col in range(box_col * 3, (box_col + 1) * 3):
                        idx = row * 9 + col
                        if valid_complete_sudoku[idx] is not None:
                            box_has_filled_cell = True
                            break
                    if box_has_filled_cell:
                        break

                # Each box should have at least one filled cell for solvability
                assert box_has_filled_cell, f"Box ({box_row}, {box_col}) has no filled cells"

    def test_difficulty_config_custom_grid_sizes(self):
        """Test difficulty configuration for custom grid sizes."""
        # Test 6x6 grid (36 cells total)
        grid_6x6 = Grid(grid_size=6)
        # Fill it with a valid pattern for testing
        for i in range(36):
            grid_6x6[i] = (i % 6) + 1

        # Test easy difficulty on custom size
        Game.remove_cells(grid_6x6, difficulty=Difficulty.EASY)
        filled_cells = sum(1 for cell in grid_6x6 if cell is not None)
        # Should be between 55% and 70% of 36 cells = 20-25 cells
        assert 20 <= filled_cells <= 25

        # Test medium difficulty on custom size
        grid_6x6_medium = Grid(grid_size=6)
        for i in range(36):
            grid_6x6_medium[i] = (i % 6) + 1
        Game.remove_cells(grid_6x6_medium, difficulty=Difficulty.MEDIUM)
        filled_cells = sum(1 for cell in grid_6x6_medium if cell is not None)
        # Should be between 40% and 55% of 36 cells = 14-20 cells
        assert 14 <= filled_cells <= 20

        # Test hard difficulty on custom size
        grid_6x6_hard = Grid(grid_size=6)
        for i in range(36):
            grid_6x6_hard[i] = (i % 6) + 1
        Game.remove_cells(grid_6x6_hard, difficulty=Difficulty.HARD)
        filled_cells = sum(1 for cell in grid_6x6_hard if cell is not None)
        # Should be between 30% and 45% of 36 cells = 11-16 cells
        assert 11 <= filled_cells <= 16

    def test_remove_cells_excess_removals_adjustment(self):
        """Test adjustment when too many cells would be removed."""
        # Create a 4x4 grid to test edge cases more easily
        grid_data = [1, 2, 3, 4, 3, 4, 1, 2, 2, 1, 4, 3, 4, 3, 2, 1]
        grid = Grid(grid=grid_data)

        # Mock random to force many removals initially
        with patch("random.random", return_value=0.1):  # Always remove (< removal_probability)
            with patch("random.shuffle"):  # Don't shuffle to make test deterministic
                Game.remove_cells(grid, difficulty=Difficulty.EASY)

                filled_cells = sum(1 for cell in grid if cell is not None)
                # Should still respect the target range for easy difficulty (10-12 for 4x4)
                assert 10 <= filled_cells <= 12

    def test_remove_cells_insufficient_removals_adjustment(self):
        """Test adjustment when too few cells would be removed."""
        # Create a 4x4 grid
        grid_data = [1, 2, 3, 4, 3, 4, 1, 2, 2, 1, 4, 3, 4, 3, 2, 1]
        grid = Grid(grid=grid_data)

        # Mock random to force few removals initially
        with patch("random.random", return_value=0.9):  # Never remove (> removal_probability)
            with patch("random.shuffle"):  # Don't shuffle to make test deterministic
                Game.remove_cells(grid, difficulty=Difficulty.HARD)

                filled_cells = sum(1 for cell in grid if cell is not None)
                # Should still respect the target range for hard difficulty (6-8 for 4x4)
                assert 6 <= filled_cells <= 8

    def test_is_valid_placement_method(self):
        """Test the _is_valid_placement helper method."""
        grid = Grid()
        # Set up a partial grid with known values
        grid[0] = 1  # Row 0, Col 0
        grid[1] = 2  # Row 0, Col 1
        grid[9] = 3  # Row 1, Col 0

        # Test valid placement
        assert Game._is_valid_placement(grid, 2, 4)  # Row 0, Col 2 with value 4

        # Test invalid placement - row conflict
        assert not Game._is_valid_placement(grid, 2, 1)  # Row 0, Col 2 with value 1 (conflicts with grid[0])

        # Test invalid placement - column conflict
        assert not Game._is_valid_placement(grid, 18, 1)  # Row 2, Col 0 with value 1 (conflicts with grid[0])

        # Test invalid placement - box conflict
        assert not Game._is_valid_placement(grid, 10, 1)  # Row 1, Col 1 with value 1 (conflicts in same box)

    def test_get_box_cell_indices_method(self):
        """Test the _get_box_cell_indices helper method."""
        grid = Grid()  # 9x9 grid

        # Test top-left box (0,0)
        indices = Game._get_box_cell_indices(grid, 0, 0, 3)
        expected = [0, 1, 2, 9, 10, 11, 18, 19, 20]
        assert indices == expected

        # Test center box (1,1)
        indices = Game._get_box_cell_indices(grid, 1, 1, 3)
        expected = [30, 31, 32, 39, 40, 41, 48, 49, 50]
        assert indices == expected

        # Test bottom-right box (2,2)
        indices = Game._get_box_cell_indices(grid, 2, 2, 3)
        expected = [60, 61, 62, 69, 70, 71, 78, 79, 80]
        assert indices == expected

    def test_can_remove_cell_safely_method(self):
        """Test the _can_remove_cell_safely helper method."""
        grid = Grid()

        # Test removing from a box with multiple cells
        already_removing = [1, 2]  # Removing cells 1 and 2 from top-left box
        # Cell 0 is in the same box, but there are still other cells in the box
        assert Game._can_remove_cell_safely(grid, 0, already_removing, 3)

        # Test removing when it would leave box empty
        already_removing = [0, 1, 2, 9, 10, 11, 18, 19]  # Remove 8 of 9 cells from top-left box
        # Cell 20 is the last cell in the box, so it can't be safely removed
        assert not Game._can_remove_cell_safely(grid, 20, already_removing, 3)

        # Test removing from different box
        already_removing = [0, 1, 2]  # Removing from top-left box
        # Cell 30 is in a different box, so it can be safely removed
        assert Game._can_remove_cell_safely(grid, 30, already_removing, 3)


class TestMoveDataclassSerialization:
    """Test suite for Move dataclass serialization methods."""

    def test_move_to_dict(self):
        """Test Move.to_dict() method."""
        grid = Grid()
        grid[0] = 5
        grid[1] = 7
        move_time = datetime.now(UTC)
        move = Move(grid=grid, moved_at=move_time)

        result = move.to_dict()

        assert isinstance(result, dict)
        assert "grid" in result
        assert "moved_at" in result
        assert result["grid"]["grid_size"] == 9
        assert result["grid"]["data"][0] == 5
        assert result["grid"]["data"][1] == 7
        assert result["moved_at"] == move_time.isoformat()

    def test_move_from_dict(self):
        """Test Move.from_dict() method."""
        move_data = {"grid": {"grid_size": 9, "data": [5, 7] + [None] * 79}, "moved_at": "2023-01-01T12:00:00+00:00"}

        move = Move.from_dict(move_data)

        assert isinstance(move, Move)
        assert move.grid.grid_size == 9
        assert move.grid[0] == 5
        assert move.grid[1] == 7
        assert move.moved_at == datetime.fromisoformat("2023-01-01T12:00:00+00:00")

    def test_move_serialization_roundtrip(self):
        """Test that Move can be serialized and deserialized correctly."""
        # Create original move
        grid = Grid(grid_size=4)
        grid[0] = 1
        grid[5] = 3
        move_time = datetime.now(UTC)
        original_move = Move(grid=grid, moved_at=move_time)

        # Serialize to dict
        move_dict = original_move.to_dict()

        # Serialize to JSON and back
        json_str = json.dumps(move_dict)
        loaded_dict = json.loads(json_str)

        # Deserialize back to Move
        restored_move = Move.from_dict(loaded_dict)

        # Verify everything matches
        assert restored_move.grid.grid_size == original_move.grid.grid_size
        assert restored_move.grid[0] == original_move.grid[0]
        assert restored_move.grid[5] == original_move.grid[5]
        assert restored_move.moved_at == original_move.moved_at
        assert list(restored_move.grid) == list(original_move.grid)

    def test_move_direct_json_serialization_fails(self):
        """Test that Move objects cannot be directly JSON serialized."""
        grid = Grid()
        move = Move(grid=grid, moved_at=datetime.now(UTC))

        # Direct serialization should fail - this is expected behavior
        with pytest.raises(TypeError, match="not JSON serializable"):
            json.dumps(move)
