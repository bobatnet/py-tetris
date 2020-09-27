import asyncio
import concurrent.futures

from curses import wrapper, noecho, cbreak

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
        await asyncio.sleep(TIMER_SEC)


async def interact(lwin: LevelWindow):
    loop = asyncio.get_running_loop()

    key = ''
    if win := lwin.sky:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            key = await loop.run_in_executor(pool, win.getkey)

    if key == ' ':
        async with level_locker:
            if block := lwin.floating:
                block.rotate_cw()
    elif key.lower() == 'q' or key.lower() == 'esc':
        raise Quit
    elif key == 'KEY_LEFT':
        async with level_locker:
            lwin.float_move('left')
    elif key == 'KEY_RIGHT':
        async with level_locker:
            lwin.float_move('right')


async def main(stdscr):
    stdscr.clear()
    noecho()
    cbreak()
    stdscr.keypad(True)

    lwin = LevelWindow(height=WIN_HEIGHT, width=WIN_WIDTH)

    await asyncio.gather(motion(lwin), interact(lwin), return_exceptions=False)

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
