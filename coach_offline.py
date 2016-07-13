import sys
import socket
import threading
import time
from umayux_base.parser import parse

INIT_SERVER = ("127.0.0.1", 6001)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


sock.sendto("(init (version 15.2))"+"\0", INIT_SERVER)
data, addr = sock.recvfrom(10000)
SERVER = addr

class ReceiveMessagesThread(threading.Thread):
    def run(self):
        global SERVER, sock
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
                pass
            else:
                print "received:", data



receive_messages_thread = ReceiveMessagesThread()
receive_messages_thread.daemon = True
receive_messages_thread.start()


def send(msg):
    sock.sendto(msg+"\0", SERVER)


send("(change_mode play_on)")
send("(move (ball) 10 10)")
send("(move (player UmayuxBase 1) 0 0)")



while True:
    command = raw_input(">>> ")
    send(command)