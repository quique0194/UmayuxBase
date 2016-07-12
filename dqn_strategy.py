import random
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
    def playing(self):
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
