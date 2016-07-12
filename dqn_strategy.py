import random
import numpy as np
from umayux_base.simplified_strategy import SimplifiedStrategy

################################################################################
# CREATE ACTIONS
################################################################################

kick_powers = [1,2,5,10,20,50,100]
turn_angles = [1,2,5,10,20,45,90]
turn_angles = list(reversed(map(lambda x:-x, turn_angles))) + turn_angles
dash_powers = [5,10,20,50,100]

dash_actions = []
turn_actions = []
kick_actions = []

for i in dash_powers:
    dash_actions.append("(dash %d)" % i)
for i in turn_angles:
    turn_actions.append("(turn %d)" % i)
for k in kick_powers:
    for a in turn_angles:
        kick_actions.append("(kick %d %d)" % (k, a))

ACTIONS = dash_actions + turn_actions + kick_actions

################################################################################
# CLASS
################################################################################


class DQNStrategy(SimplifiedStrategy):
    D = []
    
    def build_state(self):
        def get_pos_in_ranges(val, ranges):
            for i, v in enumerate(ranges):
                if val < v:
                    return i-1
            raise Exception("This should never happen")

        frames = np.zeros((3,3,2))
        for p in self.ws.see.mates:
            ang_pos = get_pos_in_ranges(p.direction, [-45,-5,5,45])
            dist_pos = get_pos_in_ranges(p.distance, [0,1,10,1000])
            frames[ang_pos, dist_pos, 0] = 1
        for p in self.ws.see.opponents:
            ang_pos = get_pos_in_ranges(p.direction, [-45,-5,5,45])
            dist_pos = get_pos_in_ranges(p.distance, [0,1,10,1000])
            frames[ang_pos, dist_pos, 0] = -1
        if self.ws.see.ball is not None:
            ang_pos = get_pos_in_ranges(self.ws.see.ball.direction, [-45,-5,5,45])
            dist_pos = get_pos_in_ranges(self.ws.see.ball.distance, [0,1,10,1000])
            frames[ang_pos, dist_pos, 1] = 1

        return self.ws.position + [self.ws.orientation] + list(frames.reshape(-1))

    def playing(self):
        if self.ws.unum == 1:
            print self.build_state()
        i = random.randint(1, len(ACTIONS)) - 1
        self.ws.do = ACTIONS[i]

    def free_kick(self):
        self.playing()

    def waiting(self):
        self.playing()

    def get_initial_position(self, kick_off_side="l"):
        return -10*self.ws.unum, -10*self.ws.unum

################################################################################
# RUN
################################################################################
if __name__ == "__main__":
    s = DQNStrategy()
    s.run()
