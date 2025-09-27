# /hosting/forward-localhostdotrun.py


import subprocess
import core


# [===== START OF SETTINGS =====]

# put something between "quotes" to add a passphrase suffix.
# is optional, does not affect the passphrase generation at all
# suffix = "very silly suffix here"
suffix = ""

# change this ONLY IF you're using a different local port,
# should be left untouched otherwise.
local_port = 65333

# replace False with True to confirm you've read this
#                      vvvvv
i_know_what_im_doing = False
#                      ^^^^^

# [===== END OF SETTINGS =====]
# scroll down if you're a nerd and love reading code


if not i_know_what_im_doing:
    print("""
    Hello there!
    Please open this script in any text editor you like,
    there are some important settings you need to look at.
    Thanks for understanding!
""")
    input("Press ENTER to quit: ")
    exit(-1)


if suffix.strip():
    # if suffix exists, add // prefix to it
    suffix = " // " + suffix.strip()

cmd = f"""
ssh -o ServerAliveInterval=60 -R 80:127.0.0.1:{local_port} nokey@localhost.run
"""[1:-1]

print(f"""


ALL OF THIS IS EXPERIMENTAL, THINGS **WILL** BREAK

Running ssh forwarding via localhost.run on port {local_port}
Check their website for more information: https://localhost.run
If you get any errors, try running the command in your console instead

{cmd}

""")

input("Press ENTER to confirm and run the command above: ")
print("Running. Something should appear in a few seconds...\n")


p = subprocess.Popen(
    cmd,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT,
    shell = True,
)

for line in p.stdout:
    if b"tunneled with tls termination, " not in line:
        continue
    url = line.split()[0].decode()
    print("Tunnel reset, new URL:", url)
    
    bits = core.http_tobits(url, 80)
    words = core.wordip_encode(bits)
    if suffix:
        words = words + suffix
    print("New passphrase:", words)
