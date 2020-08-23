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

class KillerL(StrategyBase):
    #level: 3 no delay, 2 wait for 回调，1 wait for 确认
    #连续三次
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "KillerL", manager)
        self.MAX_EARN = 50
        self.level = 1

        self.mark_start_id = 0

        self.init_flag = False
        self.done_flag = False

        print("........[KillerL] running........")

    def set_level(self, level):
        self.level = level
        self.debug("level=%d"%(self.level))

    def on_bar(self, klines):
        if (self.run_flag == False):
            return
        if (self.init_flag == False):
            self.mark_start_id = klines.iloc[-1].id
            self.init_flag = True

        StrategyBase.on_bar(self, klines)
        self.cur_bar = self.get_current_minute_bar()

        if (self.position == 0 and self.done_flag == False):
            if (self.level == 1):
                self.level_1(klines)
            elif(self.level == 2):
                self.level_2(klines)
            elif(self.level == 3):
                self.level_3(klines)
        
        '''
        lt = time.localtime(time.time())
        # 开仓时间
        if (lt.tm_hour == 9 and lt.tm_min < 30 or
            lt.tm_hour == 21 and lt.tm_min < 30):
            if(self.position == 0):
                self.open_time(klines, ask_price, bid_price)
            if (self.position != 0):
                hest_inday = self.indictor.get_hest_inday()
                lest_inday = self.indictor.get_lest_inday()
                open_inday = self.indictor.get_open_inday()
                if (open_inday-klines.iloc[-1].close - open_inday > 30):
                    self.stop()
        #  
        '''
        
        if (self.position != 0):
            self.done_flag = True
            #出场-时间、空间
            #cur_bar = self.get_current_minute_bar()
            hest_bar = pplib.get_highest_bar_today_fix(klines)
            #if ((self.cur_bar-self.entry_bar>90) or (self.cur_bar_id-hest_bar>30)):
            if ((self.cur_bar-self.entry_bar>90)):
                l_checksum = pplib.get_checksum(klines, 17, 2)
                if (abs(l_checksum) < 4):
                    self.debug("持仓时间过长")
                    self.set_position(0)
            if (self.position != 0):
                atr_day = self.indictor.get_atr_daily()
                if (atr_day is None):
                    atr_day = 45
                else:
                    atr_day = atr_day - 10
                
                if (self.ask_price-self.entry_price > atr_day):
                    self.set_position(0)
                elif(self.ask_price-self.entry_price < -10):
                    avg_p = pplib.get_average(klines, 12)
                    if (avg_p-self.entry_price < -20):
                        self.set_position(0)

    '''
    #ask_price1: 3886.0 (卖一价)
    #bid_price1: 3881.0 (买一价)
    def open_time(self, klines, ask_price, bid_price):
        cur_bar = get_current_minute_bar()
        if (self.level == 3):
            self.position = 1
            self.set_position(self.position)
        elif (cur_bar > 5):
            hest_inday = self.indictor.get_hest_inday()
            lest_inday = self.indictor.get_lest_inday()
            open_inday = self.indictor.get_open_inday()

            id,count = get_number_of_less(klines, 5, get_current_minute_bar)
            if (self.level==2 and count > 8):
                self.position = 1
                self.set_position(self.position)
            elif (self.level==1 and count > 28):
                self.position = 1
                self.set_position(self.position)
                self.entry_price = klines.iloc
        '''

    def level_1(self, klines):
        open_wait = 10
        open_end = 20
        open_out = 40
        #max_diff = 15
        #monitor_bar = 20
        wait_price1 = 15
        wait_price2 = 10

        self.make_level(klines, open_wait, open_end, open_out, wait_price1, wait_price2)

    def level_2(self, klines):
        open_wait = 10
        open_end = 30
        open_out = 50
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
        if (self.position >= 1):
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
        #min_passed = tool_utils.time_diff_min(start_time.tm_hour, start_time.tm_min, lt.tm_hour, lt.tm_min)
        min_passed = self.cur_bar_id - self.mark_start_id
        open_inday = self.get_open_price()
        #self.debug("open_inday=%d"%(open_inday))
        # 开仓时间
        if (min_passed > open_wait and min_passed < open_end):
            ll = pplib.get_lest_in_range(klines, 1, open_wait)
            if (open_inday - ll > wait_price1):
                self.set_position(1)
                self.debug("min_passed=%d in open_wait"%(min_passed))
        elif (min_passed > open_end and min_passed < open_out and self.position != 1):
            bars = open_end - open_wait
            bars = int(bars/2)
            if (bars < 6):
                bars = 6
            c_sum = pplib.get_checksum(klines, bars, 1)
            ll = pplib.get_lest_in_range(klines, 1, self.cur_bar)
            if (abs(c_sum) < 6 and open_inday - ll > wait_price2):
                self.debug("min_passed=%d out open_end"%(min_passed))
                self.set_position(1)
        elif (min_passed > open_out):
            sum_count = int(open_out/2)
            if (sum_count < 10):
                sum_count = 10
            c_sum = pplib.get_checksum(klines, sum_count, 1)
            if (abs(c_sum) < 5):
                self.set_position(1)
                self.debug("min_passed=%d out waiting, must enter"%(min_passed))