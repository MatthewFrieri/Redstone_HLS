from enum import Enum


class CDir(Enum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"

    @staticmethod
    def get_opposite(cdir: "CDir"):
        if cdir == CDir.NORTH:
            return CDir.SOUTH
        if cdir == CDir.EAST:
            return CDir.WEST
        if cdir == CDir.SOUTH:
            return CDir.NORTH
        if cdir == CDir.WEST:
            return CDir.EAST