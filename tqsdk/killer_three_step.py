from strategy_base import StrategyBase
from param_defines import TradeDirection, WalkPath
import pplib
from datetime import datetime
import time
# 折线向上、向下
class KillerThreeStep(StrategyBase):
    def __init__(self, manager, preset_path):
        self.TAG = "KillerThreeStep"
        self.FIRST_MAX_HOLD_TERM = 40
        self.SECOND_MAX_HOLD_TERM = 40
        self.MAX_LOSS = 25

        self.preset_path = preset_path
        self.manager = manager

        self.setup = 0

        self.entry_bar = 0
        self.entry_price = 0
        self.entry_dir = TradeDirection.BUYSELL

        self.cur_price = 0

        #

    def preset_hh(self, hh):
        self.preset_HH = hh

    def preset_ll(self, ll):
        self.preset_LL = ll

    def set_trade_direction(self, tdir):
        self.trade_dir = tdir

    def make_long(self, klines):
        lt = time.localtime(time.time())
        cur_bar = self.get_current_minute_bar()
        if (self.preset_HH == 0 and lt.tm_hour == 9 and lt.tm_min < 30):
            return
        if (self.preset_HH == 0):
            self.preset_HH = pplib.get_lest_in_range(klines, 1, cur_bar)
        
        end_bar = cur_bar
        if (end_bar > 120):
            end_bar = 120
        hh, hh_bar= pplib.get_hest_in_range_fix(klines, 1, end_bar)
        ll, ll_bar= pplib.get_lest_in_range_fix(klines, 1, end_bar)
        ma5 = pplib.get_avg_price(self, 6)

        tmp_position = self.position
        
        #零段
        if (cur_bar<60):
            open_inday = pplib.get_open_today(klines, 0)
            if (hh - open_inday > open_inday - ll):
                self.step = 1
        #一段
        if(abs(ma5-self.preset_HH)<15 and self.cur_bar_id - hh_bar < 20):
            lcsum = pplib.get_checksum(klines, 10, 1)
            if (abs(lcsum) <= 5):
                tmp_position = -1
                self.setup = 1

        degree = 0
        indictor = self.manager.get_indicotor()
        if (indictor is not None):
            degree = indictor.get_degree()
        
        #二段
        if (cur_bar>60 and self.step == 1 and lt.tm_hour < 14):
            '''
            degree = 0
            indictor = self.manager.get_indicotor()
            if (indictor is not None):
                degree = indictor.get_degree()
            '''
            swinghighs = pplib.SwingHighPriceSeries(klines, 20, 1)
            swinglows = pplib.SwingHighPriceSeries(klines, 30, 1)

            swing_h = 0
            swing_h_len = len(swinghighs)
            if (swing_h_len > 0):
                swing_h = swinghighs[swing_h_len-1]["price"]
            swing_l = 0
            swing_l_len = len(swinglows)
            if (swing_l_len > 0):
                swing_l = swinglows[swing_l_len-1]["price"]
            else:
                swing_l = ll - 10
            #底
            if (hh - swing_l < 20):
                swing_l = (swing_l + open_inday)/2

            if (self.position < 0 and cur_bar - self.entry_bar > 20 
                and self.cur_price > swing_h):
                tmp_position = 0

            #时间
            scsum = pplib.get_checksum(klines, 10, 1)
            if (self.position < 0 and self.cur_price <= swing_l):
                tmp_position = 1
                self.setup = 2
            elif (self.position < 0 and cur_bar - self.entry_bar>25
                    and degree > 50 and abs(self.cur_price-swing_l)<10 and scsum < 3):
                tmp_position = 0
            elif (self.position < 0 and cur_bar - self.entry_bar>40):
                if (abs(scsum) < 5):
                    tmp_position = 1
                    self.setup = 2
            if (degree > 10 and self.position == 0 and abs(self.cur_price-swing_l)<10 and scsum < 3):
                tmp_position = 1
                self.setup = 2

            if (self.position > 0 and cur_bar - self.entry_bar > 20 and
                     self.cur_price > swing_h):
                tmp_position = 0

        #三段
        if (lt.tm_hour >= 13 or self.step == 2 and degree > 10):
            lcsum = pplib.get_checksum(klines, 10, 1)
            lesses = pplib.get_count_of_nearest_less(klines, 10, 100)
            if (abs(lcsum) < 5 and lesses > 30):
                tmp_position = 1

        
        if (self.position > 0 and self.entry_price - self.cur_price > self.MAX_LOSS):
            tmp_position = 0
        if (self.position < 0 and self.cur_price - self.entry_price > self.MAX_LOSS):
            tmp_position = 0

        #ping
        if (tmp_position != self.position):
            self.set_position(tmp_position)

    def make_short(self, klines):
        lt = time.localtime(time.time())
        cur_bar = self.get_current_minute_bar()
        if (self.preset_LL == 0 and lt.tm_hour == 9 and lt.tm_min < 30):
            return
        if (self.preset_LL == 0):
            self.preset_LL = pplib.get_lest_in_range(klines, 1, cur_bar)

        end_bar = cur_bar
        if (end_bar > 120):
            end_bar = 120
        hh, hh_bar= pplib.get_hest_in_range_fix(klines, 1, end_bar)
        ll, ll_bar= pplib.get_lest_in_range_fix(klines, 1, end_bar)
        ma5 = pplib.get_avg_price(self, 6)

        tmp_position = self.position
        
        #零段
        if (cur_bar<60):
            open_inday = pplib.get_open_today(klines, 0)
            if (hh - open_inday < open_inday -ll):
                self.step = 1
        #一段
        if(abs(ma5-self.preset_LL)<15 and self.cur_bar_id - ll_bar < 20):
            lcsum = pplib.get_checksum(klines, 10, 1)
            if (abs(lcsum) <= 5):
                tmp_position = -1
                self.setup = 1

        degree = 0
        indictor = self.manager.get_indicotor()
        if (indictor is not None):
            degree = indictor.get_degree()
        
        #二段
        if (cur_bar>60 and self.step == 1 and lt.tm_hour < 14):
            '''
            degree = 0
            indictor = self.manager.get_indicotor()
            if (indictor is not None):
                degree = indictor.get_degree()
            '''
            swinghighs = pplib.SwingHighPriceSeries(klines, 20, 1)
            swinglows = pplib.SwingHighPriceSeries(klines, 30, 1)

            swing_h = 0
            swing_h_len = len(swinghighs)
            if (swing_h_len > 0):
                swing_h = swinghighs[swing_h_len-1]["price"]
            else:
                swing_h = hh + 10
            swing_l = 0
            swing_l_len = len(swinglows)
            if (swing_l_len > 0):
                swing_l = swinglows[swing_l_len-1]["price"]
            else:
                swing_l = ll - 10

            #底
            if (hh - swing_l < 20):
                swing_l = (swing_l + open_inday)/2

            if (self.position < 0 and cur_bar - self.entry_bar > 20 
                and self.cur_price > swing_h):
                tmp_position = 0

            #时间
            scsum = pplib.get_checksum(klines, 10, 1)
            if (self.position > 0 and self.cur_price >= swing_h):
                tmp_position = -1
                self.setup = 2
            elif (self.position > 0 and cur_bar - self.entry_bar>25
                    and degree < -50 and abs(swing_h - self.cur_price)<10 and scsum < 3):
                tmp_position = 0
            elif (self.position < 0 and cur_bar - self.entry_bar>40):
                if (abs(scsum) < 5):
                    tmp_position = -1
                    self.setup = 2
            if (degree > 10 and self.position == 0 and abs(swing_h - self.cur_price)<10 and scsum < 3):
                tmp_position = -1
                self.setup = 2
              
            if (self.position < 0 and cur_bar - self.entry_bar > 20 
                and self.cur_price > swing_l):
                tmp_position = 0
        #三段
        if (lt.tm_hour >= 13 or self.step == 2 and degree > 10):
            lcsum = pplib.get_checksum(klines, 10, 1)
            lesses = pplib.get_count_of_nearest_less(klines, 10, 100)
            if (abs(lcsum) < 5 and lesses > 30):
                tmp_position = 1

        if (self.position > 0 and self.entry_price - self.cur_price > self.MAX_LOSS):
            tmp_position = 0
        if (self.position < 0 and self.cur_price - self.entry_price > self.MAX_LOSS):
            tmp_position = 0

        #ping
        if (tmp_position != self.position):
            self.set_position(tmp_position)


    def run(self, klines, bid_price, ask_price, avg_price):
        self.cur_price = ask_price
        lt = time.localtime(time.time())
        if(lt.tm_hour == 9 and lt.tm_min <= 30):
            pass
        
        if (self.preset_path == WalkPath.TreeStepUp):
            self.make_long(klines)
        elif (self.preset_path == WalkPath.TrendDown):
            self.make_short(klines)

    def set_position(self, pos):
        print("[%s] set_position pos=%d"%(self.TAG, pos))
        if(pos > 1 and self.trade_dir == TradeDirection.SELLONLY):
            self.manager.set_position(self.TAG, 0)
            self.position = 0
            self.logger.info(self.TAG, "平仓")
            print("[%s] 平多"%(self.TAG))
        elif(pos < 1 and self.trade_dir == TradeDirection.BUYONLY):
            self.manager.set_position(self.TAG,0)
            self.position = 0
            self.logger.info(self.TAG, "平仓")
            print("[%s] 平空"%(self.TAG))
        else:
            if (pos > 1):
                pos = 1
            elif (pos < -1):
                pos = -1
            if (pos != 0):
                self.entry_bar = self.get_current_minute_bar()
                self.entry_price = self.cur_price
            self.manager.set_position(self.TAG,pos)
            self.position = pos
            self.logger.info(self.TAG, "开仓 position=%d"%(self.position))
            print("[%s] 开仓 position=%d"%(self.TAG, self.position))

    def get_strategy_position(self):
        return NotImplemented
    

    def timer_task(self):
        pass

    def get_name(self):
        return self.TAG

    def set_logger(self, logger):
        self.logger = logger