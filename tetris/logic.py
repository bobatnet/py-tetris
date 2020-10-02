import asyncio
import concurrent.futures

from curses import wrapper, noecho, cbreak
import curses

from .blocks import any_block
from .draw import LevelWindow, NotDrawable


WIN_HEIGHT = 60
WIN_WIDTH = 30
TIMER_SEC = 2.

level_locker = asyncio.Lock()


class Quit(Exception):
    pass


async def motion(lwin: LevelWindow):
    just_grounded = True

    curses.halfdelay(int(TIMER_SEC*10))

    while True:
        async with level_locker:
            if just_grounded:
                lwin.float_new(any_block())

            undo_move = lwin.float_move('down')
            try:
                lwin.draw()
            except NotDrawable:
                undo_move()
                if just_grounded:
                    raise Quit
                lwin.make_grounded()
                just_grounded = True
                continue
            just_grounded = False

        try:
            await asyncio.wait_for(interact(lwin), timeout=TIMER_SEC)
        except asyncio.TimeoutError:
            continue


async def interact(lwin: LevelWindow):
    loop = asyncio.get_running_loop()

    key = 0
    if win := lwin.sky:
        win.keypad(True)
        key = win.getch()

    if key == ord(' '):
        async with level_locker:
            if block := lwin.floating:
                block.rotate_cw()
    elif key == ord('q') or key == ord('Q'):
        raise Quit
    elif key == curses.KEY_LEFT:
        async with level_locker:
            lwin.float_move('left')
    elif key == curses.KEY_RIGHT:
        async with level_locker:
            lwin.float_move('right')


async def main(stdscr):
    stdscr.clear()
    noecho()
    cbreak()

    lwin = LevelWindow(height=WIN_HEIGHT, width=WIN_WIDTH)

    try:
        await asyncio.gather(motion(lwin), return_exceptions=False)
    except Quit:
        pass

wrapper(lambda stdscr: asyncio.run(main(stdscr), debug=True))


# def main(stdscr):
#     # Clear screen
#     stdscr.clear()

#     import curses
#     w2 = curses.newwin(20, 50, 0, 0)

#     for i in range(0, 10):
#         v = i-10
#         w2.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))

#     w2.refresh()
#     w2.getkey()


# wrapper(main)
