from strategy_base import StrategyBase
from param_defines import TradeDirection, StgEvent, Indicator, WalkStep
import pplib
from datetime import datetime
import time
from tqsdk.tafunc import time_to_str
import numpy as np
import pandas as pd

#
# 
# 计划：根据涨跌的趋势，动态的调整开口大小

class KillerTank(StrategyBase):
    def  __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "KillerTank", manager)
        self.TAG = "KillerTank"
        self.SMALL_COUNT = 35
        self.LARGE_COUNT = 60
        self.EXTENDED_BARS = 20 
        self.std_overs_max = 130
        self.std_downs_max = 130

        self.trade_dir = TradeDirection.BUYSELL
        self.manager = manager

        self.run_flag = True
        self.position = 0
        self.cond_down_count = 0
        self.cond_up_count = 0
        self.entry_bar = 0

        self.ups = 0
        self.downs = 0
        self.last_uper_bar = -999
        self.last_downer_bar = -999
        self.last_uper_count = 0
        self.last_downer_count = 0

        self.low_range_flag = False
        self.count_for_checksum = 10

        if (self.trade_dir == TradeDirection.SELLONLY):
            self.cond_down_count = self.LARGE_COUNT
            self.cond_up_count = self.SMALL_COUNT
        elif (self.trade_dir == TradeDirection.BUYONLY):
            self.cond_down_count = self.SMALL_COUNT
            self.cond_up_count = self.LARGE_COUNT
        else:
            self.cond_down_count = 50
            self.cond_up_count = 50

        c = ['id', 'time', 'avg']
        self.list_ = pd.DataFrame(columns=c)

        print("[%s] running..........."%(self.TAG))

        self.debug("cond_down_count=%d cond_up_count=%d"%(self.cond_down_count,self.cond_up_count))

    def set_trade_direction(self, t_dir):
        StrategyBase.set_trade_direction(self, t_dir)
        if (self.trade_dir == TradeDirection.SELLONLY):
            self.cond_down_count = self.LARGE_COUNT
            self.cond_up_count = self.SMALL_COUNT
        elif (self.trade_dir == TradeDirection.BUYONLY):
            self.cond_down_count = self.SMALL_COUNT
            self.cond_up_count = self.LARGE_COUNT
        else:
            self.cond_down_count = 60
            self.cond_up_count = 60

    def set_up_count(self, ups):
        self.cond_up_count = ups
        self.debug("change cond_up_count=%d "%(self.cond_up_count))
        self.std_ups_max = int(ups*1.3)

    def set_down_count(self, downs):
        self.cond_down_count = downs
        self.debug("change cond_down_count=%d "%(self.cond_down_count))
        self.std_overs_max = int(downs*1.3)

    def set_mode_wave_up(self):
        self.cond_up_count = 90
        self.cond_down_count = 35

    def set_mode_wave_down(self):
        self.cond_up_count = 35
        self.cond_down_count = 90

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        if (self.run_flag == False or self.trade_dir == TradeDirection.INVALID):
            return
        lt = self.get_real_time()
        if (lt.tm_hour == 9 and lt.tm_sec <= 20):
            return
        cur_bar = self.get_current_minute_bar()
        if (self.cond_up_count < 15):
            self.cond_up_count = 15
        if (self.cond_down_count < 15):
            self.cond_down_count = 15
        self.on_self_bar(klines,self.cond_up_count, self.cond_down_count, 1, cur_bar)

    def on_kpattern(self, kpt):
        if (kpt.name == StgEvent.CrossOverAvgLine and self.position > 0):
            profit = self.get_profit()
            if (profit >= 100 and kpt.score >= 120):
                self.set_position(0)
        if (kpt.name == StgEvent.CrossUnderAvgLine and self.position < 0):
            profit = self.get_profit()
            if (profit >= 100 and kpt.score >= 120):
                self.set_position(0)

    def run(self, klines, bid_price, ask_price, avg_price):
        StrategyBase.run(self, klines, bid_price, ask_price, avg_price)

    def timer_task(self):
        pass

    def profit_monitor(self):
        pass
   
    def on_bar10(self, klines):
        self.monitor()
                
    def on_bar5(self, klines):
        #低波动
        cur_bar = self.get_current_minute_bar()
        if (self.get_current_minute_bar() > 120):
            height = pplib.get_height_in_range(klines, 1, cur_bar)
            if (height <= 35):
                self.count_for_checksum = 15 # low range z这个值需要调整
                self.low_range_flag = True
            else:
                #self.count_for_checksum = 15 #15好像太大了
                self.count_for_checksum = 8
                self.low_range_flag = False
        #监控行情情况，不断更新cond_up_count, cond_down_count
        if (self.ups > 210):
            if (self.low_range_flag == False):
                self.cond_down_count = 45
                self.cond_up_count = 60
            else:
                self.cond_down_count = 60
                self.cond_up_count = 60
            self.debug("change cond_down_count=%d cond_up_count=%d"%(self.cond_down_count, self.cond_up_count))
        if (self.downs > 210):
            if (self.low_range_flag == False):
                self.cond_down_count = 60
                self.cond_up_count = 45
            else:
                self.cond_down_count = 60
                self.cond_up_count = 60
            self.debug("change cond_down_count=%d cond_up_count=%d"%(self.cond_down_count, self.cond_up_count))

    def on_self_bar(self, klines, UPS_COUNT, DOWNS_COUNT, start, end):
        tmp_position = self.position

        tmp_bar, ups = pplib.get_count_of_greater2(klines, start, end)
        tmp_bar, downs = pplib.get_count_of_less2(klines, start, end)
        checksum = pplib.get_checksum2(klines, start, self.count_for_checksum, 1)

        cur_bar_id = klines.iloc[-(start)].id
        if (self.cur_bar < 10):
            return

        if (cur_bar_id%5 == 0):
            self.on_bar5(klines)

        if (ups > UPS_COUNT):
            self.last_uper_bar = cur_bar_id
            self.last_uper_count = ups
            self.debug("datetime:%s ups:%d downs:%d checksum=%d"%(time_to_str(klines.iloc[-start].datetime), ups, downs, checksum))
            self.debug("datetime:%s up_mark_bar=%d"%(time_to_str(klines.iloc[-start].datetime), cur_bar_id))

        if (downs > DOWNS_COUNT):
            self.last_downer_bar = cur_bar_id
            self.last_downer_count = downs
            self.debug("datetime:%s ups:%d downs:%d checksum=%d"%(time_to_str(klines.iloc[-start].datetime), ups, downs, checksum))
            self.debug("datetime:%s down_mark_bar=%d"%(time_to_str(klines.iloc[-start].datetime), cur_bar_id))
        #开
        #if (cur_bar_id % 3 == 0):
        #    print(time_to_str(klines.iloc[-start].datetime), ups, downs, checksum)
        if (abs(checksum)<5 and cur_bar_id - self.last_downer_bar < 16 and self.position <= 0):
            self.debug("ups=%d, downs=%d, lst_downer_count=%d checksum=%d"%(ups, downs,self.last_downer_count,checksum))
            score_inday = self.get_kpi_inday()
            #if (score_inday < -50 and self.last_downer_bar > 110):
            if (score_inday < 0 and self.last_downer_bar > self.std_downs_max):
                if (self.position<0 and self.entry_price - self.ask_price >35):
                    tmp_position = 0
                    self.debug("空平(p=%d time=%s) 强降到价格 "%(klines.iloc[-start].close,time_to_str(klines.iloc[-start].datetime)))
            if (self.last_downer_count > self.std_downs_max and ups > 5):
                if (self.position < 0):
                    tmp_position = 0
                    self.debug("空平(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,time_to_str(klines.iloc[-start].datetime)))
            elif(self.last_downer_count < self.std_downs_max and ups > 2):
                if (self.low_range_flag == True):
                    if (ups < 8):
                        tmp_position = 1
                        self.debug("多开(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,time_to_str(klines.iloc[-start].datetime)))
                else:
                    tmp_position = 1
                    self.debug("多开(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,time_to_str(klines.iloc[-start].datetime)))
        elif (abs(checksum)<3 and cur_bar_id - self.last_uper_bar < 16 and self.position >= 0):
            self.debug("ups=%d, downs=%d, lst_uper_count=%d checksum=%d"%(ups, downs,self.last_uper_count,checksum))
            score_inday = self.get_kpi_inday()
            if (score_inday > 0 and self.last_uper_count > self.std_overs_max):
                if (self.position>0 and self.ask_price -self.entry_price>35):
                    tmp_position = 0
                    self.debug("多平(p=%d time=%s) 强升到价格 "%(klines.iloc[-start].close,  time_to_str(klines.iloc[-start].datetime)))
            elif (self.last_uper_count > self.std_overs_max):
                if (self.position > 0 and downs > 5):
                    tmp_position = 0
                    self.debug("多平(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,  time_to_str(klines.iloc[-start].datetime)))
            elif(self.last_uper_count < self.std_overs_max and downs > 3):
                if (self.low_range_flag == True):
                    if (downs < 8):
                        tmp_position = -1
                        self.debug("空开(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,  time_to_str(klines.iloc[-start].datetime)))
                else:
                    tmp_position = -1
                    self.debug("空开(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,  time_to_str(klines.iloc[-start].datetime)))
        #止平
        if (self.position < 0 and self.last_uper_count > self.std_overs_max and abs(checksum)<5):
             tmp_position = 0
             self.cond_up_count = self.cond_up_count+10
             self.cond_down_count = self.cond_down_count -10
             self.debug("空止平(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,time_to_str(klines.iloc[-start].datetime)))
        if (self.position > 0 and self.last_downer_count > self.std_downs_max and abs(checksum)<5):
            self.cond_up_count = self.cond_up_count-10
            self.cond_down_count = self.cond_down_count+10
            tmp_position = 0
            self.debug("多止平(p=%d time=%s) 条件1 "%(klines.iloc[-start].close,time_to_str(klines.iloc[-start].datetime)))
        '''
        if (cur_bar_id - self.last_downer_bar == 10):

        '''
        if (tmp_position != self.position):
            if (self.check_open_position(tmp_position) == True):
                self.set_position(tmp_position)

    def check_open_position(self, new_pos):
        cur_bar = self.get_current_minute_bar()
        #控制间隔
        if ((cur_bar-self.entry_bar<10) or (cur_bar-self.exit_bar<10)):
            return False
        #窄幅
        return True

    def on_event(self, event_name, e_param):
        if (event_name == StgEvent.DownTrendBreak):
            self.set_trade_direction(TradeDirection.BUYSELL)
        elif (event_name == StgEvent.UpTrendBreak):
            self.set_trade_direction(TradeDirection.BUYSELL)
        elif (event_name == StgEvent.WalkStep):
            if (e_param == WalkStep.FarAwayBottom):
                self.far_from_bottom()
            elif (e_param == WalkStep.FarAwayTop):
                self.far_from_top()
            elif (e_param == WalkStep.InBottom):
                pass
            elif (e_param == WalkStep.ToBottom):
                self.to_bottom()
            elif (e_param == WalkStep.ToTop):
                self.to_top()

    def monitor(self):
        #赶顶、赶底

        #达到atr
        atr_inday = self.get_indor_value(Indicator.AtrInday)
        atr_daily = self.get_indor_value(Indicator.AtrDaily)
        
        if (atr_inday - atr_daily > -10):
            self.set_up_count(120)
            self.set_down_count(120)

    def far_from_top(self):
        self.set_up_count(120)
        self.set_down_count(120)
        #self.set_trade_direction(TradeDirection.BUYSELL)

    def far_from_bottom(self):
        self.set_up_count(120)
        self.set_down_count(120)
        #self.set_trade_direction(TradeDirection.BUYSELL)

    def to_bottom(self):
        if (self.cur_bar > 120):
            self.set_down_count(120)
        else:
            self.set_down_count(60)
        self.set_up_count(45)
        self.set_trade_direction(TradeDirection.SELLONLY)

    def to_top(self):
        if (self.cur_bar > 120):
            self.set_up_count(120)
        else:
            self.set_up_count(60)
        self.set_down_count(45)
        self.set_trade_direction(TradeDirection.SELLONLY)

    '''
    def mointor(self, klines):
        #监控行情情况，不断更新cond_cond_up_count, cond_cond_down_count
        if (self.ups > 210):
    '''

'''
from tqsdk import TqApi
from back_test import StrategyManagerTest

api = TqApi()
stg_m = StrategyManagerTest()
klines = api.get_kline_serial("SHFE.rb2010", 60, 500)
tank = KillerTank(stg_m)
#225
for i in range(1, 200):
    index = 200 -i 
    tank.on_bar(klines, 90, 30, index,225)

while True:
    api.wait_update()
'''