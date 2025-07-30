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

    def opposite(self):
        dict_opposite_map = {
            Direction.W: Direction.E,
            Direction.E: Direction.W,
            Direction.N: Direction.S,
            Direction.S: Direction.N
        }
        return dict_opposite_map[self]

    @classmethod
    def keys(cls):
        """返回所有方向名称的列表 ['N', 'S', 'E', 'W']"""
        return [item.name for item in cls]

    @classmethod
    def values(cls):
        """返回所有方向值的列表 [(0, 1), (0, -1), (1, 0), (-1, 0)]"""
        return [item.value for item in cls]

    @classmethod
    def items(cls):
        """返回所有方向名称和值组成的列表 [('N', (0, 1)), ('S', (0, -1)), ('E', (1, 0)), ('W', (-1, 0))]"""
        return [(item.name, item.value) for item in cls]


if __name__ == '__main__':
    print(Direction.N)
    print(Direction.N.name)
    print(Direction.N.value)
    obj = Direction((0, 1))
    print(obj)
    print(Direction.S.opposite())
    print(Direction.keys())
    print(Direction.values())
    print(Direction.items())
