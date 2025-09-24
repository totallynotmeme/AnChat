# /hosting/server.py

import socket as sock
from threading import Thread
from time import sleep

IP = "127.0.0.1"
PORT = 65333

PACKET_QUEUE = {}
PACKET_IDS = {}
CONNECTIONS = {}

def threaded(func):
    Thread(target=func).start()

#print = lambda *a, **kwa: 0 # uncomment to suppress console output


@threaded
def server_loop():
    while True:
        sleep(0.1)
        if len(PACKET_IDS) == 0:
            continue
        
        chosen = min(PACKET_IDS.keys())
        current_id = PACKET_IDS[chosen]
        sleep(0.1)
        
        while current_id != PACKET_IDS[chosen]:
            current_id = PACKET_IDS[chosen]
            sleep(0.1)
        
        PACKET_IDS.pop(chosen)
        packet = PACKET_QUEUE.pop(chosen)
        
        for usr_id, con_obj in CONNECTIONS.items():
            if usr_id != chosen: # don't send to sender
                con_obj.send(packet)


def handle_con(con, user_id):
    print(f"establishing connection of #{user_id} with {con=}")
    
    # join_packet = con.recv(16384)
    # con.send(b"\x00\x00\x00\x00")
    # 
    # leave_packet = con.recv(16384)
    # con.send(b"\x00\x00\x00\x00")
    # 
    CONNECTIONS[user_id] = con
    # for usr_id, con_obj in CONNECTIONS.items():
    #     con_obj.send(join_packet)
    
    print(f"accepted connection with #{user_id}")
    try:
        while True:
            packet = con.recv(16384)
            print(f"#{user_id}: {packet}")
            if packet == b"":
                break
            PACKET_QUEUE[user_id] = PACKET_QUEUE.get(user_id, b"") + packet
            PACKET_IDS[user_id] = PACKET_IDS.get(user_id, 0) + 1
    except Exception as e:
        print(f"#{user_id} errored: {e}")
    finally:
        print(f"disconnecting #{user_id} with {con=}")
        CONNECTIONS.pop(user_id)
        # for usr_id, con_obj in CONNECTIONS.items():
        #     con_obj.send(leave_packet)


s = sock.socket()
s.bind((IP, PORT))
s.listen()
print(f"server listening on {IP}:{PORT}")

# accept loop
while True:
    con, addr = s.accept()
    user_id = max(CONNECTIONS.keys() or (0,)) + 1
    Thread(target=handle_con, args=[con, user_id]).start()
