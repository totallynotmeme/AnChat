# /res/__init__.py


if __name__ == "__main__":
    print("This module cannot be launched directly.")
    print("Please use 'from res import *' in your script")
    exit(-1)


from . import message
from . import encryption
from . import connection
from . import wordip
from importlib.machinery import SourceFileLoader
import time
import sys
import os


# standard variables that should not be overwritten
# system
RES_PATH = os.path.dirname(__file__).replace("\\", "/") + "/"
DOWNLOADS_PATH = os.getcwd() + "\\downloads"
CLIENTS_PATH = RES_PATH
# state
ACTIVE_CLIENT = None
LAST_SLEEP = 0
LOGS = []

class VARS:
    CORE_VERSION = "0.1-BETA"
    RUNNING = False

class CONFIG:
    OWN_NAME = "Anon"
    PASSWORD = b""
    PROTOCOL = "Socket"

# function map enum
F_INIT = 0
F_HANDLE_LOG = 1
F_TICK = 2
F_SENDMSG = 3
F_RECVMSG = 4
F_APPLY_CONFIG = 5
F_SHUTDOWN = 6
FILE_TO_FUNC_MAP = {
    "f_init.py": F_INIT,
    "f_handle_log.py": F_HANDLE_LOG,
    "f_tick.py": F_TICK,
    "f_sendmsg.py": F_SENDMSG,
    "f_recvmsg.py": F_RECVMSG,
    "f_apply_config.py": F_APPLY_CONFIG,
    "f_shutdown.py": F_SHUTDOWN,
}


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
    fmap[F_HANDLE_LOG]()
    
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
        fmap[F_RECVMSG](msg)
    
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

def init():
    global ACTIVE_CLIENT
    global clients
    global fmap
    
    if not os.path.isdir(DOWNLOADS_PATH):
        log("Creating downloads folder at currect working dir")
        os.mkdir(DOWNLOADS_PATH)
    
    log("Fetching available clients")
    clients = [i for i in os.listdir(CLIENTS_PATH) if os.path.isdir(CLIENTS_PATH+i)]
    #clients = []
    if "__pycache__" in clients:
        clients.remove("__pycache__")
    len_clients = len(clients)
    
    if len_clients == 0:
        ACTIVE_CLIENT = None
        log("No client folders located. Running as console application")
    elif len_clients == 1:
        ACTIVE_CLIENT = clients[0]
        log(f"Running as '{ACTIVE_CLIENT}' client since it's the only one found")
    else: # 1+
        print(f"Found {len_clients} clients. Please choose one you want to import:")
        choices = {}
        for ind, i in enumerate(clients, start=1):
            choices[str(ind)] = i
            print(f"{ind}\t- {i}")
        print("\nType your option and press ENTER")
        
        # safe user input
        while True:
            user_choice = input(">>: ").strip()
            if user_choice == "":
                continue
            if user_choice in choices:
                break
            print(f"Invalid option {repr(user_choice)}")
        
        ACTIVE_CLIENT = choices[user_choice]
        log(f"Running as '{ACTIVE_CLIENT}' client (found {len_clients}, user picked {repr(user_choice)})")
    
    fmap = [
        DEFAULT_init,
        DEFAULT_handle_log,
        DEFAULT_tick,
        DEFAULT_sendmsg,
        DEFAULT_recvmsg,
        DEFAULT_apply_config,
        DEFAULT_shutdown,
    ]
    
    if ACTIVE_CLIENT is None:
        log("Created default function map, leaving it as is")
    else:
        log(f"Importing functions from '{ACTIVE_CLIENT}' client on top of defaults")
        client_path = CLIENTS_PATH + ACTIVE_CLIENT + "/"
        client_files = os.listdir(client_path)
        sys.path.append(client_path)
        for file, val in FILE_TO_FUNC_MAP.items():
            if file not in client_files:
                continue
            try:
                a = SourceFileLoader(ACTIVE_CLIENT + "_" + file, client_path + file).load_module()
                a.bootstrap(globals())
                fmap[val] = a.func
                log(f"Successfully imported and bootstrapped {file}")
            except Exception as e:
                log(f"Error when importing {file}: {e}")


# initialization routine
init()
