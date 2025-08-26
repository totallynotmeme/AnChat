# /res/connection.py


import random
import socket as sock
from threading import Thread


ADDR = ""
SOCKET = None
PACKET = bytearray()
PACKET_EXPECTED_LEN = -1
PACKET_QUEUE = []
OVERFLOW = b""
ALIVE = False
EXIT_CODE = "Not connected to the server"


class Protocol_socket:
    def handle():
        global PACKET
        global PACKET_EXPECTED_LEN
        global OVERFLOW
        try:
            while True:
                chunk = OVERFLOW or SOCKET.recv(16384)
                OVERFLOW = b""
                if PACKET_EXPECTED_LEN == -1:
                    if len(chunk) < 4:
                        # only received 1-3 bytes of the first packet, wait for more
                        continue
                    # new packet received
                    PACKET_EXPECTED_LEN = int.from_bytes(chunk[:4], "big")
                    PACKET.extend(chunk[4:])
                    chunk = b""
                if len(PACKET) + len(chunk) >= PACKET_EXPECTED_LEN:
                    # finished receiving new packet (+ beginning of the next)
                    PACKET.extend(chunk)
                    PACKET_QUEUE.append(bytes(PACKET[:PACKET_EXPECTED_LEN]))
                    OVERFLOW = PACKET[PACKET_EXPECTED_LEN:]
                    PACKET = bytearray()
                    PACKET_EXPECTED_LEN = -1
                else:
                    # receiving middle part of the packet
                    PACKET.extend(chunk)
        except Exception as e:
            disconnect(f"Exception: {e}")
            return
    
    def send(packet):
        if SOCKET is None:
            return False
        
        try:
            packet_len = len(packet).to_bytes(4, "big")
            SOCKET.send(packet_len + packet)
            return True
        except Exception:
            return False
    
    def tobits(addr, port):
        if addr.count(".") != 3:
            raise ValueError("Invalid IP format")
        if not 0x0000 <= port <= 0xFFFF:
            raise ValueError("Invalid port format")
        
        raw_bytes = bytes(map(int, addr.split(".")))
        raw_bytes += port.to_bytes(2, "big")
        raw_bytes += random.randbytes(3)
        
        bitarray = "".join(bin(i)[2:].zfill(8) for i in raw_bytes)
        return bitarray
    
    def frombits(bitarray):
        raw_bytes = bytes(int(bitarray[i: i+8], 2) for i in range(0, len(bitarray), 8))
        raw_ip = raw_bytes[0:4]
        raw_port = raw_bytes[4:6]
        
        ip = ".".join(str(i) for i in raw_ip)
        port = int.from_bytes(raw_port, "big")
        return ip, port


http_header = b"""
POST / HTTP/1.1
Host: {ADDR}
Content-Type: application/octet-stream
Content-Length: {LENGTH}
Connection: keep-alive


"""[1:-1].replace(b"\n", b"\r\n")

http_first_get = b"""
GET / HTTP/1.1
Host: {ADDR}
Content-Type: application/octet-stream
Content-Length: 0
Connection: keep-alive


"""[1:-1].replace(b"\n", b"\r\n")

