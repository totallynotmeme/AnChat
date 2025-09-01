# /chat-standalone.py
# To-be-compiled wrapper with a somewhat user-friendly crash handler
# If you're running raw Python code, use chat.py instead


from res import *
import traceback
import random
import time


crash_log_name = f"anchat-crash-log-{random.randint(0, 999999999)}.txt"
funny = random.choice([
"Shit happens, buddy, just give it another shot!",
"I guess too much privacy can lead to crashes like this. Oh well",
"According to all known laws of coding, there's no way spaghetti should be able to work",
"im a haxxor youve been BEAMED send crypto to this address 0xT07AL7Y-A-R3AL-W4LL37",
"Timmy, i told you NOT to mess with the freaking console!",
"There is no funny text here, keep scrolling",
"Look at me reading the crash log as if i understand something!",
"I stole this idea from Minecraft's crash logs, you can't judge me!!!",
"I am currently writing these phrases at 3 am. Say hi to my past self!",
"Very important error code: 418 Im a teapot",
"It's dangerous to go alone, take this! https://www.reddit.com/r/cutecats/",
])


crash_message_on_init = f"""
AnChat has crashed *during initialization stage* at {{}}
{funny}


Please reinstall the application from the official GitHub repository:
(blah blah blah, will add the link later)
Feel free to create an issue with this message attached so the dev can fix it!



Here's the traceback, nothing interesting here unless you're a nerd:
(if there's nothing after this line, the dump failed, oof)

"""
crash_message_at_runtime = f"""
AnChat has crashed *at runtime* at {{}}
{funny}


Try to re-launch the application to see if it fixes the problem

If that doesn't help, reinstall the application from the official GitHub repository:
(blah blah blah, will add the link later)
Feel free to create an issue with this message attached so the dev can fix it!
If possible, describe what you were doing before the crash happened



Here's the traceback, nothing interesting here unless you're a nerd:
(if there's nothing after this line, the dump failed, oof)

"""

try:
    fmap["init"]()
    fmap["handle_log"]()
except Exception as e:
    time_when = time.strftime("[%c]")
    with open(crash_log_name, "w") as crash_dump:
        crash_dump.write(crash_message_on_init.format(time_when))
        traceback.print_exception(e, file=crash_dump)
    exit()


errors = 0
err = None
reinit_err = None


while VARS.RUNNING:
    try:
        fmap["tick"]()
        errors = 0
    except Exception as e:
        errors += 1
        err = e
    
    if errors == 3:
        try:
            fmap["init"]()
        except Exception as e:
            errors = 69
            reinit_err = e
    
    elif errors >= 4:
        time_when = time.strftime("[%c]")
        with open(crash_log_name, "w") as crash_dump:
            crash_dump.write(crash_message_at_runtime.format(time_when))
            traceback.print_exception(err, file=crash_dump)
            if reinit_err:
                traceback.print_exception(reinit_err, file=crash_dump)
        exit()
