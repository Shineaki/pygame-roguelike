from enum import Enum, IntEnum, auto


class IntTiles(IntEnum):
    WALL = 0
    FLOOR = 1


class TileState(IntEnum):
    UNEXPLORED = 0
    EXPLORED = 1
    VISIBLE = 2


class Tiles(Enum):
    WALL = 0
    FLOOR = 1
    VOID = auto()

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
