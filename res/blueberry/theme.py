# /res/blueberry/theme.py


categories = [
    "background", "bgdetails", "base", "accent", "accent2",
    "text", "accent text", "bubble", "bubble edge",
]
c = {i: None for i in categories}

all_themes = {
    "Default": {
        "background": (0, 0, 0),
        "bgdetails": (0, 32, 64),
        "base": (0, 64, 128),
        "accent": (0, 100, 200),
        "accent2": (128, 0, 0),
        "text": (255, 255, 255),
        "accent text": (255, 255, 127),
        "bubble": (25, 35, 45),
        "bubble edge": (40, 60, 80),
    }, "Purpleberry": {
        "background": (10, 0, 20),
        "bgdetails": (20, 10, 88),
        "base": (39, 20, 177),
        "accent": (18, 75, 219),
        "accent2": (163, 22, 181),
        "accent text": (255, 150, 255),
        "text": (255, 255, 255),
        "bubble": (40, 28, 61),
        "bubble edge": (64, 35, 109),
    }, "Charcoal": {
        "background": (0, 0, 0),
        "bgdetails": (47, 47, 47),
        "base": (0, 0, 0),
        "accent": (102, 102, 102),
        "accent2": (76, 0, 0),
        "accent text": (255, 255, 184),
        "text": (255, 255, 255),
        "bubble": (0, 0, 0),
        "bubble edge": (51, 51, 51),
    }
}
name = "Default"


def load_theme(theme):
    c.update(all_themes["Default"])
    c.update(theme)


tohexbyte = lambda x: hex(x)[2:].zfill(2)
def colortohex(color):
    return tohexbyte(color[0]) + tohexbyte(color[1]) + tohexbyte(color[2])

def hextocolor(color):
    return tuple(int(color[i:i+2], 16) for i in range(0, 6, 2))


def theme_to_str(name, theme):
    strings = (f"{key}:{colortohex(val)}" for key, val in theme.items())
    return name + "/" + "/".join(strings)

def parse_string_theme(raw):
    verbals = []
    theme = {}
    name, *raw_vals = raw.split("/")
    for i in raw_vals:
        if ":" in i:
            prop, value = i.split(":", 1)
            try:
                value = hextocolor(value)
                theme[prop] = value
            except Exception as e:
                verbals.append(f"Error occured on theme parsing: {e} (@ {i})")
    return name, theme, verbals
