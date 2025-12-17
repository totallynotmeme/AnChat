# /res/blueberry/background.py


from . import theme
import pygame as pg
import random
import math


surface = pg.Surface((5, 5))
size = pg.Vector2(5, 5)


class Black:
    def init():
        pass
    
    def step():
        surface.fill(theme.c["background"])


class Lines:
    line_1 = 0
    line_2 = 0
    
    def init():
        pass
    
    def step():
        surface.fill(theme.c["background"])
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
            pg.draw.aaline(surface, theme.c["bgdetails"], p_from, p_to)
            y1 += step
        for offset in range(3):
            p_from = (0, y2 + 50)
            p_to = (size.x, y2)
            pg.draw.aaline(surface, theme.c["bgdetails"], p_from, p_to)
            y2 += step*2


class Grid:
    colors = [pg.Color(0) for _ in range(4*3)]
    colors_next = None
    timer = 0
    chunk = (6, 9)
    
    def init():
        if Grid.colors_next is None:
            Grid.colors_next = [pg.Color(theme.c["background"]) for _ in range(4*3)]
        Grid.chunk = (math.ceil(size.x / 4), math.ceil(size.y / 3))
    
    def step():
        Grid.timer -= 2
        if Grid.timer < 0:
            c = pg.Color(theme.c["background"])
            for this, next in zip(Grid.colors, Grid.colors_next):
                this.update(next)
                next.update(c.lerp(theme.c["bgdetails"], random.random()))
            Grid.timer = 255
        
        for ind, (this, next) in enumerate(zip(Grid.colors, Grid.colors_next)):
            y, x = divmod(ind, 4)
            x *= Grid.chunk[0]
            y *= Grid.chunk[1]
            c = this.lerp(next, 1 - Grid.timer / 255)
            pg.draw.rect(surface, c, pg.Rect(x, y, *Grid.chunk))


class Rain:
    active = []
    
    def init():
        pass
    
    def step():
        surface.fill(theme.c["background"])
        to_remove = []
        for ind, i in enumerate(Rain.active):
            i[1] += 20
            # X, Y, Length
            x, y, l = i
            pg.draw.line(surface, theme.c["bgdetails"], (x, y), (x, y-l))
            if y - l > size.y:
                to_remove.append(ind - len(to_remove))
        for i in to_remove:
            Rain.active.pop(i)
        Rain.active.append([
            random.randint(0, int(size.x)), 0,
            random.randint(100, 200),
        ])


class Snow:
    surf = None
    active = []
    cooldown = 0
    
    def init():
        Snow.surf = pg.Surface(size)
        Snow.surf.fill(theme.c["background"])
        # drawing the ground
        for x in range(0, int(size.x)+1, 50):
            r = math.sin(x / 100) * 5 + 75
            pg.draw.circle(Snow.surf, theme.c["bgdetails"], (x, size.y), r)
    
    def step():
        surface.blit(Snow.surf, (0, 0))
        to_remove = []
        for ind, i in enumerate(Snow.active):
            # X, Y, speed
            x, y, s = i
            i[0] += s
            i[1] += 2
            i[2] += random.random() - 0.5
            i[2] /= 1.1
            pg.draw.circle(surface, theme.c["bgdetails"], (x, y), 5)
            if y > size.y - 60:
                to_remove.append(ind - len(to_remove))
        for i in to_remove:
            Snow.active.pop(i)
        
        Snow.cooldown -= 1
        if Snow.cooldown < 0:
            Snow.cooldown = 10
            Snow.active.append([random.randint(0, int(size.x)), 0, 0])


bglist = [Black, Lines, Rain, Grid, Snow]
bgmap = {i.__name__: i for i in bglist}

