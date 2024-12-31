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


class AnimState(Enum):
    IDLE = 1
    RUN = 2
    HIT = 3


class Direction(Enum):
    NULL = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class AIRoundState(Enum):
    DONE = 0
    MOVING = 1


class AIState(Enum):
    IDLE = 0
    CHASING = 1
