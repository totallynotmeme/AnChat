# /hosting/server.py

import socket as sock
from threading import Thread
from time import sleep
import traceback


# use this command to set up a tunnel
# ssh -o ServerAliveInterval=60 -R 80:127.0.0.1:65333 nokey@localhost.run
# where 65333 is your port

IP = "127.0.0.1"
PORT = 65333

QUEUE = {}
# {user_id: [time, packet, was_header_sent]}


http_response = b"""
HTTP/1.1 200 Y
Content-Length: {LENGTH}
Content-Type: application/octet-stream
Connection: close


"""[1:-1].replace(b"\n", b"\r\n")

http_ping = b"""
HTTP/1.1 200 Y
content-length: 5
content-type: application/octet-stream
connection: close

silly
"""[1:-1].replace(b"\n", b"\r\n")


def threaded(func):
    Thread(target=func).start()

#print = lambda *a, **kwa: 0 # uncomment to suppress console output


@threaded
def server_loop():
    while True:
        sleep(1)
        for key in QUEUE.copy().keys():
            QUEUE[key][0] -= 1
            if QUEUE[key][0] < 0:
                #print(f"popping {key} from queue")
                QUEUE.pop(key)


def http_send(con, content):
    header = http_response.replace(b"{LENGTH}", str(len(content)).encode())
    con.send(header + content)


def handle_con(con):
    print("accepted connection")
    addr = "{unknown}"
    try:
        packet = con.recv(16384)
        header, packet = packet.split(b"\r\n\r\n", 1)
        header = header.split(b"\r\n", 1)[0]
        if header == b"GET /p HTTP/1.1":
            # ping
            print("ping")
            con.send(http_ping)
            return
        addr = packet[:4]
        packet = packet[4:]
        print("user id:", addr)
        if header == b"GET /r HTTP/1.1":
            # recv
            print("listening connection")
            if addr not in QUEUE.keys():
                QUEUE[addr] = [69, bytearray(), False]
            QUEUE[addr][0] = 15
            QUEUE[addr][2] = False
            con.settimeout(0.1)
            # wait for it to disconnect
            for _ in range(100): # 10s
                try:
                    if QUEUE[addr][1]:
                        print(f"sending {len(QUEUE[addr][1])} bytes to {addr}")
                        if QUEUE[addr][2]:
                            con.send(QUEUE[addr][1])
                        else:
                            QUEUE[addr][2] = True
                            http_send(con, QUEUE[addr][1])
                        QUEUE[addr][1] = bytearray()
                    chunk = con.recv(1024)
                    if chunk == b"":
                        break
                except TimeoutError:
                    pass
                except Exception as e:
                    traceback.print_exception(e)
                    break
            print("listening socket disconnected")
            return
        if header == b"GET /s HTTP/1.1":
            # send
            print("sending connection")
            con.settimeout(1)
            try:
                for _ in range(150): # 15s
                    chunk = con.recv(16384)
                    if chunk == b"":
                        break
                    packet += chunk
            except:
                pass
            print(f"received {len(packet)} bytes")
            for this_id, val in QUEUE.items():
                if addr != this_id:
                    val[1].extend(packet)
            return
    except Exception as e:
        traceback.print_exception(e)
    finally:
        print(f"closing connection {addr}")
        con.shutdown(sock.SHUT_RDWR)
        con.close()


s = sock.socket()
s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
s.bind((IP, PORT))
s.listen()
print(f"server listening on {IP}:{PORT}")

# accept loop
while True:
    con, addr = s.accept()
    Thread(target=handle_con, args=[con]).start()
