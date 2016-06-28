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
    def send(self, msg):
        self.sock.sendto(msg, self.server)
    def recv(self):
        data, addr = self.sock.recvfrom(1024)
        return data

    # Player state
    team_name = "UmayuxBase"
    tic = 0
    side = ""
    unum = 0
    play_mode = "" #"before_kick_off"
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

    # Action to do next
    do = "" # "(turn 50)"
    turn_neck = 0