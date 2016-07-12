import time
import sys
import getopt

from parser import parse
from state import WorldState
from communication import ReceiveDataThread, SendActionsThread, UpdateTicThread


class StrategyBase(object):
    ws = WorldState()
    x = -1.0
    y = 0.0

    def get_initial_position(self, kick_off_side="l"):
        return self.x, self.y

    def move_to_initial_position(self, kick_off_side="l"):
        x, y = self.get_initial_position(kick_off_side)
        self.ws.send("(move %f %f)" % (x, y))
        if self.ws.side == "l":
            self.ws.position = x, y
        else:
            self.ws.position = -x, -y
        self.ws.play_mode = "before_kick_off"

    def proc_opts(self):
        opts, args = getopt.getopt(sys.argv[1:],"ht:g",["help", "team=", "goalie"])
        for opt, arg in opts:
            if opt in ("-t", "--team"):
                self.ws.team_name = arg
            elif opt in ("-h", "--help"):
                print "Usage: ./%s -t TeamName" % sys.argv[0]
                sys.exit(0)
            elif opt in ("-g", "--goalie"):
                self.ws.goalie = True

    def init(self):
        self.proc_opts()
        if self.ws.goalie:
            goalie = " (goalie)"
        else:
            goalie = ""
        data = self.ws.init("(init %s (version 15.2)%s)" % (self.ws.team_name, goalie))
        msg = parse(data)
        self.ws.side = msg[1]
        if self.ws.side == "r":
            self.ws.orientation = -180.0
        self.ws.unum = msg[2]
        self.ws.play_mode = msg[3]
        print "Side:", self.ws.side, ", Unum:", self.ws.unum

        self.move_to_initial_position(self.ws.play_mode_side)

    # UTILS
    def change_side(self, side):
        if side == "l":
            return "r"
        elif side == "r":
            return "l"
        else:
            raise Exception("ERROR: Wrong side:", side)

    # PLAY MODES TO OVERWRITE
    def playing(self):
        self.ws.do = "(turn 20)"
        self.ws.turn_neck = 0

    def waiting(self):
        self.ws.do = "(turn 20)"
        self.ws.turn_neck = 0

    def free_kick(self):
        self.ws.do = "(turn 20)"
        self.ws.turn_neck = 0


    # PLAY MODES NOT TO OVERWRITE
    def goal(self, side="l"):
        time.sleep(0.1)
        self.move_to_initial_position(self.change_side(side))



    def choose_play_mode(self):
        playing_modes = (
            "play_on",
        )
        waiting_modes = (
            "before_kick_off",
            "time_over",
            "drop_ball",
            "offside",
            "goalie_catch_ball",
            "back_pass",
            "catch_fault",
        )
        free_kick_modes = (
            "kick_off",
            "kick_in",
            "free_kick",
            "corner_kick",
            "goal_kick",
        )
        if self.ws.play_mode in playing_modes:
            self.playing()
        elif self.ws.play_mode in waiting_modes:
            self.waiting()
        elif self.ws.play_mode in free_kick_modes:
            if self.ws.play_mode_side == self.ws.side:
                self.free_kick()
            else:
                self.waiting()
        elif self.ws.play_mode == "goal":
            self.goal(self.ws.play_mode_side)
        else:
            raise Exception("This should never happen")

    def run_strategy(self):
        while True:
            if self.ws.see is not None:
                self.ws.see_lock.acquire()
                try:
                    if self.ws.new_state:
                        self.choose_play_mode()
                        self.ws.new_state = False
                finally:
                    self.ws.see_lock.release()
                    time.sleep(0.05)

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
        self.run_strategy()