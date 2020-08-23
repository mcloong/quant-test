class KClock(object):
    def __init__(self):
        self.bar_inday = 0
        self.bar = 0 #kline中的值
        self.back_bar = 0
        self.entry_bar = 0
        self.exit_bar = 0
        self.day_bar = 0
        self.lt = None
        
    def update_localtime(self, tm):
        self.lt = tm