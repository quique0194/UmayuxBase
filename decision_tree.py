import sys
import time
from umayux_base.strategy import StrategyBase

class DecisionTreeBase(StrategyBase):
    def cur_action(self):
        self.ws.do = ""
        return False

    def choose_play_mode(self):
        super(DecisionTreeBase, self).choose_play_mode()
        self.cur_action()



class DecisionTreeStrategy(DecisionTreeBase):
    # QUESTIONS
    def can_see_ball(self):
        return self.ws.see.ball is not None

    def ball_is_near(self, dist=0.7):
        return self.can_see_ball() and self.ws.see.ball.distance <= dist

    def can_see_opp_goal(self):
        return self.ws.see.goal.r is not None

    # LOW LEVEL ACTIONS
    def ll_do_nothing(self):
        self.ws.do = ""
        return False

    def ll_look_for_opp_goal(self):
        if self.can_see_opp_goal():
            return self.ll_do_nothing()
        self.ws.do = "(turn 40)"
        return True

    def ll_look_for_ball(self):
        if self.can_see_ball():
            return self.ll_do_nothing()        # Action finished
        self.ws.do = "(turn 30)"
        return True

    def ll_kick_off(self):
        if not self.ball_is_near(2):
            return self.ll_do_nothing()
        self.ws.do = "(kick 50 135)"
        return True

    def ll_kick_to_goal(self):
        if not self.ball_is_near():
            return self.ll_do_nothing()
        if not self.can_see_opp_goal():
            return self.ll_do_nothing()
        angle = self.ws.see.goal.r.direction
        self.ws.do = "(kick 100 "+ str(angle) +")"
        return True

    def ll_pass_to_closer_mate(self):
        if not self.ball_is_near():
            return self.ll_do_nothing()
        if len(self.ws.see.mates) == 0:
            return self.ll_do_nothing()
        mate = self.ws.see.mates[0]         # closer mate
        angle = mate.direction
        self.ws.do = "(kick 100 "+ str(angle) +")"
        return True

    def ll_go_to_ball(self):
        if not self.can_see_ball() or self.ball_is_near():
            return False
        if abs(self.ws.see.ball.direction) > 10:
            self.ws.do = "(turn " + str(self.ws.see.ball.direction/2.0) + ")"
        else:
            self.ws.do = "(dash 100)"
        return True


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

    def hl_kick_to_goal(self):
        if self.can_see_ball():
            if self.ball_is_near():
                if self.can_see_opp_goal():
                    self.cur_action = self.ll_kick_to_goal
                else:
                    self.cur_action = self.ll_look_for_opp_goal
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
        self.hl_kick_to_goal()

    def before_kick_off(self, side="l"):
        self.hl_look_for_ball()

    def kick_off(self, side="l"):
        if self.ws.side == side and self.ws.unum == 2:
            self.hl_kick_off()
        else:
            self.hl_look_for_ball()

s = DecisionTreeStrategy()
s.run()
