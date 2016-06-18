import time
import sys
import getopt

from parser import parse
from state import WorldState
from communication import ReceiveDataThread, SendActionsThread, UpdateTicThread


class StrategyBase(object):
    ws = WorldState()
    x = 20.0
    y = 0.0

    def get_initial_position(self):
        return self.x, self.y

    def move_to_initial_position(self):
        x, y = self.get_initial_position()
        if self.ws.side == "l":
            x = -x
        self.ws.send("(move %f %f)" % (x, y))

    def select_team_name(self):
        opts, args = getopt.getopt(sys.argv[1:],"ht:",["help", "team="])
        for opt, arg in opts:
            if opt in ("-t", "--team"):
                self.ws.team_name = arg
            elif opt in ("-h", "--help"):
                print "Usage: ./%s -t TeamName" % sys.argv[0]
                sys.exit(0)

    def init(self):
        self.select_team_name()

        self.ws.send("(init %s)" % self.ws.team_name)
        msg =  parse(self.ws.recv())
        self.ws.side = msg[1]
        self.ws.unum = msg[2]
        self.ws.play_mode = msg[3]
        print "Side:", self.ws.side, ", Unum:", self.ws.unum

        self.move_to_initial_position()

    def strategy(self):
        self.ws = WorldState()
        self.ws.do = "(turn 50)"

    def run(self):
        # INIT
        self.init()

        # INIT THREADS
        receive_data_thread = ReceiveDataThread()
        receive_data_thread.daemon = True
        receive_data_thread.start()
        send_actions_thread = SendActionsThread()
        send_actions_thread.daemon = True
        send_actions_thread.start()
        update_tic_thread = UpdateTicThread()
        update_tic_thread.daemon = True
        update_tic_thread.start()

        # STRATEGY
        while self.ws.see is None:
            pass

        while True:
            self.strategy()
            time.sleep(0.05)