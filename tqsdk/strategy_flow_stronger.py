'''
强力方向
和其他的策略在指标使用上有重复
注意 关键时刻和上下两个半场
区间突破 回调时介入
支撑 阻力
'''
from pplib import get_checksum,get_hest_in_range
from strategy_base import StrategyBase
from param_defines import TradeDirection, TrendType, StgEvent, ParamUnion
from datetime import datetime
import time
import pplib
from tqsdk import tafunc
from tqsdk.tafunc import time_to_s_timestamp
from tqsdk.tafunc import time_to_str
from tqsdk.ta import ATR,BOLL
import pandas as pd
from indicator_recorder import IndicatorRecorder

class StrategyFlowStronger(StrategyBase):
    def  __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyFlowStronger", manager)
        self.MAX_HOLD = 120
        self.TAG = "StrategyFlowStronger"

        self.trade_dir = TradeDirection.BUYSELL

        #big bang
        self.bigbang_up_height = 0
        self.bigbang_up_bar_start = 0
        self.bigbang_up_bar_end = 0

        self.bigbang_down_height = 0
        self.bigbang_down_bar_start = 0
        self.bigbang_down_bar_end = 0
        #
        self.region_last_h = 0
        self.region_last_l = 0

        self.break_region_bar = 0

        #调整 when loss
        self.adjust_loss = 0

        self.kpi = 0
        print("[%s] running..........."%(self.TAG))

        self.init_data()

    def init_data(self):
        self.atr_daily = 0
        #=========recorder===============#
        self.max_ck_sum = 0
        self.min_ck_sum = 0
        self.last_big_up_bang = -99
        self.last_big_down_bang = -99
        self.last_fit_less_bar = -99
        self.last_fit_greater_bar = -99

        self.peak_recorder = IndicatorRecorder("peak") #当前bar高于回溯bar的数量
        self.valley_recorder = IndicatorRecorder("valley")
        #============================#
        self.support_ll = 0
        self.resistance_hh = 0
        self.range_hh = 0
        self.range_ll = 0
        self.boll_top = 0
        self.boll_bottom = 0
        self.trade_ll = 0
        self.trade_hh = 0
        self.hh_3day = 0
        self.ll_3day = 0
        self.hh_50day = 0
        self.ll_50day = 0
        self.boll_trade_dir = TradeDirection.BUYSELL

        self.hh_near_bar = 0
        self.ll_near_bar = 0

        self.trend_type_daily = TrendType.INVALID #
        self.trend_type_inday = TrendType.INVALID #

        #=================================#
        self.adjust_hh = 0
        self.adjust_ll = 0
        
        self.market_mode = 0
    def on_tick(self, serial):
        StrategyBase.on_tick(self, serial)

    def run(self, klines, bid_price, ask_price, avg_price):
        #big bang
        #连续上涨bar数
        #连续上涨范围
        if (self.run_flag == False):
            return

        self.bid_price = bid_price
        self.ask_price = ask_price
        self.avg_price = avg_price
        self.on_bar(klines)

    def on_day_bar(self, dklines):
        start_id = 2
        #find_range
            #自然波动区间
            #强势后整理波动区间
        #find_strong_price

        self.support_ll = 0
        self.resistance_hh = 0
        self.range_hh = 0
        self.range_ll = 0
        self.boll_top = 0
        self.boll_bottom = 0
        self.trade_ll = 0
        self.trade_hh = 0

        atr = ATR(dklines, 30)
        self.atr_daily = int(atr.atr.iloc[-1])

        #如果区间线和强势线重合，确定方向
        inrange_result = self.find_inrange_daily(start_id, dklines)
        #支撑、阻力
        strong_result = self.find_strong_daliy(start_id, dklines)
        # boll
        self.find_boll_daily(start_id, dklines)

        if (inrange_result == True or strong_result == True):
            if (self.support_ll!=0 and self.range_ll!=0):
                self.trade_ll = int((self.range_ll + self.support_ll)/2)
            elif(self.support_ll != 0):
                self.trade_ll = self.support_ll
            elif(self.range_ll != 0):
                self.trade_ll = self.range_ll

            if (self.resistance_hh!=0 and self.range_hh!=0):
                self.trade_hh = int((self.range_hh + self.resistance_hh)/2)
            elif(self.resistance_hh != 0):
                self.trade_hh = self.resistance_hh
            elif(self.range_hh != 0):
                self.trade_hh = self.range_hh
            
            self.trend_type_daily = TrendType.WAVE
            if (self.support_ll!=0 and self.resistance_hh!=0):
                self.set_trade_direction(TradeDirection.BUYSELL)
            elif (self.support_ll != 0):
                self.set_trade_direction(TradeDirection.BUYONLY)
            elif(self.resistance_hh != 0):
                self.set_trade_direction(TradeDirection.SELLONLY)
            
            if (self.trade_hh == 0):
                self.trade_hh = self.boll_top
            if (self.trade_ll == 0):
                self.trade_ll = self.boll_bottom
        else:
            self.trend_type_daily = TrendType.TREND
            self.trade_ll = self.boll_bottom
            self.trade_hh = self.boll_top
        
        self.debug("on_day_bar trade_hh=%d trade_ll=%d"%(self.trade_hh, self.trade_ll))
        self.hh_3day = pplib.get_hest_in_range(dklines, start_id, start_id+3)
        self.ll_3day = pplib.get_lest_in_range(dklines, start_id, start_id+3)
        self.debug("on_day_bar hh_3day=%d ll_3day=%d"%(self.hh_3day, self.ll_3day))
        self.hh_50day = pplib.get_hest_in_range(dklines, start_id, start_id+50)
        self.ll_50day = pplib.get_lest_in_range(dklines, start_id, start_id+50)

    def on_bar_2(self, klines):
        self.update_kpi(klines)
    
    def on_bar_5(self, klines):
        self.find_bigbang(klines)
        self.find_break(klines)
        self.find_break_day(klines)
        self.check_strong()

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        if (self.run_flag == False):
            return
        lt = self.get_real_time()
        s_checksum = pplib.get_checksum(klines, 2, 5)
        cur_bar = self.get_current_minute_bar()
        self.cur_bar = cur_bar

        if (lt.tm_min%2==0 and self.cur_bar>2):
            self.on_bar_2(klines)

        if (lt.tm_min%5==0 and self.cur_bar>5):
            self.on_bar_5(klines)
        # bigbang
        
        #break

        # 窄幅
        
        #===============================================#
        
        if (self.market_mode == 0):
            self.make_trade_daliy(klines)
        elif (self.market_mode == 1):
            self.make_break(klines)

        self.monitor_position(klines)
    # 根据行情类型生成hh、ll
    # 根据类型设置退场逻辑
    def make_trade(self):
        pass

    # 日线级别重要价格
    def make_trade_daliy(self, klines):
        debug_open = False
        #tmp_position = 0#self.day_position
        '''
        if (self.strong_level == 2):
            tmp_position = 1
            exit_price = self.ask_price - 20
        '''
        self.adjust_hh_ll()
        trade_hh = self.trade_hh + self.adjust_hh
        trade_ll = self.trade_ll + self.adjust_ll

        if (trade_hh!=0 and self.position>=0 and self.ask_price>=trade_hh):
            
            if (self.trend_type_daily == TrendType.TREND 
                and self.boll_trade_dir == TradeDirection.BUYONLY
                and self.position > 0):
                self.set_position(0)
                if (debug_open):
                    self.debug("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))
                    self.debug("多平，arraive hh")
                else:
                    self.info("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))
                    self.info("多平，arraive hh")
            elif(self.check_open_order(-1, 30)):
                self.set_position(-1)
                if (debug_open):
                    self.debug("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))
                    self.debug("空开，arraive hh")
                else:
                    self.info("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))
                    self.info("空开，arraive hh")
        elif(trade_ll!=0 and self.position<=0 and self.ask_price<=trade_ll):
            if (self.trend_type_daily == TrendType.TREND 
                and self.boll_trade_dir == TradeDirection.SELLONLY
                and self.position < 0):
                self.set_position(0)
                if (debug_open):
                    self.debug("空平，arraive ll")
                    self.debug("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))
                else:
                    self.info("空平，arraive ll")
                    self.info("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))
            elif(self.check_open_order(1, 30)):
                self.set_position(1)
                if (debug_open):
                    self.debug("多开，arraive ll")
                    self.debug("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))
                else:
                    self.info("多开，arraive ll")
                    self.info("trend_type_daily=%s trade_hh=%d trade_ll=%d"%(self.trend_type_daily, trade_hh, trade_ll))

        #return tmp_position

    def make_bigbang(self, klines):
        pass

    def make_break(self, klines):
        #区间边沿线突破
        #压力、支撑突破
        
        pass

    #应该放到waves里
    def make_wm(self, klines):
        #//参照日线
        pass

    def make_inrange(self, klines):
        #区间边沿线
        #压力、支撑
        pass

    #只做一个方向
    def make_boll(self, klines):
        pass
    '''
    def make_support_resistance(self, klines):
        if (self.cur_bar < 0)
        pass
    '''
    
    def monitor_position(self, klines):
        if (self.cur_bar-self.entry_bar > self.MAX_HOLD):  
            tmp_bar, ups = pplib.get_count_of_greater2(klines, 1, self.cur_bar)
            tmp_bar, downs = pplib.get_count_of_less2(klines, 1, self.cur_bar)
            if (self.position > 0 and ups>30):
                self.set_position(0)
                self.debug("多平，持仓时间过长")
                self.loss_mark_flag = 1
                self.loss_mark_bar = self.get_current_minute_bar()
            elif (self.position < 0 and downs>30):
                self.set_position(0)
                self.debug("空平，持仓时间过长")
                self.loss_mark_flag = 1
                self.loss_mark_bar = self.get_current_minute_bar()

        if(self.position<0 and self.cur_bar-self.entry_bar>5):
            profit = self.entry_price-self.ask_price
            if (profit>self.MAX_PROFIT):#ying
                self.set_position(0)
                self.debug("空平，达到最大盈利")
            elif (profit < -abs(self.MAX_LOSS)):
                self.set_position(0)
                self.debug("空平，止损(%d)"%(profit))
            elif(self.cur_bar-self.entry_bar>30):
                ll, ll_bar = pplib.get_lest_in_range_fix(klines, 1, 30)
                if (ll-self.trade_ll < 8):
                    self.ll_near_bar = ll_bar
                if (self.ll_near_bar != 0 and self.cur_bar_id-self.ll_near_bar>25):
                    tmp_bar, downs = pplib.get_count_of_less2(klines, 1, self.cur_bar)
                    if (downs > 20):
                        self.set_position(0)
                        self.debug("离开ll时间过长")  

        if(self.position>0):
            profit = self.ask_price-self.entry_price
            if (profit>self.MAX_PROFIT):#ying
                self.set_position(0)
                self.debug("多平，达到最大盈利(self.ask_price=%d  self.entry_price=%d"%(self.ask_price, self.entry_price))
            elif (profit < -abs(self.MAX_LOSS)):
                self.set_position(0)
                self.debug("多平，止损(%d)"%(profit))
                self.debug("多平，达到最大损失(self.ask_price=%d  self.entry_price=%d"%(self.ask_price, self.entry_price))
            elif(self.cur_bar-self.entry_bar>30):
                hh, hh_bar = pplib.get_hest_in_range_fix(klines, 1, 30)
                if (self.trade_hh - hh < 8):
                    self.hh_near_bar = hh_bar
                if (self.hh_near_bar != 0 and self.cur_bar_id-self.hh_near_bar>25):
                    tmp_bar, ups = pplib.get_count_of_greater2(klines, 1, self.cur_bar)
                    if (ups > 25):
                        self.set_position(0)     
                        self.debug("离开hh时间过长")   

    def monitor_market(self, klines):
        #监控强弱变化
        pass

    def set_strong_level(self, level):
        self.strong_level = level

    def set_strong_treatment(self, treat):
        self.strong_treat = treat

    def update_kpi(self, klines):
        self.kpi = 0
        cur_bar = self.get_current_minute_bar()
        if (cur_bar - self.bigbang_up_bar_end < 15):#数量
            self.kpi = self.kpi + 60
        elif (cur_bar - self.bigbang_up_bar_end < 30):
            self.kpi = self.kpi + 50
        elif (cur_bar - self.bigbang_up_bar_end < 60):
            self.kpi = self.kpi + 30
        #
        if (cur_bar - self.bigbang_down_bar_end < 15):#数量
            self.kpi = self.kpi - 60
        elif (cur_bar - self.bigbang_down_bar_end < 30):
            self.kpi = self.kpi - 50
        elif (cur_bar - self.bigbang_down_bar_end < 60):
            self.kpi = self.kpi - 30

        open_price = pplib.get_open_today(klines, 0)
        hh_inday = pplib.get_open_today(klines, 0)
        ll_inday = pplib.get_open_today(klines, 0)
        if (hh_inday- open_price > 3*(open_price - ll_inday)):
            self.kpi = self.kpi + 40
        elif (hh_inday- open_price > 2*(open_price - ll_inday)):
            self.kpi = self.kpi + 30
        elif (hh_inday- open_price > (open_price - ll_inday)):
            self.kpi = self.kpi + 30
        
        if (open_price - ll_inday > 3*(hh_inday- open_price)):
            self.kpi = self.kpi + 40
        elif (open_price - ll_inday > 2*(hh_inday- open_price)):
            self.kpi = self.kpi + 30
        elif (open_price - ll_inday > (hh_inday- open_price)):
            self.kpi = self.kpi + 30


    def find_bigbang2(self, klines):
        reds = pplib.get_reds_candle(klines, 20)
        greens = pplib.get_greens_candle(klines, 20)
        height = pplib.get_height_in_range(klines, 1, 20)
        if (reds>15 or height>20):
            self.bigbang_up_height = height
            tmp, self.bigbang_up_bar_start = pplib.get_lest_in_range2(klines, 1, 20)
            self.bigbang_up_bar_start = self.cur_bar - self.bigbang_up_bar_start
            tmp, self.bigbang_up_bar_end = pplib.get_hest_in_range2(klines, 1, 20)
            self.bigbang_up_bar_end = self.cur_bar - self.bigbang_up_bar_end

        elif (greens>15 or height<-20):# 
            self.bigbang_up_height = height
            tmp, self.bigbang_down_bar_start = pplib.get_hest_in_range2(klines, 1, 20)
            self.bigbang_down_bar_start = self.cur_bar - self.bigbang_down_bar_start
            tmp, self.bigbang_down_bar_end = pplib.get_lest_in_range2(klines, 1, 20)
            self.bigbang_down_bar_end = self.cur_bar - self.bigbang_down_bar_end
    
    def find_break2(self, klines):
        region_hh = pplib.get_hest_in_range(klines, 10, 10+30)
        region_ll = pplib.get_lest_in_range(klines, 10, 10+30)
        # 标记
        if (klines.iloc[-1].close > region_hh):
            self.break_region_bar = 1
        elif (klines.iloc[-1].close < region_ll):
            self.break_region_bar = -1

    def find_lowrange(self, klines):
        if (self.cur_bar < 20):
            return
        l_checksum = pplib.get_checksum(klines, 2, 30)
        if (abs(l_checksum) < 10):
            range_len = 50
            if (self.cur_bar < 50):
                range_len = self.cur_bar
            recent_height = pplib.get_height_in_range(klines, 1, range_len)
            if (recent_height < 25):
                self.debug("find lowrange")

    def find_bigbang(self, klines):
        #速度
        ck_sum_10 = pplib.get_checksum(klines, 11, 1)
        if (abs(ck_sum_10) > 10):
            pass
        '''
            msg = "ck_sum_10=%d"%(ck_sum_10)
            self.info(msg)
        '''

        if (ck_sum_10 > self.max_ck_sum):
            self.max_ck_sum = ck_sum_10
            msg = "max_ck_sum_10=%d"%(ck_sum_10)
            self.info(msg)
        if (ck_sum_10 < self.min_ck_sum):
            self.min_ck_sum = ck_sum_10
            msg = "min_ck_sum_10=%d"%(ck_sum_10)
            self.info(msg)

        # 高度
        # cksum 和 height有重复
        height_10 = pplib.get_hest_in_range(klines, 1, 11)
        if (ck_sum_10 > 20 or (height_10> 20 and ck_sum_10>10)):
            self.last_big_up_bang = self.get_current_minute_bar()
            if (height_10 > 25):
                self.strong_level = 2
        if (ck_sum_10 < -20 or (height_10> 20 and ck_sum_10<-10)):
            self.last_big_down_bang = self.get_current_minute_bar()
            if (height_10 > 25):
                self.strong_level = -2

    def find_break_day(self, klines):
        if (self.cur_bar < 30):
            return
        avg_p = pplib.get_avg_price(klines, 30)
        if (abs(self.get_kpi_daily()) > 35):
            avg_p = pplib.get_avg_price(klines, 10)
        if (avg_p > self.hh_3day):
            self.change_trade_mode(0, 1, 1)
            '''
            self.trade_hh += 31
            
            if (self.position <= 0):
                self.debug("hh breakout.....")
                
                self.set_position(1)
                self.market_mode = 1
                self.trade_hh += 30
            '''
        elif (avg_p < self.ll_3day):
            self.change_trade_mode(0, 1, -1)
            '''
            self.trade_ll -= 31
            
            if (self.position >= 0):
                self.debug("ll breakout.....")
                
                self.set_position(-1)
                self.market_mode = 1
                self.trade_ll -= 30
            '''


    def change_trade_mode(self, A, B, t_dir):
        if (B == 1):
            if (t_dir > 0 ):
                self.debug("hh breakout.....")
                if (self.hh_50day - self.ask_price < 40):
                    self.trade_hh = self.ask_price+18
                else:
                    self.trade_hh = self.ask_price+30
                if (self.position <= 0):
                    self.set_position(1)
            else:
                self.debug("ll breakout.....")
                if (self.ask_price - self.ll_50day<40):
                    self.trade_ll = self.ask_price - 15
                else:
                    self.trade_ll = self.ask_price - 30
                if (self.position >= 0):
                     self.set_position(-1)

        
        self.market_mode = B

    def find_break(self, klines):
        #===============================================# 
        #边界
        if (self.cur_bar < 20):
            return
        length = 50
        if (self.cur_bar < 50):
            length = self.cur_bar
        bid, self.count_of_less_near = pplib.get_count_of_nearest_less(klines, 5, length)
        bid, self.count_of_greater_near = pplib.get_count_of_nearest_greater(klines, 5, length)

        if (self.count_of_less_near>=50):
            greaters = pplib.get_count_of_greater(klines, length)
            if (greaters > 2):
                self.valley_recorder.add(self.count_of_less_near, self.cur_bar_id, self.cur_bar_time)
            
        if (self.count_of_greater_near >= 50): 
            lesses = pplib.get_count_of_less(klines, length)
            if (lesses > 2):
                self.valley_recorder.add(self.count_of_less_near, self.cur_bar_id, self.cur_bar_time)

        std_count = 120
        if (self.cur_bar < 100):
            std_count = self.cur_bar

        if (self.count_of_less_near > std_count):
            self.last_fit_less_bar = self.get_current_minute_bar()
            self.debug("find break down")
        if (self.count_of_greater_near > std_count):
            self.last_fit_greater_bar = self.get_current_minute_bar()
            self.debug("find break up")

    def find_reverse(self, klines):
        #创新高，反向拉回，创新低
        last_greater_59_bar = self.peak_recorder.find_gt(59)
        last_less_59_bar = self.valley_recorder.find_gt(59)
        if (last_greater_59_bar!=-1 and last_less_59_bar!=-1):
            diff = last_greater_59_bar - last_less_59_bar
            if (diff>0 and diff<50):
                self.debug("反转Up")
            if (diff<0 and diff>-50):
                self.debug("反转Down")

    def find_w(self):
        pass

    def find_m(self):
        pass

    def check_strong(self):
        if (self.check_less(self.last_big_down_bang, 10) and 
            self.check_less(self.last_fit_less_bar, 10)):
            param = ParamUnion()
            param.put_param("BarId", self.last_big_down_bang)
            self.manager.drive_event(self.TAG, StgEvent.BigBangBreakDown, self.last_big_down_bang)
            #pass
        
        if (self.check_less(self.last_big_up_bang, 10) and 
            self.check_less(self.last_fit_greater_bar, 10)):
            param = ParamUnion()
            param.put_param("BarId", self.last_big_up_bang)
            self.manager.drive_event(self.TAG, StgEvent.BigBangBreakUp, param)
            #pass

    def find_strong_inday(self, dklines):
        pass

    def find_strong_daliy(self, start_id, dklines):
        self.resistance_hh = 0
        self.support_ll = 0
        std = tafunc.std(dklines.high, 4)  # 收盘价序列每5项计算一个标准差
        for i in range(start_id, start_id+1):
            if (list(std)[-i] < 15):
                print(self.TAG, i, time_to_str(dklines.iloc[-i].datetime), dklines.iloc[-i].high)
                avg_high = pplib.get_average_in_series(dklines.high, i, 3)
                self.debug("get resistance hh = %d"%(avg_high))
                self.resistance_hh = avg_high
                break

        #print("过滤 low 离散性小的bar")
        std = tafunc.std(dklines.low, 4)  # 收盘价序列每5项计算一个标准差
        #print(type(std))
        #print(list(std))
        for i in range(start_id, start_id+1):
            if (list(std)[-i] < 15):
                print(i, time_to_str(dklines.iloc[-i].datetime), dklines.iloc[-i].low)
                avg_low = pplib.get_average_in_series(dklines.low, i, 3)
                self.debug("get support ll = %d"%(avg_low))
                self.support_ll = avg_low
                break
        
        if (self.resistance_hh != 0 or self.support_ll != 0):
            return True
        else:
            return False
        
    def find_inrange_inday(self, dklines):
        #结合长线趋势：比如Bigbang，连续
        pass

    def find_inrange_daily(self, start_id, dklines):
        hhv = tafunc.hhv(dklines.high, 3)
        llv = tafunc.llv(dklines.low, 3)
        hclose = tafunc.hhv(dklines.close, 3)
        lclose = tafunc.llv(dklines.close, 3)

        range_h = 0
        range_l = 0
        for i in range(start_id, start_id+1):
            close_height = list(hclose)[-i] - list(lclose)[-i]
            hl_height = list(hhv)[-i] - list(llv)[-i]
            if (close_height < 25 or hl_height < 60):
                range_l = pplib.get_average_in_series(dklines.low, i, 3)
                range_h = pplib.get_average_in_series(dklines.high, i, 3)
        
            
            print(i, close_height, hl_height,list(hhv)[-i], list(llv)[-i],dklines.iloc[-i].open, dklines.iloc[-i].close, time_to_str(dklines.iloc[-i].datetime))
        
        self.debug("range_l=%d range_h=%d"%(range_l, range_h))
        self.range_ll = range_l
        self.range_h = range_h

        if (range_h !=0 and range_l != 0):
            return True
        else:
            return False

    #watcher 可以根据 ma线
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

    #boll=BOLL(dklines,5, 1)
        boll = new_df
        ma_ck = 0
        j = 1
        for i in range(j+1, j+3+1):
            ma_ck += list(boll["mid"])[-i] - list(boll["mid"])[-(i+1)]
        #print(ma_ck)
        if (ma_ck > 0):
            self.boll_top = int(list(boll["mid"])[-(j+1)] + std.iloc[-(j+1)]*1.2)
            self.boll_bottom = int(list(boll["mid"])[-(j+1)] - std.iloc[-(j+1)])
            self.boll_trade_dir = TradeDirection.BUYONLY
            
        if (ma_ck < 0):
            self.boll_top = int(list(boll["mid"])[-(j+1)] + std.iloc[-(j+1)])
            self.boll_bottom = int(list(boll["mid"])[-(j+1)] - std.iloc[-(j+1)]*1.2)
            self.boll_trade_dir = TradeDirection.SELLONLY

        '''
        print(list(boll["mid"]))
        print(list(boll["top"]))
        print(list(boll["bottom"]))
        '''
    def loss_happend(self, t_dir, loss_p):
        StrategyBase.loss_happend(self, t_dir, loss_p)
        if (t_dir < 0):
            self.adjust_hh = 39
        else:
            self.adjust_ll = 39

    def gain_happend(self, t_dir, gain_p):
        StrategyBase.gain_happend(self, t_dir, gain_p)
        '''
        if (t_dir < 0):
            self.adjust_hh = 0
        else:
            self.adjust_ll = 0
        '''

    def adjust_hh_ll(self):
        pass

    def set_position(self, pos):
        if (self.check_order(10)):
            StrategyBase.set_position(self, pos)
        else:
            self.debug("开平间隔检测失败")