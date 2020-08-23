#基于事件统计分析
#充当全局事件记录器
#基于event、参考指标indicator
#事件标定优先级
#根

'''
#mc_pattern 负责产生
#kpattern_record 负责记录，初期pattern不全部来自mc_pattern
'''

from strategy_base import StrategyBase
from kpattern_record import KPatternRecord
from mc_pattern import McPattern
from param_defines import Indicator, TrendType, StgEvent, BarType
from kpattern.trade_factory import TradeFactory
from kpattern.kpattern_matching import KpatternMatchingModule
import copy

class StrategyEventDrive(StrategyBase):
    def __init__(self):
        #self.min_pt_recorder = KPatternRecord("min", 1)
        #self.day_pt_recorder = KPatternRecord("day", 0)
        self.pt_recorder = KPatternRecord("day")
        self.pt_factory = McPattern()
        self.kpmatching = KpatternMatchingModule()

        self.start()

    def close(self):
        self.pt_recorder.clear()

    def on_event(self):
        pass
    '''
    def on_indicator(self):
        #将指标转化成时间
        pass
    '''
    def on_indicator(self, indictor, value):
        #self.pt_factory.drive_indor(indictor, value)
        self.pt_factory.drive_indicator(indictor, value)

    def on_kpattern(self, pattern):
        pt = copy.deepcopy(pattern)
        self.pt_recorder.add(pt)

    def on_dkpattern(self, pattern):
        pt = copy.deepcopy(pattern)
        self.pt_recorder.add(pt)

    def on_day_bar(self, dkline):
        pass

    def find_(self):
        pass
        #back
        #up_mode = []
        #find
   
    def on_bar(self, klines):
        '''
        if (self.cur_bar == 5):
            self.parse_pattern()
        '''
        self.pt_factory.on_bar(klines)

    def on_bar5(self):
        pass

     #写好后放到watcher里一份
    def parse_pattern(self):
        t_type = self.pt_recorder.get_trend_type(0)
        if (t_type == TrendType.StrongUp):
            self.strong_up()
        else:
            self.strong_down()

    def find(self):
        pass

    # StrongUp: Only Buy
    # up: 低1/3Atr buy; BuyLowRange At Bottom; 
    # wave: 
    # down: 
    # StrongDown: Only Sell
    def aa(self):

        pass

    def strong_up(self):
        target_profit = self.get_indor_value(Indicator.PreBuyProfit)
        task = TradeFactory.create_target_buy_task("StrongUpTask", target_profit)
        self.addTradeTask(task)
    
    def up(self):
        pass

    def wave(self):
        pass

    def down(self):

        pass

    def strong_down(self):
        target_profit = self.get_indor_value(Indicator.PreBuyProfit)
        task = TradeFactory.create_target_sell_task("StrongDownTask", target_profit)
        self.addTradeTask(task)

    def monitor_event(self):
        #寻找日线和日内的错位
        actions = self.kpmatching.find_and_get_action(StgEvent.BigUp, BarType.MIN)
        if (actions == None):
            return

        size = len(actions)
        if (size == 0):
            return

        print(actions)
'''
1. 顶部、顶部的Bigbang
2. 关键位置折回后的前2~3个交易日
3. 
'''