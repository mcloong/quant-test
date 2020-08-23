#boll 当做出厂线
from strategy_base import StrategyBase
import pandas as pd
from tqsdk import tafunc
from param_defines import TradeDirection

class StrategyBollDaily(StrategyBase):
    def  __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyBollDaily", manager)
        self.TAG = "StrategyBollDaily"
        self.boll_trade_dir = TradeDirection.BUYSELL
        self.mark_bar = 0

        self.debug("runing.......................")
    
    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        if (self.run_flag == False):
            return
        #开仓过滤
        if (self.wait_open() == True):
            return 
        #防止跳空
        if (self.check_open_condition()):
            return

        if (self.boll_top!=0 and self.position>=0 and self.ask_price>=self.boll_top):
            if (self.boll_trade_dir == TradeDirection.BUYONLY
                and self.position > 0):
                self.set_position(0)
                self.debug("平多")
            else:
                self.set_position(-1)
                self.debug("开空")

        elif(self.boll_bottom!=0 and self.position<=0 and self.ask_price<=self.boll_bottom):
            if (self.boll_trade_dir == TradeDirection.SELLONLY
                and self.position > 0):
                self.set_position(0)
                self.debug("平空")
            else:
                self.set_position(1)
                self.debug("开多")

    def on_day_bar(self, dklines):
        self.find_boll_daily(1, dklines)

    def find_boll_daily(self, start_id, dklines):
        '''
        boll=BOLL(dklines, 6, 1.5)
        self.boll_bottom = list(boll["bottom"])[-2]
        self.boll_top = list(boll["top"])[-2]
        '''

        p = 1
        n = 5
        new_df = pd.DataFrame()
        mid = tafunc.ma(dklines["close"], n)
        std = dklines["close"].rolling(n).std()
        new_df["mid"] = mid
        new_df["top"] = mid + p * std
        new_df["bottom"] = mid - p * std

        boll = new_df
        ma_ck = 0
        j = 1
        for i in range(j+1, j+3+1):
            ma_ck += list(boll["mid"])[-i] - list(boll["mid"])[-(i+1)]
        #print(ma_ck)
        if (ma_ck > 0):
            self.boll_top = int(list(boll["mid"])[-(j+1)] + std.iloc[-(j+1)]*1.3)
            self.boll_bottom = int(list(boll["mid"])[-(j+1)] - std.iloc[-(j+1)])
            self.boll_trade_dir = TradeDirection.BUYONLY
            
        elif (ma_ck < 0):
            self.boll_top = int(list(boll["mid"])[-(j+1)] + std.iloc[-(j+1)])
            self.boll_bottom = int(list(boll["mid"])[-(j+1)] - std.iloc[-(j+1)]*1.3)
            self.boll_trade_dir = TradeDirection.SELLONLY
            
        self.debug("boll_top=%d boll_bottom=%d direction=%s"%(self.boll_top, self.boll_bottom, self.boll_trade_dir))


    def check_open_condition(self):
        return True