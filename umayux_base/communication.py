import time
import threading

from parser import parse
from state import WorldState
from position import triangulate_position, calculate_orientation

class Something(object):
    distance = 0
    direction = 0
    def __init__(self, distance, direction):
        self.distance = distance
        self.direction = direction
    def __str__(self):
        return "(Dist: %d, Dir: %d)" % (self.distance, self.direction)
    __repr__ = __str__

class Goals(object):
    r = None
    l = None

class See(object):
    def __init__(self):
        self.ball = None
        self.opponents = []
        self.mates = []
        self.flags = {}
        self.goal = Goals()

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
        ws = WorldState()
        for i in msg[2:]:
            if i[0][0] == "b": # ball
                see.ball = Something(i[1], i[2])
            elif i[0][0] == "g": # goal
                key = i[0][1]
                see.flags[key] = Something(i[1], i[2])
                if key == "r":
                    see.goal.r = Something(i[1], i[2])
                else:
                    see.goal.l = Something(i[1], i[2])
            elif i[0][0] == "p": # player
                if len(i[0]) >= 2 and len(i) >= 3:
                    if i[0][1] == ws.team_name:
                        see.mates.append(Something(i[1], i[2]))
                    else:
                        see.opponents.append(Something(i[1], i[2]))
            elif i[0][0] == "f" and len(i) >= 3: # flag
                i[0] = map(lambda x: str(x), i[0])
                key = "".join(i[0][1:])
                see.flags[key] = Something(i[1], i[2])
        return see

    def run(self):
        ws = WorldState()
        while True:
            msg =  parse(ws.recv())
            if msg[0] == "see":
                ws.see = self.msg_to_see(msg)
                ws.tic = msg[1]
                ws.position = triangulate_position(ws.see.flags, ws.position)
                ws.orientation = calculate_orientation(ws.see.flags, ws.position) or ws.orientation
            elif msg[0] == "sense_body":
                ws.sense_body = self.msg_to_sense_body(msg)
            elif msg[0] == "hear":
                if len(msg) >= 4 and msg[2] == "referee":
                    ws.play_mode = msg[3]
            elif msg[0] == "warning":
                print "################ WARNING:", msg[1]
            elif msg[0] == "player_type":
                pass
            elif msg[0] == "player_param":
                pass
            elif msg[0] == "server_param":
                pass
            elif msg[0] == "change_player_type":
                pass
            else:
                print "$$$$$$$$$$$$$$$$ Unknown message type:", msg


class SendActionsThread(threading.Thread):
    def send_action_in_play_mode(self,play_mode):
        return play_mode in (
            "before_kick_off",
            "play_on",
            "kick_off_l",
            "kick_off_r",
            "kick_in_l",
            "kick_in_r",
            "free_kick_l",
            "free_kick_r",
            "corner_kick_l",
            "corner_kick_r",
            "goal_kick_l",
            "goal_kick_r",
        )
    def run(self):
        ws = WorldState()
        while True:
            if self.send_action_in_play_mode(ws.play_mode):
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