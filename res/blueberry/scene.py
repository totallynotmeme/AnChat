# /res/blueberry/scene.py


from . import utils
from . import icons
from . import theme
from . import element
from . import background
from . import lang
from .chat_message import ChatMessage
import pygame as pg
from threading import Thread
import os

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


class Main:
    elements = []
    connecting = False
    protocol_button = None
    field_username = None
    field_address = None
    field_status = None
    background = None
    line_1 = 0
    line_2 = 0
    
    def draw(canvas):
        Main.background.step()
        for i in Main.elements:
            i.draw(canvas)
    
    def init(is_soft):
        c_base = theme.c["base"]
        c_background = theme.c["background"]
        c_text = theme.c["text"]
        c_accenttext = theme.c["accent text"]
        c_accent = theme.c["accent"]
        c_accent2 = theme.c["accent2"]
        
        Main.background = background.bgmap.get(CONFIG.CLIENT["background"], background.Lines)
        Main.background.init()
        origin = VARS.window_size/2
        
        Main.elements = []
        txt = VARS.lang.CONNECT_BUTTON
        button_size_x = VARS.fonts[25].size(txt)[0] + 25
        button = element.Button(
            pos = origin + pg.Vector2(0, 100),
            size = (button_size_x, 50),
            align = "center",
            callback = lambda: Thread(target=Main.button_connect).start(),
            hover_scale = 0.1,
        )
        button.surface.fill(c_base)
        txt = VARS.fonts[25].render(txt, True, c_text)
        button.surface.blit(txt, txt.get_rect(center=(button_size_x // 2, 25)))
        button.update_surf()
        Main.elements.append(button)
        
        if is_soft:
            username = Main.field_username.text
            address = Main.field_address.text
            status = Main.field_status.text
            protocol = Main.protocol_button.current
        
        Main.protocol_button = element.Optionsbutton(
            pos = origin + pg.Vector2(0, 40),
            size = (210, 30),
            align = "center",
            hover_scale = 0.05,
            color = c_accent,
            font = VARS.fonts[20],
            options = sorted(connection.protocol_list.keys()),
        )
        Main.elements.append(Main.protocol_button)
        
        
        Main.field_username = element.Line(
            pos = origin + pg.Vector2(0, -60),
            size = (580, 30),
            color = c_text,
            font = VARS.fonts[25],
            align = "center",
            edit = True,
            placeholder = VARS.lang.FIELD_USERNAME,
        )
        Main.elements.append(Main.field_username)
        Main.field_address = element.Line(
            pos = origin + pg.Vector2(0, -10),
            size = (580, 30),
            color = c_text,
            font = VARS.fonts[25],
            align = "center",
            edit = True,
            placeholder = VARS.lang.FIELD_ADDRESS,
        )
        Main.elements.append(Main.field_address)
        Main.field_status = element.Line(
            pos = origin + pg.Vector2(0, 170),
            size = (VARS.window_size.x-25, 25),
            color = c_accenttext,
            font = VARS.fonts[20],
            align = "center",
            edit = False,
        )
        Main.field_status.set_text(VARS.lang.STATUS_TEXT_DEFAULT)
        Main.elements.append(Main.field_status)
        if is_soft:
            Main.field_username.set_text(username)
            Main.field_address.set_text(address)
            Main.field_status.set_text(status)
            Main.protocol_button.current = protocol
            Main.protocol_button.redraw()
    
    
    def button_connect():
        t = task.Connect(Main.field_address.text, Main.protocol_button.current)
        t.run()
    
    
    def handle_event(ev):
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                Console.toggle()
            elif Main.connecting:
                return
        
        if ev.type == pg.TEXTINPUT and Main.connecting:
            return
        
        if ev.type == pg.MOUSEBUTTONDOWN and Main.connecting:
            return
        
        if ev.type == pg.MOUSEMOTION:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        
        any(i.handle_event(ev) for i in Main.elements)



class Chat:
    messages = []
    scroll = 0
    scroll_goal = 0
    scroll_step = 0
    input_box = None
    status_text_pos = (0, 0)
    elements = []
    
    def draw(canvas):
        Main.background.step()
        
        Chat.scroll = (Chat.scroll * 3 + Chat.scroll_goal) / 4
        
        for i in Chat.messages:
            i.draw(canvas, Chat.scroll)
            if VARS.debug:
                pg.draw.rect(canvas, (0, 255, 127), i.rect, 1)
        
        canvas.blit(ChatMessage.expanded, (5, 40))
        
        pg.draw.line(canvas, (50, 50, 50), (0, Chat.y_limit-1), (VARS.window_size.x, Chat.y_limit-1))
        pg.draw.rect(canvas, theme.c["background"], pg.Rect(0, Chat.y_limit, VARS.window_size.x, 50))
        for i in Chat.elements:
            i.draw(canvas)
        
        if not connection.ALIVE:
            txt = VARS.fonts[15].render(connection.EXIT_CODE, True, (255, 127, 127))
            canvas.blit(txt, Chat.status_text_pos)
    
    def push(msg):
        if len(Chat.messages) == 0:
            offset = 25
        else:
            last = Chat.messages[-1]
            offset = last.offset + last.size[1] + 5
        msg.offset = offset
        Chat.messages.append(msg)
        scroller = offset + msg.size[1] - VARS.window_size.y + 100
        Chat.scroll_goal = max(Chat.scroll_goal, scroller)
    
    def disconnect():
        txt = VARS.lang.MESSAGE_DISCONNECTED.encode()
        sys_msg = {b"author": b"~SYSTEM", b"content": txt}
        fmap["recvmsg"](sys_msg)
        connection.protocol.disconnect("Client disconnected from the server")
        VARS.active = Main
    
    def parse_command(prompt):
        if not prompt.startswith("/"):
            return False
        
        if prompt == "/disconnect":
            Chat.disconnect()
        
        if prompt == "/dump":
            filename = utils.random_string(16) + ".txt" #".dump"
            
            """ to do: make in-app dump reader
            for i in Chat.messages:
                chunk = bytearray()
                for name, data in i.raw.items():
                    name_length = len(name).to_bytes(1, "big")
                    data_length = len(data).to_bytes(3, "big")
                    chunk.extend(data + data_length + name + name_length)
                dump.append(len(chunk).to_bytes(4, "big") + chunk)
            open(filename, "wb").write(b"".join(dump))
            """
            dump = "\n\n\n".join(f"[{i.author}]\n{i.content}" for i in Chat.messages)
            open(filename, "w", encoding="utf-8").write(dump)
            
            txt = VARS.lang.MESSAGE_DUMPED.format(filename).encode()
            sys_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](sys_msg)
        
        if prompt == "/clear":
            Chat.messages = []
            Chat.scroll_goal = 0
            txt = VARS.lang.MESSAGE_CLEARED.encode()
            sys_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](sys_msg)
        
        if prompt == "/help":
            txt = VARS.lang.MESSAGE_HELP.encode()
            sys_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](sys_msg)
        
        return True
    
    def init(is_soft):
        c_base = theme.c["base"]
        c_background = theme.c["background"]
        c_text = theme.c["text"]
        c_accent = theme.c["accent"]
        c_accent2 = theme.c["accent2"]
        
        Chat.elements = []
        Chat.input_box = element.Line(
            pos = (VARS.window_size.x/2, VARS.window_size.y - 25),
            size = (VARS.window_size.x - 50, 50),
            color = c_text,
            font = VARS.fonts[25],
            align = "center",
            edit = True,
            placeholder = VARS.lang.CHATBOX_FIELD,
        )
        Chat.y_limit = VARS.window_size.y - 50
        Chat.scroll_step = VARS.window_size.y / 5
        Chat.status_text_pos = (5, VARS.window_size.y - 70)
        Chat.elements.append(Chat.input_box)
        if Chat.messages:
            # preventing a weird crash - updating settings in Chat scene
            for i in Chat.messages:
                i.author_element.font = VARS.fonts[25]
                i.text_element.font = VARS.fonts[20]
                i.reinit()
            last = Chat.messages[-1]
            scroller = last.offset + last.size[1] - VARS.window_size.y + 100
            Chat.scroll_goal = max(Chat.scroll_goal, scroller)
        # disconnect button
        button = element.Button(
            pos = (110, 20),
            size = (120, 30),
            align = "center",
            callback = Chat.disconnect,
            hover_scale = 0.1,
        )
        button.surface.fill(c_accent2)
        txt = VARS.lang.CHAT_DISCONNECT
        txt = VARS.fonts[15].render(txt, True, c_text)
        button.surface.blit(txt, txt.get_rect(center=(60, 15)))
        button.update_surf()
        Chat.elements.append(button)
        if is_soft:
            # to be refactored - realign messages after window resize
            last = None
            for msg in Chat.messages:
                if last:
                    offset = last.offset + last.size[1] + 5
                else:
                    offset = 25
                msg.offset = offset
                last = msg
    
    
    def handle_event(ev):
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                Console.toggle()
                return
            elif ev.key == pg.K_RETURN:
                if Chat.input_box.active and Chat.input_box.text:
                    prompt = Chat.input_box.text
                    Chat.input_box.set_text("")
                    if Chat.parse_command(prompt.strip()):
                        return
                    
                    t = task.Sendmsg(
                        author = CONFIG.OWN_NAME.encode(),
                        content = prompt.encode()
                    )
                    t.run()
                else:
                    # this causes a bug when you press enter with text selected
                    # doesn't affect anything and gets fixed with one click so eh
                    Chat.input_box.active = True
                return
        
        if ev.type == pg.MOUSEWHEEL:
            if len(Chat.messages) == 0:
                limit = 0
            else:
                last = Chat.messages[-1]
                limit = last.offset + last.size[1] - 200
            Chat.scroll_goal -= ev.precise_y * Chat.scroll_step
            Chat.scroll_goal = min(max(Chat.scroll_goal, -200), limit)
            Chat.scroll -= ev.precise_y * Chat.scroll_step / 10
            return
        
        if ev.type == pg.MOUSEMOTION:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        
        if ev.type == pg.MOUSEBUTTONDOWN and ev.button == pg.BUTTON_RIGHT:
            # MORE SPAGHETTI OHNOES
            ChatMessage.expanded = pg.Surface((0, 0))
        
        if ev.type == pg.TEXTINPUT:
            Chat.input_box.event_TEXTINPUT(ev)
            return
    
        if ev.type == pg.DROPFILE:
            if not os.path.isfile(ev.file):
                return
            
            if VARS.show_stream_warn: # temp
                VARS.show_stream_warn = False
                txt = VARS.lang.MESSAGE_STREAMING_WARN.encode()
            else:
                try:
                    t = task.Stream(ev.file)
                    t.run()
                    txt = VARS.lang.MESSAGE_STREAMING_START.format(t.name).encode()
                except Exception as e:
                    txt = VARS.lang.MESSAGE_STREAMING_FAIL.format(e).encode()
            
            you_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](you_msg)
            return
        
        any(i.handle_event(ev) for i in Chat.elements + Chat.messages)



