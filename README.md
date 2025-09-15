# AnChat

> [!WARNING]
> This project is currently Work In Progress.
> Server hosting files are unavailable and some features may be broken / scuffed.

Private anonymous tool for chatting with your friends.
Just create your own tunnel and send the passphrase to your friend, it's that easy.

Please keep in mind that this is ***not a replacement for existing chatting platforms***
and should only be used for sharing information with people you actually trust.
NEVER connect to random people you don't know, and don't let random people connect to you.

## Current features and flaws:
### +
1. e2e encryption
2. direct connection between chat members, no central servers
3. supports multiple protocols (Socket for local networks or direct port forwarding; HTTP for 3rd party port forwarding)
4. interactive UI, dynamic settings menu
5. passphrases are cool

### -
1. HTTP protocol is extremely scuffed
2. connection can expose your ip address to server host (doesn't really matter if you're friends)
3. features don't work in some cases (Linux: clipboard doesn't work)
4. file transfers can fail miserably, especially for big files
5. a lot of other small issues
