# /res/blueberry/lang/en.py
# English localization for this client



WINDOW_TITLE = "AnChat - Blueberry client"
CORE_VERSION = "Core version: {}"
CLIENT_VERSION = "Client version: {}"

FIELD_USERNAME = "Your username (Anon)"
FIELD_ADDRESS = "Server address"
CONNECT_BUTTON = "Connect"

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
OPTIONS_DEVELOPER = "Developer options"
OPTIONS_APPLY = "Apply"
OPTIONS_RESET = "Reset"


TASK_UNKNOWN = "Unknown status text '{}' for task {}"

TASK_STREAM_RUNNING = "Streaming file {} (#{}/{} chunks  {}%)"
TASK_STREAM_DONE = "Finished streaming file {} ({} chunks)"
TASK_STREAM_FAILED = "Streaming failed at chunk #{}/{} (check console for more info)"

TASK_CONNECT_RUNNING = "Trying to connect to the server"
TASK_CONNECT_DONE = "Connected successfully!"
TASK_CONNECT_FAILED = "Connection failed"

TASK_SENDMSG_RUNNING = "Sending your message..."
TASK_SENDMSG_DONE = "Success!"
TASK_SENDMSG_FAILED = "Failed to send a message"


MESSAGE_CONNECTED = "Connected to the server, send /disconnect to get back to menu"
MESSAGE_DISCONNECTED = "Disconnected from the server"
MESSAGE_DUMPED = "Dumped message history into {}"
MESSAGE_CLEARED = "Message history cleared"
MESSAGE_STREAMING_START = "Streaming file '{}' to members of this chat"
MESSAGE_STREAMING_END = "Streaming finished."
MESSAGE_STREAMING_FAIL = "Can't stream this file: {}"
MESSAGE_STREAMING_WARN = """File streaming currently doesn't work as intended. This will be fixed in the future.
If you really want to stream this file, drag it into this window again"""
MESSAGE_HELP = """
/disconnect - from the server
/dump - message history into a file
/clear - message history
/help - menu has been shown to you!
(SYSTEM messages are only visible to you)
"""[1:-1]

CHATBOX_FIELD = "Type your message here"
CONNECTION_ERROR = "Connection error: {}"

ERROR_CODES = {
    b"BADPACKET": "Received invalid message packet",
    b"WRONGHASH": "Message hash check failed, this packet is corrupted",
    b"DUPESALT": "Received message with duplicate salt. Possible packet replay attack?",
}
