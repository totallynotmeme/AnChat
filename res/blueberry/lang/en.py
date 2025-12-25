# /res/blueberry/lang/en.py
# English localization for this client



WINDOW_TITLE = "AnChat - Blueberry client   //   "
CORE_VERSION = "Core version: {}"
CLIENT_VERSION = "Client version: {}"

FIELD_USERNAME = "Your username (Anon)"
FIELD_ADDRESS = "Server address"
CONNECT_BUTTON = "Connect"
LOADED_ALG_TEXT = "Using encryption functions {}/{}"

STATUS_TEXT_DEFAULT = "Fill in the fields and press Connect"
STATUS_TEXT_TRYING = "Trying to connect, please wait..."
STATUS_TEXT_FAILED = "Failed: {}"
STATUS_TEXT_BADIP = "Bad IP address format: {}"

OPTIONS_TITLE = "Settings"
OPTIONS_LANGUAGE = "Language"
OPTIONS_RESOLUTION = "Window size"
OPTIONS_FONT = "Font"
OPTIONS_FONT_WARN = "This is an experimental setting"
OPTIONS_BACKGROUND = "Background style"
OPTIONS_THEME = "App theme"
OPTIONS_DEVELOPER = "Developer options"
OPTIONS_APPLY = "Apply"
OPTIONS_RESET = "Reset"

OPTIONS_ADVANCED_WARN1 = "Dangerous settings!"
OPTIONS_ADVANCED_WARN2 = """
Below are options which can break important functions of this client
or even completely disable the encryption of your chats. Be careful!
""".replace("\n", " ")

OPTIONS_TOOLS_TITLE = "Tools"
OPTIONS_TOOLS_RUN = "Run"
OPTIONS_TOOLS_DESC = """
A set of simple tools that can be used outside of chatting!
To paste path to a file: click on the text line and drag your file into this window
"""[1:-1]

ABOUT_TEXT = """
AnChat v{client_ver}
Blueberry client v{core_ver}

Running Python {ver}
Compiled to .exe: {is_exe}
"""[1:-1]
ABOUT_TEXT2 = """
Made by people for people
Privacy is a human right.

Link to the project repository:
https://github.com/totallynotmeme/AnChat
"""[1:-1]


TASK_UNKNOWN = "Unknown status text '{}' for task {}"

TASK_STREAM_RUNNING = "Streaming file {} (#{}/{} chunks  {}%)"
TASK_STREAM_DONE = "Finished streaming file {} ({} chunks)"
TASK_STREAM_FAILED = "Streaming failed at chunk #{}/{} (check console for more info)"

TASK_CONNECT = {
    "running": "Trying to connect to the server",
    "done": "Connected successfully!",
    "failed": "Connection failed",
}
TASK_SENDMSG = {
    "running": "Sending your message...",
    "done": "Success!",
    "failed": "Failed to send a message",
}
TASK_TOOL = {
    "running": "{} is running...",
    "done": "{} finished!",
    "failed": "{} exited with an error",
}


