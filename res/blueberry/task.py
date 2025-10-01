# /res/blueberry/task.py
# Handles background tasks (mostly file streaming)


from threading import Thread
from time import sleep
import math
import os


# bootstrapping cba nonsense
def bootstrap(_globals):
    orig_globals = globals().copy()
    globals().update(_globals)
    globals().update(orig_globals)


LOGS = []
RUNNING = []
FINISHED = []
FAILED = []

def threaded(func):
    def wrapper(*args):
        Thread(target=func, args=args).start()
    return wrapper


class Stream:
    chunksize = 1024 * 512
    
    def __init__(self, filepath):
        dataio = open(filepath, "rb")
        name = filepath.replace("\\", "/").rsplit("/", 1)[-1]
        name = utils.random_string(4) + name
        totalsize = os.path.getsize(filepath)
        totalsize = max(totalsize, 1)
        for i in '\\/:*?"<>|':
            name = name.replace(i, "_")
        
        self.dataio = dataio
        self.name = name
        self.bytename = name.encode()
        self.totalsize = totalsize
        self.totalchunks = math.ceil(totalsize / Stream.chunksize)
        self.status = "ready"
        self.finished = False
        self.chunkid = 0
    
    def __repr__(self):
        return f"Stream(filename={self.name} [{self.status}])"
    
    def __str__(self):
        if self.status == "running":
            part = f"{100 * self.chunkid / self.totalchunks:.2f}"
            args = (self.name, self.chunkid, self.totalchunks, part)
            return VARS.lang.TASK_STREAM_RUNNING.format(*args)
        
        if self.status == "done":
            return VARS.lang.TASK_STREAM_DONE.format(self.name, self.totalchunks)
        
        if self.status == "failed":
            return VARS.lang.TASK_STREAM_FAILED.format(self.chunkid, self.totalchunks)
        
        return VARS.lang.TASK_UNKNOWN.format(self.status, repr(self))
    
    @threaded
    def run(self):
        if self.status != "ready":
            LOGS.append(f"Tried to run a non-ready task {repr(self)}")
            return
        self.status = "running"
        RUNNING.append(self)
        while self.status == "running":
            if self.tick():
                sleep(2)
        
        if self in RUNNING:
            RUNNING.remove(self)
        if self.status == "done":
            FINISHED.append([self, 240])
        if self.status == "failed":
            FAILED.append([self, 240])
    
    def tick(self):
        if self.finished:
            self.terminate()
            return False
        
        try:
            chunk = self.dataio.read(Stream.chunksize)
            if len(chunk) == 0:
                self.terminate("done")
                return False
            msg = {
                b"author": CONFIG.OWN_NAME.encode(),
                b"content": f"[[Attachment: {self.name}]]".encode(),
                b"filename": self.bytename,
                b"filedata": chunk,
            }
            success = fmap["sendmsg"](msg)
            if success:
                self.chunkid += 1
                return True
            log = f"Failed to send chunk #{self.chunkid}. Are you connected to the server?"
            LOGS.append(log)
            self.terminate()
            return False
        except Exception as e:
            log = f"Exception when sending #{self.chunkid}: {e}"
            LOGS.append(log)
            self.terminate()
            return False
    
    def terminate(self, status="failed"):
        self.finished = True
        self.status = status
        try:
            self.dataio.close()
        except Exception as io_e:
            log = f"Couldn't close IO object: {io_e}"
            LOGS.append(log)
            self.dataio = None


