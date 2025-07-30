from enum import Enum


class Difficulty(Enum):
    """Enumeration for sudoku puzzle difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "Difficulty":
        """Convert string to Difficulty enum, raising ValueError for invalid values."""
        try:
            return cls(value.lower())
        except ValueError as e:
            valid_values = [difficulty.value for difficulty in cls]
            raise ValueError(f"Invalid difficulty '{value}'. Valid options are: {', '.join(valid_values)}") from e
