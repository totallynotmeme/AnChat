# /chat.py
# Main wrapper around fmap and a fallback debug client
# Use this if you're running raw Python code (recommended)


from res import *
import traceback


fmap["init"]()
fmap["handle_log"]()

headless = client is None
errors = 0


while VARS.RUNNING:
    if not headless:
        try:
            fmap["tick"]()
            errors = 0
        except Exception as e:
            traceback.print_exception(e)
            e_str = traceback.format_exception_only(e)[-1].strip()
            log(f"Unhandled exception! {e_str}")
            errors += 1
        
        if errors == 3:
            print("\nException loop detected. Attempting to re-initialize the client")
            fmap["init"]()
        
        elif errors == 4:
            print("That didn't seem to help. Entering recovery environment")
            print("Run 'headless = False' to resume execution\n")
        
        headless = errors >= 4
        continue
    
    
    # headless cmd version for debugging / recovery
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

# shutdown in case user ran `VARS.RUNNING=False
try:
    fmap["shutdown"]()
except Exception:
    pass
