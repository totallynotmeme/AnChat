# /res/blueberry/utils.py


import os
import random

def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


# some constants and default stuff
GET_DEFAULT_CONFIG_OPTIONS = lambda: {
    "seen_intro": "0",
    "window_size": "1400-800",
    "lang": "en",
    "font": "lucidaconsole",
}
DEFAULT_CONFIG_FILE = """
// /config.txt


// This is a standard config file for this client!

// Add comments by adding '//' at the start of the line
// (note: 'a = b // comment' will not strip the comment)


// It's recommended to modify these settings through the client instead of here,
// but you can do whatever you want. it's your file, i can't stop you.



"""[1:-1]
config_lines = "\n".join(f"{k} = {v}" for k, v in GET_DEFAULT_CONFIG_OPTIONS().items())
DEFAULT_CONFIG_FILE += config_lines + "\n"
CONFIG_FILE_PATH = ""


def parse_config_file(current_config):
    verbals = []
    current_config.update(GET_DEFAULT_CONFIG_OPTIONS()) # just to be safe
    if os.path.isfile(CONFIG_FILE_PATH):
        config_file_data = open(CONFIG_FILE_PATH, "r").readlines()
        for i in config_file_data:
            if i.strip() == "" or i.startswith("//"):
                continue
            if "=" not in i:
                verbals.append(f"WARN: Couldn't parse line {repr(i)}")
                continue
            key, val = i.split("=", 1)
            key = key.strip()
            val = val.strip()
            current_config[key] = val
    else:
        verbals.append("Config file not found, creating a default one")
        open(CONFIG_FILE_PATH, "w").write(DEFAULT_CONFIG_FILE)
    return verbals

def parse_screen_res(raw, max_res):
    try:
        res = tuple(map(int, raw.split("-", 1)))
        limited_x = max(min(res[0], max_res[0]), 600)
        limited_y = max(min(res[1], max_res[1]), 300)
        return limited_x, limited_y
    except Exception:
        return None

def save_config_file(current_config):
    if os.path.isfile(CONFIG_FILE_PATH):
        config_file_data = open(CONFIG_FILE_PATH, "r").read().rstrip()
    else:
        config_file_data = DEFAULT_CONFIG_FILE
    config_file_data = config_file_data.split("\n")
    
    linemap = {}
    for ind, line in enumerate(config_file_data):
        if line.startswith("//") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        linemap[key] = ind
    
    for key, val in current_config.items():
        line = f"{key} = {val}"
        if key in linemap.keys():
            line_ind = linemap[key]
            config_file_data[line_ind] = line
        else:
            config_file_data.append(line)
    
    while config_file_data[-1] == "":
        config_file_data.pop()
    
    open(CONFIG_FILE_PATH, "w").write("\n".join(config_file_data) + "\n")


def find_space_left(line):
    if " " not in line.strip():
        return 0
    return line.strip().rindex(" ") + 1

def find_space_right(line):
    if " " not in line.strip():
        return len(line)
    offset = len(line) - len(line.lstrip())
    return line.strip().index(" ") + offset


def random_string(length):
    thing = hex(random.randint(0, (1 << length * 4) - 1))
    return thing[2:].zfill(length)


# had to rewrite it twice :SILENCE:
def text_to_lines(text, max_length):
    text = text.strip()
    raw_lines = text.split("\n")
    
    lines = []
    for i in raw_lines:
        if len(i) <= max_length:
            #print(f"APPENDING RAW {i}")
            lines.append(i)
            continue
        while i:
            chunk = i[:max_length]
            if len(chunk) < max_length:
                lines.append(chunk)
                #print(f"MERGING LINE {chunk}")
                break
            elif " " in chunk:
                split_at = chunk.rindex(" ") + 1
                line = chunk[:split_at]
                i = i[split_at:]
                #print(f"ADDING LINE {line}")
                lines.append(line)
            else:
                i = i[max_length:]
                #print(f"PLACING CHUNK {chunk}")
                lines.append(chunk)
    
    return lines


def is_monospace(font, sample="iW ,"):
    goal = font.size(sample[0])
    return all(font.size(i) == goal for i in sample[1:])

