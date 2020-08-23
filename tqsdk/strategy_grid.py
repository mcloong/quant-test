from param_defines import TradeDirection
from pplib import get_avg_price ,get_checksum
from datetime import datetime
import time
from param_defines import StrategyKpi,WalkPath
from strategy_base import StrategyBase

class StrategyGrid(StrategyBase):
    def __init__(self, symbol, managerager, HH2, HH1, LL1, LL2):
        StrategyBase.__init__(self, symbol, "StrategyGrid", managerager)
        self.TAG = "StrategyGrid"
        self.FLOW_GAP_BAR = 3
        self.MAX_HOLD = 100

        self.HH2 = HH2
        self.HH1 = HH1
        self.LL1 = LL1
        self.LL2 = LL2

        self.run_flag = True
        self.h_break_flag = False
        self.l_break_flag = False
        self.cur_price_flag = 0
        
        self.price_immediate = False

        self.H2_breakout_flag = False
        self.H2_breakout_index = 0
        self.L2_breakout_flag = False
        self.L2_breakout_index = 0

        self.mark_bar = 0

        self.report_flag = 0

        self.STD_CHECHSUM = 5

        print("[%s] runing............"%(self.TAG))
        print("[%s] hh2=%d hh1=%d ll1=%d ll2=%d"%(self.TAG, self.HH2, self.HH1, self.LL1, self.LL2))

    def get_name(self):
        return self.TAG

    def set_params(self,HH2, HH1, LL1, LL2):
        pass
    
    def new_day(self):
        pass

    def set_price_immediate(self, doit):
        self.price_immediate = doit

    def update_price(self,ask_price, bid_price):
        if (ask_price <= self.LL1):
            self.buy()
        elif (bid_price >= self.HH1):
            self.sell()

    def on_tick(self, serial):
        if (self.run_flag == False):
            return
        StrategyBase.on_tick(self, serial)

    def on_tick2(self, ask_price, bid_price, avg_price):
        if (self.run_flag == False):
            return

        self.ask_price = ask_price
        self.bid_price = bid_price
        self.avg_price = avg_price

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)

        if (self.run_flag == False):
            return
        cur_bar = self.get_current_minute_bar()
        avg_price = get_avg_price(klines, 5)
        s_checksum = get_checksum(klines, 5, 1) # short
        l_checksum = get_checksum(klines, 30, 1) # long
        
        tmp_position = self.position
        high = klines.iloc[-1].high
        low = klines.iloc[-1].low
        lt = self.get_real_time()
        #if (lt.tm_min%2==0 and lt.tm_sec==0):
        #    print("[%s] avg_price=%d s_checksum=%d l_checksum=%d "%(self.TAG, avg_price, s_checksum, l_checksum))

         #更新数据
        if (high >= self.HH2 ):
            self.cur_price_flag = 2
            self.mark_bar = cur_bar
        elif (high >= self.HH1):
            self.cur_price_flag = 1
            self.mark_bar = cur_bar
        elif (low <= self.LL2):
            self.cur_price_flag = -2
            self.mark_bar = cur_bar
        elif (high <= self.LL1):
            self.cur_price_flag = -1
            self.mark_bar = cur_bar

        # 到达
        if (avg_price >self.HH2):
            if  (self.position < 0 and abs(s_checksum)<self.STD_CHECHSUM):
                tmp_position = 0
                self.debug("[decision] tmp_position=0 (avg_price >self.HH2)")
            self.trade_dir = TradeDirection.BUYONLY
        elif (avg_price > self.HH1 and abs(s_checksum)<5):
            if (self.position ==0 and abs(s_checksum)<5):
                tmp_position = -1
                self.debug("[decision] tmp_position=-1 (avg_price > self.HH1)")
        elif (avg_price < self.LL2):
            if (self.position == 1 and abs(s_checksum) <5):
                tmp_position = 0
                self.debug("[decision] tmp_position=0 (avg_price < self.LL2)")
            self.trade_dir = TradeDirection.SELLONLY
        elif (avg_price < self.LL1 and abs(s_checksum)<5):
            if(self.position <= 0):
                tmp_position = 1
                self.debug("[decision] tmp_position=1 (avg_price < self.LL1)")

        #出场
        #均线到达
        if (self.cur_price_flag >= 1 and cur_bar-self.mark_bar>2):
            if (self.position > 0 and avg_price > self.HH1 and avg_price < self.HH2):
                tmp_position = 0
                self.debug("[decision] tmp_position=0 (多屏)")
        elif (self.cur_price_flag <= -1 and cur_bar-self.mark_bar>2):
            if (self.position < 0 and avg_price < self.LL1 and avg_price > self.LL2):
                tmp_position = 0
                self.debug("[decision] tmp_position=0 (空瓶)")
        #
        #时间过长
        if (cur_bar - self.entry_bar >= self.MAX_HOLD and self.position != 0):
            m_checksum = get_checksum(klines, 10, 1) # short
            if (self.position > 0 and abs(m_checksum) < 2):
                tmp_position = 0
                self.debug("[decision] tmp_position=0 (多太长)")
            if (self.position < 0 and abs(m_checksum) < 2):
                tmp_position = 0
                self.debug("[decision] tmp_position=0 (空太长)")
       
        # 
        if (tmp_position != self.position):
            self.set_position(tmp_position)

    def run(self, klines, ask_price, bid_price, avg_price):
        if (self.run_flag == False):
            return

        lt = time.localtime(time.time())
        if (lt.tm_sec==1):
            return

        self.ask_price = ask_price
        self.bid_price = bid_price

        if (self.price_immediate == True):
           self.update_price(ask_price, bid_price)

        self.on_bar(klines)
        '''
        cur_bar = get_current_minute_bar()
        avg_price = get_avg_price(klines, 5)
        s_checksum = get_checksum(klines, 5, 1) # short
        l_checksum = get_checksum(klines, 30, 1) # long
        
        tmp_position = self.position
        high = klines.iloc[-1].high
        low = klines.iloc[-1].low

        if (lt.tm_min%2==0 and lt.tm_sec==0):
            print("[%s] avg_price=%d s_checksum=%d l_checksum=%d "%(self.TAG, avg_price, s_checksum, l_checksum))

        # 到达
        if (avg_price >self.HH2):
            if  (self.position < 0 and abs(s_checksum)<5):
                tmp_position = 0
            self.trade_dir = TradeDirection.BUYONLY
        elif (avg_price > self.HH1 and abs(s_checksum)<5):
            if (self.position ==0 and s_checksum <2):
                tmp_position = -1
        elif (avg_price < self.LL2):
            if (self.position == 1 and s_checksum <-2):
                tmp_position = 0
            self.trade_dir = TradeDirection.SELLONLY
        elif (avg_price < self.LL1 and abs(s_checksum)<2):
            if(self.position <= 0):
                tmp_position = 1

        #出场
        if (self.cur_price_flag >= 1 and cur_bar-self.mark_bar>2):
            if (self.position > 0 and avg_price < self.HH1):
                tmp_position = 0
        elif (self.cur_price_flag <= -1 and cur_bar-self.mark_bar>2):
            if (self.position < 0 and avg_price > self.LL1):
                tmp_position = 0

        #时间过长
        if (self.entry_bar >= self.MAX_HOLD and self.position != 0):
            m_checksum = get_checksum(klines, 10, 1) # short
            if (self.position > 0 and abs(m_checksum) < 2):
                tmp_position = 0
            if (self.position < 0 and abs(m_checksum) < 2):
                tmp_position = 0
        #更新数据
        if (high >= self.HH2 ):
            self.cur_price_flag = 2
            self.mark_bar = get_current_minute_bar()
        elif (high >= self.HH1):
            self.cur_price_flag = 1
            self.mark_bar = get_current_minute_bar()
        elif (low <= self.LL2):
            self.cur_price_flag = -2
            self.mark_bar = get_current_minute_bar()
        elif (high <= self.LL1):
            self.cur_price_flag = -1
            self.mark_bar = get_current_minute_bar()
        # 
        if (tmp_position != self.position):
            self.set_position(tmp_position)
        '''

    '''
    def set_position(self, pos):
        #print("[%s] set_position pos=%d"%(self.TAG, pos))
        real_price = self.ask_price
        if (pos > 0):
            real_price = self.ask_price
        elif (pos < 0):
            real_price = self.bid_price
        else:
            if (self.position <0):
                real_price = self.ask_price
            else:
                real_price = self.bid_price

        if(pos > 0 and self.trade_dir == TradeDirection.SELLONLY and self.position !=0):
            if (self.position > 0):
                msg = "平多 price="%(real_price)
            else:
                 msg = "平空 price="%(real_price)
            self.manager.set_position(self.TAG, 0)
            self.position = 0
            self.logger.info(self.TAG, msg)
            self.my_print(msg)
        elif(pos < 0 and self.trade_dir == TradeDirection.BUYONLY and self.position !=0):
            self.manager.set_position(self.TAG,0)
            self.position = 0
            if (self.position > 0):
                msg = "平多 price="%(real_price)
            else:
                 msg = "平空 price="%(real_price)
            self.logger.info(self.TAG, msg)
            self.my_print(msg)
        else:
            if (pos > 1):
                pos = 1
            elif (pos < -1):
                pos = -1
            if (pos != 0):
                self.entry_bar = get_current_minute_bar()
                self.entry_price = real_price
            if (pos > 0):
                msg = "开多 position=%d price=%d"%(self.position, real_price)
            elif (pos < 0):
                msg = "开空 position=%d price=%d"%(self.position, real_price)
            elif (pos == 0 and self.position > 0):
                msg = "平多 position=%d price=%d"%(self.position, real_price)
            elif (pos == 0 and self.position < 0):
                msg = "平空 position=%d price=%d"%(self.position, real_price)
            self.logger.info(self.TAG, msg)
            self.my_print(msg)
            self.manager.set_position(self.TAG, pos)
            self.position = pos
    '''
    #检查这个价格在策略中持仓情况
    def check_price(self):
        pass

    def report_event(self, avgprice):
        if (avgprice > self.HH2 and self.report_flag < 2):
            if (self.report_flag < 0):
                self.report_flag = 0
            self.report_flag = self.report_flag + 1
            self.manager.report_kpi(self.TAG, StrategyKpi.InEffective)
            self.manager.report_walkpath(self.TAG, WalkPath.RangeBreakUp)
        
        if (avgprice < self.LL2 and self.report_flag > -2):
            if (self.report_flag > 0):
                self.report_flag = 0
            self.report_flag = self.report_flag - 1

    def buy(self):
        if (self.position < 0):
            self.position = 0
        if (self.trade_dir == TradeDirection.SELLONLY):
            return
        else:
           self.position = 1
        self.manager.set_position(self.position)

    def sell(self):
        if (self.position > 0):
            self.position = 0
        if (self.trade_dir == TradeDirection.BUYONLY):
            return
        else:
            self.position = -1
        self.manager.set_position(self.position)

    def timer_task(self):
        pass

    def set_h2(self, h2):
        self.HH2 = h2

    def set_h1(self, h1):
        self.HH1 = h1

    def set_l1(self, l1):
        self.LL1 = l1

    def set_l2(self, l2):
        self.LL2 = l2

    def loss_happend(self, t_dir, loss_p):
        StrategyBase.loss_happend(self, t_dir, loss_p)
        self.debug("loss hanpend t_dir=%d loss_money=%d"%(t_dir, loss_p))
        if (abs(loss_p) > 19 and t_dir > 0):
            self.LL1 = self.LL2 - 10
            self.LL2 = self.LL1 - 25
            self.trade_dir = TradeDirection.SELLONLY
        elif (abs(loss_p) > 19 and t_dir < 0):
            self.HH1 = self.HH2 + 10
            self.HH2 = self.HH1 + 25
            self.trade_dir = TradeDirection.BUYONLY

    '''
    def set_trade_direction(self, dir):
        self.trade_dir = dir
    '''
    