class Connect:
    def __init__(self, raw):
        self.raw = raw
        self.status = "ready"
    
    def __repr__(self):
        return f"Connect(raw=<...> [{self.status}])"
    
    def __str__(self):
        # can be replaced with a dictionary but im too lazy.
        # if you're reading this, go ahead, do it
        if self.status == "running":
            return VARS.lang.TASK_CONNECT_RUNNING
        
        if self.status == "done":
            return VARS.lang.TASK_CONNECT_DONE
        
        if self.status == "failed":
            return VARS.lang.TASK_CONNECT_FAILED
        
        return VARS.lang.TASK_UNKNOWN.format(self.status, repr(self))
    
    @threaded
    def run(self):
        if self.status != "ready":
            LOGS.append(f"Tried to run a non-ready task {repr(self)}")
            return
        
        self.status = "running"
        RUNNING.append(self)
        Main = scene.Main
        passphrase = self.raw.strip()
        Main.connecting = True
        Main.field_status.set_text(VARS.lang.STATUS_TEXT_TRYING)
        direct_ip = None
        if "@" in passphrase:
            passphrase, direct_ip = passphrase.split("@", 1)
            passphrase = passphrase.strip()
            direct_ip = direct_ip.strip()
            try:
                address, port = direct_ip.split(":", 1)
                port = int(port)
                direct_ip = (address, port)
            except Exception as e:
                LOGS.append(f"Bad direct_ip address format: {e}")
                Main.connecting = False
                Main.field_status.set_text(VARS.lang.STATUS_TEXT_BADIP.format(e))
                RUNNING.remove(self)
                FAILED.append([self, 240])
                self.status = "failed"
                return
        
        try:
            CONFIG.OWN_NAME = Main.field_username.text or "Anon"
            CONFIG.PASSWORD = passphrase.encode()
            CONFIG.PROTOCOL = Main.protocol_button.current
            fmap["apply_config"]()
            
            if direct_ip:
                connection.protocol.connect(*direct_ip)
            else:
                bitarray = wordip.decode(Main.field_address.text)
                addr, port = connection.protocol.frombits(bitarray)
                connection.protocol.connect(addr, port)
            VARS.active = scene.Chat
            
            txt = VARS.lang.MESSAGE_CONNECTED.encode()
            system_join_msg = {b"author": b"~SYSTEM", b"content": txt}
            fmap["recvmsg"](system_join_msg)
            Main.connecting = False
            Main.field_status.set_text(VARS.lang.STATUS_TEXT_DEFAULT)
            RUNNING.remove(self)
            FINISHED.append([self, 240])
            self.status = "done"
        except Exception as e:
            LOGS.append(f"Error during connection attempt: {e}")
            Main.connecting = False
            Main.field_status.set_text(VARS.lang.STATUS_TEXT_FAILED.format(e))
            RUNNING.remove(self)
            FAILED.append([self, 240])
            self.status = "failed"


class Sendmsg:
    def __init__(self, **kwargs):
        self.message = {i.encode(): j for i, j in kwargs.items()}
        self.status = "ready"
    
    def __repr__(self):
        return f"Sendmsg(<{len(self.message)} attributes>  [{self.status}])"
    
    def __str__(self):
        # can be replaced with a dictionary but im too lazy.
        # if you're reading this, go ahead, do it
        # and yes, this section was copied from Connect task.
        if self.status == "running":
            return VARS.lang.TASK_SENDMSG_RUNNING
        
        if self.status == "done":
            return VARS.lang.TASK_SENDMSG_DONE
        
        if self.status == "failed":
            return VARS.lang.TASK_SENDMSG_FAILED
        
        return VARS.lang.TASK_UNKNOWN.format(self.status, repr(self))
    
    @threaded
    def run(self):
        if self.status != "ready":
            LOGS.append(f"Tried to run a non-ready task {repr(self)}")
            return
        
        self.status = "running"
        RUNNING.append(self)
        try:
            own_message = {
                b"author": b"~YOU",
                b"content": self.message[b"content"],
            }
            chatmsg = fmap["recvmsg"](own_message)
            if chatmsg:
                try:
                    chatmsg.status = 0
                except Exception as e:
                    LOGS.append(f"Error when setting message status: {e}")
            if not fmap["sendmsg"](self.message):
                raise RuntimeError("recvmsg call failed")
            RUNNING.remove(self)
            FINISHED.append([self, 240])
            self.status = "done"
            if chatmsg:
                try:
                    chatmsg.status = 1
                except Exception as e:
                    LOGS.append(f"Error when setting message status: {e}")
        except Exception as e:
            LOGS.append(f"Error when sending message: {e}")
            RUNNING.remove(self)
            FAILED.append([self, 240])
            self.status = "failed"
            if chatmsg:
                try:
                    chatmsg.status = -1
                except Exception as e:
                    LOGS.append(f"Error when setting message status: {e}")
