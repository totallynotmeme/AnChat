# /res/blueberry/element.py


from . import utils
import pygame as pg

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


event_null = lambda *a: False

def handle_event(self, ev):
    func = self.evmap.get(ev.type, event_null)
    return func(self, ev)


ctrl_a = "\x01"
ctrl_c = "\x03"
ctrl_v = "\x16"
ctrl_x = "\x18"
scrap_text = "text/plain;charset=utf-8"


def clipboard_copy(text):
    if not text:
        return
    text = text.encode("utf-16")
    text = text.strip(b"\xff\xfe") + b"\x00\x00" # evil cyrillic hack
    pg.scrap.put(scrap_text, text)

def clipboard_paste():
    raw = pg.scrap.get(scrap_text)
    if raw is None:
        return
    return raw.decode("utf-16", errors="ignore").replace("\x00", "")


class Line:
    type = "line"
    placeholder_color = pg.Color(127, 127, 127)
    def __init__(self, pos, size, color, font, align="topleft", edit=False, placeholder=""):
        self.pos = pg.Vector2(pos)
        self.size = pg.Vector2(size)
        self.color = pg.Color(color)
        self.font = font
        self.font_size = pg.Vector2(font.size(" "))
        self.max_chars = int(self.size.x / self.font_size.x)
        self.align = align
        self.edit = edit
        self.text = ""
        self.placeholder = placeholder
        self.selecting = False
        self.selection_start = -1
        self.selection_end = -1
        self.cursor_pos = 0
        self.scroll_pos = 0
        # surely there's a better way to do this
        bb = pg.Rect(self.pos, self.size)
        true_pos = 2*self.pos - pg.Vector2(getattr(bb, align))
        self.bounding_box = pg.Rect(true_pos, self.size)
        self.true_bb = pg.Rect(0, 0, 0, 0)
        self.active = False
    
    def _delete_selection(self):
        points = (self.selection_start, self.selection_end)
        left = self.text[:min(points)]
        right = self.text[max(points):]
        self.text = left + right
        self.set_cursor(min(points))
        self.selection_start = -1
        self.selection_end = -1
        self.selecting = False
    
    def set_text(self, text):
        self.text = text
        self.set_cursor(len(text))
        self.selection_start = -1
        self.selection_end = -1
        self.selecting = False
    
    def set_cursor(self, new_pos, no_select=False):
        new_pos = max(new_pos, 0)
        
        if VARS.holding_shift and not no_select:
            if self.selection_start == -1:
                self.selection_start = self.cursor_pos
            self.selection_end = new_pos
        self.cursor_pos = new_pos
        
        relative = new_pos - self.scroll_pos
        if relative < 0:
            self.scroll_pos = new_pos
        if relative > self.max_chars:
            self.scroll_pos = new_pos - self.max_chars - 1
        
        # safeguard
        limit = max(len(self.text) - self.max_chars - 1, 0)
        self.scroll_pos = min(self.scroll_pos, limit)
    
    
    def draw(self, canvas, offset=pg.Vector2()):
        to_render = self.text or self.placeholder or " "
        if self.text == "":
            color = self.placeholder_color
            self.scroll_pos = 0
        else:
            color = self.color
        
        trimmed = to_render[self.scroll_pos: self.scroll_pos+self.max_chars+1]
        txt = self.font.render(trimmed, True, color)
        rect = txt.get_rect(**{self.align: self.pos + offset})
        
        if self.selection_start >= 0:
            x_points = (
                (self.selection_start - self.scroll_pos),
                (self.selection_end - self.scroll_pos),
            )
            x_start = max(min(x_points), 0) * self.font_size.x
            x_end = min(max(x_points), self.max_chars+1) * self.font_size.x
            
            highlight_rect = pg.Rect(
                x_start + self.true_bb.x,
                rect.topleft[1],
                x_end - x_start,
                self.font_size.y,
            )
            pg.draw.rect(canvas, (2, 49, 146), highlight_rect)
        
        self.true_bb = canvas.blit(txt, rect)
        if VARS.debug:
            if offset:
                display_bb = pg.Vector2(self.bounding_box.topleft) + offset
                display_bb = pg.Rect(display_bb, self.bounding_box.size)
                pg.draw.rect(canvas, (255, 127, 0), display_bb, 1)
            else:
                pg.draw.rect(canvas, (255, 0, 0), self.bounding_box, 1)
            pg.draw.rect(canvas, (127, 0, 0), self.true_bb, 1)
        
        if self.active and self.edit:
            offset_x = (self.cursor_pos - self.scroll_pos) * self.font_size.x
            cursor_height = int(VARS.frame % 40 >= 20) * self.font_size.y // 5
            cursor_origin = rect.topleft + pg.Vector2(offset_x, 2 + cursor_height)
            cursor_finish = cursor_origin + pg.Vector2(0, self.font_size.y - 4 - cursor_height*2)
            pg.draw.line(canvas, (255, 255, 255), cursor_origin, cursor_finish)
        
        text_len = len(self.text)
        if text_len > self.max_chars + 1:
            left = offset + self.bounding_box.bottomleft
            right = offset + self.bounding_box.bottomright
            pg.draw.line(canvas, (100, 100, 100), left, right)
            where_start = self.scroll_pos / text_len
            where_start = pg.Vector2(where_start * self.size.x, -1) + left
            where_end = (self.scroll_pos + self.max_chars + 1) / text_len
            where_end = pg.Vector2(where_end * self.size.x, -1) + left
            pg.draw.line(canvas, (255, 255, 255), where_start, where_end)
        
        return self.true_bb
    
    
    def event_MOUSEMOTION(self, ev):
        if self.selecting:
            at_char = int((ev.pos[0] - self.true_bb.x) / self.font_size.x + 0.5) + self.scroll_pos
            at_char = min(max(at_char, 0), len(self.text))
            self.selection_end = at_char
            self.set_cursor(at_char)
        
        if self.bounding_box.collidepoint(ev.pos):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_IBEAM)
            return True
        return False
    
    
    def event_MOUSEBUTTONDOWN(self, ev):
        if ev.button == pg.BUTTON_LEFT:
            self.active = False
            self.selection_start = -1
            self.selection_end = -1
            
            if self.bounding_box.collidepoint(ev.pos):
                self.active = True
                self.selecting = True
                at_char = int((ev.pos[0] - self.true_bb.x) / self.font_size.x + 0.5) + self.scroll_pos
                at_char = min(max(at_char, 0), len(self.text))
                self.selection_start = at_char
                self.selection_end = at_char
                self.set_cursor(at_char)
        return False
    
    
    def event_MOUSEBUTTONUP(self, ev):
        if ev.button == pg.BUTTON_LEFT:
            self.selecting = False
    
    
    def event_KEYDOWN(self, ev):
        if not self.active:
            return False
        
        if not self.edit:
            if ev.unicode == ctrl_c:
                points = (self.selection_start, self.selection_end)
                selected = self.text[min(points): max(points)]
                clipboard_copy(selected)
            return True
        
        self.selecting = False
        if self.selection_start == self.selection_end:
            self.selection_start = -1
            self.selection_end = -1
        
        if ev.unicode == ctrl_a:
            self.selection_start = 0
            self.selection_end = len(self.text)
            self.set_cursor(len(self.text))
            return True
        if ev.unicode == ctrl_c or ev.unicode == ctrl_x:
            points = (self.selection_start, self.selection_end)
            selected = self.text[min(points): max(points)]
            clipboard_copy(selected)
            if ev.unicode == ctrl_x:
                # cut
                if self.selection_start >= 0:
                    self._delete_selection()
            return True
        if ev.unicode == ctrl_v:
            if self.selection_start >= 0:
                self._delete_selection()
            pasted = clipboard_paste()
            if pasted is not None:
                left = self.text[:self.cursor_pos]
                right = self.text[self.cursor_pos:]
                self.text = left + pasted + right
                self.set_cursor(self.cursor_pos + len(pasted), no_select=True)
            return True
        
        if ev.key == pg.K_LEFT:
            new_pos = max(self.cursor_pos - 1, 0)
            if VARS.holding_ctrl:
                new_pos = utils.find_space_left(self.text[:new_pos])
            
            if not VARS.holding_shift:
                self.selection_start = -1
                self.selection_end = -1
            self.set_cursor(new_pos)
        if ev.key == pg.K_RIGHT:
            new_pos = min(self.cursor_pos + 1, len(self.text))
            if VARS.holding_ctrl:
                new_pos += utils.find_space_right(self.text[new_pos:])
            
            if not VARS.holding_shift:
                self.selection_start = -1
                self.selection_end = -1
            self.set_cursor(new_pos)
        
        if ev.key == pg.K_HOME:
            if not VARS.holding_shift:
                self.selection_start = -1
                self.selection_end = -1
            self.set_cursor(0)
            return True
        if ev.key == pg.K_END:
            if not VARS.holding_shift:
                self.selection_start = -1
                self.selection_end = -1
            self.set_cursor(len(self.text))
            return True
        
        if ev.key == pg.K_BACKSPACE:
            if self.selection_start >= 0:
                self._delete_selection()
                return True
            if self.cursor_pos <= 0:
                return True
            
            left = self.text[:self.cursor_pos]
            right = self.text[self.cursor_pos:]
            left = left[:-1]
            new_pos = self.cursor_pos - 1
            if VARS.holding_ctrl:
                where = utils.find_space_left(left)
                left = left[:where]
                new_pos = where
            
            self.text = left + right
            self.set_cursor(new_pos)
            self.selection_start = -1
            self.selection_end = -1
            return True
        if ev.key == pg.K_DELETE:
            if self.selection_start >= 0:
                self._delete_selection()
                return True
            
            left = self.text[:self.cursor_pos]
            right = self.text[self.cursor_pos:]
            right = right[1:]
            if VARS.holding_ctrl:
                where = utils.find_space_right(right)
                right = right[where:]
            self.text = left + right
            self.set_cursor(self.cursor_pos)
        return True
    
    
    def event_TEXTINPUT(self, ev):
        if not self.active:
            return False
        
        if not self.edit:
            return True
        if self.selection_start >= 0:
            self._delete_selection()
        
        left = self.text[:self.cursor_pos]
        right = self.text[self.cursor_pos:]
        self.text = left + ev.text + right
        self.set_cursor(self.cursor_pos + 1, no_select=True)
        return True
    
    
    handle_event = handle_event
    evmap = {
        pg.MOUSEMOTION: event_MOUSEMOTION,
        pg.MOUSEBUTTONDOWN: event_MOUSEBUTTONDOWN,
        pg.MOUSEBUTTONUP: event_MOUSEBUTTONUP,
        pg.KEYDOWN: event_KEYDOWN,
        pg.TEXTINPUT: event_TEXTINPUT,
    }


