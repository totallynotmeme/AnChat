# /res/encryption_old.py
# old/insecure encryption functions and utils


import operator
from hashlib import sha256


def xor_v1(data, salt, password):
    """
    ADDED: v0.1.0-INDEV (core version)
    DEPRECATED: v0.2.0-ALPHA (core version)
    
    apparently packets can be cracked without the password if the attacker knows
    the first 32 decrypted bytes. highly unlikely, but it's still a possibility
    
    easy fix - add password to sha256 hash inside the loop so you can't de-xor
    the first few bytes and generate the rest of the key without the password
    """
    hashed = sha256(password + salt).digest()
    key = [hashed]
    len_key = 32
    len_data = len(data)
    while len_key < len_data:
        hashed = sha256(hashed + salt).digest()
        key.append(hashed)
        len_key += 32
    key = b"".join(key)
    return bytes(map(operator.xor, data, key))


funcs = [xor_v1]
funcs = {i.__name__: i for i in funcs}
