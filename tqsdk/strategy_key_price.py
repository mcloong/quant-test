#关键价格
#同时只能有一个
#突破和折回，两个交易方向
#来自于：
# ma线，boll线，压力、阻力线
# 整数值
#      
from strategy_base import StrategyBase
import pplib
from tqsdk import tafunc
from k_parser import KParser
from param_defines import ParamUnion, StgEvent, Indicator
from utils.price_tools import PriceCombine

class StrategyKeyPrice(StrategyBase):
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyKeyPrice", manager)
        self.TAG = "StrategyKeyPrice"
        self.key_price = 0

        self.inited = False 
        self.init_price_state = 0

        self.KEY_MA = 1
        self.KEY_STRONG = 2
        self.KEY_GOOG_NUM = 3

        self.auto = True

        self.KParser = KParser()

        self.debug("running..........")

    def init_data(self):
        if (self.ask_price > self.key_price):
            self.init_price_state = 1
        else:
            self.init_price_state = -1

    def set_key_price(self,price):
        self.key_price = price
        self.inited = False
        self.auto = False

    def on_tick(self, serial):
        if (self.run_flag == False or self.key_price == 0):
            return
        StrategyBase.on_tick(self, serial)
        if (self.inited == False):
            self.init_data()
            self.inited = True
        
        if (abs(self.ask_price - self.key_price) > 30):
            return

        #防止一启动就达到关键位置（参数未更新）
        if (self.init_price_state == 1 and abs(self.ask_price - self.key_price+15)<11):
            self.mark_bar = self.get_current_minute_bar()
        elif (self.init_price_state == -1 and abs(self.ask_price - self.key_price)<11):
            self.mark_bar = self.get_current_minute_bar()

    def on_bar(self, klines):
        if (self.run_flag == False or self.key_price == 0):
            return
        StrategyBase.on_bar(self, klines)

        if (abs(self.ask_price - self.key_price)>30
            and self.mark_bar == 0):
            return
            #lt = self.get_real_time()
        if (self.mark_bar != 0 and self.init_price_state==1): #上云盖
            cur_bar = self.get_current_minute_bar()
            hh = pplib.get_hest_in_range(self, 1, 30)
            #阻击
            if (cur_bar - self.mark_bar < 30 and self.position != -1):
                #c_sum_10 = pplib.get_checksum(klines, 10, 1)
                #avg_10 = pplib.get_avg_price(klines, 10)
                if (cur_bar - self.mark_bar < 5 and hh - self.ask_price < 20):
                    avg_6 = pplib.get_avg_price(klines, 6)
                    c_sum_8 = pplib.get_checksum(klines, 8, 1)
                    if (abs(avg_6 - self.key_price)<10):
                        self.set_position(-1)
                elif (cur_bar - self.mark_bar > 5 and hh - self.ask_price < 20):
                    avg_6 = pplib.get_avg_price(klines, 6)
                    c_sum_10 = pplib.get_checksum(klines, 10, 1)
                    if (self.key_price - avg_6 > -5 and self.key_price - avg_6 < 14 and abs(c_sum_10)<4):
                        self.set_position(-1)
            #顺势
            elif (cur_bar - self.mark_bar > 30 and self.position != 1):
                c_sum_10 = pplib.get_checksum(klines, 10, 1)
                avg_10 = pplib.get_avg_price(klines, 10)
                if (avg_10 > self.key_price and abs(c_sum_10) < 4):
                    self.set_position(1)
            
        if (self.mark_bar != 0 and self.init_price_state==-1): #上云盖
            cur_bar = self.get_current_minute_bar()
            ll = pplib.get_lest_in_range(self, 1, 30)
            #阻击
            if (cur_bar - self.mark_bar < 30 and self.position != 1):
                #c_sum_10 = pplib.get_checksum(klines, 10, 1)
                #avg_10 = pplib.get_avg_price(klines, 10)
                if (cur_bar - self.mark_bar < 5 and ll - self.ask_price < 20):
                    avg_6 = pplib.get_avg_price(klines, 6)
                    c_sum_8 = pplib.get_checksum(klines, 8, 1)
                    if (abs(avg_6 - self.key_price)<10 and abs(c_sum_8)<4):
                        self.set_position(1)
                elif (cur_bar - self.mark_bar > 5 and ll - self.ask_price < 20):
                    avg_6 = pplib.get_avg_price(klines, 6)
                    c_sum_10 = pplib.get_checksum(klines, 10, 1)
                    if (avg_6 - self.key_price > -5 and avg_6 - self.key_price < 14 and abs(c_sum_10)<4):
                        self.set_position(1)
            #顺势
            elif (cur_bar - self.mark_bar > 30 and self.position != -1):
                c_sum_10 = pplib.get_checksum(klines, 10, 1)
                avg_10 = pplib.get_avg_price(klines, 10)
                if (avg_10 < self.key_price and abs(c_sum_10) < 4):
                    self.set_position(1)

        if (self.cur_bar > 10):
            self.check_key_price(klines)

    def on_day_bar(self, dklines):
        self.ma10day =  0
        ma = tafunc.ma(dklines.close, 20)
        self.ma20day = ma.iloc[-1]
        self.ma30day =  0
        self.key_ma = 0
        
        self.debug("key_price = %d"%(self.key_price))
        if (self.key_price != 0):
            return
        #理论上用不到了，用KParser
        #get ma20 price
        if (dklines.iloc[-1].close > self.ma20day):
            last_crossup_ma = 30
            for i in range(1, 30):
                if (dklines.iloc[-i].low > ma.iloc[-i]
                    and dklines.iloc[-(i+1)].low <= ma.iloc[-i]):
                    last_crossup_ma = i
                    break
            if (last_crossup_ma > 10): #支撑
                #self.key_price = self.ma20day
                self.key_ma = self.ma20day
        elif (dklines.iloc[-1].close < self.ma20day):
            last_crossdown_ma = 30
            for i in range(1, 30):
                if (dklines.iloc[-i].high < ma.iloc[-i]
                    and dklines.iloc[-(i+1)].high >= ma.iloc[-i]):
                    last_crossdown_ma = i
                    break
            if (last_crossdown_ma > 10): #阻力
                #self.key_price = self.ma20day
                self.key_ma = self.ma20day
            #    self.key_price = self.ma20day

        #获取反复触及的线
        high_id = pplib.get_key_high_bar(dklines, 10)
        low_id = pplib.get_key_low_bar(dklines, 10)
        self.debug("hh_hard_touch high_id=%d"%(high_id))
        self.debug("ll_hard_touch low_id=%d"%(low_id))
        self.hh_hard_touch = 0
        self.ll_hard_touch = 0
        if (high_id < low_id and high_id < 5):
            self.hh_hard_touch = dklines.iloc[-high_id].high
            self.debug("hh_hard_touch=%d"%(self.hh_hard_touch))
        elif (low_id < high_id and low_id < 5):
            self.ll_hard_touch = dklines.iloc[-low_id].low
            self.debug("ll_hard_touch=%d"%(self.ll_hard_touch))

        self.KParser.on_bar(dklines)
        self.find_key_mode()
        kp_event = self.KParser.generate_event(dklines)
        self.boardcast_kpevent(kp_event)
        day_price = dklines.iloc[-1].close
        self.key_ll_ma = self.KParser.get_last_key_ll_price(day_price, 5)
        self.key_hh_ma = self.KParser.get_last_key_hh_price(day_price, 5)

        #平均price, 计算key
        priceCombine = PriceCombine()
        priceCombine.refer_price = day_price
        priceCombine.min_diff = -10
        priceCombine.max_diff = 100
        priceCombine.add(self.key_hh_ma)
        priceCombine.add(self.hh_hard_touch)
        key_hh = priceCombine.get()

        priceCombine.min_diff = -100
        priceCombine.max_diff = 10
        priceCombine.add(self.key_ll_ma)
        priceCombine.add(self.ll_hard_touch)
        key_ll = priceCombine.get()
        self.debug("final_key_hh=%d, final_key_ll=%d"%(key_hh, key_ll))

        if (key_hh != 0):
            self.set_indor_value(Indicator.KeyHHPrice, key_hh)
        if (key_ll != 0):
            self.set_indor_value(Indicator.KeyLLPrice, key_ll)

    def boardcast_kpevent(self, kp_events):
        for kpt in kp_events:
            kpt.author = self.TAG
            self.manager.drive_kpattern(kpt)


    def check_key_price(self, klines):
        if (self.auto == False):
            return False

        parser_hh = self.KParser.get_last_key_hh_price(self.ask_price, 3)
        parser_ll = self.KParser.get_last_key_ll_price(self.ask_price, 3)
        if (parser_hh != -1 and abs(self.ask_price - parser_hh) < 20):
            self.key_price = parser_hh
            self.debug("new self.key_price=%d"%(self.key_price))
            if (klines[-1].high >= parser_hh and klines[-2] < parser_hh):
                name = self.KParser.get_last_key_hh_name(self.ask_price, 3)
                param = ParamUnion()
                param.put_param("name", name)
                self.manager.on_event(StgEvent.CrossOverHKey, param)

        if (parser_ll != -1 and abs(self.ask_price - parser_ll) < 20):
            self.key_price = parser_ll
            self.debug("new self.key_price=%d"%(self.key_price))
            if (klines[-1].low <= parser_ll and klines[-2] > parser_ll):
                name = self.KParser.get_last_key_ll_name(self.ask_price, 3)
                param = ParamUnion()
                param.put_param("name", name)
                self.manager.on_event(StgEvent.CrossUnderLKey, param)

    # 发现重要模式
    #
    def find_key_mode(self):
        pass

    def set_observate_period(self, period):
        pass