from res import *


fmap["init"]()
fmap["handle_log"]()

headless = client is None

while VARS.RUNNING:
    if not headless:
        try:
            fmap["tick"]()
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
        fmap["sendmsg"](msg)
        continue
    
    if _user_input == "shut":
        fmap["shutdown"]()
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
