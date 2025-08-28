# /res/blueberry/scene.py


from . import utils
from . import element
import pygame as pg
from threading import Thread
import os

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


class Main:
    surf = None
    elements = []
    connecting = False
    protocol_button = None
    field_username = None
    field_address = None
    field_status = None
    bg_filler = None
    bg_scanline_1 = 0
    bg_scanline_2 = 0
    
    def update_surf():
        Main.surf.blit(Main.bg_filler, (0, 0))
        step = VARS.window_size.y / 4
        Main.bg_scanline_1 += 1
        Main.bg_scanline_1 %= step
        Main.bg_scanline_2 += 0.73
        Main.bg_scanline_2 %= step * 2
        y1 = Main.bg_scanline_1 - 100
        y2 = Main.bg_scanline_2 - 100
        for offset in range(5):
            p_from = (0, y1 + 100)
            p_to = (VARS.window_size.x, y1)
            pg.draw.aaline(Main.surf, (0, 30, 60), p_from, p_to)
            y1 += step
        for offset in range(3):
            p_from = (0, y2 + 50)
            p_to = (VARS.window_size.x, y2)
            pg.draw.aaline(Main.surf, (0, 30, 60), p_from, p_to)
            y2 += step*2
    
    def draw(canvas):
        Main.update_surf()
        canvas.blit(Main.surf, (0, 0))
        for i in Main.elements:
            #if i.type == "line" and i.edit:
            #    pg.draw.rect(canvas, (255, 255, 255), i.bounding_box, 1)
            i.draw(canvas)
    
    def init():
        Main.bg_filler = pg.Surface(VARS.window_size)
        txt = VARS.lang.CORE_VERSION.format(VARS.CORE_VERSION)
        txt = VARS.fonts[15].render(txt, True, (100, 100, 100))
        Main.bg_filler.blit(txt, txt.get_rect(topright=(VARS.window_size.x-3, 3)))
        
        txt = VARS.lang.CLIENT_VERSION.format(VARS.CLIENT_VERSION)
        txt = VARS.fonts[15].render(txt, True, (100, 100, 100))
        Main.bg_filler.blit(txt, txt.get_rect(topright=(VARS.window_size.x-3, 18)))
        
        Main.surf = pg.Surface(VARS.window_size)
        Main.update_surf()
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
        button.surface.fill((0, 63, 127))
        txt = VARS.fonts[25].render(txt, True, (255, 255, 255))
        button.surface.blit(txt, txt.get_rect(center=(button_size_x // 2, 25)))
        button.update_surf()
        Main.elements.append(button)
        
        Main.protocol_button = element.Button(
            pos = origin + pg.Vector2(0, 40),
            size = (210, 30),
            align = "center",
            callback = Main.button_change_protocol,
            hover_scale = 0.05,
        )
        Main.protocol_button.surface.fill((0, 63, 31))
        txt = VARS.fonts[20].render(CONFIG.PROTOCOL, True, (255, 255, 255))
        Main.protocol_button.surface.blit(txt, txt.get_rect(center=(105, 15)))
        Main.protocol_button.update_surf()
        Main.elements.append(Main.protocol_button)
        
        
        Main.field_username = element.Line(
            pos = origin + pg.Vector2(0, -60),
            size = (600, 30),
            color = (255, 255, 255),
            font = VARS.fonts[25],
            align = "center",
            edit = False,
            placeholder = VARS.lang.FIELD_USERNAME,
        )
        Main.elements.append(Main.field_username)
        Main.field_address = element.Line(
            pos = origin + pg.Vector2(0, -10),
            size = (600, 30),
            color = (255, 255, 255),
            font = VARS.fonts[25],
            align = "center",
            edit = False,
            placeholder = VARS.lang.FIELD_ADDRESS,
        )
        Main.elements.append(Main.field_address)
        Main.field_status = element.Line(
            pos = origin + pg.Vector2(0, 170),
            size = (VARS.window_size.x-25, 25),
            color = (255, 255, 190),
            font = VARS.fonts[20],
            align = "center",
            edit = False,
        )
        Main.field_status.set_text(VARS.lang.STATUS_TEXT_DEFAULT)
        Main.elements.append(Main.field_status)
    
    
    def button_connect():
        Main.connecting = True
        Main.field_status.set_text(VARS.lang.STATUS_TEXT_TRYING)
        try:
            CONFIG.OWN_NAME = Main.field_username.text or "Anon"
            CONFIG.PASSWORD = Main.field_address.text.encode()
            fmap["apply_config"]()
            
            bitarray = wordip.decode(Main.field_address.text)
            addr, port = connection.protocol.frombits(bitarray)
            connection.connect(addr, port)
            VARS.active = Chat
            
            txt = VARS.lang.MESSAGE_CONNECTED.encode()
            system_join_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](system_join_msg)
            Main.connecting = False
            Main.field_status.set_text(VARS.lang.STATUS_TEXT_DEFAULT)
        except Exception as e:
            log(f"Error during connection attempt: {e}")
            Main.connecting = False
            Main.field_status.set_text(VARS.lang.STATUS_TEXT_FAILED.format(e))
    
    
    def button_change_protocol():
        sorted_protocols = sorted(connection.protocol_list.keys())
        
        if CONFIG.PROTOCOL in sorted_protocols:
            this_ind = sorted_protocols.index(CONFIG.PROTOCOL)
        else:
            this_ind = 0
        
        this_ind += 1
        this_ind %= len(sorted_protocols)
        CONFIG.PROTOCOL = sorted_protocols[this_ind]
        
        Main.protocol_button.surface.fill((0, 63, 31))
        txt = VARS.fonts[20].render(CONFIG.PROTOCOL, True, (255, 255, 255))
        Main.protocol_button.surface.blit(txt, txt.get_rect(center=(105, 15)))
        Main.protocol_button.update_surf()
    
    
    def event_KEYDOWN(ev):
        if ev.key == pg.K_ESCAPE:
            Console.toggle()
        elif not Main.connecting:
            any(i.event_KEYDOWN(ev) for i in Main.elements)
    
    def event_MOUSEBUTTONDOWN(ev):
        if Main.connecting:
            return
        cursor_y = ev.pos[1]
        if ev.button == pg.BUTTON_LEFT:
            for i in Main.elements:
                if i.type == "line" and i != Main.field_status:
                    i.edit = abs(cursor_y - i.pos.y) < i.size.y / 2
        any(i.event_MOUSEBUTTONDOWN(ev) for i in Main.elements)
    
    def event_MOUSEBUTTONUP(ev):
        if Main.connecting:
            return
        any(i.event_MOUSEBUTTONUP(ev) for i in Main.elements)
    
    def event_MOUSEMOTION(ev):
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        any(i.event_MOUSEMOTION(ev) for i in Main.elements)
    
    def event_TEXTINPUT(ev):
        if Main.connecting:
            return
        any(i.event_TEXTINPUT(ev) for i in Main.elements)



class Chat:
    messages = []
    scroll = 0
    scroll_goal = 0
    scroll_step = 0
    input_box = None
    status_text_pos = (0, 0)
    streaming_file = None
    streaming_name = ""
    stream_followup = False
    elements = []
    
    def draw(canvas):
        Main.update_surf()
        canvas.blit(Main.surf, (0, 0))
        
        Chat.scroll = (Chat.scroll * 3 + Chat.scroll_goal) / 4
        
        for i in Chat.messages:
            i.draw(canvas, Chat.scroll)
        
        pg.draw.line(canvas, (50, 50, 50), (0, Chat.y_limit-1), (VARS.window_size.x, Chat.y_limit-1))
        pg.draw.rect(canvas, (0, 0, 0), pg.Rect(0, Chat.y_limit, VARS.window_size.x, 50))
        for i in Chat.elements:
            i.draw(canvas)
        
        if connection.ALIVE:
            # stream file if needed
            if Chat.streaming_file is not None:
                chunk = Chat.streaming_file.read(12288)
                if chunk == b"":
                    txt = VARS.lang.MESSAGE_STREAMING_END.encode()
                    you_msg = {b"author": b"~YOU", b"content": txt}
                    fmap["recvmsg"](you_msg)
                    Chat.streaming_file.close()
                    Chat.streaming_file = None
                    public_msg = {
                        b"author": CONFIG.OWN_NAME.encode(),
                        b"content": b"File:",
                        b"filename": Chat.streaming_name,
                        b"filefollowup": b".",
                        b"file-eof": b".",
                    }
                    fmap["sendmsg"](public_msg)
                    return
                public_msg = {
                    b"author": CONFIG.OWN_NAME.encode(),
                    b"content": b"File:",
                    b"filename": Chat.streaming_name,
                    b"filedata": chunk
                }
                if Chat.stream_followup:
                    public_msg[b"filefollowup"] = b"."
                Chat.stream_followup = True
                fmap["sendmsg"](public_msg)
        else:
            if Chat.streaming_file is not None:
                try:
                    Chat.streaming_file.close()
                    Chat.streaming_file = None
                except Exception:
                    Chat.streaming_file = None
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
    
    def parse_command(prompt):
        if not prompt.startswith("/"):
            return False
        
        if prompt == "/disconnect":
            txt = VARS.lang.MESSAGE_DISCONNECTED.encode()
            sys_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](sys_msg)
            connection.disconnect()
            VARS.active = Main
        
        if prompt == "/dump":
            filename = utils.random_string(16) + ".dump"
            dump = []
            
            for i in Chat.messages:
                chunk = bytearray()
                for name, data in i.raw.items():
                    name_length = len(name).to_bytes(1, "big")
                    data_length = len(data).to_bytes(3, "big")
                    chunk.extend(data + data_length + name + name_length)
                dump.append(len(chunk).to_bytes(4, "big") + chunk)
            open(filename, "wb").write(b"".join(dump))
            
            txt = VARS.lang.MESSAGE_DUMPED.format(filename).encode()
            sys_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](sys_msg)
        
        return True
    
    def init():
        Chat.elements = []
        Chat.input_box = element.Line(
            pos = (VARS.window_size.x/2, VARS.window_size.y - 25),
            size = (VARS.window_size.x - 50, 50),
            color = (255, 255, 255),
            font = VARS.fonts[25],
            align = "center",
            edit = True,
            placeholder = VARS.lang.CHATBOX_FIELD,
        )
        Chat.y_limit = VARS.window_size.y - 50
        Chat.scroll_step = VARS.window_size.y / 5
        Chat.status_text_pos = (5, VARS.window_size.y - 70)
        Chat.elements.append(Chat.input_box)
    
    
    def event_KEYDOWN(ev):
        if ev.key == pg.K_ESCAPE:
            Console.toggle()
        elif ev.key == pg.K_RETURN and Chat.input_box.text:
            prompt = Chat.input_box.text
            Chat.input_box.set_text("")
            if Chat.parse_command(prompt.strip()):
                return
            
            prompt = prompt.encode()
            you_msg = {b"author": b"~YOU", b"content": prompt}
            public_msg = {b"author": CONFIG.OWN_NAME.encode(), b"content": prompt}
            
            fmap["recvmsg"](you_msg)
            fmap["sendmsg"](public_msg)
        else:
            any(i.event_KEYDOWN(ev) for i in Chat.elements + Chat.messages)
    
    def event_MOUSEBUTTONDOWN(ev):
        if ev.button == pg.BUTTON_WHEELDOWN:
            if len(Chat.messages) == 0:
                limit = 0
            else:
                last = Chat.messages[-1]
                limit = last.offset + last.size[1] - 200
            Chat.scroll_goal = min(Chat.scroll_goal + Chat.scroll_step, limit)
            Chat.scroll += Chat.scroll_step / 5
        elif ev.button == pg.BUTTON_WHEELUP:
            Chat.scroll_goal = max(Chat.scroll_goal - Chat.scroll_step, -200)
            Chat.scroll -= Chat.scroll_step / 5
        else:
            any(i.event_MOUSEBUTTONDOWN(ev) for i in Chat.elements + Chat.messages)
    
    def event_MOUSEBUTTONUP(ev):
        any(i.event_MOUSEBUTTONUP(ev) for i in Chat.elements + Chat.messages)
    
    def event_MOUSEMOTION(ev):
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        any(i.event_MOUSEMOTION(ev) for i in Chat.elements + Chat.messages)
    
    def event_TEXTINPUT(ev):
        Chat.input_box.event_TEXTINPUT(ev)
    
    def event_DROPFILE(ev):
        file = ev.file
        if not os.path.isfile(file):
            return
        name = file.replace("\\", "/").rsplit("/", 1)[1]
        txt = VARS.lang.MESSAGE_STREAMING_START.format(name).encode()
        you_msg = {b"author": b"~YOU", b"content": txt}
        fmap["recvmsg"](you_msg)
        Chat.streaming_file = open(file, "rb")
        Chat.streaming_name = f"{utils.random_string(4)}_{name}".encode()
        Chat.stream_followup = False



