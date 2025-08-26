# /res/blueberry/f_recvmsg.py


from chat_message import ChatMessage
from scene import Chat
import pygame as pg

# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


# your function here
def func(msg):
    chat_msg = ChatMessage(msg)
    if chat_msg.show:
        Chat.push(chat_msg)
