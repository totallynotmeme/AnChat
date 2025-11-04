# /res/blueberry/icons.py


# from . import theme # also todo
import pygame as pg

theme = None


accent_color = (100, 150, 255)
options_points = 18

def draw():
    global app
    global options
    
    # more todo: make this into separate color categories
    background_color = tuple(i//2 for i in theme["base"])
    middle_color = theme["base"]
    accent_color = tuple(min(100 + i, 255) for i in theme["base"])
    
    # app logo
    app = pg.Surface((32, 32))
    app.fill(background_color)
    pg.draw.rect(app, accent_color, pg.Rect(4, 4, 12, 4))
    pg.draw.rect(app, accent_color, pg.Rect(4, 4, 4, 24))
    pg.draw.rect(app, accent_color, pg.Rect(4, 24, 24, 4))
    
    
    # options button
    options = pg.Surface((30, 30))
    options.fill(middle_color)
    center = pg.Vector2(15, 15)
    up = pg.Vector2(0, -12)
    up_small = pg.Vector2(0, -9)
    up_smaller = pg.Vector2(0, -5)
    angle_step = 360 / options_points
    
    # - outer gear
    prev_point = center + up.rotate(-angle_step)
    for r in range(options_points):
        if r % 3 == 0:
            this_up = up_small
        else:
            this_up = up
        point = center + this_up.rotate(r * angle_step)
        pg.draw.aaline(options, accent_color, point, prev_point)
        prev_point = point
    point = center + up_small
    pg.draw.aaline(options, accent_color, point, prev_point)
    
    # - inner circle
    prev_point = center + up_smaller.rotate(-angle_step)
    for r in range(options_points):
        point = center + up_smaller.rotate(r * angle_step)
        pg.draw.aaline(options, accent_color, point, prev_point)
        prev_point = point


def dump():
    pg.image.save(app, "icon_app.png")
    pg.image.save(options, "icon_options.png")
    return "Success! Active icons were dumped into the app folder"
