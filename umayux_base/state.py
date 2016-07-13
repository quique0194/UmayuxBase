import threading
import socket


def singleton(cls):
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls


@singleton
class WorldState(object):
    # Comunication state
    server = ("127.0.0.1", 6000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def init(self, msg):
        self.sock.sendto(msg+"\0", self.server)
        data, addr = self.sock.recvfrom(10000)
        self.server = addr
        return data
    def send(self, msg):
        self.sock.sendto(msg+"\0", self.server)
    def recv(self):
        data, addr = self.sock.recvfrom(10000)
        return data

    # Player state
    team_name = "UmayuxBase"
    tic = 0
    side = ""
    unum = 0
    goalie = False
    play_mode = "" # "before_kick_off"
    play_mode_side = "l" # left is first to kick off
    see_lock = threading.Lock()
    see = None      # See object
    sense_body = {
        "view_mode": ["high", "normal"],
        "stamina": [7285, 1],
        "speed": 0,
        "kick": 0,
        "dash": 0,
        "turn": 0,
        "say": 0
    }
    reward = 0.0

    position = None # [0.0, 0.0]
    orientation = 0.0


    opp_goal = [52.5, 0.0]
    my_goal = [-52.5, 0.0]

    # Action to do next
    do = "" # "(turn 50)"
    turn_neck = 0
