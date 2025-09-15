
# Technical information

Only for people who know what they're doing :,)
> [!WARNING]
> Things will probably change during development.
> Do not rely on this information until at least the first release.

## Layers
There are multiple layers in this program:
- Wrapper - anything that runs `from res import *`. Typically runs `tick()` function in a loop, handles crashes if needed
- Core - every script in `/res` folder. Handles basic functions, as well as loading and bootstrapping clients
- Client - everything in `/res/{client_name}` folder. Defines its own functions such as tick, init, etc; handles basically every interaction

<!-- todo: add more info about layers -->

## Messages
Messages are structured in the following way:
- Raw message object - dictionary `{b"field": b"value", ...}` (can be converted to/from bytes)
- Packet - raw message (bytes) + sha256 hash of raw message
- Encrypted packet - encryption salt (64 bytes) + encrypted packet

<!-- todo: add more info about messages -->

<!-- todo: add more stuff -->
