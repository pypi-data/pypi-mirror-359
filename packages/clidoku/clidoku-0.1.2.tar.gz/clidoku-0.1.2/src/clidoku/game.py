import json
import math
import random
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from clidoku.enums import Difficulty
from clidoku.grid import Grid
from clidoku.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Move:
    grid: Grid
    moved_at: datetime

    def to_dict(self) -> dict:
        """Convert Move to a dictionary for JSON serialization."""
        return {
            "grid": {
                "grid_size": self.grid.grid_size,
                "data": list(self.grid),
                "fixed_cells": list(self.grid.fixed_cells),
            },
            "moved_at": self.moved_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Move":
        """Create Move from a dictionary loaded from JSON."""
        grid_data = data["grid"]
        # Handle backward compatibility - fixed_cells might not exist in old save files
        fixed_cells = set(grid_data.get("fixed_cells", []))
        grid = Grid(grid_size=grid_data["grid_size"], grid=grid_data["data"], fixed_cells=fixed_cells)
        moved_at = datetime.fromisoformat(data["moved_at"])
        return cls(grid=grid, moved_at=moved_at)


class Game:
    SAVE_DIR = ".clidoku"
    SAVE_PATH = Path(Path.home(), SAVE_DIR)
    SAVE_FILE = "savegame.jsonl"

    started_at: datetime | None

    grid: Grid
    history: list[Move] = []

    @property
    def save_file_path(self) -> Path:
        """
        Property that gets the save file's path, creating the save dir if it doesn't exist
        """
        if not self.SAVE_PATH.exists():
            Path.mkdir(self.SAVE_PATH)

        return Path(self.SAVE_PATH, self.SAVE_FILE)

    def __init__(
        self,
        save_file: str | None = None,
        reset: bool = False,
        grid_size: int = 9,
        difficulty: Difficulty | str = Difficulty.MEDIUM,
    ):
        if save_file is not None:
            self.SAVE_FILE = save_file

        if (not reset) and self.save_file_path.exists():
            self.load_game(self.save_file_path)
        else:
            self.restart(grid_size=grid_size, difficulty=difficulty)

    @classmethod
    def gen_game(cls, grid: Grid, difficulty: Difficulty | str = Difficulty.MEDIUM) -> None:
        """Generate a complete sudoku puzzle by filling the grid and removing cells."""
        # Use simple recursive backtracking with minimal optimization
        if not cls._gen_game_simple(grid):
            raise RuntimeError("Couldn't generate game.")

        cls.remove_cells(grid, difficulty=difficulty)

        # Mark all remaining filled cells as fixed (starting cells)
        grid.mark_all_filled_cells_as_fixed()

    @classmethod
    def _gen_game_simple(cls, grid: Grid) -> bool:
        """Simple recursive backtracking - finds first empty cell and tries numbers."""
        # Find the first empty cell
        empty_cell = -1
        for i in range(grid.grid_size**2):
            if grid[i] is None:
                empty_cell = i
                break

        # If no empty cells, we're done
        if empty_cell == -1:
            return True

        # Try each number in random order for variety
        numbers = list(grid.NUMBERS)
        random.shuffle(numbers)

        for number in numbers:
            # Quick validation: only check if this specific placement is valid
            if cls._is_valid_placement(grid, empty_cell, number):
                grid[empty_cell] = number  # Place the number

                # Recursively solve the rest
                if cls._gen_game_simple(grid):
                    return True

                # Backtrack
                grid[empty_cell] = None

        return False

    @classmethod
    def _is_valid_placement(cls, grid: Grid, cell_idx: int, number: int) -> bool:
        """Check if placing a number at a specific cell violates sudoku rules."""
        row = cell_idx // grid.grid_size
        col = cell_idx % grid.grid_size

        # Check row for duplicates
        for c in range(grid.grid_size):
            if grid[row * grid.grid_size + c] == number:
                return False

        # Check column for duplicates
        for r in range(grid.grid_size):
            if grid[r * grid.grid_size + col] == number:
                return False

        # Check box for duplicates
        box_size = int(math.sqrt(grid.grid_size))
        box_row = row // box_size
        box_col = col // box_size

        for r in range(box_row * box_size, (box_row + 1) * box_size):
            for c in range(box_col * box_size, (box_col + 1) * box_size):
                if grid[r * grid.grid_size + c] == number:
                    return False

        return True

    def load_game(self, file_path: Path) -> None:
        """Load a saved game from the specified file path."""
        logger.debug(f"Loading game from {file_path}")

        self.history = []
        self.started_at = None

        with Path.open(file_path) as _file:
            for line in _file:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                move_data = json.loads(line)
                move = Move.from_dict(move_data)
                self.history.append(move)

                if self.started_at is None:
                    self.started_at = move.moved_at

        if not self.history:
            logger.debug("No history found in save file, restarting with new game")
            self.restart()
        else:
            logger.debug(f"Loaded game with {len(self.history)} moves, started at {self.started_at}")
            self.grid = self.history[-1].grid

    def save_game(self, file_path: Path | None = None) -> None:
        """Save the current game state to the specified file path or default save location."""
        if file_path is None:
            file_path = self.save_file_path

        logger.debug(f"Saving game to {file_path}")
        move = Move(grid=self.grid, moved_at=datetime.now(UTC))

        # Add the move to history
        self.history.append(move)

        # Save all moves in history to file (one per line)
        with Path.open(file_path, "w") as _file:
            for i, historical_move in enumerate(self.history):
                if i > 0:
                    _file.write("\n")
                _file.write(json.dumps(historical_move.to_dict()))

        logger.debug("Game saved successfully")

    def restart(self, grid_size: int | None = None, difficulty: Difficulty | str = Difficulty.MEDIUM) -> None:
        """Restart the game with a new grid of the specified size."""
        self.started_at = datetime.now(UTC)

        self.clear(grid_size)
        self.gen_game(self.grid, difficulty=difficulty)

    def clear(self, grid_size: int | None = None) -> None:
        """Clear the game state and create a new empty grid."""
        self.history = []
        self.grid = Grid(grid_size=grid_size)

    def check_game(self) -> bool:
        return self.grid.check_grid()

    def is_complete(self) -> bool:
        """Check if the game is completely solved."""
        # Check if grid is completely filled (no empty cells)
        if len(self.grid.empty_cells()) > 0:
            return False

        # Check if grid is valid (no rule violations)
        return self.check_game()

    def get_completion_time(self) -> str:
        """Get formatted completion time from game start to now."""
        if not self.started_at:
            return "Unknown"

        completion_time = datetime.now(UTC) - self.started_at
        total_seconds = int(completion_time.total_seconds())

        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes} minutes {seconds} seconds"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours} hours {minutes} minutes {seconds} seconds"

    def get_move_count(self) -> int:
        """Get the number of user moves made during the game."""
        # The first move in history is the initial game state after generation
        # All subsequent moves are user actions (add/remove)
        return max(0, len(self.history) - 1)

    def display(self) -> None:
        """Display the current game grid to the console."""
        logger.info(str(self.grid))

    @classmethod
    def remove_cells(cls, grid: Grid, difficulty: Difficulty | str = Difficulty.MEDIUM) -> None:
        """
        Remove cells from a complete sudoku grid to create a solvable puzzle.

        Args:
            grid: Complete sudoku grid to remove cells from
            difficulty: Difficulty level (Difficulty enum or string)
        """
        # Get difficulty configuration
        removal_probability, target_filled_range = cls._get_difficulty_config(grid, difficulty)
        box_size = int(math.sqrt(grid.grid_size))

        # Collect initial removal candidates from each box
        cells_to_remove = cls._collect_initial_removal_candidates(grid, box_size, removal_probability)

        # Adjust removals to meet target range
        cells_to_remove = cls._adjust_removals_to_target(grid, cells_to_remove, target_filled_range, box_size)

        # Execute the cell removals
        cls._execute_cell_removals(grid, cells_to_remove)

    @classmethod
    def _get_difficulty_config(cls, grid: Grid, difficulty: Difficulty | str) -> tuple[float, tuple[int, int]]:
        """Get removal probability and target range for the given difficulty level."""
        # Convert string to enum if needed
        if isinstance(difficulty, str):
            difficulty = Difficulty.from_string(difficulty)

        # Define removal probabilities and target ranges for each difficulty
        # Adjust for different grid sizes
        total_cells = grid.grid_size**2

        if difficulty == Difficulty.EASY:
            removal_probability = 0.4  # Remove ~40% of cells
            if total_cells == 81:  # 9x9 grid
                target_filled_range = (45, 55)
            elif total_cells == 16:  # 4x4 grid
                target_filled_range = (10, 12)
            else:
                target_filled_range = (int(total_cells * 0.55), int(total_cells * 0.7))
        elif difficulty == Difficulty.HARD:
            removal_probability = 0.7  # Remove ~70% of cells
            if total_cells == 81:  # 9x9 grid
                target_filled_range = (25, 35)
            elif total_cells == 16:  # 4x4 grid
                target_filled_range = (6, 8)
            else:
                target_filled_range = (int(total_cells * 0.3), int(total_cells * 0.45))
        else:  # MEDIUM (default)
            removal_probability = 0.55  # Remove ~55% of cells
            if total_cells == 81:  # 9x9 grid
                target_filled_range = (35, 45)
            elif total_cells == 16:  # 4x4 grid
                target_filled_range = (8, 10)
            else:
                target_filled_range = (int(total_cells * 0.4), int(total_cells * 0.55))

        return removal_probability, target_filled_range

    @classmethod
    def _collect_initial_removal_candidates(cls, grid: Grid, box_size: int, removal_probability: float) -> list[int]:
        """Collect initial candidates for cell removal from each box."""
        cells_to_remove = []

        # First pass: identify candidates for removal from each box
        for box_row in range(box_size):
            for box_col in range(box_size):
                box_cells = cls._get_box_cell_indices(grid, box_row, box_col, box_size)

                # Keep at least one cell per box, remove others based on probability
                random.shuffle(box_cells)
                # Always keep the first cell (box_cells[0])

                for cell_idx in box_cells[1:]:
                    if random.random() < removal_probability:
                        cells_to_remove.append(cell_idx)

        return cells_to_remove

    @classmethod
    def _adjust_removals_to_target(
        cls, grid: Grid, cells_to_remove: list[int], target_filled_range: tuple[int, int], box_size: int
    ) -> list[int]:
        """Adjust the list of cells to remove to meet the target difficulty range."""
        current_filled = grid.grid_size**2
        target_min, target_max = target_filled_range

        # If we're removing too many cells, keep some
        if current_filled - len(cells_to_remove) < target_min:
            excess_removals = target_min - (current_filled - len(cells_to_remove))
            cells_to_remove = cells_to_remove[:-excess_removals]

        # If we're not removing enough cells, add more (but respect box constraints)
        elif current_filled - len(cells_to_remove) > target_max:
            additional_removals_needed = (current_filled - len(cells_to_remove)) - target_max
            all_cells = set(range(grid.grid_size**2))
            remaining_cells = all_cells - set(cells_to_remove)

            # Only remove additional cells if each box still has at least one cell
            additional_candidates = []
            for cell_idx in remaining_cells:
                if cls._can_remove_cell_safely(grid, cell_idx, cells_to_remove, box_size):
                    additional_candidates.append(cell_idx)

            random.shuffle(additional_candidates)
            cells_to_remove.extend(additional_candidates[:additional_removals_needed])

        return cells_to_remove

    @classmethod
    def _execute_cell_removals(cls, grid: Grid, cells_to_remove: list[int]) -> None:
        """Execute the actual removal of selected cells from the grid."""
        for cell_idx in cells_to_remove:
            grid[cell_idx] = None

    @classmethod
    def _get_box_cell_indices(cls, grid: Grid, box_row: int, box_col: int, box_size: int) -> list[int]:
        """Get all cell indices in a specific 3x3 box."""
        indices = []
        start_row = box_row * box_size
        start_col = box_col * box_size

        for row in range(start_row, start_row + box_size):
            for col in range(start_col, start_col + box_size):
                idx = row * grid.grid_size + col
                indices.append(idx)

        return indices

    @classmethod
    def _can_remove_cell_safely(cls, grid: Grid, cell_idx: int, already_removing: list[int], box_size: int) -> bool:
        """Check if a cell can be safely removed while maintaining box constraints."""
        # Find which box this cell belongs to
        row = cell_idx // grid.grid_size
        col = cell_idx % grid.grid_size
        box_row = row // box_size
        box_col = col // box_size

        # Get all cells in this box
        box_cells = cls._get_box_cell_indices(grid, box_row, box_col, box_size)

        # Count how many cells in this box would remain after all removals
        remaining_in_box = 0
        for box_cell_idx in box_cells:
            if box_cell_idx not in already_removing and box_cell_idx != cell_idx:
                remaining_in_box += 1

        # Only allow removal if at least one cell would remain in the box
        return remaining_in_box >= 1
