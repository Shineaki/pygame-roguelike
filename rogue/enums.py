from enum import Enum, IntEnum, auto


class IntTiles(IntEnum):
    WALL = 0
    FLOOR = 1


class Tiles(Enum):
    WALL = 0
    FLOOR = 1
    VOID = auto()

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
