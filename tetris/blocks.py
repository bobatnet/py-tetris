from typing import Tuple

import numpy as np


class NotDrawable(RuntimeError):
    pass


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

                    try:
                        if canvas[y, x]:
                            raise NotDrawable
                    except IndexError:
                        raise NotDrawable
                    canvas[y, x] = True
        return True

    @property
    def right(self) -> int:
        return self.pixels.shape[1] + self.left

    @property
    def bottom(self) -> int:
        return self.pixels.shape[0] + self.top


class Static(Drawable):
    def __init__(self, width: int, top: int) -> None:
        super().__init__(0, top)
        self.pixels = np.empty((0, width), dtype=bool)

    def join(self, obj: Drawable):

        if obj.top < self.top:
            new_rows = np.zeros((self.top - obj.top, self.pixels.shape[1]))
            self.pixels = np.vstack((new_rows, self.pixels))
            self.top = obj.top

        if obj.bottom > self.bottom:
            assert False

        old_pix = self.pixels[:(obj.bottom-obj.top), obj.left:obj.right]
        new_pix = np.logical_or(obj.pixels, old_pix)
        self.pixels[:(obj.bottom-obj.top), obj.left:obj.right] = new_pix

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
    return np.zeros((ht, wd), dtype=bool)
