# /res/blueberry/f_recvmsg.py


from .chat_message import ChatMessage
from .scene import Chat
import pygame as pg

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


files_received = []


# your function here
def func(msg):
    if b"filename" in msg and b"filedata" in msg:
        try:
            name = msg[b"filename"].decode()
            for i in '\\/:*?"<>|':
                name = name.replace(i, "_")
            full_path = DOWNLOADS_PATH + "/" + name
            open(full_path, "wb").write(msg[b"filedata"])
        except Exception as e:
            print("SHIT HAPPENED:", e)
            return
        if msg[b"filename"] in files_received:
            print(f"ignoring message {msg['content']}")
            return
        files_received.append(msg[b"filename"])
    chat_msg = ChatMessage(msg)
    Chat.push(chat_msg)

