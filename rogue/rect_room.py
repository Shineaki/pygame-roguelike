from typing import Self

import numpy as np

from rogue.enums import Tiles


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: Self) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

    def block(self, grid: np.array):
        # Center
        grid[self.inner] = Tiles.FLOOR
        # Corners
        grid[self.x1, self.y1] = Tiles.TL_C
        grid[self.x2, self.y1] = Tiles.TR_C
        grid[self.x1, self.y2] = Tiles.BL_C
        grid[self.x2, self.y2] = Tiles.BR_C
        # Top wall
        grid[self.x1+1:self.x2, self.y1] = Tiles.WALL
        # Bottom wall
        grid[self.x1+1:self.x2, self.y2] = Tiles.WALL_BOTTOM
        # Left wall
        grid[self.x1, self.y1+1:self.y2] = Tiles.WALL_LEFT
        # Right wall
        grid[self.x2, self.y1+1:self.y2] = Tiles.WALL_RIGHT