class Multiline:
    # todo: make it editable
    type = "multiline"
    nullrect = pg.Rect(0, 0, 0, 0)
    def __init__(self, pos, size, color, font, align="topleft", edit=False, placeholder=""):
        self.pos = pg.Vector2(pos)
        self.size = pg.Vector2(size)
        self.color = pg.Color(color)
        self.font = font
        self.font_size = pg.Vector2(font.size(" "))
        self.max_per_line = int(self.size.x / self.font_size.x)
        self.max_lines = int(self.size.y / self.font_size.y)
        self.align = align
        self.edit = edit
        self.lines = []
        self.placeholder = placeholder
        self.selecting = False
        self.selection_start = (-1, -1)
        self.selection_end = (-1, -1)
        self.cursor_pos = (-1, -1)
        self.scroll_pos = 0
        self.bounding_boxes = []
    
    def set_text(self, text):
        self.lines = utils.text_to_lines(text, self.max_per_line)
        self.scroll_pos = min(self.scroll_pos, len(self.lines))
    
    def append_text(self, text):
        self.lines.extend(utils.text_to_lines(text, self.max_per_line))
        self.scroll_pos = max(self.scroll_pos, len(self.lines) - self.max_lines)
    
    def set_cursor(self, char, line):
        # double and give it to the next person
        pass
    
    
    def draw(self, canvas):
        self.bounding_boxes = []
        trimmed = self.lines[self.scroll_pos: self.scroll_pos+self.max_lines]
        
        if self.selection_start[1] >= 0:
            start_line, end_line = sorted(
                (self.selection_start, self.selection_end),
                key = lambda x: x[1] * 999 + x[0]
            )
            
            for line_ind in range(start_line[1], end_line[1]+1):
                line_pos = (line_ind - self.scroll_pos) * self.font_size.y + self.pos.y
                
                x_start = 0
                x_end = len(self.lines[line_ind])
                if line_ind == start_line[1]:
                    x_start = start_line[0]
                if line_ind == end_line[1]:
                    x_end = end_line[0]
                
                x_start = max(x_start, 0) * self.font_size.x
                x_end = min(x_end, self.max_per_line+1) * self.font_size.x
                
                highlight_rect = pg.Rect(
                    x_start + self.pos.x,
                    line_pos,
                    x_end - x_start,
                    self.font_size.y,
                )
                pg.draw.rect(canvas, (2, 49, 146), highlight_rect)
        
        for ind, i in enumerate(trimmed):
            if i.strip() == "":
                self.bounding_boxes.append(self.nullrect)
                continue
            txt = self.font.render(i, True, self.color)
            offset = pg.Vector2(0, self.font_size.y * ind)
            rect = txt.get_rect(**{self.align: self.pos + offset})
            bb = canvas.blit(txt, rect)
            self.bounding_boxes.append(bb)
        
        if VARS.debug:
            for i in self.bounding_boxes:
                pg.draw.rect(canvas, (255, 127, 0), i, 1)
        
        return self.bounding_boxes
    
    
    def event_MOUSEMOTION(self, ev):
        if any(bb.collidepoint(ev.pos) for bb in self.bounding_boxes):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_IBEAM)
            VARS.reset_cursor = False
        if self.selecting:
            at_line = int((ev.pos[1] - self.pos.y) / self.font_size.y)
            at_line = max(at_line, 0)
            at_line = min(at_line, len(self.bounding_boxes) - 1) + self.scroll_pos
            at_char = int((ev.pos[0] - self.pos.x) / self.font_size.x + 0.5)
            at_char = min(max(at_char, 0), len(self.lines[at_line]))
            self.selection_end = (at_char, at_line)
            self.set_cursor(at_char, at_line)
    
    
    def event_MOUSEBUTTONDOWN(self, ev):
        if ev.button == pg.BUTTON_LEFT:
            self.selection_start = (-1, -1)
            self.selection_end = (-1, -1)
            at_line = int((ev.pos[1] - self.pos.y) / self.font_size.y)
            if at_line >= len(self.bounding_boxes) or at_line < 0:
                return
            if self.bounding_boxes[at_line].collidepoint(ev.pos):
                self.selecting = True
                at_line += self.scroll_pos
                at_char = int((ev.pos[0] - self.pos.x) / self.font_size.x + 0.5)
                at_char = min(max(at_char, 0), len(self.lines[at_line]))
                self.selection_start = (at_char, at_line)
                self.selection_end = (at_char, at_line)
                self.set_cursor(at_char, at_line)
    
    
    def event_MOUSEBUTTONUP(self, ev):
        if ev.button == pg.BUTTON_LEFT:
            self.selecting = False
    
    
    def event_KEYDOWN(self, ev):
        if ev.unicode == ctrl_a:
            self.selection_start = (0, 0)
            self.selection_end = (len(self.lines[-1]), len(self.lines) - 1)
            self.set_cursor(*self.selection_end)
            return
        if self.selection_start == (-1, -1):
            return
        if ev.unicode == ctrl_c or ev.unicode == ctrl_x:
            start_line, end_line = sorted(
                (self.selection_start, self.selection_end),
                key = lambda x: x[1] * 999 + x[0]
            )
            selected = self.lines[start_line[1]: end_line[1]+1]
            
            if start_line[1] == end_line[1]:
                selected = selected[0][start_line[0]: end_line[0]]
            else:
                selected[0] = selected[0][start_line[0]:]
                selected[-1] = selected[-1][:end_line[0]]
                selected = "\n".join(selected)
            
            clipboard_copy(selected)
            return
    
    def event_TEXTINPUT(self, ev):
        if self.selection_start != (-1, -1):
            self.selection_start = (-1, -1)
            self.selection_end = (-1, -1)
    
    def event_MOUSEWHEEL(self, ev):
        limit = len(self.lines) - 1
        self.scroll_pos = min(max(self.scroll_pos - ev.y * 3, 0), limit)
    
    
    handle_event = handle_event
    evmap = {
        pg.MOUSEMOTION: event_MOUSEMOTION,
        pg.MOUSEBUTTONDOWN: event_MOUSEBUTTONDOWN,
        pg.MOUSEBUTTONUP: event_MOUSEBUTTONUP,
        pg.KEYDOWN: event_KEYDOWN,
        pg.TEXTINPUT: event_TEXTINPUT,
        pg.MOUSEWHEEL: event_MOUSEWHEEL,
    }


