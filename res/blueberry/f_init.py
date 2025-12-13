# /res/blueberry/f_init.py


from . import lang
from . import task
from . import utils
from . import scene
from . import icons
from . import theme
from . import element
from . import background
from . import chat_message
import pygame as pg
import random
import os

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


class fonts_table:
    def __init__(self, name):
        self.name = name
        self.cache = {}
    
    def __repr__(self):
        return f"fonts_table(name={self.name} size={len(self.cache)})"
    
    def __getitem__(self, size):
        if size in self.cache:
            return self.cache[size]
        
        # print(f"creating font of {size=}")
        font = pg.font.SysFont(self.name, size)
        self.cache[size] = font
        return font


# your function here
def func():
    intentional_reset = getattr(VARS, "RESETTING", False) # this is cursed(?)
    is_soft = VARS.RUNNING
    VARS.RESETTING = False
    if is_soft:
        # soft reset - no shutdown before reinitialization
        if intentional_reset:
            # intentional reset guh
            log("-- Reinitialization, the window should re-open in a moment --")
        else:
            # non-intentional reset - crash
            log("WARN: Soft reset detected. Did the client just crash?")
    else:
        # hard reset - after shutdown, most likely first run
        log("")
        log("---[  INITIALIZING BLUEBERRY CLIENT  ]---")
        log("")
        encryption.old.funcs["Current"] = (encryption._f_encrypt, encryption._f_decrypt)
        encryption.old.docs["Current"] = encryption._f_encrypt.__doc__ or\
                                         encryption._f_decrypt.__doc__ or "\n    bro what\n"
    
    # generic variables setup
    chat_message.downloads_path = DOWNLOADS_PATH
    VARS.CLIENT_VERSION = "0.2.1-ALPHA"
    VARS.mousepos = pg.Vector2(-1, -1)
    VARS.frame = 0
    VARS.holding_ctrl = False
    VARS.holding_shift = False
    VARS.debug = False
    if not is_soft:
        VARS.active = scene.Main
    
    # bootstrapping everything lol
    task.bootstrap(globals())
    utils.bootstrap(globals())
    scene.bootstrap(globals())
    element.bootstrap(globals())
    task.Stream.sendmsg = fmap["sendmsg"]
    
    log("Initializing Pygame")
    pg.init() # yes that's it
    
    log("Reading config and parsing themes")
    # initializing path variables
    CONFIG.DEFAULTS = utils.GET_DEFAULT_CONFIG_OPTIONS()
    CONFIG.CLIENT = utils.GET_DEFAULT_CONFIG_OPTIONS()
    utils.CONFIG_FILE_PATH = os.getcwd() + "/config.txt"
    
    # parsing config file
    for i in utils.parse_config_file(CONFIG.CLIENT):
        log(i)
    
    # parsing app theme from config file
    name, this_theme, verbals = theme.parse_string_theme(CONFIG.CLIENT["theme"])
    theme.name = name
    theme.load_theme(this_theme)
    for i in verbals:
        log(i)
    
    # load different encryption alg if specified
    alg_pair = encryption.old.funcs.get(CONFIG.CLIENT["!algorithm"], None)
    if alg_pair is None:
        error_msg = f"Failed to load encryption algorithm {CONFIG.CLIENT['!algorithm']}, using Current instead"
        log(error_msg)
        task.FAILED.append([error_msg, 300])
        alg_pair = (encryption._f_encrypt, encryption._f_decrypt)
        CONFIG.CLIENT["!algorithm"] = "Current"
    else:
        encryption._f_encrypt, encryption._f_decrypt = alg_pair
    
    # set task.Stream values because it's currently extremely spaghetti
    # and i want to play with the numbers until it works
    try:
        chunksize = int(CONFIG.CLIENT["!stream-chunksize"])
        chunksize = min(max(chunksize, 1), 2048) # clamp to 1kb-2mb range
    except Exception as e:
        error_msg = f"Couldn't parse stream-chunksize: {e}"
        log(error_msg)
        task.FAILED.append([error_msg, 300])
        chunksize = 512
    task.Stream.chunksize = chunksize * 1024
    try:
        sleep_for = float(CONFIG.CLIENT["!stream-sleep_for"])
        sleep_for = max(sleep_for, 0.05)
    except Exception as e:
        error_msg = f"Couldn't parse stream-sleep_for: {e}"
        log(error_msg)
        task.FAILED.append([error_msg, 300])
        sleep_for = 2.0
    task.Stream.sleep_for = sleep_for
    
    # getting screen resolution from config (or default)
    display_data = pg.display.Info()
    max_res = display_data.current_w, display_data.current_h
    window_size = utils.parse_screen_res(CONFIG.CLIENT["window_size"], max_res)
    if window_size is None:
        log("Couldn't parse 'window_size' parameter, will use default")
        window_size = utils.parse_screen_res(CONFIG.DEFAULTS["window_size"], max_res)
    CONFIG.CLIENT["window_size"] = f"{window_size[0]}-{window_size[1]}"
    old_size = getattr(VARS, "window_size", None) # this is also cursed
    
    # setting up stuff in chat_message context
    VARS.window_size = pg.Vector2(window_size)
    chat_message.window_size = window_size
    VARS.lang = lang.langmap.get(CONFIG.CLIENT["lang"], lang.default)
    chat_message.error_codes = VARS.lang.ERROR_CODES
    
    # that log() explains what this block does lol
    log("Creating pygame window")
    splash = random.choice(VARS.lang.SPLASHES)
    pg.display.set_caption(VARS.lang.WINDOW_TITLE + splash)
    if not intentional_reset or VARS.window_size != old_size:
        VARS.canvas = pg.display.set_mode(window_size)
    VARS.clock = pg.time.Clock()
    
    # creating a dynamic table for fonts
    VARS.fonts = fonts_table(CONFIG.CLIENT["font"])
    chat_message.fonts = VARS.fonts
    
    # drawing the thing
    txt = VARS.fonts[30].render("Initializing Blueberry client", True, (255, 255, 255))
    VARS.canvas.blit(txt, txt.get_rect(center=VARS.window_size/2))
    pg.display.flip()
    pg.scrap.init()
    
    icons.draw()
    pg.display.set_icon(icons.app)
    
    # initializing elements and stuff
    pg.key.set_repeat(250, 30)
    element.Colorpicker._init()
    background.surface = VARS.canvas
    background.size = VARS.window_size
    
    for i in scene.to_init:
        i.init(is_soft)
    
    # soft restart checks
    if is_soft:
        scene.Console.logs_multiline.set_text("\n".join(scene.Console.logs_raw))
    
    # on-boot command
    if CONFIG.CLIENT["onboot"] and not CONFIG.CLIENT["onboot"].startswith("#"):
        log("Running on-boot command")
        try:
            exec(CONFIG.CLIENT["onboot"])
        except Exception as e:
            log(f"Exception occured: {e}")
            task.FAILED.append([f"On-boot command exception: {e}", 300])
    
    log("Done! Showing the UI")
    VARS.RUNNING = True
