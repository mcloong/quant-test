'''
做多
用于行情比较明显的涨跌
5分钟之内开仓

'''
from datetime import datetime
import time
from pplib import get_number_of_less,get_checksum
from tool_utils import get_current_minute_bar

class KillerLV(object):
    #level: 3 no delay, 2 wait for 回调，1 wait for 确认
    def __init__(self, level, mc_indor):
        if (level > 3 or level < 1):
            self.level = 1
        else:
            self.level = level
        self.run_flag = True
        self.position = 0

        self.indictor = mc_indor
        self.entry_time = 0
        self.entry_price = 0

        self.TAG = "KillerLV"

    def set_log(self, logger):
        self.logger = logger

    def set_pos_manger(self, pos_manager):
        self.pos_man = pos_manager

    def run(self, klines, ask_price, bid_price):
        if (self.run_flag == False):
            return
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
        #出场-时间、空间
        if ((self.position != 0 and get_current_minute_bar-self.entry_time>90) or
            (self.position != 0 and get_current_minute_bar() - self.indictor.get_hest_bar_inday() > 30)):
            l_checksum = get_checksum(klines, 10, 2)
            if (l_checksum == 0):
                self.position = 0
                self.set_position(0)
       
        # 止盈
        if (self.position != 0 and )

    def start(self):
        pass

    def stop(self):
        self.run_flag = False
        if (self.position != 0):
            self.pos_man.set_position(0)

    def set_position(self, pos):
        print("[%s], set position=%d"%(self.TAG, pos))
        if (pos != 0):
            self.bar_entry = get_current_minute_bar()

        if(pos > 1):
            self.pos_man.set_position(0)
            self.position = 0
            self.logger.info(self.TAG, "平仓")
        elif(pos < 1):
            self.pos_man.set_position(0)
            self.position = 0
            self.logger.info(self.TAG, "平仓")
        
        else:
            if (pos > 1):
                pos = 1
            elif (pos < -1):
                pos = -1

            self.pos_man.set_position(pos)
            self.position = pos
            self.logger.info(self.TAG, "开仓 position=%d"%(self.position))

    def run_level_1(self):
        pass

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

        

    
