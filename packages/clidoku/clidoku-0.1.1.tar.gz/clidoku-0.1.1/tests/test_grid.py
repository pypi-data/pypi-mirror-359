import random

import pytest

from src.clidoku.grid import Grid


class TestGrid:
    def test___init__(self):
        grid = Grid()
        assert grid == [None] * grid.DEFAULT_GRID_SIZE * grid.DEFAULT_GRID_SIZE
        assert len(grid.NUMBERS) == grid.DEFAULT_GRID_SIZE
        assert len(grid.ROWS) == grid.DEFAULT_GRID_SIZE
        assert all(isinstance(r, str) for r in grid.ROWS)
        assert len(grid.COLS) == grid.DEFAULT_GRID_SIZE
        assert all(isinstance(c, int) for c in grid.COLS)

        random_grid = random.choices(range(1, 10), k=(9**2))
        grid = Grid(grid=random_grid)
        assert grid == random_grid

    def test___repr__(self, grid_random_9x9):
        print(grid_random_9x9)

        grid_random_9x9[2] = None
        print(grid_random_9x9)

    def test___getitem__(self):
        test_grid = [1, 2, 3, 4]
        grid = Grid(grid=test_grid)

        assert grid[1] == test_grid[1]
        assert grid["a0"] == test_grid[0]  # "a0" should map to index 0 (row a=0, col 0=0)
        assert grid["A0"] == test_grid[0]  # Same as "a0"
        assert grid["0a"] == test_grid[0]  # Same as "a0"
        with pytest.raises(TypeError):
            grid[True]
        with pytest.raises(TypeError):
            grid[None]
        with pytest.raises(TypeError):
            grid[1.0]
        with pytest.raises(IndexError):
            grid[11]

    def test__parse_index(self):
        test_grid = [1, 2, 3, 4]
        grid = Grid(grid=test_grid)

        assert grid["a0"] == grid["0a"]
        assert grid["a0"] == grid["A0"]
        with pytest.raises(ValueError):
            grid["a"]
        with pytest.raises(ValueError):
            grid["1"]
        with pytest.raises(ValueError):
            grid["abc"]
        with pytest.raises(ValueError):
            grid["123"]
        with pytest.raises(IndexError):
            grid["C0"]
        with pytest.raises(ValueError):
            grid["CC"]

    def test_empty_cells(self):
        grid = Grid(grid=[1, 2, 3, 4])
        assert grid.empty_cells() == []

        grid = Grid(grid=[1, 2, None, 4])
        assert grid.empty_cells() == [2]

    def test_row_bump(self):
        grid = Grid(grid=[1, 2, 3, 4])
        assert grid.row_bump("a") == 0
        assert grid.row_bump("a") == grid.row_bump("A")

    def test_check_grid__complete(self, valid_complete_sudoku):
        """Test validation of a complete, valid 9x9 sudoku grid."""
        assert valid_complete_sudoku.check_grid() is True

    def test_check_grid__incomplete(self, valid_incomplete_sudoku):
        """Test validation of a partially filled grid with no conflicts."""
        assert valid_incomplete_sudoku.check_grid() is True

    def test_check_grid__invalid(self, invalid_row_conflict):
        """Test validation of grids with sudoku rule violations."""
        assert invalid_row_conflict.check_grid() is False

    def test_check_grid__row_conflict(self, invalid_row_conflict):
        """Test validation fails when there are duplicate numbers in the same row."""
        assert invalid_row_conflict.check_grid() is False

    def test_check_grid__column_conflict(self, invalid_column_conflict):
        """Test validation fails when there are duplicate numbers in the same column."""
        assert invalid_column_conflict.check_grid() is False

    def test_check_grid__box_conflict(self, invalid_box_conflict):
        """Test validation fails when there are duplicate numbers in the same 3x3 box."""
        assert invalid_box_conflict.check_grid() is False

    def test_check_grid__empty_grid(self, empty_grid):
        """Test validation of completely empty grid (should be valid)."""
        assert empty_grid.check_grid() is True

    def test_check_grid__invalid_numbers(self, grid_with_invalid_numbers):
        """Test validation fails when grid contains numbers outside 1-9 range."""
        assert grid_with_invalid_numbers.check_grid() is False

    def test_check_grid__single_cell_valid(self):
        """Test validation of a single-cell grid with valid number."""
        grid = Grid(grid=[1])
        assert grid.check_grid() is True

    def test_check_grid__single_cell_invalid(self):
        """Test validation of a single-cell grid with invalid number."""
        grid = Grid(grid=[0])
        assert grid.check_grid() is False

    def test_check_grid__single_cell_empty(self):
        """Test validation of a single-cell grid that is empty."""
        grid = Grid(grid=[None])
        assert grid.check_grid() is True

    def test_check_grid__4x4_valid(self):
        """Test validation of a valid 4x4 grid (2x2 boxes)."""
        # Valid 4x4 sudoku solution
        grid_data = [1, 2, 3, 4, 3, 4, 1, 2, 2, 1, 4, 3, 4, 3, 2, 1]
        grid = Grid(grid=grid_data)
        assert grid.check_grid() is True

    def test_check_grid__4x4_invalid_row(self):
        """Test validation of a 4x4 grid with row conflict."""
        # Invalid 4x4 grid with duplicate in row
        grid_data = [
            1,
            2,
            3,
            1,  # Row conflict: two 1s
            3,
            4,
            1,
            2,
            2,
            1,
            4,
            3,
            4,
            3,
            2,
            1,
        ]
        grid = Grid(grid=grid_data)
        assert grid.check_grid() is False

    def test_check_grid__specific_row_violations(self):
        """Test validation catches violations in specific rows."""
        # Create a grid with conflicts in different rows
        base_grid = [None] * 81

        # Row 0: duplicate 5s at positions 0 and 8
        base_grid[0] = 5
        base_grid[8] = 5
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

        # Row 4: duplicate 3s at positions 36 and 44
        base_grid = [None] * 81
        base_grid[36] = 3  # Row 4, Col 0
        base_grid[44] = 3  # Row 4, Col 8
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

    def test_check_grid__specific_column_violations(self):
        """Test validation catches violations in specific columns."""
        # Create a grid with conflicts in different columns
        base_grid = [None] * 81

        # Column 0: duplicate 7s at positions 0 and 72
        base_grid[0] = 7  # Row 0, Col 0
        base_grid[72] = 7  # Row 8, Col 0
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

        # Column 8: duplicate 2s at positions 8 and 80
        base_grid = [None] * 81
        base_grid[8] = 2  # Row 0, Col 8
        base_grid[80] = 2  # Row 8, Col 8
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

    def test_check_grid__specific_box_violations(self):
        """Test validation catches violations in specific 3x3 boxes."""
        # Test each of the 9 boxes for conflicts
        base_grid = [None] * 81

        # Top-left box (0,0): duplicate 4s at positions 0 and 10
        base_grid[0] = 4  # Row 0, Col 0
        base_grid[10] = 4  # Row 1, Col 1
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

        # Center box (1,1): duplicate 6s at positions 30 and 40
        base_grid = [None] * 81
        base_grid[30] = 6  # Row 3, Col 3
        base_grid[40] = 6  # Row 4, Col 4
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

        # Bottom-right box (2,2): duplicate 9s at positions 60 and 80
        base_grid = [None] * 81
        base_grid[60] = 9  # Row 6, Col 6
        base_grid[80] = 9  # Row 8, Col 8
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

    def test_check_grid__boundary_numbers(self):
        """Test validation with boundary valid numbers (1 and 9)."""
        base_grid = [None] * 81

        # Test with all 1s in different positions (should be invalid due to conflicts)
        base_grid[0] = 1
        base_grid[1] = 1  # Same row conflict
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is False

        # Test with valid placement of 1 and 9
        base_grid = [None] * 81
        base_grid[0] = 1  # Row 0, Col 0
        base_grid[80] = 9  # Row 8, Col 8 (different row, column, and box)
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is True

    def test_check_grid__multiple_violations(self):
        """Test validation with multiple types of violations simultaneously."""
        # Grid with row, column, and box violations
        grid_data = [
            5,
            3,
            4,
            6,
            7,
            8,
            9,
            1,
            5,  # Row conflict: two 5s
            6,
            5,
            2,
            1,
            9,
            5,
            3,
            4,
            8,  # Box conflict: 5 in same box as position 0
            1,
            9,
            8,
            3,
            4,
            2,
            5,
            6,
            7,
            8,
            5,
            9,
            7,
            6,
            1,
            4,
            2,
            3,
            4,
            2,
            6,
            8,
            5,
            3,
            7,
            9,
            1,
            7,
            1,
            3,
            9,
            2,
            4,
            8,
            5,
            6,
            9,
            6,
            1,
            5,
            3,
            7,
            2,
            8,
            4,
            2,
            8,
            7,
            4,
            1,
            9,
            6,
            3,
            5,
            5,
            4,
            5,
            2,
            8,
            6,
            1,
            7,
            9,  # Column conflict: 5 in same column as position 0
        ]
        grid = Grid(grid=grid_data)
        assert grid.check_grid() is False

    def test_check_grid__partial_fill_valid(self):
        """Test validation with various partial fill patterns that are valid."""
        # Diagonal pattern
        base_grid = [None] * 81
        for i in range(9):
            base_grid[i * 9 + i] = i + 1  # Diagonal: 1,2,3,4,5,6,7,8,9
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is True

        # Single number in each box
        base_grid = [None] * 81
        base_grid[0] = 1  # Top-left box
        base_grid[5] = 2  # Top-center box
        base_grid[8] = 3  # Top-right box
        base_grid[27] = 4  # Middle-left box
        base_grid[40] = 5  # Center box
        base_grid[35] = 6  # Middle-right box
        base_grid[54] = 7  # Bottom-left box
        base_grid[77] = 8  # Bottom-center box
        base_grid[80] = 9  # Bottom-right box
        grid = Grid(grid=base_grid)
        assert grid.check_grid() is True

    def test_grid_constructor_with_none_grid_size(self):
        """Test that Grid constructor handles None grid_size properly."""
        grid = Grid(grid_size=None)
        assert grid.grid_size == 9  # Should default to DEFAULT_GRID_SIZE
        assert len(grid) == 81
        assert all(cell is None for cell in grid)

    def test_fixed_cells_initialization(self):
        """Test that fixed_cells set is properly initialized."""
        grid = Grid()
        assert isinstance(grid.fixed_cells, set)
        assert len(grid.fixed_cells) == 0

    def test_mark_cell_as_fixed(self):
        """Test marking cells as fixed using string position."""
        grid = Grid(grid_size=4)

        # Mark cell 'a0' as fixed
        grid.mark_cell_as_fixed("a0")
        assert grid.is_cell_fixed("a0") is True
        assert grid.is_cell_fixed("a1") is False

    def test_mark_cell_as_fixed_invalid_position(self):
        """Test that marking invalid cell positions raises ValueError."""
        grid = Grid(grid_size=4)

        # Test invalid positions
        with pytest.raises(ValueError, match="Invalid cell position"):
            grid.mark_cell_as_fixed("z9")  # Invalid row/col

    def test_mark_all_filled_cells_as_fixed(self):
        """Test marking all filled cells as fixed."""
        grid = Grid(grid_size=4)

        # Fill some cells
        grid["a0"] = 1
        grid["a1"] = 2
        grid["b1"] = 3

        # Mark all filled cells as fixed
        grid.mark_all_filled_cells_as_fixed()

        # Check that filled cells are fixed
        assert grid.is_cell_fixed("a0") is True
        assert grid.is_cell_fixed("a1") is True
        assert grid.is_cell_fixed("b1") is True

        # Check that empty cells are not fixed
        assert grid.is_cell_fixed("a2") is False
        assert grid.is_cell_fixed("b0") is False

    def test_fixed_cells_with_initialization(self):
        """Test that fixed_cells can be passed during initialization."""
        fixed_cells = {"a0", "a1", "b1"}
        grid = Grid(grid_size=4, fixed_cells=fixed_cells)

        assert grid.is_cell_fixed("a0") is True
        assert grid.is_cell_fixed("a1") is True
        assert grid.is_cell_fixed("b1") is True
        assert grid.is_cell_fixed("a2") is False
