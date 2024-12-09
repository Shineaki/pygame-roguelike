from enum import Enum, auto


class Tiles(Enum):
    FLOOR = 0
    WALL = auto()
    VOID = auto()

    TL_C = auto()
    TR_C = auto()
    BL_C = auto()
    BR_C = auto()

    WALL_SINGLE = auto()
    WALL_SINGLE_LEFT = auto()
    WALL_SINGLE_RIGHT = auto()

    TL_I_C = auto()
    TR_I_C = auto()
    BL_I_C = auto()
    BR_I_C = auto()

    WALL_BOTTOM = auto()
    WALL_LEFT = auto()
    WALL_RIGHT = auto()

    WALL_DOUBLE_VERTICAL_TOP = auto()
    WALL_DOUBLE_VERTICAL_MID = auto()
    WALL_DOUBLE_VERTICAL_BOT = auto()

    WALL_TRILE_TRB = auto()
    WALL_TRILE_TLB = auto()

    WALL_TRILE_TLB_2 = auto()
    WALL_TRILE_TRB_2 = auto()

    WALL_TD_LRB = auto()
    WALL_BD_LRT = auto()

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
