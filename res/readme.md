
# Technical information

Only for people who know what they're doing :,)
> [!NOTE]
> Due to laziness of user **totallynotmeme**, this information table is not finished.
> More info will be added in the future


## Layers
There are multiple layers in this program:
- Wrapper - anything that runs `from res import *`. Typically runs `tick()` function in a loop, handles crashes if needed
- Core - every script in `/res` folder. Handles basic functions, as well as loading and bootstrapping clients
- Client - everything in `/res/{client_name}` folder. Defines its own functions such as tick, init, etc; handles basically every interaction


## Messages
Messages are structured in the following way:
- Raw message object - dictionary `{b"field": b"value", ...}` (can be converted to/from bytes)
- Packet - raw message (bytes) + sha256 hash of raw message
- Encrypted packet - encryption salt (64 bytes) + packet (encrypted)

Generic information:
- Only encrypted packet should be sent to/received from the server.
- Prefix `~` can be used in system messages that are handled locally,
as it's stripped away when receiving data from connection (ex. `b"author": b"~SYSTEM"`, or `b"~errorcode": b"SOMETHING"`)


## Client (Blueberry)
Useful info will appear here, but not now...

<!-- todo: add more stuff -->
