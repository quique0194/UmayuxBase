from umayux_base.strategy import StrategyBase


class MyStrategy(StrategyBase):
    def get_initial_position(self):
        return 1, 0

    def strategy(self):
        self.ws.do = "(kick 100 0)"
        print self.ws.tic

s = MyStrategy()
s.run()
