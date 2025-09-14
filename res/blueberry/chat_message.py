# /res/blueberry/chat_message.py


from . import utils
from . import element
import pygame as pg
import os


fonts = {}
window_size = 0
downloads_path = ""

def safe_decode(text):
    try:
        res = text.decode()
    except UnicodeDecodeError:
        res = repr(text)
    return res

special_names = {
    "~YOU": "[YOU]",
    "~SYSTEM": "[SYSTEM]",
}

error_codes = {}

writing_files = {}


class ChatMessage:
    corners = (25, 10, 15, 10)
    def __init__(self, raw):
        #print("="*40, *raw.keys(), "="*40, sep="\n")
        self.raw = raw
        self.content = safe_decode(raw[b"content"])
        self.author = safe_decode(raw[b"author"])
        
        if self.author in special_names:
            self.author = special_names[self.author]
        
        self.offset = 0
        self.type = "text"
        self.show = True
        
        if b"~errorcode" in raw:
            self.type = "error"
            self.errorcode = raw[b"~errorcode"]
            self.content = error_codes.get(self.errorcode, self.content)
        
        author_color = (255, 255, 255)
        
        if self.author == "[YOU]":
            self.align = "topright"
            self.x_pos = window_size[0] - 25
            self.corners = ChatMessage.corners[::-1]
            author_color = (255, 255, 127)
        else:
            self.align = "topleft"
            self.x_pos = 25
            self.corners = ChatMessage.corners
        
        if self.author == "[SYSTEM]":
            author_color = (127, 190, 255)
        
        # drawing the message
        author_font = fonts[25]
        self.author_element = element.Line(
            pos = (10, 10),
            size = author_font.size(self.author),
            color = author_color,
            font = author_font,
        )
        self.author_element.set_text(self.author)
        
        if self.type == "file":
            self.content += f"\n[[Attachment: {self.filename}]]"
        text_font = fonts[20]
        font_size = pg.Vector2(text_font.size(" "))
        lines = utils.text_to_lines(self.content, int(500 / font_size.x))
        #size_x = int(max(len(i) for i in lines) * font_size.x)
        size_x = 500
        size_y = int(len(lines) * font_size.y)
        self.text_element = element.Multiline(
            pos = (15, 40),
            size = (size_x, size_y),
            color = (200, 200, 200),
            font = text_font,
        )
        self.text_element.set_text(self.content)
        self.surface = pg.Surface((size_x + 30, size_y + 50))
        self.size = self.surface.get_size()
        self.rect = pg.Rect(0, 0, 0, 0)
        self.elements = (self.author_element, self.text_element)
    
    def draw(self, canvas, scroll_offset):
        if self.size[1] + self.offset <= scroll_offset:
            return
        if self.offset - scroll_offset >= window_size[1]:
            return
        
        surf_rect = self.surface.get_rect()
        pg.draw.rect(self.surface, (25, 35, 45), surf_rect, 0, *self.corners)
        pg.draw.rect(self.surface, (40, 60, 80), surf_rect, 2, *self.corners)
        self.author_element.draw(self.surface)
        self.text_element.draw(self.surface)
        true_offset = int(self.offset - scroll_offset)
        self.rect = self.surface.get_rect(**{self.align: (self.x_pos, true_offset)})
        canvas.blit(self.surface, self.rect)
    
    def reinit(self):
        if self.align == "topright":
            self.x_pos = window_size[0] - 25
    
    
    def event_MOUSEMOTION(self, ev):
        if self.rect.collidepoint(ev.pos):
            ev.pos = pg.Vector2(ev.pos) - pg.Vector2(self.rect.topleft)
            res = any(i.event_MOUSEMOTION(ev) for i in self.elements)
            ev.pos += pg.Vector2(self.rect.topleft)
            return res
    
    def event_MOUSEBUTTONDOWN(self, ev):
        if ev.button != pg.BUTTON_LEFT:
            return False
        ev.pos = pg.Vector2(ev.pos) - pg.Vector2(self.rect.topleft)
        res = any(i.event_MOUSEBUTTONDOWN(ev) for i in self.elements)
        ev.pos += pg.Vector2(self.rect.topleft)
        return res
    
    def event_MOUSEBUTTONUP(self, ev):
        ev.pos = pg.Vector2(ev.pos) - pg.Vector2(self.rect.topleft)
        res = any(i.event_MOUSEBUTTONUP(ev) for i in self.elements)
        ev.pos += pg.Vector2(self.rect.topleft)
        return res
    
    
    def event_KEYDOWN(self, ev):
        return any(i.event_KEYDOWN(ev) for i in self.elements)
    
    def event_TEXTINPUT(self, ev):
        return any(i.event_TEXTINPUT(ev) for i in self.elements)
    
    
    handle_event = element.handle_event
    evmap = {
        pg.MOUSEMOTION: event_MOUSEMOTION,
        pg.MOUSEBUTTONDOWN: event_MOUSEBUTTONDOWN,
        pg.MOUSEBUTTONUP: event_MOUSEBUTTONUP,
        pg.KEYDOWN: event_KEYDOWN,
        pg.TEXTINPUT: event_TEXTINPUT,
    }
