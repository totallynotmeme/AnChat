# /res/__init__.py


if __name__ == "__main__":
    print("This module cannot be launched directly.")
    print("Please use 'from res import *' in your script")
    exit(-1)


client = None # default headless mode

# for client developers: replace "blueberry" with the name of your client
from . import blueberry as client
from . import message
from . import encryption
from . import connection
from . import wordip
import time
import sys
import os


# standard variables that should not be overwritten
# system
RES_PATH = os.path.dirname(__file__).replace("\\", "/") + "/"
DOWNLOADS_PATH = os.getcwd() + "\\downloads"
CLIENTS_PATH = RES_PATH
# state
LAST_SLEEP = 0
LOGS = []

class VARS:
    CORE_VERSION = "0.1-BETA"
    RUNNING = False

class CONFIG:
    OWN_NAME = "Anon"
    PASSWORD = b""
    PROTOCOL = "Socket"


# handler functions to process things
def DEFAULT_init():
    print("WARNING: running headless version that is used for testing, BUGS WILL HAPPEN!")
    VARS.RUNNING = True

def DEFAULT_handle_log():
    while LOGS:
        at_time, text = LOGS.pop(0)
        print(f"<{at_time}>  {text}")

def DEFAULT_tick():
    global LAST_SLEEP
    
    # show logs
    fmap["handle_log"]()
    
    # handle messages
    if len(connection.PACKET_QUEUE) > 0:
        packet = connection.PACKET_QUEUE.pop(0)
        valid = encryption.validate(packet)
        if valid:
            packet = encryption.decrypt(packet)
            if message.verify_hash(packet):
                msg = message.parse_packet(packet)
            else:
                msg = message.error_invalid_hash()
        else:
            msg = message.error_duplicate_salt()
        fmap["recvmsg"](msg)
    
    # sleep for 0.1 to maintain 10 tps
    this_time = time.time()
    sleep_for = max(LAST_SLEEP - this_time + 0.1, 0)
    time.sleep(sleep_for)
    LAST_SLEEP = time.time()

def DEFAULT_sendmsg(msg):
    packet = message.gen_packet(msg)
    packet = encryption.encrypt(packet)
    return connection.protocol.send(packet)

def DEFAULT_recvmsg(msg):
    fields = [
        msg[b"author"].decode(),
        msg[b"content"].decode(),
        f"Attributes: {len(msg)}",
    ]
    
    if b"filedata" in msg:
        if b"filename" in msg:
            filename = msg[b"filename"].decode()
        else:
            filename = time.strftime("file_%H-%M-%S")
        for i in '\\/:*?"<>|':
            filename = filename.replace(i, "_")
        fields.insert(2, f"Attached file data of: {filename}")
        open(DOWNLOADS_PATH + "\\" + filename, "ab").write(msg[b"filedata"])
    
    lines = len(fields)
    fields = "\x1b[1E".join(fields) # move cursor down 1 + to the start of line
    #       SetPosTo1,1 + (ClearLine + Newl) x lines + 1 + ClearLine + MoveUp  x lines
    clear = "\x1b[1;1H" + ("\x1b[2K" + "\n") * (lines+1) + "\x1b[2K" + "\x1bM" * lines
    #     SavePos + vvvvv + cntent + LoadPos
    seq = "\x1b7" + clear + fields + "\x1b8"
    print(seq)

def DEFAULT_apply_config():
    encryption.password = CONFIG.PASSWORD
    protocol = connection.protocol_list.get(CONFIG.PROTOCOL, connection.default)
    connection.protocol = protocol

def DEFAULT_shutdown():
    connection.disconnect()
    VARS.RUNNING = False


# standard function that should not be overwritten
def log(what):
    time_str = time.strftime("%X")
    LOGS.append((time_str, what))


# initialization routine
if not os.path.isdir(DOWNLOADS_PATH):
    log("Creating downloads folder at currect working dir")
    os.mkdir(DOWNLOADS_PATH)

fmap = {
    "init": DEFAULT_init,
    "handle_log": DEFAULT_handle_log,
    "tick": DEFAULT_tick,
    "sendmsg": DEFAULT_sendmsg,
    "recvmsg": DEFAULT_recvmsg,
    "apply_config": DEFAULT_apply_config,
    "shutdown": DEFAULT_shutdown,
}

# loading funcs and 
if client is not None:
    fmap.update(client.fmap)
    for i in client.to_bootstrap:
        i.bootstrap(globals())