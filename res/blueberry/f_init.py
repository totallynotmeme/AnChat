# /res/blueberry/f_init.py


from . import lang
from . import utils
from . import scene
from . import element
from . import chat_message
import pygame as pg
import os

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


# your function here
def func():
    did_crash = pg.get_init()
    is_soft = VARS.RUNNING
    if is_soft:
        # soft reset - no shutdown before reinitialization
        if did_crash:
            # pygame is still initialized - crash
            log("WARN: Soft reset detected. Did the client just crash?")
        else:
            # pygame is not initialized - intended reset
            log("-- Reinitialization, the window should re-open in a moment --")
    else:
        # hard reset - after shutdown, most likely intended
        log("")
        log("---[  INITIALIZING BLUEBERRY CLIENT  ]---")
        log("")
    
    chat_message.downloads_path = DOWNLOADS_PATH
    VARS.CLIENT_VERSION = "0.1.0-INDEV"
    VARS.mousepos = pg.Vector2(-1, -1)
    VARS.frame = 0
    VARS.holding_ctrl = False
    VARS.holding_shift = False
    VARS.debug = False
    if not is_soft:
        VARS.active = scene.Main
    
    if connection.ALIVE:
        # soft reset while connected to the server
        VARS.active = scene.Chat
    
    utils.bootstrap(globals())
    scene.bootstrap(globals())
    element.bootstrap(globals())
    
    log("Initializing Pygame")
    pg.init() # yes that's it
    
    log("Reading config and language files")
    
    # initializing some variables
    CONFIG.DEFAULTS = utils.GET_DEFAULT_CONFIG_OPTIONS()
    CONFIG.CLIENT = utils.GET_DEFAULT_CONFIG_OPTIONS()
    utils.CONFIG_FILE_PATH = os.getcwd() + "/config.txt"
    
    # parsing config file
    for i in utils.parse_config_file(CONFIG.CLIENT):
        log(i)
    
    # getting screen resolution from config (or default)
    display_data = pg.display.Info()
    max_res = display_data.current_w, display_data.current_h
    window_size = utils.parse_screen_res(CONFIG.CLIENT["window_size"], max_res)
    if window_size is None:
        log("Couldn't parse 'window_size' parameter, will use default")
        window_size = utils.parse_screen_res(CONFIG.DEFAULTS["window_size"], max_res)
    CONFIG.CLIENT["window_size"] = f"{window_size[0]}-{window_size[1]}"
    
    VARS.window_size = pg.Vector2(window_size)
    chat_message.window_size = window_size
    VARS.lang = lang.langmap.get(CONFIG.CLIENT["lang"], lang.default)
    chat_message.error_codes = VARS.lang.ERROR_CODES
    
    # that log() explains what this block does lol
    log("Creating pygame window")
    pg.display.set_caption(VARS.lang.WINDOW_TITLE)
    VARS.canvas = pg.display.set_mode(window_size)
    VARS.clock = pg.time.Clock()
    VARS.fonts = {}
    for i in range(10, 50, 5):
        VARS.fonts[i] = pg.font.SysFont(CONFIG.CLIENT["font"], i)
    chat_message.fonts = VARS.fonts
    txt = VARS.fonts[30].render("Initializing Blueberry client", True, (255, 255, 255))
    VARS.canvas.blit(txt, txt.get_rect(center=VARS.window_size/2))
    pg.display.flip()
    pg.scrap.init()
    
    log("Drawing window logo")
    background_color = (20, 30, 40)
    accent_color = (100, 150, 255)
    logo = pg.Surface((32, 32))
    logo.fill(background_color)
    pg.draw.rect(logo, accent_color, pg.Rect(4, 4, 12, 4))
    pg.draw.rect(logo, accent_color, pg.Rect(4, 4, 4, 24))
    pg.draw.rect(logo, accent_color, pg.Rect(4, 24, 24, 4))
    pg.display.set_icon(logo)
    
    if is_soft:
        saved_console_logs = scene.Console.logs_multiline.lines
    
    log("Initializing elements")
    pg.key.set_repeat(250, 30)
    for i in scene.to_init:
        i.init(is_soft)
    
    if is_soft:
        scene.Console.logs_multiline.lines.extend(saved_console_logs)
    
    log("Done! Showing the UI")
    VARS.RUNNING = True
