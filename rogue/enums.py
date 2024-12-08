from enum import Enum, auto


class Tiles(Enum):
    VOID = auto()
    FLOOR = auto()
    WALL = auto()
    TL_C = auto()
    TR_C = auto()
    BL_C = auto()
    BR_C = auto()
    WALL_BOTTOM = auto()
    WALL_LEFT = auto()
    WALL_RIGHT = auto()
