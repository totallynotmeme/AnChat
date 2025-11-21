# /res/encryption.py


from . import encryption_old as old
import operator
import os
from hashlib import sha256
#import rsa


SALT_BYTES = 64
USED_SALT = set()
SALT_MASK = b'\xf1y[\x80>\xd7\x0eK\r\x8chd\x07o\xf0\xf7\x80 \xf2\xf6,\xdf\x88|\xb8\x84\x8a\xd5\xbe\xa0"6\x1e\xb5\xe3:\x8b\xad\xf1Z\x92\x8fC\x87!w\x04C\xa50+\xcew\xe4\x8c\x96\xfd~\xa9\xb1\x1eG\xa4}'

password = b""


# basic encryption function
def xor(data, salt, password):
    """
    unique name: xor_v2
    ADDED: v0.2.0-ALPHA (core version)
    
    default encryption function with no vulnerabilities found so far.
    
    if you think you found a way to crack it without knowing the password,
    please create an issue on github (same page where you got this from :P)
    """
    hashed = sha256(password + salt).digest()
    key = [hashed]
    len_key = 32
    len_data = len(data)
    while len_key < len_data:
        hashed = sha256(hashed + password + salt).digest()
        key.append(hashed)
        len_key += 32
    key = b"".join(key)
    return bytes(map(operator.xor, data, key))

# xor works both ways so we can just use it for both encryption/decryption
_f_encrypt = xor
_f_decrypt = xor

def process_salt(salt):
    return bytes(map(operator.xor, salt, SALT_MASK))


# main encryptor/decryptor functions that are used in the code
def encrypt(raw):
    salt = os.urandom(SALT_BYTES)
    return process_salt(salt) + _f_encrypt(raw, salt, password)

def decrypt(raw):
    salt = process_salt(raw[:SALT_BYTES])
    raw = raw[SALT_BYTES:]
    return _f_decrypt(raw, salt, password)


# throw away packets with salt that has already been used
def validate(raw):
    salt = raw[:SALT_BYTES]
    if salt in USED_SALT:
        return False
    USED_SALT.add(salt)
    return True



""" UNUSED CONCEPT
talking to the server without it having to know the password.
could be useful in some cases like server-side commands (ex: ?membercount),
but idk, the server code is already spaghetti enough.
looking back, i have no idea what i was doing when writing this lol


# client 2 server encryption (commands)
SERVER_KEYS_BYTES = 64
SERVER_INIT_PRIVATE = None
SERVER_INIT_PUBLIC = None
SERVER_INIT_SKEY = None

server_pword = None
"#""
protocol:
# c_accept_init
S : generate private/public keys
S -> C : public key, not encrypted
# s_init_create
C : generate own private/public keys, encrypt with server's key
C -> S : public key
# c_accept_generate
S : create challenge for client to repeat, encrypt with client's key
S -> C : challenge
# s_init_solve
C : decrypt and re-encrypt the challenge with own key
C -> S : same challenge
# s_accept_validate
S : validate the challenge and accept the connection
"#""
def s_init_create(packet):
    global SERVER_INIT_PUBLIC
    global SERVER_INIT_PRIVATE
    global SERVER_INIT_SKEY
    
    key = int.from_bytes(packet, "big")
    SERVER_INIT_PUBLIC, SERVER_INIT_PRIVATE = rsa.newkeys(SERVER_KEYS_BYTES*8)
    SERVER_INIT_SKEY = rsa.PublicKey(key, 65537)
    key = SERVER_INIT_PUBLIC.n.to_bytes(SERVER_KEYS_BYTES, "big")
    split_at = len(key) // 2
    chunk1 = rsa.encrypt(key[:split_at], SERVER_INIT_SKEY)
    chunk2 = rsa.encrypt(key[split_at:], SERVER_INIT_SKEY)
    return chunk1 + chunk2

def s_init_solve(packet):
    split_at = len(packet) // 2
    chunk1 = rsa.decrypt(packet[:split_at], SERVER_INIT_PRIVATE)
    chunk2 = rsa.decrypt(packet[split_at:], SERVER_INIT_PRIVATE)
    challenge = chunk1 + chunk2
    split_at = len(challenge) // 2
    chunk1 = rsa.encrypt(challenge[:split_at], SERVER_INIT_SKEY)
    chunk2 = rsa.encrypt(challenge[split_at:], SERVER_INIT_SKEY)
    return chunk1 + chunk2


# test environment
# S : generate private/public keys
serverkey_public, serverkey_private = rsa.newkeys(SERVER_KEYS_BYTES*8)
packet = serverkey_public.n.to_bytes(SERVER_KEYS_BYTES, "big")
# S -> C : public key, not encrypted
resp = s_init_create(packet)

split_at = len(resp) // 2
chunk1 = rsa.decrypt(resp[:split_at], serverkey_private)
chunk2 = rsa.decrypt(resp[split_at:], serverkey_private)
resp = chunk1 + chunk2

clientkey = rsa.PublicKey(int.from_bytes(resp, "big"), 65537)
# S : create challenge for client to repeat, encrypt with client's key
challenge = os.urandom(64)

split_at = len(challenge) // 2
chunk1 = rsa.encrypt(challenge[:split_at], clientkey)
chunk2 = rsa.encrypt(challenge[split_at:], clientkey)
packet = chunk1 + chunk2

# S -> C : challenge
resp = s_init_solve(packet)
split_at = len(resp) // 2

chunk1 = rsa.decrypt(resp[:split_at], serverkey_private)
chunk2 = rsa.decrypt(resp[split_at:], serverkey_private)
their_chal = chunk1 + chunk2

# S : validate the challenge and accept the connection
print(challenge)
print(their_chal)
"""