class Button:
    type = "button"
    default_cb = lambda: print("Callback not defined for this button!")
    def __init__(self, pos, size, align="center", callback=default_cb, hover_scale=0.05):
        self.pos = pg.Vector2(pos)
        self.size = pg.Vector2(size)
        self.align = align
        self.callback = callback
        self.scale_factor = 1
        self.hover_scale = hover_scale
        self.hovering = False
        self.holding = False
        self.surface = pg.Surface(self.size)
        self.surf_hovering = self.surface.copy()
        self.surf_holding = self.surface.copy()
        bb = pg.Rect(self.pos, self.size)
        true_pos = 2*self.pos - pg.Vector2(getattr(bb, align))
        self.bounding_box = pg.Rect(true_pos, self.size)
        self.true_bb = pg.Rect(0, 0, 0, 0)
    
    def update_surf(self):
        self.surf_hovering = self.surface.copy()
        self.surf_hovering.fill((25, 25, 25), special_flags=pg.BLEND_RGB_ADD)
        self.surf_holding = self.surface.copy()
        self.surf_holding.fill((25, 25, 25), special_flags=pg.BLEND_RGB_SUB)
    
    def draw(self, canvas, offset=pg.Vector2()):
        if self.holding:
            scale_factor_goal = 1 - self.hover_scale
            surf = self.surf_holding
        elif self.hovering:
            scale_factor_goal = 1 + self.hover_scale
            surf = self.surf_hovering
        else:
            scale_factor_goal = 1
            surf = self.surface
        
        self.scale_factor = (self.scale_factor * 2 + scale_factor_goal) / 3
        if abs(self.scale_factor - 1) > 0.01:
            surf = pg.transform.smoothscale_by(surf, self.scale_factor)
        
        rect = surf.get_rect(**{self.align: self.pos + offset})
        self.true_bb = canvas.blit(surf, rect)
        return self.true_bb
    
    
    def event_MOUSEMOTION(self, ev):
        self.hovering = self.bounding_box.collidepoint(ev.pos)
    
    
    def event_MOUSEBUTTONDOWN(self, ev):
        if self.hovering and ev.button == pg.BUTTON_LEFT:
            self.holding = True
    
    
    def event_MOUSEBUTTONUP(self, ev):
        if self.holding and self.hovering and ev.button == pg.BUTTON_LEFT:
            self.callback()
        self.holding = False
    
    
    def event_KEYDOWN(self, ev):
        return False
    
    def event_TEXTINPUT(self, ev):
        return False
    
    handle_event = handle_event
    evmap = {
        pg.MOUSEMOTION: event_MOUSEMOTION,
        pg.MOUSEBUTTONDOWN: event_MOUSEBUTTONDOWN,
        pg.MOUSEBUTTONUP: event_MOUSEBUTTONUP,
    }


