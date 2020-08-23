'''
last_cross 不是越大越好，最好是倾斜的向上或向下，上次到达均线位置的时间也不长
防止上下是两个半场，比如上半场都在均线下，下半场都在均线上
必须限定开仓价格，在均线上下10个点之内，不然和其他策略重复了
'''
from pplib import get_checksum,get_hest_in_range
from tool_utils import get_minute,get_second
from strategy_base import StrategyBase
from param_defines import TradeDirection
from datetime import datetime
import time
import pplib

class StrategyAvgCross(StrategyBase):
    def  __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyAvgCross", manager)

        self.MAX_HOLD = 159
        self.interval_bar = 20

        self.cross_avg_run_flag = 0
        self.total_bars_inday = 4*60 - 15

        self.short_term = 10
        self.long_term = 30

        self.init_crs_downs= 0
        self.init_crs_overs = 0

        self.trade_dir = TradeDirection.BUYSELL
        self.TAG = "StrategyAvgCross"

        #=============================================#
        self.lastday_bar = 2
        self.hh_20 = 0
        self.ll_20 = 0
        self.to_hh_20_bar = 0
        self.to_ll_20_bar = 0

        self.d_hh_3 = 0
        self.d_hh_3_bar = 0
        self.d_ll_3 = 0
        self.d_ll_3_bar = 0

        self.last_crossdown_bar = 999
        self.last_crossover_bar = 999

        print("[%s] runing............"%(self.TAG))

    def preset(self, crs_downs, crs_overs, last_crs_down, last_crs_up):
        self.init_crs_downs = crs_downs
        self.init_crs_overs = crs_overs
    
    def get_crs_downs(self):
        return self.init_crs_overs + self.avg_recorder.bars_of_over
    
    def get_crs_overs(self):
        self.init_crs_overs

    def set_avg_recorder(self, avg_recorder):
        print ("[%s] set_avg_recorder"%(self.TAG))
        self.avg_recorder = avg_recorder
    
    def make_decision(self):
        score = 0

        degree = self.manager.get_trade_direction_degree()

    def short_nowait(self):
        pass

    def long_nowait(self):
        pass

    def make_short(self):
        pass

    def make_long(self):
        pass

    def run(self, klines, bid_price, ask_price, avg_price):
        if (self.run_flag == False):
            return
        StrategyBase.run(self, klines, bid_price, ask_price, avg_price)
        self.on_bar(klines)
    
    '''
    def on_bar10(self, klines):

        last_crossdown_bar = self.avg_recorder.get_last_cross_under(klines, 2)
        last_crossover_bar = self.avg_recorder.get_last_cross_over(klines, 2)
        overs = self.avg_recorder.bars_of_over(klines)
        downs = self.avg_recorder.bars_of_under(klines)
        s_checksum = get_checksum(klines, self.short_term, 1)
        l_checksum = get_checksum(klines, self.long_term, 1)

        msg = "[last_crossdown_bar=%d, last_crossdown_bar=%d, overs=%d, downs=%d, s_checksum=%d, l_checksum=%d"%(last_crossdown_bar, 
                last_crossdown_bar, overs, downs, s_checksum, l_checksum)
    
        self.info(msg)
    '''

    def on_day_bar(self, dklines):
        lastday_bar = 2
        hh_30, to_hh_30_bar = pplib.get_hest_in_range2(dklines, 2, 30)
        ll_30, to_ll_30_bar = pplib.get_lest_in_range2(dklines, 2, 30)
        
        self.hh_30 = hh_30
        self.ll_30 = ll_30
        self.to_hh_30_bar = to_hh_30_bar
        self.to_ll_30_bar = to_ll_30_bar

        self.d_hh_3, self.d_hh_3_bar = pplib.get_hest_in_range2(dklines, 2, 2+3)
        self.d_ll_3, self.d_ll_3_bar = pplib.get_lest_in_range2(dklines, 2, 2+3)
    
    def on_bar(self, klines):
        #self.debug("====1111======")
        #print(self.TAG, self.run_flag)
        if (self.run_flag == False):
            return
        StrategyBase.on_bar(self, klines)

        lt = self.get_real_time()
        if (lt.tm_hour==21 and lt.tm_min<5):
            return
        # update 
        last_crossdown_bar = self.avg_recorder.get_last_cross_under(klines, 2)
        last_crossover_bar = self.avg_recorder.get_last_cross_over(klines, 2)
        overs = self.avg_recorder.bars_of_over(klines)
        downs = self.avg_recorder.bars_of_under(klines)
        s_checksum = get_checksum(klines, self.short_term, 1)
        l_checksum = get_checksum(klines, self.long_term, 1)
        cur_bar = self.get_current_minute_bar()

         # 弱势 提前
        hh_inday, hh_bar_inday = pplib.get_highest_bar_today2(klines) #不用替换_fix
        ll_inday, ll_bar_inday = pplib.get_lowest_bar_today2(klines)

        tmp_position = self.position

        if (last_crossover_bar > 20):
            self.cross_avg_run_flag = 1
        elif (last_crossdown_bar > 20):
            self.cross_avg_run_flag = -1
        else:
            self.cross_avg_run_flag = 0
        
        if (lt.tm_min%10 == 0):
            msg = "[last_crossdown_bar=%d, last_crossover_bar=%d, overs=%d, downs=%d, s_checksum=%d, l_checksum=%d"%(last_crossdown_bar, 
                last_crossover_bar, overs, downs, s_checksum, l_checksum)
            self.info(msg)
            self.debug(msg)
        #过滤
        #中途运行的情况
        if (overs + downs < 20):
            return
        #开
        
        if (self.position == 0 and lt.tm_hour <= 13): 
            ma10 = pplib.get_avg_price(klines,10)
            #用于区间突破 全程在线的一边
            if (last_crossover_bar < last_crossdown_bar and last_crossover_bar > 50 
                and ma10 > self.d_hh_3
                and self.position <= 0):
                self.debug("overs avg and over hh_3")
                tmp_position = 1
            elif (last_crossover_bar > last_crossdown_bar and last_crossdown_bar > 50 
                and ma10 < self.d_ll_3
                and self.position >= 0):
                self.debug("downs avg and down ll_3")
                tmp_position = -1
            degree = self.manager.get_market_prediction()
            #degree = 
            #数量
            dif = self.avg_price - self.ask_price
            if (abs(dif)<=12 and downs/cur_bar < 0.1 and abs(s_checksum)<5 and degree > 20):
                if (last_crossover_bar<15 and degree < 35):
                    tmp_position = 1
                    print("[%s] 多开 条件1 "%(self.TAG))
                if (last_crossdown_bar<20 and degree > 35): #均线以下
                    tmp_position = 1
                    print("[%s] 多开 条件2 "%(self.TAG))
            elif (abs(dif)<=12 and overs/cur_bar < 0.1 and abs(s_checksum)<5 and degree < -20):
                if (last_crossdown_bar<15 and degree > -35):
                    tmp_position = -1
                    print("[%s] 空开 条件1 "%(self.TAG))
                if (last_crossover_bar<20 and degree < -35): #均线以下
                    tmp_position = -1
                    print("[%s] 空开 条件2 "%(self.TAG))
            #峰度
            if (overs < downs/5 and degree<-50):
                if (l_checksum<-20 and last_crossdown_bar<5):
                    tmp_position = -1
                    print("[%s] 空开 条件3 "%(self.TAG))
            elif (downs < overs/5 and degree>35):
                if (l_checksum>20 and last_crossover_bar<5):
                    tmp_position = 1
                    print("[%s] 多开 条件3 "%(self.TAG))
            #趋向
            if (overs < downs/2 and degree<-35 and self.position >= 0):
                if (self.cross_avg_run_flag == -1 and abs(l_checksum)<5):
                #if (self.cross_avg_run_flag == -1)<5):
                    tmp_position = -1
                    self.debug("趋向 修正")
                    #ups = pplib.get_count_of_greater(klines, 50)
                    #if (ups > 30):
            elif (downs < overs/2 and degree>35 and self.position <=0):
                if (self.cross_avg_run_flag == 1 and abs(l_checksum)<5):
                    tmp_position = 1
                    self.debug("趋向 修正")
        
            #修正
            #或者根据degree来修正
            #if (cur_bar - hh_bar_inday > 60 and ll_bar_inday < hh_bar_inday and tmp_position >0):
            if (hh_bar_inday > 60 and tmp_position >0):
                tmp_position = 0
                print("[%s] degree来修正 "%(self.TAG))

            #if (cur_bar - ll_bar_inday > 60 and ll_bar_inday > hh_bar_inday and tmp_position<0):
            if (ll_bar_inday > 60 and tmp_position<0):
                tmp_position = 0
                print("[%s] degree来修正 "%(self.TAG))

        #===========================================#
        #*******************************************#
        # 对应20200601
        kpi_daily = self.get_kpi_daily()
        if (kpi_daily > 35 and self.position <=0 and overs>downs):
            if (last_crossdown_bar> 3 and last_crossdown_bar < 30):
                ups = pplib.get_count_of_greater(klines, 30)
                if (ups >= 5):
                    tmp_position = 1
                    self.debug("kpi_daily > 35 and crossdown")
        if (kpi_daily < -35 and self.position >=0 and overs<downs):
            if (last_crossover_bar> 3 and last_crossover_bar < 30):
                donws = pplib.get_count_of_less(klines, 30)
                if (downs >= 5):
                    tmp_position = -1
                    self.debug("kpi_daily < -35 and crossover")
        #===========================================#
        #*******************************************#
        #平
        #时间过长
        if (self.cur_bar - self.entry_bar >= self.MAX_HOLD and self.position != 0):
            m_checksum = get_checksum(klines, 10, 1) # short
            if (self.position > 0 and abs(m_checksum) < 2):
                ups = pplib.get_count_of_greater(klines, 60)
                if (ups > 30):
                    tmp_position = 0
                    print("[%s] 多平 时间过长 "%(self.TAG))
            if (self.position < 0 and abs(m_checksum) < 2):
                downs = pplib.get_count_of_less(klines, 60)
                if (downs > 30):
                    tmp_position = 0
                    print("[%s] 空平 时间过长 "%(self.TAG))

        if (self.position > 0 and last_crossdown_bar < last_crossover_bar
            and self.cur_bar - self.entry_bar > 30):
            ups = pplib.get_count_of_greater(klines, 50)
            if (ups > 29):
                tmp_position = 0
        # 前高点
        if (self.cur_bar - self.entry_bar > 20 and self.position>0):
            long_hh = pplib.get_hest_in_range(klines, 0, 60)#长期的高
            short_hh = pplib.get_hest_in_range(klines,0, 30)#短期的高
            m_checksum = get_checksum(klines, 20, 1) # short
            if (long_hh == short_hh and abs(m_checksum)<=3):
                tmp_position = 0
                print("[%s] 多平 前高点 "%(self.TAG))
        if (self.position > 0 and self.ask_price - self.entry_price > 48):
            tmp_position = 0
            self.debug("最大盈...")

        if (self.position < 0 and last_crossdown_bar > last_crossover_bar
            and self.cur_bar - self.entry_bar > 30):
            downs = pplib.get_count_of_less(klines, 50)
            if (downs > 29):
                tmp_position = 0
        # 前低点
        if (self.cur_bar - self.entry_bar > 20 and self.position<0):
            long_ll = pplib.get_lest_in_range(klines, 0, 60) #长期的高
            short_ll = pplib.get_lest_in_range(klines,0, 30) #短期的高
            m_checksum = get_checksum(klines, 20, 1) # short
            if (long_ll == short_ll and abs(m_checksum)<=3):
                tmp_position = 0
                print("[%s] 空平 前低点 "%(self.TAG))
        if (self.position<0 and self.entry_price - self.ask_price > 39):
            tmp_position = 0
            self.debug("最大盈...")

        if (tmp_position != self.position):
            if (tmp_position > 0):
                if (self.check_open_order(1, 10)):
                    self.set_position(tmp_position)
            elif (tmp_position < 0):
                if (self.check_open_order(-1, 10)):
                    self.set_position(tmp_position)
            else:
                self.set_position(tmp_position)

    def on_bar5(self):
        pass
        
    def update_price(self, bid_price, ask_price):
        pass

    # 0 ~ 100
    def fit_level(self):
        pass

    def timer_task(self):
        pass

    def matching_degree(self):
        return 0
    
    def my_print(self, msg):
        lt = time.localtime(time.time())
        print("[%s] %d-%d %d:%d:%d - :%s"%(self.TAG, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec, msg))