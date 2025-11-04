# /res/blueberry/background.py


# from . import theme # TODO
import pygame as pg
import random

theme = None

surface = pg.Surface((5, 5))
size = pg.Vector2(5, 5)
filler = pg.Surface((5, 5))
color = (0, 30, 60)


class Black:
    def init():
        surface.blit(filler, (0, 0))
    
    step = lambda *a: 0


class Lines:
    line_1 = 0
    line_2 = 0
    
    def init():
        global color
        color = tuple(i//2 for i in theme["base"])
        surface.blit(filler, (0, 0))
        # Lines.line_1 = 0
        # Lines.line_2 = 0
    
    def step():
        surface.blit(filler, (0, 0))
        step = size.y / 4
        Lines.line_1 += 1
        Lines.line_1 %= step
        Lines.line_2 += 0.73
        Lines.line_2 %= step * 2
        y1 = Lines.line_1 - 100
        y2 = Lines.line_2 - 100
        for offset in range(5):
            p_from = (0, y1 + 100)
            p_to = (size.x, y1)
            pg.draw.aaline(surface, color, p_from, p_to)
            y1 += step
        for offset in range(3):
            p_from = (0, y2 + 50)
            p_to = (size.x, y2)
            pg.draw.aaline(surface, color, p_from, p_to)
            y2 += step*2


"""
# makes my fans spin too fast, need to do something about it
# feel free to bring this back rn if you want to
class Glow:
    raw = pg.Surface((6, 4))
    prev_surf = pg.Surface((6, 4))
    this_surf = pg.Surface((6, 4))
    colors = [0] * 6*4
    timer = 0
    
    def init():
        surface.blit(filler, (0, 0))
        Glow.prev_surf = pg.Surface(size)
        Glow.this_surf = pg.Surface(size)
        Glow.colors = [random.random() for i in range(6*4)]
        Glow.timer = 0
    
    def step():
        #surface.blit(filler, (0, 0))
        Glow.timer -= 2
        if Glow.timer < 0:
            for ind, i in enumerate(Glow.colors):
                y, x = divmod(ind, 6)
                Glow.raw.set_at((x, y), (0, i*31, i*63))
            Glow.timer = 255
            Glow.prev_surf = Glow.this_surf
            Glow.this_surf = pg.transform.smoothscale(Glow.raw, size)
            Glow.colors = [(i + random.random() / 2) % 1 for i in Glow.colors]
        
        surface.blit(Glow.this_surf, (0, 0))
        Glow.prev_surf.set_alpha(Glow.timer)
        surface.blit(Glow.prev_surf, (0, 0))
"""


class Rain:
    active = []
    
    def init():
        global color
        color = tuple(i//2 for i in theme["base"])
        surface.blit(filler, (0, 0))
        Rain.active = []
    
    def step():
        surface.blit(filler, (0, 0))
        to_remove = []
        for ind, i in enumerate(Rain.active):
            # 0 - X, 1 - Y, 2 - Length
            i[1] += 20
            # to do: make this readable
            pg.draw.line(surface, color, (i[0], i[1]), (i[0], i[1]-i[2]))
            if i[1] - i[2] > size.y:
                to_remove.append(ind - len(to_remove))
        for i in to_remove:
            Rain.active.pop(i)
        Rain.active.append([
            random.randint(0, int(size.x)), 0,
            random.randint(100, 200),
        ])


bglist = [Black, Lines, Rain]#, Glow]
bgmap = {i.__name__: i for i in bglist}
