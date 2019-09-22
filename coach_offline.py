import sys
import socket
import threading
import time
import random
from umayux_base.parser import parse
from umayux_base.mymath import dist

INIT_SERVER = ("127.0.0.1", 6001)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


sock.sendto("(init (version 15.2))"+"\0", INIT_SERVER)
data, addr = sock.recvfrom(10000)
SERVER = addr


def send(msg):
    sock.sendto(msg+"\0", SERVER)


send("(eye on)")
send("(move (ball) 0 0)")
send("(move (player UmayuxBase 1) -7 -7)")
send("(change_mode play_on)")

player = (-7,-7)
ball = (0,0)

class ReceiveMessagesThread(threading.Thread):
    def run(self):
        global SERVER, sock
        global ball, player
        while True:
            data, addr = sock.recvfrom(10000)
            data = parse(data)
            if data[0] == "player_type":
                pass
            elif data[0] == "player_param":
                pass
            elif data[0] == "server_param":
                pass
            elif data[0] == "see_global":
                for obj in data[2:]:
                    if obj[0][0] == "b":
                        ball = (obj[1], obj[2])
                    elif obj[0][0] == "p":
                        player = (obj[1], obj[2])

                if dist(player, ball) < 5:
                    send("(say (reward 1 1.0))")
                    send("(move (player UmayuxBase 1) %d %d)" % (random.uniform(-7,7), random.uniform(-7,7)))
                elif dist(player, ball) > 15:
                    send("(say (reward 1 -1.0))")
                    send("(move (player UmayuxBase 1) %d %d)" % (random.uniform(-7,7), random.uniform(-7,7)))
            else:
                print "received:", data



receive_messages_thread = ReceiveMessagesThread()
receive_messages_thread.daemon = True
receive_messages_thread.start()


while True:
    command = raw_input(">>> ")
    send(command)