class Optionsbutton(Button):
    def __init__(self, *a, color=(0, 0, 0), font=None, options=("Undefined",), **kwa):
        super().__init__(*a, **kwa)
        self.options = options
        self.current = options[-1]
        self.color = color
        self.font = font
        self.callback = lambda: Optionsbutton.f_callback(self)
        self.redraw()
    
    def f_callback(self):
        if self.current in self.options:
            this_ind = self.options.index(self.current)
        else:
            this_ind = -1
        
        this_ind += 1
        this_ind %= len(self.options)
        self.current = self.options[this_ind]
        self.redraw()
        
    def redraw(self):
        self.surface.fill(self.color)
        txt = self.font.render(self.current, True, (255, 255, 255))
        self.surface.blit(txt, txt.get_rect(center=self.size / 2))
        self.update_surf()


class Container:
    # still not finished, but we're getting closer
    def __init__(self, pos, size, align="topleft", step=50):
        self.pos = pg.Vector2(pos)
        self.size = pg.Vector2(size)
        self.align = align
        self.elements = []
        self.scroll = 0
        self.scroll_goal = 0
        self.scroll_step = step
        self.rect = pg.Rect(self.pos, self.size)
        self.last = None
    
    def draw(self, canvas):
        self.scroll = (self.scroll * 3 + self.scroll_goal) / 4
        scroll_offset = pg.Vector2(0, self.scroll)
        for i in self.elements:
            i.draw(canvas, offset = self.pos - scroll_offset)
    
    def push(self, element, **kwargs):
        if "size_y" in kwargs:
            kwargs["size"] = (self.size.x - 10, kwargs.pop("size_y"))
        
        if self.elements:
            last = self.elements[-1]
            pos_y = last.pos.y + last.size.y + 5
        else:
            pos_y = 5
        
        pos_x = 5
        if "offset" in kwargs:
            offset = kwargs.pop("offset")
            pos_x += offset[0]
            pos_y += offset[1]
        
        kwargs["pos"] = (pos_x, pos_y)
        
        self.last = element(**kwargs)
        self.elements.append(self.last)
        return self.last
    
    
    def event_MOUSEMOTION(self, ev):
        offset = pg.Vector2(self.rect.topleft)
        offset.y -= self.scroll
        ev.pos = pg.Vector2(ev.pos) - offset
        res = any(i.event_MOUSEMOTION(ev) for i in self.elements)
        ev.pos += offset
        return res
    
    def event_MOUSEBUTTONDOWN(self, ev):
        offset = pg.Vector2(self.rect.topleft)
        offset.y -= self.scroll
        ev.pos = pg.Vector2(ev.pos) - offset
        res = any(i.event_MOUSEBUTTONDOWN(ev) for i in self.elements)
        ev.pos += offset
        # if res:
        #     return
    
    def event_MOUSEBUTTONUP(self, ev):
        offset = pg.Vector2(self.rect.topleft)
        offset.y -= self.scroll
        ev.pos = pg.Vector2(ev.pos) - offset
        res = any(i.event_MOUSEBUTTONUP(ev) for i in self.elements)
        ev.pos += offset
        return res
    
    def event_KEYDOWN(self, ev):
        return any(i.event_KEYDOWN(ev) for i in self.elements)
    
    def event_TEXTINPUT(self, ev):
        return any(i.event_TEXTINPUT(ev) for i in self.elements)
    
    def event_MOUSEWHEEL(self, ev):
        if len(self.elements) == 0:
            limit = 0
        else:
            last = self.elements[-1]
            limit = last.pos.y + last.size.y
        self.scroll_goal -= ev.precise_y * self.scroll_step
        self.scroll_goal = min(max(self.scroll_goal, 0), limit)
        self.scroll -= ev.precise_y * self.scroll_step / 2
    
    handle_event = handle_event
    evmap = {
        pg.MOUSEMOTION: event_MOUSEMOTION,
        pg.MOUSEBUTTONDOWN: event_MOUSEBUTTONDOWN,
        pg.MOUSEBUTTONUP: event_MOUSEBUTTONUP,
        pg.KEYDOWN: event_KEYDOWN,
        pg.TEXTINPUT: event_TEXTINPUT,
        pg.MOUSEWHEEL: event_MOUSEWHEEL,
    }
