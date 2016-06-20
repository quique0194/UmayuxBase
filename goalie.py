from umayux_base.strategy import StrategyBase


class MyStrategy(StrategyBase):
    x = -50
    y = 0

    def kick_off(self):
        pass

    def goal(self):
        pass

    def goal_kick(self):
        pass

    def play_on(self):
        pass

s = MyStrategy()
s.run()
