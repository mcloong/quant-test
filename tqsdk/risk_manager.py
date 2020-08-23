#监控日内突发行情，通过特殊的bar
from tool_utils import get_minute

class RiskManager(object):
    def __init__(self):
        self.name = "RiskManager"
        self.update_interval = 5

    def time_to_update(self):
        if (get_minute()%self.update_interval == 0):
            return True
        else:
            return False

    def run(self, klines):
        pass