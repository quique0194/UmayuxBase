from umayux_base.strategy import StrategyBase

class MyStrategy(StrategyBase):
    def get_initial_position(self, kick_off_side="l"):
        if self.ws.side == kick_off_side:
            return -1, 0
        else:
            return -15, 0

s = MyStrategy()
s.run()
