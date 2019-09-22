import time
import threading
import random
import numpy as np
from umayux_base.simplified_strategy import SimplifiedStrategy
from mlp import MLP

################################################################################
# CREATE ACTIONS
################################################################################

kick_powers = [1,2,5,10,20,50,100]
# turn_angles = [1,2,5,10,20,45,90]
turn_angles = [30]
turn_angles = list(reversed(map(lambda x:-x, turn_angles))) + turn_angles
# dash_powers = [5,10,20,50,100]
dash_powers = [50]

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

ACTIONS = [""] + dash_actions + turn_actions #+ kick_actions

################################################################################
# CLASS
################################################################################

D = []
# mlp = MLP(111, 200, len(ACTIONS))
mlp = MLP(6, 100, len(ACTIONS))
mlp_hat = mlp.clone()
mlp_lock = threading.Lock()

class DQNStrategy(SimplifiedStrategy):
    prev_state = None
    prev_action = None

    def build_state(self):
        def get_pos_in_ranges(val, ranges):
            for i, v in enumerate(ranges):
                if val <= v:
                    return i-1
            print "################", val, ranges
            raise Exception("This should never happen")

        # angle_ranges = [-45,-20,-10,-5,-2,2,5,10,20,45]
        # distance_ranges = [0.5, 1, 2, 5, 10, 20, 1000]
        angle_ranges = [-45,-10,10,45]
        distance_ranges = [10, 1000]
        frames = np.zeros((len(angle_ranges)-1,len(distance_ranges)-1,2))

        for p in self.ws.see.mates:
            ang_pos = get_pos_in_ranges(p.direction, angle_ranges)
            dist_pos = get_pos_in_ranges(p.distance, distance_ranges)
            frames[ang_pos, dist_pos, 0] = 1
        for p in self.ws.see.opponents:
            ang_pos = get_pos_in_ranges(p.direction, angle_ranges)
            dist_pos = get_pos_in_ranges(p.distance, distance_ranges)
            frames[ang_pos, dist_pos, 0] = -1
        if self.ws.see.ball is not None:
            ang_pos = get_pos_in_ranges(self.ws.see.ball.direction, angle_ranges)
            dist_pos = get_pos_in_ranges(self.ws.see.ball.distance, distance_ranges)
            frames[ang_pos, dist_pos, 1] = 1

        # return [self.ws.position[0]/100.0, self.ws.position[1]/100.0, self.ws.orientation/180.0] + list(frames.reshape(-1))
        return list(frames.reshape(-1))


    prev_see_ball = None
    def get_reward(self):
        ball = self.ws.see.ball
        if ball is None:
            return 0.0
        if ball.distance < 10:
            return 1.0
        return 0.0


    def playing(self):
        global D, mlp, ACTIONS
        state = self.build_state()
        reward = self.get_reward()
        if self.prev_state is not None and self.prev_action is not None:
            D.append((self.prev_state, self.prev_action, state, reward))
        
        if random.random() < 0.3:
            i = random.randint(1, len(ACTIONS)) - 1
        else:
            mlp_lock.acquire()
            qval = mlp.predict(np.array([state]))
            mlp_lock.release()
            # print "QVAL", qval[0]
            i = np.argmax(qval[0])
        self.ws.do = ACTIONS[i]
        self.prev_state = state
        self.prev_action = self.ws.do

    def free_kick(self):
        self.playing()

    def waiting(self):
        self.playing()

    def get_initial_position(self, kick_off_side="l"):
        return -10*self.ws.unum, -10*self.ws.unum

################################################################################
# RUN
################################################################################

def get_batch(dataset, n):
    states_t0, actions, states_t1, rewards = [],[],[],[]
    for t in range(n):
        i = random.randint(0, len(dataset)-1)
        states_t0.append(dataset[i][0])
        actions.append(dataset[i][1])
        states_t1.append(dataset[i][2])
        rewards.append(dataset[i][3])
    return np.array(states_t0), actions, np.array(states_t1), np.array(rewards)


if __name__ == "__main__":
    class DQNThread(threading.Thread):
        def run(self):
            alpha = 1
            while True:
                global D, mlp, ACTIONS, mlp_hat
                for i in range(500):
                    alpha = alpha*0.9999999
                    print "alpha:", alpha
                    # if len(D) > 100:
                    #     D = D[-500:]
                    tam = min(len(D), 10)
                    if tam > 0:
                        # print "#", len(D)
                        states_t0, actions, states_t1, rewards = get_batch(D, tam)
                        mlp_lock.acquire()
                        qval = mlp_hat.predict(states_t1)
                        mlp_lock.release()
                        maxqval = qval.max(axis=1)
                        y = alpha*rewards + (1-alpha)*maxqval
                        actions_idx = map(lambda x: ACTIONS.index(x), actions)
                        mlp_lock.acquire()
                        qval = mlp.predict(states_t0)
                        print "val", qval
                        qval[np.arange(len(qval)), actions_idx] = y
                        mlp.train(states_t0, qval)
                        # print "r", rewards
                        # print "Y", qval
                        mlp_lock.release()
                mlp_hat = mlp.clone()

    dqn_thread = DQNThread()
    dqn_thread.daemon = True
    dqn_thread.start()

    s = DQNStrategy()
    s.run()
