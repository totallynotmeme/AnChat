# AnChat

README in different languages:
- [Русский перевод](README.ru.md)
- more coming soon(?)

---

> [!WARNING]
> This project is currently Work In Progress.
> Some features may be broken and scuffed, and server hosting files are only available in `raw_code.py` version.
> Please don't try to host your own server unless you know what you're doing.

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
3. features don't work in some cases (Linux: clipboard is broken)
4. file transfers can fail miserably, especially for big files
5. a lot of other small issues


## Why use this instead of other (and better) chat platforms?
If you found a better alternative that actually works, that's great, feel free to use it!
This is mainly a passion project, not a tool that's meant to be used by real people.
In case every single other app is banned in your country (i'm so sorry), you can try using this as a temporary alternative.

Currently this app is not too useful as it lacks important features like proper file sharing.
Feel free to contribute to this repository if you want, every small change is welcome and greatly helps in development process!
(especially when there's only one person working on it ;-;)