class Options:
    button = None
    behind = None
    container = None
    apply_button = None
    option_elements = {}
    theme_elements = []
    elements = ()
    category_elements = {}
    category_current = "standard"
    all_fonts = {}
    font_preview = None
    # i need to refactor this smh
    previous_font = None
    previous_bg = None
    previous_preset = None
    previous_category = None
    previous_algorithm = None
    previous_pickerhold = False
    
    def draw(canvas):
        Main.background.step()
        
        # title thingy
        txt = VARS.lang.OPTIONS_TITLE
        txt = VARS.fonts[35].render(txt, True, theme.c["text"])
        txt_shift = (VARS.window_size.x < 750) * 100
        canvas.blit(txt, txt.get_rect(center=(VARS.window_size.x/2 + txt_shift, 25)))
        
        # font
        this_font = Options.option_elements["font"].current
        if Options.previous_font != this_font:
            Options.previous_font = this_font
            Options.font_preview.font = Options.all_fonts[this_font]
        
        # background
        this_bg = Options.option_elements["bg"].current
        if Options.previous_bg is None:
            Options.previous_bg = this_bg
        if Options.previous_bg != this_bg:
            Options.previous_bg = this_bg
            Main.background = background.bgmap.get(this_bg, background.Black)
            Main.background.init()
        
        # themes
        this_category = Options.option_elements["colorcategory"].current.lower()
        picker = Options.option_elements["colorpicker"]
        preset_button = Options.option_elements["themepreset"]
        
        if Options.previous_preset != preset_button.current:
            Options.previous_preset = preset_button.current
            Options.previous_category = None
            if preset_button.current != "Custom":
                theme.temp = theme.all_themes[preset_button.current].copy()
        
        if Options.previous_category != this_category:
            Options.previous_category = this_category
            color = theme.temp[this_category]
            picker.set_color(color)
            Options.update_preview()
        
        if Options.previous_pickerhold and not picker.holding:
            theme.temp[this_category] = picker.color[:3]
            if preset_button.current != "Custom":
                preset_button.current = "Custom"
                preset_button.redraw()
            Options.update_preview()
        Options.previous_pickerhold = picker.holding
        
        # encryption algorithm
        alg_button = Options.option_elements["alg"]
        if Options.previous_algorithm != alg_button.current:
            Options.previous_algorithm = alg_button.current
            doc_string = encryption.old.funcs[alg_button.current].__doc__
            doc_string = "Documentation notes:\n" + doc_string
            Options.option_elements["alg_docs"].set_text(doc_string)
        
        # drawing everything
        Options.container.draw(canvas)
        pg.draw.rect(canvas, theme.c["background"], pg.Rect(0, 0, 270, 40))
        pg.draw.line(canvas, theme.c["base"], (0, 40), (270, 40))
        pg.draw.line(canvas, theme.c["base"], (270, 40), (270, 0))
        for i in Options.elements:
            i.draw(canvas)
    
    def update_preview():
        for ind, color in enumerate(theme.categories):
            this = Options.theme_elements[ind]
            text_color = theme.temp["text"]
            if "text" in color:
                fill_color = (sum(theme.temp[color]) <= 381) * 255
                this.surface.fill((fill_color, fill_color, fill_color))
                if color == "accent text":
                    text_color = theme.temp[color]
            else:
                this.surface.fill(theme.temp[color])
            display_name = VARS.lang.THEME_TABLE.get(color, color.title())
            txt = VARS.fonts[20].render(display_name, True, text_color)
            this.surface.blit(txt, txt.get_rect(center=this.size/2))
            this.update_surf()
    
    def init(is_soft):
        c_base = theme.c["base"]
        c_background = theme.c["background"]
        c_text = theme.c["text"]
        c_accenttext = theme.c["accent text"]
        c_accent = theme.c["accent"]
        c_accent2 = theme.c["accent2"]
        
        # draw main options menu button
        button = element.Button(
            pos = (5, 5),
            size = (30, 30),
            align = "topleft",
            callback = Options.toggle,
            hover_scale = 0,
        )
        button.surface.blit(icons.options, (0, 0))
        button.update_surf()
        
        Options.button = button
        Main.elements.append(button)
        Chat.elements.append(button)
        
        # apply and restart button
        button = element.Button(
            pos = (100, 20),
            size = (100, 30),
            align = "center",
            callback = Options.apply_and_restart,
            hover_scale = 0.1,
        )
        button.surface.fill(c_base)
        txt = VARS.lang.OPTIONS_APPLY
        txt = VARS.fonts[15].render(txt, True, c_text)
        button.surface.blit(txt, txt.get_rect(center=(50, 15)))
        button.update_surf()
        Options.apply_button = button
        
        # reset options button
        button = element.Button(
            pos = (210, 20),
            size = (100, 30),
            align = "center",
            callback = Options.reset_settings,
            hover_scale = 0.1,
        )
        button.surface.fill(c_accent2)
        txt = VARS.lang.OPTIONS_RESET
        txt = VARS.fonts[15].render(txt, True, c_text)
        button.surface.blit(txt, txt.get_rect(center=(50, 15)))
        button.update_surf()
        Options.reset_button = button
        
        if is_soft:
            container_scroll = Options.container.scroll_goal
        
        # create container for all options
        Options.container = element.Container(
            pos = (0, 50),
            size = (VARS.window_size.x, VARS.window_size.y - 50),
        )
        
        if is_soft:
            Options.container.scroll = container_scroll
            Options.container.scroll_goal = container_scroll
        
        # option categories
        def gen_callback(name):
            def callback():
                item = Options.container
                table = Options.category_elements
                Options.category_current = name
                item.elements = table["base"].copy()
                item.elements.extend(table[name])
            return callback
        
        font_size = VARS.fonts[15].size(" ")[0]
        offset = (10, 0)
        for i in ["standard", "advanced"]:
            display_name = VARS.lang.OPTIONS_CATEGORY_TABLE[i]
            size = (20 + len(display_name) * font_size, 24)
            center = (10 + len(display_name) * font_size/2, 12)
            offset = (offset[0] + size[0]/2, offset[1])
            last = Options.container.push(element.Button,
                offset = offset,
                size = size,
                align = "midtop",
                hover_scale = 0.05,
                callback = gen_callback(i),
            )
            last.surface.fill(c_accent)
            txt = VARS.fonts[15].render(display_name, True, c_text)
            last.surface.blit(txt, txt.get_rect(center=center))
            last.update_surf()
            offset = (offset[0] + size[0]/2 + 10, -29)
        Options.category_elements["base"] = Options.container.elements
        Options.container.elements = []
        
        # start of standard category
        # language
        last = Options.container.push(element.Line,
            size_y = 30,
            offset = (0, 55),
            color = c_text,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_LANGUAGE)
        
        last = Options.container.push(element.Optionsbutton,
            offset = (40, 20),
            size = (60, 30),
            align = "center",
            hover_scale = 0.1,
            color = c_base,
            font = VARS.fonts[20],
            options = sorted(lang.langmap.keys()),
        )
        Options.option_elements["lang"] = last
        
        # window size / resolution
        last = Options.container.push(element.Line,
            offset = (0, 10),
            size_y = 30,
            color = c_text,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_RESOLUTION)
        
        last = Options.container.push(element.Line,
            offset = (10, 0),
            size_y = 30,
            color = c_accent,
            font = VARS.fonts[25],
            align = "topleft",
            edit = True,
            placeholder = "1920-1080",
        )
        Options.option_elements["res"] = last
        
        # font
        last = Options.container.push(element.Line,
            offset = (0, 15),
            size_y = 30,
            color = c_text,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_FONT)
        
        last = Options.container.push(element.Line,
            size_y = 15,
            color = c_accenttext,
            font = VARS.fonts[15],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_FONT_WARN)
        
        if is_soft:
            for i in Options.all_fonts.keys():
                # probably shouldn't throw an exception
                Options.all_fonts[i] = pg.font.SysFont(i, 30)
            all_fonts = Options.all_fonts
        else:
            all_fonts = {}
            for i in pg.font.get_fonts():
                try:
                    all_fonts[i] = pg.font.SysFont(i, 30)
                except Exception as e:
                    print(f"Error occured when importing font {i}: {e}")
            
            for key, val in all_fonts.copy().items():
                if not utils.is_monospace(val):
                    all_fonts.pop(key)
            Options.all_fonts = all_fonts
        
        last = Options.container.push(element.Optionsbutton,
            offset = (160, 20),
            size = (300, 30),
            align = "center",
            hover_scale = 0.04,
            color = c_base,
            font = VARS.fonts[20],
            options = sorted(all_fonts.keys()),
        )
        Options.option_elements["font"] = last
        
        last = Options.container.push(element.Line,
            size_y = 30,
            color = c_text,
            font = VARS.fonts[30],
            align = "topleft",
            edit = True,
            placeholder = "AaBbCc АаБбВв 0123 .,!?/@",
        )
        Options.font_preview = last
        
        # background
        last = Options.container.push(element.Line,
            offset = (0, 20),
            size_y = 30,
            color = c_text,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_BACKGROUND)
        
        last = Options.container.push(element.Optionsbutton,
            offset = (60, 20),
            size = (100, 30),
            align = "center",
            hover_scale = 0.1,
            color = c_base,
            font = VARS.fonts[20],
            options = list(background.bgmap.keys()),
        )
        Options.option_elements["bg"] = last
        
        # themes and stuff
        last = Options.container.push(element.Line,
            offset = (0, 70),
            size_y = 30,
            color = c_text,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_THEME)
        
        last = Options.container.push(element.Optionsbutton,
            offset = (110, 20),
            size = (200, 30),
            align = "center",
            hover_scale = 0.1,
            color = c_accent,
            font = VARS.fonts[20],
            options = sorted(theme.all_themes.keys()),
        )
        last.options.remove("Default")
        last.options.insert(0, "Default")
        Options.option_elements["themepreset"] = last
        
        if is_soft:
            category = Options.option_elements["colorcategory"].current
        else:
            category = theme.categories[0].title()
        
        last = Options.container.push(element.Optionsbutton,
            offset = (85, 20),
            size = (150, 30),
            align = "center",
            hover_scale = 0.1,
            color = c_base,
            font = VARS.fonts[20],
            options = list(map(str.title, theme.categories)),
        )
        last.current = category
        last.redraw()
        Options.option_elements["colorcategory"] = last
        
        last = Options.container.push(element.Colorpicker,
            offset = (10, -5),
        )
        Options.option_elements["colorpicker"] = last
        last.update()
        
        # theme preview elements
        Options.theme_elements = []
        def gen_callback(where):
            def callback():
                Options.option_elements["colorcategory"].current = where
                Options.option_elements["colorcategory"].redraw()
            return callback
        
        offset = (320, -245)
        font_size = VARS.fonts[20].size(" ")[0]
        for i in theme.categories:
            length = len(VARS.lang.THEME_TABLE.get(i, i))
            size = (20 + length * font_size, 30)
            last = Options.container.push(element.Button,
                offset = offset,
                size = size,
                align = "midleft",
                hover_scale = 0.1,
                callback = gen_callback(i.title()),
            )
            Options.theme_elements.append(last)
            offset = (320, 0)
        
        Options.category_elements["standard"] = Options.container.elements
        Options.container.elements = []
        
        # start of advanced category (might rename later idk)
        # dev options
        last = Options.container.push(element.Line,
            offset = (0, 55),
            size_y = 30,
            color = c_text,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_DEVELOPER)
        
        # debug mode
        def func():
            VARS.debug = not VARS.debug
        last = Options.container.push(element.Button,
            offset = (70, 20),
            size = (120, 30),
            align = "center",
            hover_scale = 0.04,
            callback = func,
        )
        last.surface.fill(c_base)
        txt = VARS.fonts[15].render("Toggle debug", True, c_text)
        last.surface.blit(txt, txt.get_rect(center=(60, 15)))
        last.update_surf()
        
        # switch between scenes
        # scene.Main
        def func():
            VARS.active = Main
        last = Options.container.push(element.Button,
            offset = (70, 20),
            size = (120, 30),
            align = "center",
            hover_scale = 0.04,
            callback = func,
        )
        last.surface.fill(c_base)
        txt = VARS.fonts[15].render("Go to Main", True, c_text)
        last.surface.blit(txt, txt.get_rect(center=(60, 15)))
        last.update_surf()
        # scene.Chat
        def func():
            VARS.active = Chat
        last = Options.container.push(element.Button,
            offset = (200, -35),
            size = (120, 30),
            align = "center",
            hover_scale = 0.04,
            callback = func,
        )
        last.surface.fill(c_base)
        txt = VARS.fonts[15].render("Go to Chat", True, c_text)
        last.surface.blit(txt, txt.get_rect(center=(60, 15)))
        last.update_surf()
        
        # icon dump
        last = Options.container.push(element.Button,
            offset = (70, 20),
            size = (120, 30),
            align = "center",
            hover_scale = 0.04,
            callback = icons.dump,
        )
        last.surface.fill(c_base)
        txt = VARS.fonts[15].render("Dump icons", True, c_text)
        last.surface.blit(txt, txt.get_rect(center=(60, 15)))
        last.update_surf()
        
        # warning
        last = Options.container.push(element.Line,
            offset = (20, 55),
            size_y = 40,
            color = c_accenttext,
            font = VARS.fonts[35],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_ADVANCED_WARN1)
        # warning x2
        last = Options.container.push(element.Multiline,
            offset = (20, 0),
            size_y = 100,
            color = c_accenttext,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text(VARS.lang.OPTIONS_ADVANCED_WARN2)
        
        # encryption function
        last = Options.container.push(element.Line,
            offset = (0, 55),
            size_y = 30,
            color = c_text,
            font = VARS.fonts[25],
            align = "topleft",
            edit = False,
        )
        last.set_text("Encryption function")
        
        last = Options.container.push(element.Optionsbutton,
            offset = (110, 20),
            size = (200, 30),
            align = "center",
            hover_scale = 0.1,
            color = c_base,
            font = VARS.fonts[20],
            options = ["Current"] + list(encryption.old.funcs.keys()),
        )
        Options.option_elements["alg"] = last
        
        last = Options.container.push(element.Multiline,
            offset = (20, -10),
            size_y = 500,
            color = c_text,
            font = VARS.fonts[20],
        )
        Options.option_elements["alg_docs"] = last
        
        Options.category_elements["advanced"] = Options.container.elements
        Options.container.elements = Options.category_elements["base"].copy()
        Options.container.elements.extend(Options.category_elements[Options.category_current])
        
        Options.reset_settings()
        Options.update_preview()
        Options.previous_bg = None
        Options.elements = (Options.button, Options.apply_button, Options.reset_button)
    
    def apply_and_restart():
        if CONFIG.CLIENT["window_size"] != Options.option_elements["res"].text:
            pg.quit()
        #fmap["shutdown"]()
        name = Options.option_elements["themepreset"].current
        theme_thing = theme.theme_to_str(name, theme.temp)
        new_config = CONFIG.CLIENT.copy()
        new_config.update({
            "lang": Options.option_elements["lang"].current,
            "window_size": Options.option_elements["res"].text,
            "font": Options.option_elements["font"].current,
            "background": Options.option_elements["bg"].current,
            "theme": theme_thing,
            "!algorithm": Options.option_elements["alg"].current,
        })
        utils.save_config_file(new_config)
        VARS.RESETTING = True
        fmap["init"]()
    
    def reset_settings():
        table = Options.option_elements
        table["lang"].current = CONFIG.CLIENT["lang"]
        table["lang"].redraw()
        table["res"].set_text(CONFIG.CLIENT["window_size"])
        table["font"].current = CONFIG.CLIENT["font"]
        table["font"].redraw()
        table["bg"].current = CONFIG.CLIENT["background"]
        table["bg"].redraw()
        theme.temp = theme.c.copy()
        category = table["colorcategory"].current.lower()
        table["colorpicker"].set_color(theme.temp[category])
        table["themepreset"].current = theme.name
        table["themepreset"].redraw()
        table["alg"].current = CONFIG.CLIENT["!algorithm"]
        table["alg"].redraw()
        Options.previous_algorithm = None
    
    def toggle():
        if VARS.active == Options:
            VARS.active = Options.behind
            return
        
        Options.behind = VARS.active
        VARS.active = Options
    
    
    def handle_event(ev):
        if ev.type == pg.MOUSEMOTION:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
    
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                Console.toggle()
                return
        
        # handle overlay buttons first, then the rest
        if any(i.handle_event(ev) for i in Options.elements):
            return
        Options.container.handle_event(ev)



class Console:
    history = []
    history_ind = 0
    behind = None
    surf = None
    lines = 0
    input_y = 0
    prompt_line = None
    prompt_prefix = None
    prompt_prefix_rect = None
    logs_multiline = None
    logs_raw = []
    elements = ()
    is_selecting = False
    
    def draw(canvas):
        Console.behind.draw(canvas)
        if Console.is_selecting:
            if element.last.hovered:
                rect = element.last.hovered.true_bb
                pg.draw.rect(canvas, (255, 0, 0), rect, 3)
            return
        
        canvas.blit(Console.surf, (0, 0))
        
        canvas.blit(Console.prompt_prefix, Console.prompt_prefix_rect)
        bb = Console.prompt_line.draw(canvas)
        bb2 = Console.logs_multiline.draw(canvas)
    
    def init(is_soft):
        Console.surf = pg.Surface(VARS.window_size)
        Console.surf.set_alpha(200)
        Console.lines = int(VARS.window_size.y / 16 - 1)
        Console.input_y = int(VARS.window_size.y - 16)
        prompt_line = element.Line(
            pos = (44, VARS.window_size.y),
            size = (VARS.window_size.x-55, 20),
            color = (255, 255, 255),
            font = VARS.fonts[20],
            align = "bottomleft",
            edit = True,
        )
        logs_multiline = element.Multiline(
            pos = (0, 0),
            size = (VARS.window_size.x, VARS.window_size.y-20),
            color = (150, 150, 150),
            font = VARS.fonts[20],
            align = "topleft",
            edit = False,
        )
        Console.prompt_line = prompt_line
        Console.prompt_prefix = VARS.fonts[20].render(">>>", True, (255, 255, 255))
        Console.prompt_prefix_rect = Console.prompt_prefix.get_rect(bottomleft=(0, VARS.window_size.y))
        Console.logs_multiline = logs_multiline
        Console.elements = (Console.prompt_line, Console.logs_multiline)
    
    def toggle():
        if VARS.active == Console:
            VARS.active = Console.behind
            return
        
        Console.behind = VARS.active
        VARS.active = Console
    
    def run(_user_input):
        global _
        if _user_input == "clear":
            Console.logs_multiline.set_text("")
            Console.logs_raw = []
            return
        if _user_input == "clearhistory":
            Console.history = []
            return
        if _user_input == "select":
            element.last.hovered = None
            Console.is_selecting = True
            return
        if _user_input == "?" or _user_input == "help":
            log("""

console uses eval() to run arbitrary Python code, useful for debugging.
if command format is 'var = 123', exec('global var; var = 123') is used
'some.thing = value' throws an error? try adding ` at the start

custom console commands / shortcuts:
clear - clear console output
clearhistory - erase command history
select - select element, similar to browser devtools
`(command) - run with exec() instead of eval()
""")
            return
        if _user_input.strip() == "":
            return
        if _user_input.strip().startswith("#"):
            return
        
        try:
            if _user_input.startswith("`"):
                exec(_user_input[1:])
            elif " = " in _user_input:
                # exec assignment
                _assign_what = _user_input.split("=")[0].replace("*", "")
                exec(f"global {_assign_what}; {_user_input}")
            else:
                # eval statement
                _ = eval(_user_input)
                if _ is not None:
                    log(repr(_))
        except Exception as e:
            log(f"Error: {e}. Run '?' for help")
        except SystemExit:
            log("SystemExit call blocked as it hangs the whole window. Use `VARS.RUNNING=False instead")
    
    
    def handle_event(ev):
        global _
        
        if ev.type == pg.MOUSEMOTION:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                if Console.is_selecting:
                    Console.is_selecting = False
                    return
                Console.toggle()
                return
            history = Console.history or [""]
            
            if ev.key == pg.K_RETURN:
                user_command = Console.prompt_line.text
                Console.prompt_line.active = True
                Console.logs_multiline.active = False
                
                Console.run(user_command)
                if history and user_command and user_command != history[-1]:
                    Console.history.append(user_command)
                
                Console.history_ind = len(Console.history)
                Console.logs_raw.append(">>> " + user_command)
                Console.logs_multiline.append_text(">>> " + user_command)
                Console.prompt_line.set_text("")
                return
            
            if ev.key == pg.K_UP:
                Console.history_ind = max(Console.history_ind - 1, 0)
                Console.prompt_line.set_text(history[Console.history_ind])
                return
            if ev.key == pg.K_DOWN:
                Console.history_ind = min(Console.history_ind + 1, len(history))
                if Console.history_ind == len(history):
                    Console.prompt_line.set_text("")
                else:
                   Console.prompt_line.set_text(history[Console.history_ind])
                return
        
        if Console.is_selecting:
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == pg.BUTTON_LEFT:
                _ = element.last.hovered
                Console.logs_raw.append(repr(_))
                Console.logs_multiline.append_text(repr(_))
                Console.is_selecting = False
            else:
                Console.behind.handle_event(ev)
            return
        
        any(i.handle_event(ev) for i in Console.elements)


to_init = (Main, Chat, Options, Console)
