from res import *


fmap[F_INIT]()
fmap[F_HANDLE_LOG]()

headless = ACTIVE_CLIENT is None

while VARS.RUNNING:
    if not headless:
        try:
            fmap[F_TICK]()
        except Exception as e:
            print(f"Unhandled exception: {e}")
        continue
        
    # headless cmd version for debugging
    _user_input = input(">>> ").strip()
    if _user_input == "":
        continue
    if _user_input.startswith(">"):
        msg = {
            b"author": CONFIG.OWN_NAME.encode(),
            b"content": _user_input[1:].encode(),
        }
        fmap[F_SENDMSG](msg)
        continue
    
    if _user_input == "shut":
        fmap[F_SHUTDOWN]()
        break
    
    try:
        if "=" in _user_input:
            exec(_user_input)
        else:
            _ = eval(_user_input)
            if _ is not None:
                print(_)
    except Exception as e:
        print("E:", e)
