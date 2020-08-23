# 根据价格
from strategy_base import StrategyBase
from param_defines import TradeDirection

class KillerPriceDirect(StrategyBase):
    def __init__(self, symbol,manager):
        StrategyBase.__init__(self, symbol, "KillerPriceDirect",manager)
        
        self.hh = 0
        self.ll = 0
        self.TAG = "KillerPriceDirect"

        self.MAX_LOSS = 20

        print(".....[%s] running......."%(self.TAG))

    def set_hh(self, hh):
        self.hh = hh
        self.debug("self.hh=%d"%(self.hh))

    def set_ll(self, ll):
        self.ll = ll
        self.debug("self.ll=%d"%(self.ll))

    def run(self, klines, bid_price, ask_price, avg_price):
        pass

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)

    def on_tick(self, serial):
        StrategyBase.on_tick(self, serial)
        if (self.run_flag == False):
            return
        
        if (self.hh ==0 or self.ll==0):
            return

        if (self.ask_price <=self.ll and self.position != 1):
            self.set_position(1)
        
        if (self.bid_price>=self.hh and self.position != -1):
            self.set_position(-1)
        
        