class Options:
    button = None
    behind = None
    
    def draw(canvas):
        Main.update_surf()
        canvas.blit(Main.surf, (0, 0))
        
        txt = VARS.fonts[30].render("Options will be here soon, but not now", True, (255, 255, 255))
        canvas.blit(txt, txt.get_rect(center=VARS.window_size/2))
        
        Options.button.draw(canvas)
    
    def init():
        button = element.Button(
            pos = (5, 5),
            size = (30, 30),
            align = "topleft",
            callback = Options.toggle,
            hover_scale = 0,
        )
        button.surface.fill((0, 63, 127))
        # cogwheel
        center = pg.Vector2(15, 15)
        up = pg.Vector2(0, -12)
        for r in range(6):
            point_a = center + up.rotate(r * 60 + 30)
            point_b = center + up.rotate((r+1) * 60 + 30)
            pg.draw.aaline(button.surface, (0, 127, 255), point_a, point_b)
        # inner cogwheel
        up = pg.Vector2(0, -6)
        for r in range(6):
            point_a = center + up.rotate(r * 60)
            point_b = center + up.rotate((r+1) * 60)
            pg.draw.aaline(button.surface, (0, 127, 255), point_a, point_b)
        
        button.update_surf()
        Options.button = button
        Main.elements.append(button)
        Chat.elements.append(button)
    
    def toggle():
        if VARS.active == Options:
            VARS.active = Options.behind
            return
        
        Options.behind = VARS.active
        VARS.active = Options
    
    
    def event_KEYDOWN(ev):
        pass
    
    def event_MOUSEBUTTONDOWN(ev):
        Options.button.event_MOUSEBUTTONDOWN(ev)
    
    def event_MOUSEBUTTONUP(ev):
        Options.button.event_MOUSEBUTTONUP(ev)
    
    def event_MOUSEMOTION(ev):
        Options.button.event_MOUSEMOTION(ev)



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
    elements = ()
    
    def draw(canvas):
        Console.behind.draw(canvas)
        canvas.blit(Console.surf, (0, 0))
        
        canvas.blit(Console.prompt_prefix, Console.prompt_prefix_rect)
        bb = Console.prompt_line.draw(canvas)
        bb2 = Console.logs_multiline.draw(canvas)
        #pg.draw.rect(canvas, (255, 0, 0), bb, 1)
        #for i in bb2:
        #    pg.draw.rect(canvas, (255, 0, 0), i, 1)
    
    def init():
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
            return
        if _user_input == "clearhistory":
            Console.history = []
            return
        if _user_input == "?":
            log("""

uses eval() to run Python.
if command format is 'var = 123', exec('global var; var = 123') is used

custom console commands / shortcuts:
clear - clear console output
clearhistory - erase command history
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
    
    
    def event_MOUSEBUTTONDOWN(ev):
        any(i.event_MOUSEBUTTONDOWN(ev) for i in Console.elements)
    
    def event_MOUSEBUTTONUP(ev):
        any(i.event_MOUSEBUTTONUP(ev) for i in Console.elements)
    
    def event_MOUSEMOTION(ev):
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        any(i.event_MOUSEMOTION(ev) for i in Console.elements)
    
    def event_TEXTINPUT(ev):
        any(i.event_TEXTINPUT(ev) for i in Console.elements)
    
    def event_KEYDOWN(ev):
        history = Console.history or [""]
        if ev.key == pg.K_ESCAPE:
            Console.toggle()
        
        elif ev.key == pg.K_RETURN:
            Console.prompt_line.active = True
            Console.logs_multiline.active = False
            if not Console.prompt_line.text:
                return
            
            Console.run(Console.prompt_line.text)
            if history and Console.prompt_line.text != history[-1]:
                Console.history.append(Console.prompt_line.text)
            
            Console.history_ind = len(Console.history)
            Console.logs_multiline.append_text(">>> " + Console.prompt_line.text)
            Console.prompt_line.set_text("")
        
        elif ev.key == pg.K_UP:
            Console.history_ind = max(Console.history_ind - 1, 0)
            Console.prompt_line.set_text(history[Console.history_ind])
        elif ev.key == pg.K_DOWN:
            Console.history_ind = min(Console.history_ind + 1, len(history))
            if Console.history_ind == len(history):
                Console.prompt_line.set_text("")
            else:
                Console.prompt_line.set_text(history[Console.history_ind])
        else:
            any(i.event_KEYDOWN(ev) for i in Console.elements)
    



to_init = (Main, Chat, Options, Console)
