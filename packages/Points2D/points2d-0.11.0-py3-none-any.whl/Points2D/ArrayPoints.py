"""
Author: Big Panda
Created Time: 26.06.2025 11:48
Modified Time: 26.06.2025 11:48
Description:
    使用与 np.array() 类似的惯例来定义 ArrayPoint2D 函数，参数 object 应该为 list 对象
"""
from __future__ import annotations
from Points2D.Points import *
from typing import Tuple, List

__all__ = ['ArrayPoint2D']


class ArrayPoint2D(list):
    _x: list
    _y: list
    _coord: list

    def __init__(self: ArrayPoint2D, obj) -> None:
        if all([isinstance(item, Point2D) for item in obj]) or all([isinstance(item, LinkPoint2D) for item in obj]):
            super().__init__(obj)
        else:
            raise ValueError("The input value is not an ArrayPoint2D.")

    @property
    def x(self):
        return self._x

    @x.getter
    def x(self):
        return [item.x for item in self]

    @property
    def y(self):
        return self._x

    @x.getter
    def y(self):
        return [item.y for item in self]

    @property
    def coord(self):
        return self._coord

    @x.getter
    def coord(self):
        return [(item.x, item.y) for item in self]

    # String representation of ArrayPoint2D
    # Override __str__() method in parent list
    def __str__(self: ArrayPoint2D) -> str:
        """
        Express ArrayPoint2D
        """
        return f"ArrayPoint2D{super().__str__()}"

    def sort(self, *, key=None, reverse=False):
        if not reverse:
            super().sort(key=lambda p: (p[0], p[1]))
        else:
            super().sort(key=lambda p: (-p[0], -p[1]))

    def appends(self, other: Point2D | Tuple[Point2D] | List[Point2D]):
        if isinstance(other, Point2D):
            super().append(other)
        elif isinstance(other, tuple) and all(isinstance(item, (Point2D, LinkPoint2D)) for item in other) or isinstance(other, list) and all(
                isinstance(item, (Point2D, LinkPoint2D)) for item in other):
            super().extend(other)
        else:
            raise ValueError("""\nThe input value of append function can only be: 
            1. Point2D,
            2. Tuple[Point2D],
            3. List[Point2D],
            4. Tuple[LinkPoint2D],
            5. List[LinkPoint2D]""")

    def unique(self):
        """
        Make elements in array unique, and keep the elements order
        """
        self[:] = list(dict.fromkeys(self))
        return self


if __name__ == '__main__':
    # p1 = Point2D(1, 2)
    # p2 = Point2D(4, 6)
    # test = ArrayPoint2D([p1, p2])
    # print(test)

    # sort() 方法
    # p1 = Point2D(1, 2)
    # p2 = Point2D(4, 6)
    # p3 = Point2D(2, 2)
    # p4 = Point2D(2, 6)
    # test = ArrayPoint2D([p1, p2, p3, p4])
    # test.sort()
    # print(test)

    # LinkPoints2D
    # p1 = LinkPoint2D(1, 2)
    # print(p1)

    # obj_ = ArrayPoint2D([Point2D(1, 2), Point2D(1, 2)])
    # obj_.unique()
    # print(obj_)
    # ====== Test unique() function
    obj_ = ArrayPoint2D([
        Point2D(3, 4),
        Point2D(5, 6),  # 重复
        Point2D(3, 4),
        Point2D(1, 2),  # 重复
        Point2D(5, 6)
    ])
    obj_.unique()
    print(obj_)

    print(obj_.x)
    print(obj_.y)
    print(obj_.coord)
    ...
