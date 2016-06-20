from umayux_base.strategy import StrategyBase


class MyStrategy(StrategyBase):
    def play_on(self):
        if self.ws.tic % 2 == 0:
            self.ws.do = "(dash 100)"
            self.ws.turn_neck = 80
        else:
            self.ws.do = "(turn 20)"
            self.ws.turn_neck = -80


s = MyStrategy()
s.run()