class Protocol_http:
    queue = bytearray()
    def handle():
        global PACKET
        global PACKET_EXPECTED_LEN
        global OVERFLOW
        try:
            first = http_first_get.replace(b"{ADDR}", ADDR.encode())
            SOCKET.send(first)
            resp = SOCKET.recv(1024)
            if not resp.startswith(b"HTTP/1.1 202 Y\r\n"):
                disconnect(f"Failed to establish HTTP connection ({resp=})")
                return
            
            own_req = http_header.replace(b"{ADDR}", ADDR.encode())
            SOCKET.settimeout(1)
            
            while True:
                if OVERFLOW:
                    chunk = OVERFLOW
                else:
                    this_length = len(Protocol_http.queue)
                    this_packet = Protocol_http.queue[:this_length]
                    del Protocol_http.queue[:this_length]
                    this_req = own_req.replace(b"{LENGTH}", str(this_length).encode())
                    SOCKET.send(this_req + this_packet)
                    flush()
                    try:
                        chunk = b""
                        while True:
                            chunk_chunk = SOCKET.recv(16384)
                            print("chunk>", len(chunk_chunk))
                            if len(chunk_chunk) < 1024:
                                print(chunk_chunk)
                            if chunk_chunk == b"":
                                raise RuntimeError("server disconnected")
                            chunk += chunk_chunk
                    except TimeoutError:
                        while chunk.startswith(b"HTTP/1.1 200 Y\r\n") and b"\r\n\r\n" in chunk:
                            chunk = chunk.split(b"\r\n\r\n", 1)[1]
                
                OVERFLOW = b""
                if PACKET_EXPECTED_LEN == -1:
                    if len(chunk) < 4:
                        # only received 1-3 bytes of the first packet, wait for more
                        continue
                    # new packet received
                    PACKET_EXPECTED_LEN = int.from_bytes(chunk[:4], "big")
                    PACKET.extend(chunk[4:])
                    chunk = b""
                if len(PACKET) + len(chunk) >= PACKET_EXPECTED_LEN:
                    # finished receiving new packet (+ beginning of the next)
                    PACKET.extend(chunk)
                    PACKET_QUEUE.append(bytes(PACKET[:PACKET_EXPECTED_LEN]))
                    OVERFLOW = PACKET[PACKET_EXPECTED_LEN:]
                    PACKET = bytearray()
                    PACKET_EXPECTED_LEN = -1
                else:
                    # receiving middle part of the packet
                    PACKET.extend(chunk)
        except Exception as e:
            disconnect(f"Exception: {e}")
            return
    
    def send(packet):
        if SOCKET is None:
            return False
        
        try:
            packet_len = len(packet).to_bytes(4, "big")
            Protocol_http.queue.extend(packet_len + packet)
            return True
        except Exception:
            return False
    
    def tobits(addr, port):
        if not 0x0000 <= port <= 0xFFFF:
            raise ValueError("Invalid port format")
        
        addr = addr.replace(".", "{").replace("/", "|")
        raw_bytes = addr.encode()
        raw_bytes += port.to_bytes(2, "big")
        raw_bytes += random.randbytes(1)
        
        bitarray = "".join(bin(i)[2:].zfill(8) for i in raw_bytes)
        return bitarray
    
    def frombits(bitarray):
        raw_bytes = bytes(int(bitarray[i: i+8], 2) for i in range(0, len(bitarray), 8))
        raw_addr = raw_bytes[0:-3]
        raw_port = raw_bytes[-3:-1]
        
        addr = raw_addr.decode().replace("|", "/").replace("{", ".")
        port = int.from_bytes(raw_port, "big")
        return addr, port


def connect(addr, port):
    global ALIVE
    global SOCKET
    global ADDR
    
    SOCKET = sock.socket()
    SOCKET.connect((addr, port))
    ADDR = addr
    Thread(target=protocol.handle).start()
    ALIVE = True

def disconnect(reason="[Undefined reason]"):
    global ALIVE
    global PACKET
    global PACKET_EXPECTED_LEN
    global OVERFLOW
    global EXIT_CODE
    
    ALIVE = False
    try:
        SOCKET.shutdown(sock.SHUT_RDWR)
        SOCKET.close()
    except Exception:
        pass
    
    try:
        flush()
    except Exception:
        pass
    
    PACKET = bytearray()
    PACKET_EXPECTED_LEN = -1
    OVERFLOW = b""
    EXIT_CODE = reason

def flush():
    global PACKET
    global PACKET_EXPECTED_LEN
    global OVERFLOW
    
    if PACKET == b"":
        return
    
    PACKET_QUEUE.append(bytes(PACKET[:PACKET_EXPECTED_LEN]))
    OVERFLOW = PACKET[PACKET_EXPECTED_LEN:]
    PACKET = bytearray()
    PACKET_EXPECTED_LEN = -1


protocol_list = {
    "Socket": Protocol_socket,
    "HTTP": Protocol_http,
}
protocol = Protocol_socket
default = Protocol_socket
