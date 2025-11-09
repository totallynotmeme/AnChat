# /res/blueberry/f_tick.py


from . import task
from . import utils
import pygame as pg

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


# your function here
def func():
    # parse events
    for ev in pg.event.get():
        if ev.type == pg.MOUSEMOTION:
            VARS.mousepos = pg.Vector2(pg.mouse.get_pos())
        
        if ev.type == pg.KEYDOWN:
            mods = pg.key.get_mods()
            VARS.holding_ctrl = bool(mods & pg.KMOD_CTRL)
            VARS.holding_shift = bool(mods & pg.KMOD_SHIFT)
        
        if ev.type == pg.QUIT:
            VARS.RUNNING = False
            fmap["shutdown"]()
            return
        
        VARS.active.handle_event(ev)
    
    # handle messages (pasted from __init__.py's default)
    if len(connection.QUEUE) > 0:
        packet = connection.QUEUE.pop(0)
        valid = encryption.validate(packet)
        if valid:
            packet = encryption.decrypt(packet)
            if message.verify_hash(packet):
                msg = message.parse_packet(packet)
            else:
                #open("LOST" + utils.random_string(3), "wb").write(packet)
                msg = message.error_invalid_hash()
        else:
            msg = message.error_duplicate_salt()
        fmap["recvmsg"](msg)
    
    fmap["handle_log"]()
    VARS.active.draw(VARS.canvas)
    
    
    # draw version text and stuff
    txt = VARS.lang.CORE_VERSION.format(VARS.CORE_VERSION)
    txt = VARS.fonts[15].render(txt, True, (100, 100, 100))
    VARS.canvas.blit(txt, txt.get_rect(topright=(VARS.window_size.x-3, 3)))
    
    txt = VARS.lang.CLIENT_VERSION.format(VARS.CLIENT_VERSION)
    txt = VARS.fonts[15].render(txt, True, (100, 100, 100))
    VARS.canvas.blit(txt, txt.get_rect(topright=(VARS.window_size.x-3, 18)))
    
    x_pos = VARS.window_size.x - 2
    y_pos = 32
    font = VARS.fonts[15]
    
    for i in task.FINISHED:
        txt = font.render(str(i[0]), True, (0, 200, 0))
        VARS.canvas.blit(txt, txt.get_rect(topright=(x_pos, y_pos)))
        y_pos += 16
        i[1] -= 1
    while task.FINISHED and task.FINISHED[0][1] < 0:
        task.FINISHED.pop(0)
    
    for i in task.FAILED:
        txt = font.render(str(i[0]), True, (200, 0, 0))
        VARS.canvas.blit(txt, txt.get_rect(topright=(x_pos, y_pos)))
        y_pos += 16
        i[1] -= 1
    while task.FAILED and task.FAILED[0][1] < 0:
        task.FAILED.pop(0)
    
    for i in task.RUNNING:
        txt = font.render(str(i), True, (150, 150, 150))
        VARS.canvas.blit(txt, txt.get_rect(topright=(x_pos, y_pos)))
        y_pos += 16
    
    pg.display.flip()
    VARS.frame += 1
    VARS.clock.tick(60)
