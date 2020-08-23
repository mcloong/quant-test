#追风
#趋势明确时，快进快出
from param_defines import TradeDirection
from pplib import get_avg_price ,get_checksum
from datetime import datetime
import time
from param_defines import StrategyKpi,WalkPath
from strategy_base import StrategyBase
import pplib
#
class KillerRush(StrategyBase):
    def  __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "KillerRush", manager)
        self.TAG = "KillerRush"
        self.MAX_EARN = 45
        self.MAX_TRADE_TERM =65 #最长交易时间
        self.trade_dir = TradeDirection.BUYSELL

        self.hh = 0
        self.ll = 0

        self.inited = False
        self.start_bar_id = 0

        self.step = 0
        print("........[%s] running..........."%(self.TAG))

    def init(self):
        if (self.inited == True):
            return
        
        if (self.start_bar_id < 2):
            lt = time.localtime(time.time())
            if ((lt.tm_hour == 9 and lt.tm_min<=1) or
                (lt.tm_hour == 21 and lt.tm_min<=1)):
                self.inited = True
                self.start_bar_id = self.cur_bar_id
        else:
            if (self.ask_price != 0):
                self.inited = True
                self.mark_price = self.ask_price
                self.start_bar_id = self.cur_bar_id

    def set_hh(self, hh):
        self.hh = hh

    def set_ll(self, ll):
        self.ll = ll

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        #if (self.run_flag == False or self.hh <= 0 or self.ll <= 0):
        if (self.run_flag == False):
            return
        #lt = time.localtime(time.time())
        self.cur_bar = self.get_current_minute_bar()
        lt = self.get_real_time()
        tmp_position = self.position
        if (self.inited == False):
            #init
            self.init()
        if (self.inited == False):
            self.debug("not init")
            return
        if (self.trade_dir != TradeDirection.BUYONLY and 
            self.trade_dir != TradeDirection.SELLONLY):
            return
        #===============make==================#
        if (self.position == 0 and self.step == 0):
            if (self.trade_dir == TradeDirection.BUYONLY):
                tmp_position = 1
            elif (self.trade_dir == TradeDirection.SELLONLY):
                tmp_position = -1
        if (self.position == 0 and self.step == 1):
            if (self.trade_dir == TradeDirection.BUYONLY):
                if (self.entry_price-self.ask_price > 10):
                    tmp_position = 1
                else:
                    ck_sum10 = pplib.get_checksum(klines, 11, 1)
                    ma3 = pplib.get_average(klines, 4)
                    hh_20 = pplib.get_hest_in_range(klines, 1, 31)
                    if (abs(ck_sum10)<5 and hh_20-ma3>15):
                        tmp_position = 1

            elif (self.trade_dir == TradeDirection.SELLONLY):
                if (self.entry_price-self.ask_price > 10):
                    tmp_position = -1
                else:
                    ck_sum10 = pplib.get_checksum(klines, 11, 1)
                    ma3 = pplib.get_average(klines, 4)
                    ll_20 = pplib.get_lest_in_range(klines, 1, 31)
                    if (abs(ck_sum10)<5 and ma3-hh_20>15):
                        tmp_position = -1

        elif (self.position == 0 and self.step == 2):
            pass

        #==================exit===========================#
        if (self.position == 1):
            if (self.cur_bar - self.entry_bar > 5 and self.bid_price-self.entry_price >= self.MAX_EARN):
                tmp_position = 0
            '''
            my_avg_price = pplib.get_avg_price(klines, 10)
            if (self.entry_bar > 10 and my_avg_price < self.avg_price):
                tmp_position = 0
            '''
            if (self.hh != 0 and self.ask_price >= self.hh):
                tmp_position = 0
                self.hh += 20

        if (self.position == -1):
            if (self.cur_bar - self.entry_bar > 5 and self.entry_price-self.bid_price >= self.MAX_EARN):# 达到最大profit
                tmp_position = 0
            '''    
            my_avg_price = pplib.get_avg_price(klines, 10)
            if (self.entry_bar > 10 and my_avg_price > self.avg_price):
                tmp_position = 0
            '''
            if (self.ll != 0 and self.ask_price <= self.ll):
                tmp_position = 0
                self.ll -= 20

        if (tmp_position != self.position):
            self.set_position(tmp_position)

        #===================check==========================#
        if (self.cur_bar_id - self.start_bar_id > 10): #// 不符合rush条件
            my_avg_price = pplib.get_avg_price(klines, 10)
            if (self.trade_dir == TradeDirection.SELLONLY and 
                my_avg_price > self.mark_price):
                self.stop()
            if (self.trade_dir == TradeDirection.BUYONLY and 
                my_avg_price < self.mark_price):
                self.stop()
        
        if (self.position != 0):
            self.monitor_position(klines)

    def monitor_position(self, klines):
        if (self.position!=0 and (self.cur_bar-self.entry_bar > 50)):
            hold_term = 50
            if (self.step == 0):
                hold_term = 20
            elif (self.step == 1):
                hold_term = 30
            hold_term = int(hold_term/2) + 5
            ck_sum_10 = pplib.get_checksum(klines, hold_term, 1)
            if (abs(ck_sum_10)<5):
                self.set_position(0)
        if (self.cur_bar_id - self.start_bar_id > self.MAX_TRADE_TERM):#用的是klines中的id
            self.debug("到达最大操作时间，停止。。。。")
            self.stop()



    def timer_task(self):
        pass

    def breakup_mode(self):
        pass