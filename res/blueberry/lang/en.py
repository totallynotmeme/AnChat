# /res/blueberry/lang/en.py
# English localization for this client



WINDOW_TITLE = "AnChat - Blueberry client"
CORE_VERSION = "Core version: {}"
CLIENT_VERSION = "Client version: {}"

FIELD_USERNAME = "Your username"
FIELD_ADDRESS = "Server address"
CONNECT_BUTTON = "Connect"

STATUS_TEXT_DEFAULT = "Fill in the fields and press Connect"
STATUS_TEXT_TRYING = "Trying to connect, please wait..."
STATUS_TEXT_FAILED = "Failed: {}"

OPTIONS_TITLE = "Settings"
OPTIONS_LANGUAGE = "Switch language (requires restart)"


MESSAGE_CONNECTED = "Connected to the server, send /disconnect to get back to menu"
MESSAGE_DISCONNECTED = "Disconnected from the server"
MESSAGE_DUMPED = "Dumped message history into {}"
MESSAGE_STREAMING_START = "Streaming file '{}' to members of this chat"
MESSAGE_STREAMING_END = "Streaming finished."

CHATBOX_FIELD = "Type your message here"
CONNECTION_ERROR = "Connection error: {}"

ERROR_CODES = {
    b"BADPACKET": "Received invalid message packet",
    b"WRONGHASH": "Message hash check failed, this packet is corrupted",
    b"DUPESALT": "Received message with duplicate salt. Possible packet replay attack?",
}