HELP_TITLE = "Help / basic information"
HELP_BUTTON = "Wat??"
HELP_TEXT = """
Hi there, and welcome to AnChat!
(you can scroll down, use your mouse wheel)

work in progress, things might change


If you're reading this, you're probably seeing this app for the first time.\
 In short, this is a simple project that uses end-to-end encryption so only\
 people with the passphrase can read messages you send in the chat room

Before you continue reading, feel free to change some of the options, such as\
 Language or Window size. Click the button in the top-left corner, you can\
 figure out the rest!



> But other messenger apps already do that, like DMs on Discord!!

Sure, no other USER might be able to see your messages, but they are decrypted\
 server-side to store your years-long message history. That's completely\
 normal and it probably won't affect you... unless you get hacked.\
 Feel free to use Discord or other apps if you don't need extreme levels\
 of privacy



> Then why shouldn't I use Kleopatra for true end-to-end encryption?

If you can, use it! This project was made as a more convenient alternative\
 for people who don't want to click through text menus and manage their keys.\
 Of course, it still can't be as simple as "a few clicks and you're done", but\
 copying a one-time passphrase ONCE is (in my opinion) much more user-friendly\
 rather than pasting and decrypting each individual message



> How do I let my friend connect to me?

Sadly, because this app is still being developed, it's not as easy and requires\
 some technical knowledge. Currently, the server host has to install Python\
 on their system and download a server script from the GitHub repository where\
 you got this app from. To set up a temporary server without too much trouble,\
 you can:

1. Download 2 files from the project repo:
  - hosting/server-http.py
  - hosting/forward-localhostdotrun.py
  - hosting/core.py
2. Open "forward-localhostdotrun.py" in your code editor to make sure the\
 settings are right
3. Run "server-..." and "forward-..." scripts

You should now have two windows, one saying:
  - server listening on 127.0.0.1:65333
and the other one asking you to press Enter to run the ssh command.\
 Do it, make sure it works, type "y" if needed. Finally, it should show:
  - Tunnel reset, new URL: (https link)
  - New passphrase: (a bunch of words)
Send these words to your friend, pick HTTP protocol on connection screen,\
 and now you can finally connect!

Keep in mind that the server will only last a short amount of time, around\
 5-10 minutes. If you want to host a server for much longer, I recommend using\
 Radmin VPN (or a similar tool) to directly connect to each other. If you don't\
 know how, you can follow a guide like "how to play minecraft via radmin".\
 In that case, you only need one script: server-socket.py (to connect, you can\
 use a passphrase of format "{lol anything i want}@{ip}:{port}", without {})
(built-in "run server" button is planned in future updates)



the end.
"""[1:-1]


MESSAGE_CONNECTED = "Connected to the server, send /disconnect to get back to menu"
MESSAGE_DISCONNECTED = "Disconnected from the server"
MESSAGE_DUMPED = "Dumped message history into {}"
MESSAGE_CLEARED = "Message history cleared"
MESSAGE_STREAMING_START = "Streaming file '{}' to members of this chat"
MESSAGE_STREAMING_END = "Streaming finished."
MESSAGE_STREAMING_FAIL = "Can't stream this file: {}"
MESSAGE_HELP = """
/disconnect - from the server
/dump - message history into a file
/clear - message history
/help - menu has been shown to you!
(SYSTEM messages are only visible to you)
"""[1:-1]

CHATBOX_FIELD = "Type your message here"
CHAT_DISCONNECT = "Disconnect"
CONNECTION_ERROR = "Connection error: {}"
RECEIVING_BYTES = "Receiving message: {}/{} bytes in queue"

ERROR_CODES = {
    b"BADPACKET": "Received invalid message packet",
    b"WRONGHASH": "Message hash check failed, this packet is corrupted",
    b"DUPESALT": "Received message with duplicate salt. Possible packet replay attack?",
}
THEME_TABLE = {
    "background": "Background",
    "bgdetails": "BG Details",
    "base": "Base",
    "accent": "Accent",
    "accent2": "Accent 2",
    "text": "Text",
    "accent text": "Accent Text",
    "bubble": "Bubble",
    "bubble edge": "Bubble Edge",
}
OPTIONS_CATEGORY_TABLE = {
    "standard": "Standard",
    "advanced": "Advanced",
    "tools": "Tools",
    "about": "About",
}

SPLASHES = [
    "Why does a chat app need splash texts?", # no comment
    "Privacy? What's that? Never heard of it",
    "Made by just one person!",
    "Press ESC to open a Python console",
    "Psst, have you tried right clicking the messages?",
    "Who doesn't like cat memes?",
    "What could go wrong?",
    "No AI generated code!",
    "file transfer is still broken haha (i need help)",
    "Respect to those 2 guys who starred this",
    "hi",
    "who are you",
    "insert funny splash text here",
]
