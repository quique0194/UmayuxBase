import time
import threading

from utils import print_msg
from parser import parse
from state import WorldState

class Something(object):
    distance = 0
    direction = 0
    def __init__(self, distance, direction):
        self.distance = distance
        self.direction = direction

class Goals(object):
    r = None
    l = None

class See(object):
    ball = None
    goal = Goals()

class ReceiveDataThread(threading.Thread):
    def msg_to_sense_body(self, msg):
        return {
            "view_mode": [msg[2][1], msg[2][2]],
            "stamina": [msg[3][1], msg[3][2]],
            "speed": msg[4][1],
            "kick": msg[5][1],
            "dash": msg[6][1],
            "turn": msg[7][1],
            "say": msg[8][1]
        }

    def msg_to_see(self, msg):
        see = See()
        for i in msg[2:]:
            if i[0][0] == "ball":
                see.ball = Something(i[1], i[2])
            elif i[0][0] == "goal":
                if i[0][1] == "r":
                    see.goal.r = Something(i[1], i[2])
                else:
                    see.goal.l = Something(i[1], i[2])
        return see

    def run(self):
        while True:
            ws = WorldState()
            msg =  parse(ws.recv())
            # print_msg(msg)
            if msg[0] == "see":
                ws.see = self.msg_to_see(msg)
                ws.tic = msg[1]
            elif msg[0] == "sense_body":
                ws.sense_body = self.msg_to_sense_body(msg)
            elif msg[0] == "hear":
                if len(msg) >= 4 and msg[2] == "referee":
                    ws.play_mode = msg[3]
            else:
                print_msg(msg)


class SendActionsThread(threading.Thread):
    def run(self):
        ws = WorldState()
        while True:
            if ws.play_mode == "play_on" or ws.play_mode.startswith("kick_off"):
                if ws.do:
                    ws.send(ws.do)
                ws.send("(turn_neck %i)" % ws.turn_neck)
                time.sleep(0.1)

class UpdateTicThread(threading.Thread):
    def run(self):
        ws = WorldState()
        while True:
            if ws.play_mode == "play_on":
                ws.tic += 1
                time.sleep(0.1)