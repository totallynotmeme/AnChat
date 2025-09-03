# /res/blueberry/f_tick.py


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
        fmap["recvmsg"](msg)
    
    fmap["handle_log"]()
    VARS.active.draw(VARS.canvas)
    
    pg.display.flip()
    VARS.frame += 1
    VARS.clock.tick(60)
