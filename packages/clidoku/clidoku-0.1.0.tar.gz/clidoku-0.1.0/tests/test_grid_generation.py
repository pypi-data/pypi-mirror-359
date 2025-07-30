"""Tests for grid generation functionality."""

from src.clidoku.game import Game
from src.clidoku.grid import Grid


class TestGridGeneration:
    """Test suite for grid generation functionality."""

    def test_grid_indexing_consistency(self):
        """Test that integer and string indexing are consistent."""
        grid = Grid()

        # Test basic indexing
        grid[0] = 5  # a0
        grid[1] = 7  # a1
        grid[9] = 3  # b0
        grid[10] = 8  # b1

        # Verify string indexing matches integer indexing
        assert grid["a0"] == 5
        assert grid["a1"] == 7
        assert grid["b0"] == 3
        assert grid["b1"] == 8

        # Verify integer indexing still works
        assert grid[0] == 5
        assert grid[1] == 7
        assert grid[9] == 3
        assert grid[10] == 8

    def test_zero_based_indexing(self):
        """Test that zero-based indexing works correctly."""
        grid = Grid()

        # Test corner cases
        grid["a0"] = 1  # Top-left
        grid["a8"] = 2  # Top-right
        grid["i0"] = 3  # Bottom-left
        grid["i8"] = 4  # Bottom-right

        # Verify they map to correct integer indices
        assert grid[0] == 1  # Row 0, Col 0
        assert grid[8] == 2  # Row 0, Col 8
        assert grid[72] == 3  # Row 8, Col 0
        assert grid[80] == 4  # Row 8, Col 8

    def test_generated_grid_is_valid(self):
        """Test that generated grids are valid sudoku solutions."""
        # Generate multiple grids to test consistency
        for _ in range(3):
            grid = Grid()
            success = Game._gen_game_simple(grid)

            assert success, "Grid generation should succeed"
            assert grid.check_grid(), "Generated grid should be valid"

            # Verify no empty cells in complete grid
            assert len(grid.empty_cells()) == 0, "Complete grid should have no empty cells"

    def test_generated_grid_has_no_duplicates(self):
        """Test that generated grids have no duplicate numbers in rows, columns, or boxes."""
        grid = Grid()
        Game._gen_game_simple(grid)

        # Check each row for duplicates
        for row_idx in range(9):
            row_values = [grid[row_idx * 9 + col] for col in range(9)]
            row_values = [v for v in row_values if v is not None]
            assert len(row_values) == len(set(row_values)), f"Row {row_idx} has duplicates: {row_values}"

        # Check each column for duplicates
        for col_idx in range(9):
            col_values = [grid[row * 9 + col_idx] for row in range(9)]
            col_values = [v for v in col_values if v is not None]
            assert len(col_values) == len(set(col_values)), f"Column {col_idx} has duplicates: {col_values}"

        # Check each 3x3 box for duplicates
        for box_row in range(3):
            for box_col in range(3):
                box_values = []
                for r in range(box_row * 3, (box_row + 1) * 3):
                    for c in range(box_col * 3, (box_col + 1) * 3):
                        box_values.append(grid[r * 9 + c])
                box_values = [v for v in box_values if v is not None]
                assert len(box_values) == len(set(box_values)), (
                    f"Box ({box_row},{box_col}) has duplicates: {box_values}"
                )

    def test_generated_grid_contains_all_numbers(self):
        """Test that generated grids contain all numbers 1-9 in each row, column, and box."""
        grid = Grid()
        Game._gen_game_simple(grid)

        expected_numbers = set(range(1, 10))

        # Check each row contains all numbers 1-9
        for row_idx in range(9):
            row_values = [grid[row_idx * 9 + col] for col in range(9)]
            assert set(row_values) == expected_numbers, (
                f"Row {row_idx} missing numbers: {expected_numbers - set(row_values)}"
            )

        # Check each column contains all numbers 1-9
        for col_idx in range(9):
            col_values = [grid[row * 9 + col_idx] for row in range(9)]
            assert set(col_values) == expected_numbers, (
                f"Column {col_idx} missing numbers: {expected_numbers - set(col_values)}"
            )

        # Check each 3x3 box contains all numbers 1-9
        for box_row in range(3):
            for box_col in range(3):
                box_values = []
                for r in range(box_row * 3, (box_row + 1) * 3):
                    for c in range(box_col * 3, (box_col + 1) * 3):
                        box_values.append(grid[r * 9 + c])
                assert set(box_values) == expected_numbers, (
                    f"Box ({box_row},{box_col}) missing numbers: {expected_numbers - set(box_values)}"
                )

    def test_is_valid_placement_method(self):
        """Test the _is_valid_placement method works correctly."""
        grid = Grid()

        # Place some numbers
        grid[0] = 5  # a0
        grid[1] = 7  # a1
        grid[9] = 3  # b0

        # Test valid placements
        assert Game._is_valid_placement(grid, 2, 1), "Should be able to place 1 at a2"
        assert Game._is_valid_placement(grid, 10, 1), "Should be able to place 1 at b1"

        # Test invalid placements (conflicts)
        assert not Game._is_valid_placement(grid, 2, 5), "Should not be able to place 5 at a2 (row conflict)"
        assert not Game._is_valid_placement(grid, 10, 7), "Should not be able to place 7 at b1 (column conflict)"
        assert not Game._is_valid_placement(grid, 10, 5), "Should not be able to place 5 at b1 (box conflict)"

    def test_game_generation_integration(self):
        """Test the full game generation process."""
        game = Game(reset=True)

        # Verify the game has a valid grid
        assert game.grid.check_grid(), "Game should have a valid grid"

        # Verify the grid has some empty cells (puzzle)
        empty_cells = game.grid.empty_cells()
        assert len(empty_cells) > 0, "Puzzle should have some empty cells"
        assert len(empty_cells) < 81, "Puzzle should not be completely empty"

        # Verify the difficulty is reasonable (not too easy, not too hard)
        assert 20 <= len(empty_cells) <= 60, f"Puzzle difficulty seems unreasonable: {len(empty_cells)} empty cells"
