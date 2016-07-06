import sys
import time
from umayux_base.strategy import StrategyBase
from umayux_base.position import angle_to
from umayux_base.mymath import angle_to, normalize_angle

class DecisionTreeBase(StrategyBase):
    def ll_do_nothing(self):
        self.ws.do = ""

    def cur_action(self):
        self.ws.do = ""

    def choose_play_mode(self):
        super(DecisionTreeBase, self).choose_play_mode()
        if self.ws.play_mode == "goal":
            self.cur_action = self.ll_do_nothing
        else:
            self.cur_action()



class DecisionTreeStrategy(DecisionTreeBase):
    # QUESTIONS
    def can_see_ball(self):
        return self.ws.see.ball is not None

    def ball_is_near(self, dist=0.7):
        return self.can_see_ball() and self.ws.see.ball.distance <= dist

    # LOW LEVEL ACTIONS
    def ll_look_for_ball(self):
        if self.can_see_ball():
            self.ll_do_nothing()
        else:
            self.ws.do = "(turn 30)"

    def ll_point_to_opp_goal(self):
        if self.ws.see.goal.opp is None:
            self.ws.do = "(turn 30)"
        else:
            if self.ws.see.goal.opp.direction > 5:
                print "Dir to goal", self.ws.see.goal.opp.direction
                self.ws.do = "(turn %d)" % (self.ws.see.goal.opp.direction/2.0,)
            else:
                self.ll_do_nothing()

    def ll_kick_off(self):
        self.ws.do = "(kick 40 135)"

    def ll_kick_to_goal(self):
        if self.ws.see.goal.opp is not None:
            angle = self.ws.see.goal.opp.direction
            power = 100
        else:
            angle = -angle_to(self.ws.position, self.ws.opp_goal) - self.ws.orientation
            power = 100
        angle = normalize_angle(angle)
        self.ws.do = "(kick %d %d)" % (power, angle)

    def ll_pass_to_closer_mate(self):
        mate = self.ws.see.mates[0]
        angle = mate.direction
        self.ws.do = "(kick 100 %d)" % angle

    def ll_go_to_ball(self):
        if abs(self.ws.see.ball.direction) > 5:
            self.ws.do = "(turn " + str(self.ws.see.ball.direction/2.0) + ")"
        else:
            self.ws.do = "(dash 100)"


    # HIGH LEVEL ACTIONS
    # Set cur_action
    def hl_pass_to_closer_mate(self):
        if self.can_see_ball():
            if self.ball_is_near():
                self.cur_action = self.ll_kick
            else:
                self.cur_action = self.ll_go_to_ball
        else:
            self.cur_action = self.ll_look_for_ball

    def hl_kick_off(self):
        self.cur_action = self.ll_kick_off

    def hl_look_for_ball(self):
        self.cur_action = self.ll_look_for_ball

    def hl_point_to_opp_goal(self):
        self.cur_action = self.ll_point_to_opp_goal

    def hl_kick_to_goal(self):
        if self.can_see_ball():
            if self.ball_is_near():
                self.cur_action = self.ll_kick_to_goal
            else:
                self.cur_action = self.ll_go_to_ball
        else:
            self.cur_action = self.ll_look_for_ball

    # POSITION
    def get_initial_position(self, kick_off_side="l"):
        if self.ws.unum == 1:
            return -50, 0
        elif self.ws.unum == 2:
            if self.ws.side == kick_off_side:
                return -0.1, 0
            else:
                return -10, 5
        elif self.ws.unum == 3:
            if self.ws.side == kick_off_side:
                return -7, 7
            else:
                return -10, -5
        else:
            print "Wrong player number"
            sys.exit(0)

    # PLAY_MODES
    def play_on(self):
        if self.ws.side == "r" and self.ws.unum == 3:
            self.hl_kick_to_goal()
        else:
            self.hl_look_for_ball()

    def before_kick_off(self, side="l"):
        if self.ws.side == side and self.ws.unum == 2:
            self.hl_point_to_opp_goal()
        else:
            self.hl_look_for_ball()

    def kick_off(self, side="l"):
        if self.ws.side == side and self.ws.unum == 2:
            self.hl_kick_off()
        else:
            self.hl_look_for_ball()

s = DecisionTreeStrategy()
s.run()
