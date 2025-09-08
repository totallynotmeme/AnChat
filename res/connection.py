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
            print(f"flushing {State.packet}")
            QUEUE.append(bytes(State.packet))
            del State.packet[:]
            State.expected_len = -1


class Protocol_socket:
    socket = None
    
    def handle():
        try:
            while True:
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
        Thread(target=Protocol_socket.handle).start()
        ALIVE = True
    
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
    
    def stream(data_io, name):
        print("(Socket) Streaming has not been implemented yet!")
        try:
            data_io.close()
        except Exception as e:
            print("also your io object threw an error when closing:", e)
    
    
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

http_setup = b"""
GET / HTTP/1.1
Host: {ADDR}
Content-Type: application/octet-stream
Content-Length: 1
Connection: keep-alive


"""[1:-1].replace(b"\n", b"\r\n")

class Protocol_http:
    socket_send = None
    socket_recv = None
    hostname = b""
    
    def handle():
        s = Protocol_http.socket_recv
        request = http_header.replace(b"{ADDR}", Protocol_http.hostname)
        request = request.replace(b"{LENGTH}", b"0")
        send_req = True
        try:
            while True:
                if send_req:
                    s.send(request)
                    send_req = False
                
                try:
                    chunk = s.recv(16384)
                except TimeoutError:
                    State.flush()
                    continue
                
                if chunk.startswith(b"HTTP/1.1 200 Y\r\n") and b"\r\n\r\n" in chunk:
                    chunk = chunk.split(b"\r\n\r\n", 1)[1]
                else:
                    print(f"Unknown header:\n{chunk[:1024]}")
                
                send_req = True
                State.feed(chunk)
                while True:
                    try:
                        chunk = s.recv(16384)
                        if chunk.startswith(b"HTTP/1.1 200 Y\r\n") and b"\r\n\r\n" in chunk:
                            chunk = chunk.split(b"\r\n\r\n", 1)[1]
                        State.feed(chunk)
                        if len(chunk) < 16384:
                            break
                    except TimeoutError:
                        break
        except Exception as e:
            Protocol_http.disconnect(f"Exception occured: {e}")
            return
    
    def connect(addr, port):
        global ALIVE
        
        Protocol_http.hostname = addr.encode()
        header = http_setup.replace(b"{ADDR}", addr.encode())
        
        s = sock.socket()
        s.connect((addr, port))
        s.settimeout(1)
        s.send(header + b"r") # 114
        resp = s.recv(1024)
        if not resp.startswith(b"HTTP/1.1 202 Y\r\n"):
            s.shutdown(sock.SHUT_RDWR)
            s.close()
            raise Exception(f"Invalid response for socket_recv: {resp}")
        Protocol_http.socket_recv = s
        
        s = sock.socket()
        s.connect((addr, port))
        s.settimeout(1)
        s.send(header + b"s") # 115
        resp = s.recv(1024)
        if not resp.startswith(b"HTTP/1.1 202 Y\r\n"):
            Protocol_http.socket_recv.shutdown(sock.SHUT_RDWR)
            Protocol_http.socket_recv.close()
            s.shutdown(sock.SHUT_RDWR)
            s.close()
            raise Exception(f"Invalid response for socket_send: {resp}")
        Protocol_http.socket_send = s
        
        Thread(target=Protocol_http.handle).start()
        ALIVE = True
    
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
        if Protocol_http.socket_send is None:
            return False
        
        try:
            packet_len = len(packet).to_bytes(4, "big")
            header = http_header.replace(b"{ADDR}", Protocol_http.hostname)
            header = header.replace(b"{LENGTH}", str(packet_len).encode())
            Protocol_http.socket_send.send(header + packet_len + packet)
            return True
        except Exception:
            return False
    
    def stream(data_io, name):
        print("(HTTP) Streaming has not been implemented yet!")
        try:
            data_io.close()
        except Exception as e:
            print("also your io object threw an error when closing:", e)
    
    
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
