import math
from collections.abc import Iterator
from typing import overload


class Grid:
    """Uses a flat list-like structure to represent a Sudoku grid with dynamic size and formatting."""

    DEFAULT_GRID_SIZE = 9
    MAX_GRID_SIZE = 9  # TODO: Support larger grids with multi-digit column indexing

    # ANSI color codes for grid display
    ANSI_BOLD = "\033[1m"
    ANSI_CYAN = "\033[36m"  # Cyan color for fixed cells
    ANSI_RESET = "\033[0m"

    _data: list[int | None]  # Internal storage for grid values
    COLS: list[int]
    ROWS: list[str]
    NUMBERS: list[int]
    grid_size: int
    fixed_cells: set[str]  # Track cell positions (e.g., "a0", "b1") that cannot be removed

    def __init__(
        self, grid_size: int | None = None, grid: list[int | None] | None = None, fixed_cells: set[str] | None = None
    ):
        if grid is not None:
            grid_sqrt = math.sqrt(len(grid))
            if not grid_sqrt.is_integer():
                raise ValueError("Grid is not a valid size.")
            else:
                grid_size = int(grid_sqrt)

        # Use default grid size if None is provided
        if grid_size is None:
            grid_size = self.DEFAULT_GRID_SIZE

        # Validate grid size
        if grid_size > self.MAX_GRID_SIZE:
            raise ValueError(f"Grid size {grid_size} exceeds maximum supported size {self.MAX_GRID_SIZE}")

        self.grid_size = grid_size

        if grid is not None:
            self._data = grid
        else:
            self._data = [None] * (grid_size * grid_size)

        self.NUMBERS = [*range(1, grid_size + 1)]
        self.COLS = [*range(grid_size)]
        self.ROWS = [chr(65 + n).lower() for n in range(grid_size)]

        # Initialize fixed cells set
        self.fixed_cells = fixed_cells if fixed_cells is not None else set()

    def __repr__(self):
        out = "\n"

        # Calculate box size for dynamic formatting
        box_size = int(math.sqrt(self.grid_size))

        # Dynamic column headers
        col_headers = []
        for col in self.COLS:
            col_headers.append(f"({col})")

        # Add spacing between box groups in headers
        header_parts = []
        for i in range(0, len(col_headers), box_size):
            header_parts.append(" ".join(col_headers[i : i + box_size]))

        out += "     " + "  ".join(header_parts) + "\n"

        # Calculate separator length to match the actual content line length
        # Build a sample content line to measure its length
        sample_row_values = [" "] * self.grid_size
        sample_row_parts = []
        for i in range(0, len(sample_row_values), box_size):
            box_values = sample_row_values[i : i + box_size]
            sample_row_parts.append(" | ".join(box_values))
        sample_content = "(a) | " + " || ".join(sample_row_parts) + " |"
        separator_length = len(sample_content) - 4  # Subtract 4 for the "(a) " prefix

        out += "    " + "-" * separator_length + "\n"

        for row_idx, row in enumerate(self.ROWS):
            # Build row content dynamically using integer indexing
            row_values = []
            for col in self.COLS:
                cell_idx = row_idx * self.grid_size + col
                cell_value = self[cell_idx]
                cell_position = f"{row}{col}"

                if cell_value is not None:
                    # Apply different formatting for fixed vs user-entered cells
                    if self.is_cell_fixed(cell_position):
                        # Bold text for fixed cells (starting cells) - default color
                        formatted_value = f"{self.ANSI_BOLD}{cell_value}{self.ANSI_RESET}"
                    else:
                        # Cyan text for user-entered cells
                        formatted_value = f"{self.ANSI_CYAN}{cell_value}{self.ANSI_RESET}"
                    row_values.append(formatted_value)
                else:
                    row_values.append(" ")

            # Group values by boxes and format with separators
            row_parts = []
            for i in range(0, len(row_values), box_size):
                box_values = row_values[i : i + box_size]
                row_parts.append(" | ".join(box_values))

            out += f"({row}) | " + " || ".join(row_parts) + " |\n"

            # Dynamic box row separators
            row_n = row_idx + 1
            if row_n % box_size == 0 and row_n < self.grid_size:
                out += "    " + "=" * separator_length + "\n"
            else:
                out += "    " + "-" * separator_length + "\n"
        return out

    @overload
    def __getitem__(self, val: int) -> int | None: ...
    @overload
    def __getitem__(self, val: str) -> int | None: ...
    @overload
    def __getitem__(self, val: slice) -> list[int | None]: ...
    def __getitem__(self, val):
        """Get a value from the grid using either integer, string or slice indexing."""
        if isinstance(val, int) and not isinstance(val, bool):
            # Do normal get
            return self._data[val]
        elif isinstance(val, str):
            # Get the value from the grid at the specified row and column
            row, col = self._parse_index(val)
            return self._data[self.row_bump(row) * self.grid_size + col]
        elif isinstance(val, slice):
            # Handle slice objects for list slicing
            return self._data[val]
        else:
            raise TypeError(f"Grid index must be str, int, or slice, cannot index with {type(val)}")

    @overload
    def __setitem__(self, key: str, value: int | None): ...
    @overload
    def __setitem__(self, key: int, value: int | None): ...
    def __setitem__(self, key, value):
        """Set a value in the grid using either integer or string indexing."""
        if isinstance(key, str):
            row, col = self._parse_index(key)
            self._data[self.row_bump(row) * self.grid_size + col] = value
        elif isinstance(key, int | slice):
            self._data[key] = value
        else:
            raise TypeError(f"Grid index must be str, int, or slice, cannot index with {type(key)}")

    def __len__(self) -> int:
        """Get the total number of cells in the grid."""
        return len(self._data)

    def __iter__(self) -> Iterator[int | None]:
        """Iterate over the grid values."""
        return iter(self._data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Grid):
            return self._data == other._data
        if isinstance(other, list):
            return self._data == other
        return NotImplemented

    def empty_cells(self) -> list[int]:
        """Get all the empty cells (None values) as a list of indices."""
        empty = []
        for i, x in enumerate(self):
            if x is None:
                empty.append(i)
        return empty

    def mark_cell_as_fixed(self, cell: str) -> None:
        """Mark a cell as fixed (cannot be removed) using string position (e.g., 'a0')."""
        # Validate the cell position
        try:
            self._parse_index(cell)
            self.fixed_cells.add(cell)
        except (ValueError, IndexError) as err:
            raise ValueError(f"Invalid cell position: {cell}") from err

    def is_cell_fixed(self, cell: str) -> bool:
        """Check if a cell is fixed (cannot be removed) using string position (e.g., 'a0')."""
        return cell in self.fixed_cells

    def mark_all_filled_cells_as_fixed(self) -> None:
        """Mark all currently filled cells as fixed."""
        for row_idx, row in enumerate(self.ROWS):
            for col in self.COLS:
                cell_idx = row_idx * self.grid_size + col
                if self[cell_idx] is not None:
                    cell_position = f"{row}{col}"
                    self.mark_cell_as_fixed(cell_position)

    def _parse_index(self, row_col: str) -> tuple[str, int]:
        """Parse the row and column from the input string (e.g., 'a1')."""
        if len(row_col) != 2:
            raise ValueError("Index must be a character-number pair like 'a0'.")

        row, col = None, None
        for c in row_col:
            try:
                col = int(c)
            except ValueError:
                row = c.lower()
                continue

        if row is None or col is None:
            raise ValueError("Index must be a character-number pair like 'a0'.")

        if row not in self.ROWS or col not in self.COLS:
            raise IndexError("Row or column out of bounds.")

        return row, col

    def row_bump(self, row: str) -> int:
        """Calculate the row index based on the character (e.g., 'a' -> 0, 'b' -> 1)."""
        return ord(row.lower()) - ord(self.ROWS[0])

    def check_grid(self) -> bool:
        """
        Validate the grid according to sudoku rules.
        Assumes grid is square (grid_size x grid_size).

        Returns:
            True if the grid is valid (no conflicts), False otherwise.

        Validation checks:
        - Numbers must be in valid range (1 to grid_size) or None
        - No duplicate numbers in any row
        - No duplicate numbers in any column
        - No duplicate numbers in any box
        """
        # Check all values are valid numbers or None
        for value in self:
            if value is not None and (not isinstance(value, int) or value not in self.NUMBERS):
                return False

        # Check rows for duplicates
        for row_idx in range(self.grid_size):
            if not self._is_valid_sequence(self._get_row_values(row_idx)):
                return False

        # Check columns for duplicates
        for col_idx in range(self.grid_size):
            if not self._is_valid_sequence(self._get_column_values(col_idx)):
                return False

        # Check boxes for duplicates
        box_size = int(math.sqrt(self.grid_size))
        for box_row in range(box_size):
            for box_col in range(box_size):
                if not self._is_valid_sequence(self._get_box_values(box_row, box_col, box_size)):
                    return False

        return True

    def _is_valid_sequence(self, values: list[int | None]) -> bool:
        """Check if a sequence of values has no duplicates (ignoring None)."""
        seen = set()
        for value in values:
            if value is not None:
                if value in seen:
                    return False
                seen.add(value)
        return True

    def _get_row_values(self, row_idx: int) -> list[int | None]:
        """Get all values in a specific row."""
        start_idx = row_idx * self.grid_size
        return self[start_idx : start_idx + self.grid_size]

    def _get_column_values(self, col_idx: int) -> list[int | None]:
        """Get all values in a specific column."""
        return [self[row_idx * self.grid_size + col_idx] for row_idx in range(self.grid_size)]

    def _get_box_values(self, box_row: int, box_col: int, box_size: int) -> list[int | None]:
        """Get all values in a specific box."""
        values = []
        start_row = box_row * box_size
        start_col = box_col * box_size

        for row in range(start_row, start_row + box_size):
            for col in range(start_col, start_col + box_size):
                idx = row * self.grid_size + col
                values.append(self[idx])

        return values
