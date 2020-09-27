import unittest

from tetris.blocks import *


class TestBlocks(unittest.TestCase):
    def setUp(self) -> None:
        self.canvas = new_canvas(10, 10)

    def test_draw(self):
        self.canvas.fill(False)
        b1 = L_Block(0, 0)
        b1.draw(self.canvas)
        self.assertEqual(self.canvas.sum(), 4)

    def test_overlap(self):
        self.canvas.fill(False)
        b1 = L_Block(0, 0)
        b2 = T_Block(0, 0)
        b1.draw(self.canvas)
        self.assertFalse(b2.draw(self.canvas))

    def test_rotate(self):
        self.canvas.fill(False)
        b1 = L_Block(0, 0)
        b1.rotate_cw()
        self.assertNotEqual(b1, L_Block(0, 0))
        b1.rotate_cw()
        b1.rotate_cw()
        b1.rotate_cw()
        self.assertEqual(b1, L_Block(0, 0))
