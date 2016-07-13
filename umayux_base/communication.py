import time
import threading

from parser import parse
from state import WorldState
from mymath import normalize_angle
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
    opp = None
    mine = None

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
                if key != ws.side:
                    see.goal.opp = Something(i[1], i[2])
                else:
                    see.goal.mine = Something(i[1], i[2])
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

    def msg_to_play_mode(self, msg):
        pm = msg[3]
        if pm == "before_kick_off":
            return pm, None
        elif pm == "play_on":
            return pm, None
        elif pm == "time_over":
            return pm, None
        elif pm == "drop_ball":
            return pm, None
        elif pm == "half_time":
            return pm, None
        elif pm == "time_up_without_a_team":
            return pm, None

        elif pm.startswith("kick_off_"):
            return "kick_off", pm[-1]
        elif pm.startswith("kick_in_"):
            return "kick_in", pm[-1]
        elif pm.startswith("free_kick_"):
            return "free_kick", pm[-1]
        elif pm.startswith("corner_kick_"):
            return "corner_kick", pm[-1]
        elif pm.startswith("goal_kick_"):
            return "goal_kick", pm[-1]
        elif pm.startswith("offside_"):
            return "offside", pm[-1]
        elif pm.startswith("goal_"):
            return "goal", pm[5]
        elif pm.startswith("goalie_catch_ball_"):
            return "goalie_catch_ball", pm[-1]
        elif pm.startswith("back_pass_"):
            return "back_pass", pm[-1]
        elif pm.startswith("catch_fault_"):
            return "catch_fault", pm[-1]
        else:
            print "##### WARNING: play_mode not recognized:", pm
            raise Exception("This should never happen")

    def run(self):
        ws = WorldState()
        while True:
            msg =  parse(ws.recv())
            if msg[0] == "see":
                ws.see_lock.acquire()
                ws.see = self.msg_to_see(msg)
                ws.tic = msg[1]
                pos = triangulate_position(ws.see.flags, ws.position)
                co = calculate_orientation(ws.see.flags, ws.position)
                ws.orientation = co or ws.orientation
                if ws.side == "r":
                    ws.position = [-pos[0], -pos[1]]
                    ws.orientation += 180.0
                else:
                    ws.position = pos
                ws.orientation = normalize_angle(ws.orientation)
                ws.new_state = True
                ws.see_lock.release()
            elif msg[0] == "sense_body":
                ws.see_lock.acquire()
                ws.sense_body = self.msg_to_sense_body(msg)
                ws.new_state = True
                ws.see_lock.release()
            elif msg[0] == "hear":
                if msg[2] == "referee":
                    pm, pms = self.msg_to_play_mode(msg)
                    ws.play_mode = pm
                    ws.play_mode_side = pms or ws.play_mode_side
                elif msg[2] == "coach":
                    say = msg[3]
                    if say[0] == "reward":
                        ws.reward = say[1]
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
                print "############# WARNING (Unknown message type):", msg


class SendActionsThread(threading.Thread):
    def send_action_in_play_mode(self,play_mode):
        return play_mode in (
            "before_kick_off",
            "play_on",
            "kick_off",
            "kick_in",
            "free_kick",
            "corner_kick",
            "goal_kick",
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