# /res/connection.py


import random
import socket as sock
from threading import Thread


QUEUE = []
ALIVE = False
EXIT_CODE = "Not connected to the server"


class State:
    packet = bytearray()
    expected_len = -1
    
    def feed(chunk):
        State.packet.extend(chunk)
        
        if State.expected_len == -1:
            # determine packet length
            if len(State.packet) < 4:
                return
            State.expected_len = int.from_bytes(State.packet[:4], "big")
            del State.packet[:4]
        
        if len(State.packet) >= State.expected_len:
            # got every bit of packet
            full_packet = State.packet[:State.expected_len]
            del State.packet[:State.expected_len]
            
            QUEUE.append(bytes(full_packet))
            State.expected_len = -1
            # handle overflow
            if State.packet:
                State.feed(b"")
    
    def flush():
        if State.packet:
            QUEUE.append(bytes(State.packet))
            del State.packet[:]
            State.expected_len = -1


class Protocol_socket:
    socket = None
    
    def handle():
        try:
            while ALIVE:
                try:
                    chunk = Protocol_socket.socket.recv(16384)
                except TimeoutError:
                    State.flush()
                    continue
                
                if chunk == b"":
                    Protocol_socket.disconnect("Received empty packet, connection has been closed")
                    return
                State.feed(chunk)
        except Exception as e:
            Protocol_socket.disconnect(f"Exception occured: {e}")
            return
    
    def connect(addr, port):
        global ALIVE
        
        Protocol_socket.socket = sock.socket()
        Protocol_socket.socket.connect((addr, port))
        Protocol_socket.socket.settimeout(1)
        
        ALIVE = True
        Thread(target=Protocol_socket.handle).start()
    
    def disconnect(reason="[No disconnection reason]"):
        global ALIVE
        global EXIT_CODE
        
        EXIT_CODE = reason
        ALIVE = False
        
        try:
            Protocol_socket.socket.shutdown(sock.SHUT_RDWR)
            Protocol_socket.socket.close()
        except Exception:
            pass
        Protocol_socket.socket = None
    
    def send(packet):
        if Protocol_socket.socket is None:
            return False
        
        try:
            packet_len = len(packet).to_bytes(4, "big")
            Protocol_socket.socket.send(packet_len + packet)
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


http_send = b"""
GET /s HTTP/1.1
host: {ADDR}
content-type: application/octet-stream
content-length: {LENGTH}
connection: close


"""[1:-1].replace(b"\n", b"\r\n")

http_recv = b"""
GET /r HTTP/1.1
host: {ADDR}
content-type: application/octet-stream
content-length: 4
connection: close


"""[1:-1].replace(b"\n", b"\r\n")

http_ping = b"""
GET /p HTTP/1.1
host: {ADDR}
content-type: application/octet-stream
content-length: 0
connection: close


"""[1:-1].replace(b"\n", b"\r\n")

class Protocol_http:
    user_id = random.randbytes(4)
    hostname = b""
    socket_args = ()
    
    def handle():
        get_request = http_recv + Protocol_http.user_id
        try:
            while ALIVE:
                packet = Protocol_http._send_request(get_request, 15)
                if packet == b"":
                    State.flush()
                    continue
                
                if packet.startswith(Protocol_http.user_id):
                    # own packet, ignore
                    continue
                
                if packet:
                    State.feed(packet)
        except Exception as e:
            Protocol_http.disconnect(f"Exception occured: {e}")
            return
    
    def connect(addr, port):
        global ALIVE
        
        Protocol_http.socket_args = (addr, port)
        Protocol_http.hostname = addr.encode()
        resp = Protocol_http._send_request(http_ping)
        if resp != b"silly":
            raise Exception(f"Invalid ping response from server ({resp})")
        
        ALIVE = True
        Thread(target=Protocol_http.handle).start()
    
    def disconnect(reason="[No disconnection reason]"):
        global ALIVE
        global EXIT_CODE
        
        EXIT_CODE = reason
        ALIVE = False
        
        try:
            Protocol_http.socket_send.shutdown(sock.SHUT_RDWR)
            Protocol_http.socket_send.close()
        except Exception:
            pass
        Protocol_http.socket_send = None
        
        try:
            Protocol_http.socket_recv.shutdown(sock.SHUT_RDWR)
            Protocol_http.socket_recv.close()
        except Exception:
            pass
        Protocol_http.socket_recv = None
    
    def send(packet):
        if not ALIVE:
            return False
        
        try:
            packet_len = len(packet).to_bytes(4, "big")
            header = http_send.replace(b"{LENGTH}", str(len(packet)+8).encode())
            http_packet = header + Protocol_http.user_id + packet_len + packet
            return Protocol_http._send_request(http_packet, nowait=True)
        except Exception:
            return False
    
    def _send_request(what, timeout=3, nowait=False):
        req = what.replace(b"{ADDR}", Protocol_http.hostname)
        chunks = (req[i: i+65536] for i in range(0, len(req), 65536))
        s = sock.socket()
        s.settimeout(timeout)
        try:
            s.connect(Protocol_http.socket_args)
            for i in chunks:
                s.send(i)
            if nowait:
                return True
            try:
                chunk = s.recv(16384)
                resp = chunk
            except TimeoutError:
                return b""
            if resp == b"":
                return b""
            
            resp_head, resp = resp.split(b"\r\n\r\n", 1)
            if not resp_head.startswith(b"HTTP/1.1 200 Y\r\n"):
                if b"\r\n" in resp_head:
                    resp_head = resp_head.split(b"\r\n", 1)[0]
                Protocol_http.disconnect(f"Dead connection: unknown header {resp_head}")
            
            s.settimeout(1)
            try:
                while True:
                    chunk = s.recv(16384)
                    if chunk == b"":
                        break
                    resp += chunk
            except Exception:
                pass
            return resp
        except Exception:
            return b""
        finally:
            s.shutdown(sock.SHUT_RDWR)
            s.close()
    
    
    def tobits(addr, port):
        if not 0x0000 <= port <= 0xFFFF:
            raise ValueError("Invalid port format")
        
        addr = addr
        raw_bytes = addr.encode()
        raw_bytes += port.to_bytes(2, "big")
        raw_bytes += random.randbytes(1)
        
        bitarray = "".join(bin(i)[2:].zfill(8) for i in raw_bytes)
        return bitarray
    
    def frombits(bitarray):
        raw_bytes = bytes(int(bitarray[i: i+8], 2) for i in range(0, len(bitarray), 8))
        raw_addr = raw_bytes[0:-3]
        raw_port = raw_bytes[-3:-1]
        
        addr = raw_addr.decode()
        port = int.from_bytes(raw_port, "big")
        return addr, port


protocol_list = {
    "Socket": Protocol_socket,
    "HTTP": Protocol_http,
}
default = Protocol_socket
protocol = default

