# /res/blueberry/f_handle_log.py


from .scene import Console
import pygame as pg

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


# your function here
def func():
    if LOGS:
        time, line = LOGS.pop(0)
        Console.logs_multiline.append_text(f"[{time}] {line}")
