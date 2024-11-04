from enum import Enum
from dataclasses import dataclass
from typing import List


class CreaseType(Enum):
    """Enum representing different types of creases in origami patterns."""

    NONE = 0
    MOUNTAIN = 1
    VALLEY = -1
    BORDER = 2  # Added for FOLD format compatibility


@dataclass
class Point:
    """Represents a 2D point in the origami pattern."""

    x: float
    y: float

    def __hash__(self):
        return hash((self.x, self.y))

    def to_list(self) -> List[float]:
        return [self.x, self.y]

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return abs(self.x - other.x) < 1e-10 and abs(self.y - other.y) < 1e-10

    @classmethod
    def from_list(cls, coords: List[float]) -> "Point":
        return cls(coords[0], coords[1])

    @property
    def grid_x(self) -> int:
        """Return the x coordinate rounded to nearest integer for grid operations"""
        return round(self.x)

    @property
    def grid_y(self) -> int:
        """Return the y coordinate rounded to nearest integer for grid operations"""
        return round(self.y)


@dataclass
class Crease:
    """Represents a crease in the origami pattern."""

    start: Point
    end: Point
    type: CreaseType
