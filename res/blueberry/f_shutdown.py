# /res/blueberry/f_shutdown.py


import pygame as pg

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


# your function here
def func():
    pg.quit()
    connection.protocol.disconnect()
