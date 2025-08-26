# /res/message.py


# import gzip
from hashlib import sha256


""" deprecated
# util functions
def safe_decode(text):
    try:
        res = text.decode()
    except UnicodeDecodeError:
        res = repr(text)
    return res

def compress(data):
    return gzip.compress(data, mtime=0)[8:]

def decompress(data):
    return gzip.decompress(b"\x1f\x8b\x08\x00\x00\x00\x00\x00" + data)
"""


# handle sending and receiving messages from bytes
def parse_packet(packet):
    message = {}
    packet = bytearray(packet[:-32])
    while packet:
        name_length = packet.pop()
        name = packet[-name_length:]
        del packet[-name_length:]
        name = bytes(name)
        if name.startswith(b"~"):
            name = name.lstrip(b"~")
        
        data_length = int.from_bytes(packet[-3:], "big")
        del packet[-3:]
        data = packet[-data_length:]
        del packet[-data_length:]
        
        message[name] = bytes(data)
    
    if b"author" in message and message[b"author"].startswith(b"~"):
        message[b"author"] = message[b"author"].lstrip(b"~")
    
    return message


def gen_packet(message):
    packet = bytearray()
    for name, data in message.items():
        name_length = len(name).to_bytes(1, "big")
        data_length = len(data).to_bytes(3, "big")
        
        packet.extend(data + data_length + name + name_length)
    
    hashed = sha256(packet).digest()
    return packet + hashed


def verify_hash(message):
    packet = message[:-32]
    hashed = message[-32:]
    true_hash = sha256(packet).digest()
    return hashed == true_hash


# error messages
error_invalid_packet = lambda: {
    b"author": b"~SYSTEM",
    b"content": b"Received invalid message packet",
    b"~errorcode": b"BADPACKET",
}

error_invalid_hash = lambda: {
    b"author": b"~SYSTEM",
    b"content": b"Message hash check failed, this packet is corrupted",
    b"~errorcode": b"WRONGHASH",
}

error_duplicate_salt = lambda: {
    b"author": b"~SYSTEM",
    b"content": b"Received message with duplicate salt. Possible packet replay attack?",
    b"~errorcode": b"DUPESALT",
}
