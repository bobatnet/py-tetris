from typing import Tuple

import numpy as np


class Drawable:
    pixels = np.empty((0, 0), dtype=bool)
    left, top = 0, 0

    def __init__(self, left: int, top: int) -> None:
        self.left, self.top = left, top

    def draw(self, canvas: np.array) -> bool:
        for i in range(self.pixels.shape[0]):
            for j in range(self.pixels.shape[1]):
                if self.pixels[i, j]:
                    x, y = j+self.left, i+self.top

                    if canvas[y, x]:
                        return False
                    canvas[y, x] = True
        return True

    @property
    def right(self) -> int:
        return self.pixels.shape[1] + self.right

    @property
    def bottom(self) -> int:
        return self.pixels.shape[0] + self.top


class Static(Drawable):
    def join(self, obj: Drawable):

        if obj.top < self.top:
            new_rows = np.zeros((self.top - obj.top, self.pixels.shape[1]))
            self.pixels = np.vstack((new_rows, self.pixels))
            self.top = obj.top

        if obj.left < self.left:
            new_cols = np.zeros((self.pixels.shape[0], self.left-obj.left))
            self.pixels = np.hstack((new_cols, self.pixels))
            self.left = obj.left

        if obj.right > self.right:
            new_cols = np.zeros((self.pixels.shape[0], obj.right-self.right))
            self.pixels = np.hstack((self.pixels, new_cols))

        if obj.bottom > self.bottom:
            assert False
            new_rows = np.zeros((obj.bottom-self.bottom, self.pixels.shape[1]))
            self.pixels = np.vstack((self.pixels, new_rows))

        self.pixels[(obj.left-self.left):, :] = obj.pixels

    def collapse(self):
        coll = np.any(self.pixels, axis=1).tolist()
        self.pixels = self.pixels[coll]


class Block(Drawable):
    rotation = 0

    def rotate_cw(self):
        self.pixels = np.rot90(self.pixels)

    def vertical_extent(self) -> Tuple[int, int]:
        return self.top, self.top+self.pixels.shape[0]

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Block):
            return np.array_equal(self.pixels, o.pixels)
        return False


class L_Block(Block):
    pixels = np.array([[1, 0], [1, 0], [1, 1]], dtype=bool)


class T_Block(Block):
    pixels = np.array([[1, 1, 1], [0, 1, 0]], dtype=bool)


def any_block():
    return L_Block


def new_canvas(wd: int, ht: int):
    return np.zeros((wd, ht), dtype=bool)
