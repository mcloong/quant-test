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

class StrategyThreeStepLDaliy(StrategyBase):
    #level: 3 no delay, 2 wait for 回调，1 wait for 确认
    #连续三次
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyThreeStepLDaliy", manager)
        self.MAX_EARN = 50
        self.level = 1

        self.mark_start_id = 0

        self.init_flag = False
        self.done_flag = False
        
        self.last_red_or_green = 0
        self.continue_flag = False
        self.low_range_flag = False
        self.hh_3day = 0
        self.ll_3day = 0
        self.skip_flag = False
        print("........[StrategyThreeStepLDaliy] running........")

    def on_day_bar(self, dklines):
        start_id = 2
        #low range and break
        height_3 = pplib.get_height_in_range(dklines, start_id, start_id+4)
        open_close_3 = 0
        oc_sum = 0
        for i in range(start_id, start_id+2):
            oc_sum += dklines.iloc[-i].open - dklines.iloc[-i].close
        open_close_3 = int(oc_sum/2)
        if (height_3 < 60 or abs(open_close_3) < 20):
            self.low_range_flag = True

        self.hh_3day = pplib.get_hest_in_range2(dklines, start_id, start_id+3)
        self.ll_3day = pplib.get_lest_in_range2(dklines, start_id, start_id+3)

        hh_10day_bar = pplib.get_hest_in_range2(dklines, 2, 2+4)
        if (hh_10day_bar >=2): #2 是昨天，1 是今
            self.continue_flag = False
        elif (hh_10day_bar == 2):
            self.continue_flag = True

        if (dklines.iloc[-start_id].open > dklines.iloc[-start_id].open):
            self.last_red_or_green = -1
        else:
            self.last_red_or_green = 1

        self.lastday_close = dklines.iloc[-start_id].close
        self.lastday_high = dklines.iloc[-start_id].high

        if (dklines.iloc[-1].open - dklines.iloc[-2].close > 15):
            self.skip_flag = True

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        if (self.run_flag == False or self.skip_flag == True):
            return
        tmp_position = self.position

        lt = self.get_real_time()
        
        self.cur_bar = self.get_current_minute_bar()
        ma15 = pplib.get_avg_price(klines,18)
        if (self.cur_bar < 10):
            return

        if (self.low_range_flag == True and ma15>self.hh_3day and self.position<=0):
            tmp_position = 1
        elif (self.low_range_flag == True and ma15<self.ll_3day and self.position>=0):
            tmp_position = 0
        if (self.continue_flag == False and self.position <=0):
            if (self.last_red_or_green == -1):
                if (self.lastday_close - self.ask_price > 20):
                    tmp_position = 1
                elif (self.lastday_close - self.ask_price > 15 and self.cur_bar > 30):
                    tmp_position = 1
                elif (self.cur_bar > 60):
                    downs = pplib.get_count_of_less(klines, 60)
                    if (downs > 50):
                        tmp_position = 1
        elif (self.continue_flag == True):
            if (self.lastday_close - self.ask_price > 20):
                tmp_position = 1
            elif (self.lastday_close - self.ask_price > 15 and self.cur_bar > 30):
                tmp_position = 1
            elif (self.cur_bar > 60):
                downs = pplib.get_count_of_less(klines, 60)
                if (downs > 30):
                    tmp_position = 1
        if (self.position > 0 and self.ask_price >= self.lastday_high+15):
            tmp_position = 0
        if (self.position > 0 and self.entry_price - self.ask_price > 41):
            tmp_position = 0
        elif (self.position > 0 and self.ask_price - self.entry_price > 25):
            tmp_position = 0

        if (tmp_position != self.position):
            if (self.check_order(10)):
                self.set_position(tmp_position)
