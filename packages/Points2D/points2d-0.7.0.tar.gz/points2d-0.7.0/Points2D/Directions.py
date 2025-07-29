"""
Author: Big Panda
Created Time: 01.07.2025 15:13
Modified Time: 01.07.2025 15:13
Description:
    We use mathematical coordinate rather than computer graphical coordinate
"""
from enum import Enum, unique

__all__ = ["Direction"]


@unique
class Direction(Enum):
    N = (0, 1)  # North
    S = (0, -1)  # South
    E = (1, 0)  # East
    W = (-1, 0)  # West


if __name__ == '__main__':
    print(Direction.N)
    print(Direction.N.name)
    print(Direction.N.value)
    obj = Direction((0, 1))
    print(obj)
