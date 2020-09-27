from asyncio.tasks import current_task
import curses
from typing import List, Optional, Type, Callable

import numpy as np
from numpy.core.defchararray import partition

from .blocks import Block, Drawable, Static, new_canvas

CHAR_BLOCK = '*'


class NotDrawable(RuntimeError):
    pass


class LevelWindow:
    grounded: Static
    height, width = 0, 0
    # sky: curses.window
    # ground: curses.window
    floating: Optional[Block]
    partition = 0

    def __init__(self, height: int, width: int) -> None:
        self.height, self.width = height, width
        self.canvas = new_canvas(width, height)
        self.grounded = Static(0, height)
        self.resize_bounds(0)

    def draw(self):
        canvas = self.canvas
        canvas.fill(False)

        if not self.grounded.draw(canvas):
            raise NotDrawable

        if ground := self.ground:
            self.draw_canvas(canvas, ground)

        if dx := self.floating:
            if not dx.draw(canvas):
                raise NotDrawable

        self.draw_canvas(canvas, self.sky)

    @staticmethod
    def draw_canvas(canvas: np.array, where):
        where.clear()
        for yx, v in np.ndenumerate(canvas):
            if v:
                where.addstr(*yx, CHAR_BLOCK)
        where.refresh()

    def resize_bounds(self, partition_y: int):
        self.sky = curses.newwin(self.height-partition_y, self.width, 0, 0)
        self.ground = None
        if partition_y:
            self.ground = curses.newwin(
                partition_y, self.width, self.height-partition_y, 0)
        self.partition = partition_y

    def float_move(self, dirn: str) -> Callable[[], None]:
        dirn = dirn.lower()

        if fx := self.floating:
            ctop, cleft = fx.top, fx.left

            def undo():
                if fy := self.floating:
                    fy.top, fy.left = ctop, cleft

            if dirn == 'down':
                fx.top += 1
            if dirn == 'left':
                if fx.left:
                    fx.left -= 1
            if dirn == 'right':
                right = fx.pixels.shape[0] + fx.left
                if right == self.width:
                    fx.left += 1
            return undo
        return lambda: None

    def make_grounded(self):
        lift = self.floating.pixels.shape[0]
        if ground := self.ground:
            ground.clear()
        self.sky.clear()
        self.resize_bounds(lift+self.partition)
        self.grounded.join(self.floating)
        self.floating = None

    def float_new(self, block: Type[Block]):
        self.floating = block(left=self.width//2, top=0)
