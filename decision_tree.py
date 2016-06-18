from umayux_base.strategy import StrategyBase



class DecisionTreeStrategy(StrategyBase):
    cur_action = None

    def make_decision(self):
        # self.cur_action = self.some_function
        raise NotImplementedError

    def strategy(self):
        if self.cur_action is None:
            self.make_decision()
        while not self.cur_action():
            self.make_decision()


class SampleDecisionTreeStrategy(DecisionTreeStrategy):
    # QUESTIONS
    def can_see_ball(self):
        return self.ws.see.ball is not None

    def ball_is_near(self):
        return self.can_see_ball() and self.ws.see.ball.distance <= 0.7

    # ACTIONS
    def look_for_ball(self):
        if self.can_see_ball():
            return False        # Action finished
        self.ws.do = "(turn 20)"
        return True

    def kick(self):
        if not self.ball_is_near():
            return False
        angle = 0
        if self.ws.see.goal.r is not None:
            angle = self.ws.see.goal.r.direction
        self.ws.do = "(kick 100 "+ str(angle) +")"
        return True

    def go_to_ball(self):
        if not self.can_see_ball() or self.ball_is_near():
            return False
        print "stamina", self.ws.sense_body["stamina"]
        if abs(self.ws.see.ball.direction) > 5:
            self.ws.do = "(turn " + str(self.ws.see.ball.direction/4) + ")"
        else:
            self.ws.do = "(dash 100)"
        return True

    # LOGIC
    cur_action = None

    def make_decision(self):
        if self.can_see_ball():
            if self.ball_is_near():
                self.cur_action = self.kick
            else:
                self.cur_action = self.go_to_ball
        else:
            self.cur_action = self.look_for_ball
        print "CUR", self.cur_action.__name__


s = SampleDecisionTreeStrategy()
s.run()
