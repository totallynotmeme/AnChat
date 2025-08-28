# /res/blueberry/__init__.py


from . import f_init
from . import f_handle_log
from . import f_tick
from . import f_recvmsg
from . import f_shutdown


fmap = {
    "init": f_init.func,
    "handle_log": f_handle_log.func,
    "tick": f_tick.func,
    "recvmsg": f_recvmsg.func,
    "shutdown": f_shutdown.func,
}
to_bootstrap = (f_init, f_handle_log, f_tick, f_recvmsg, f_shutdown)
