'''
做多
用于开市前，行情比较明显的涨跌
5分钟之内开仓
考虑开始前运行和中途加载
'''
from datetime import datetime
import time
from strategy_base import StrategyBase
import tool_utils
import pplib

class KillerS(StrategyBase):
    #level: 3 no delay, 2 wait for 回调，1 wait for 确认
    #连续三次
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "KillerS", manager)
        self.MAX_EARN = 30
        self.level = 3

        self.mark_start_bar = 0
        self.done_flag = False

        print("........[KillerS] running........")

    def set_level(self, level):
        self.level = level

    def on_bar(self, klines):
        if (self.run_flag == False):
            return
        if (self.mark_start_bar == 0):
            self.mark_start_bar = klines.iloc[-1].id
        StrategyBase.on_bar(self, klines)
        #self.cur_bar = self.get_current_minute_bar()

        if (self.position == 0 and self.done_flag == False):
            if (self.level == 1):
                self.level_1(klines)
            elif(self.level == 2):
                self.level_2(klines)
            elif(self.level == 3):
                self.level_3(klines)
        
        if (self.position != 0):
            #出场-时间、空间

            self.done_flag = True
            cur_bar = self.get_current_minute_bar()
            if ((cur_bar-self.entry_bar>90)):#不用替换_fix
                l_checksum = pplib.get_checksum(klines, 25, 2)
                if (abs(l_checksum) < 5):
                    self.set_position(0)
            if (self.position != 0):
                atr_day = self.indictor.get_atr_daily()
                if (atr_day is None):
                    atr_day = 45
                else:
                    atr_day = atr_day - 10
                
                if (self.entry_price - self.ask_price > atr_day):
                    self.debug("空止盈")
                    self.set_position(0)
                elif(self.ask_price-self.entry_price > 10):
                    avg_p = pplib.get_average(klines, 12)
                    if (avg_p-self.entry_price > 20):
                        self.debug("空止损")
                        self.set_position(0)

    def level_1(self, klines):
        open_wait = 5
        open_end = 10
        open_out = 15
        #max_diff = 15
        #monitor_bar = 20
        wait_price1 = 11
        wait_price2 = 8

        self.make_level(klines, open_wait, open_end, open_out, wait_price1, wait_price2)

    def level_2(self, klines):
        open_wait = 10
        open_end = 25
        open_out = 40
        #max_diff = 15
        #monitor_bar = 20
        wait_price1 = 20
        wait_price2 = 10

        self.make_level(klines, open_wait, open_end, open_out, wait_price1, wait_price2)

    def level_3(self, klines):
        open_wait = 20
        open_end = 40
        open_out = 60
        #max_diff = 15
        #monitor_bar = 20
        wait_price1 = 25
        wait_price2 = 15

        self.make_level(klines, open_wait, open_end, open_out, wait_price1, wait_price2)

    def make_level(self, klines, open_wait, open_end, open_out, wait_price1, wait_price2):
        if (self.position <= -1):
            return
        '''
        open_wait = 10
        open_end = 30
        open_out = 50
        #monitor_bar = 20
        #wait_price1 = 10
        wait_price2 = 20
        '''

        #lt = self.get_real_time()
        #start_time = tool_utils.datetime_to_localtime(self.mark_start_time)
        min_passed = self.cur_bar_id - self.mark_start_bar
        open_inday = self.get_open_price()
        self.debug("min_passed=%d"%(min_passed))
        # 开仓时间
        if (min_passed > open_wait and min_passed < open_end):
            hh = pplib.get_hest_in_range(klines, 1, open_wait)
            if (hh - open_inday > wait_price1):
                self.set_position(1)
        elif (min_passed > open_end and min_passed < open_out):
            bars = open_end - open_wait
            bars = int(bars/2)
            if (bars < 6):
                bars = 6
            c_sum = pplib.get_checksum(klines, bars, 1)
            hh = pplib.get_hest_in_range(klines, 1, self.cur_bar)
            if (abs(c_sum) < 6 and hh-open_inday> wait_price2):
                self.set_position(-1)
        elif (min_passed > open_out and min_passed < open_out + 120):
            c_sum = pplib.get_checksum(klines, int(open_out/2), 1)
            if (abs(c_sum) < 5):
                self.set_position(-1)