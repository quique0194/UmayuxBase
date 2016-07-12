from umayux_base.simplified_strategy import SimplifiedStrategy


class DQNStrategy(SimplifiedStrategy):
    def playing(self):
        self.ws.do = "(turn -20)"

    def get_initial_position(self, kick_off_side="l"):
        return -10*self.ws.unum, -10*self.ws.unum

s = DQNStrategy()
s.run()
