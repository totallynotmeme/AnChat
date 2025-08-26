# /res/blueberry/f_tick.py


import utils
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
        match ev.type:
            case pg.MOUSEMOTION:
                VARS.mousepos = pg.Vector2(pg.mouse.get_pos())
                if "event_MOUSEMOTION" in dir(VARS.active):
                    VARS.active.event_MOUSEMOTION(ev)
            
            case pg.MOUSEBUTTONDOWN:
                if "event_MOUSEBUTTONDOWN" in dir(VARS.active):
                    VARS.active.event_MOUSEBUTTONDOWN(ev)
            
            case pg.MOUSEBUTTONUP:
                if "event_MOUSEBUTTONUP" in dir(VARS.active):
                    VARS.active.event_MOUSEBUTTONUP(ev)
            
            case pg.KEYDOWN:
                mods = pg.key.get_mods()
                VARS.holding_ctrl = bool(mods & pg.KMOD_CTRL)
                VARS.holding_shift = bool(mods & pg.KMOD_SHIFT)
                if "event_KEYDOWN" in dir(VARS.active):
                    VARS.active.event_KEYDOWN(ev)
            
            case pg.TEXTINPUT:
                if "event_TEXTINPUT" in dir(VARS.active):
                    VARS.active.event_TEXTINPUT(ev)
            
            case pg.DROPFILE:
                if "event_DROPFILE" in dir(VARS.active):
                    VARS.active.event_DROPFILE(ev)
            
            case pg.QUIT:
                VARS.RUNNING = False
                fmap[F_SHUTDOWN]()
    
    # handle messages (pasted from __init__.py's default)
    if len(connection.PACKET_QUEUE) > 0:
        packet = connection.PACKET_QUEUE.pop(0)
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
        fmap[F_RECVMSG](msg)
    
    fmap[F_HANDLE_LOG]()
    VARS.active.draw(VARS.canvas)
    
    pg.display.flip()
    VARS.frame += 1
    VARS.clock.tick(60)
