#
#预置该模型下，出现某些情况的处理机制 
#波动较大
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
from kpattern.trend_base import TrendBase
from param_defines import StgEvent, MyString, Indicator
from kpattern.kcommon import TradeTask, UpperLimitCondition, RangeCondition

#class PatternStrongUpLowRange(PatternBase):
class TrendWave(TrendBase):
    def __init__(self):
        TrendBase.__init__(self, "TrendWave")
        self.PatternLowRange = 0

    def buy_task(self):
        #顶部、底部
        #gain_cond = self.create_default_exit_cond()

        #in range bottom
        buy_task1 = self.create_in_range_bottom_buy_task(1)
        self.addTradeTask(buy_task1)
        #over avg
        buy_task2 = self.create_over_avgline_in_range_bottom_task(2)
        self.addTradeTask(buy_task2)

    def sell_task(self):
        pass

    def if_lastday_down(self):
        print("")
        pass

    def if_lastday_up(self):
        print("short at open ..")
        pass

    def if_getto_range_top(self):
        #if (self.cl)
        pass

    def if_getto_range_bottom(self):
        pass

    def if_bigbangBreakUp(self):
        
        #make_trade_condtion
        pass

    def if_break_weakdir(self):
        pass

    def if_break_strongdir(self):
        pass

    def if_getto_Hkey(self, value):
        print("pattern_wave: getto_Hkey value=%d"%(value))
        pass

'''
kclock = KClock
patternor = PatternWave()
evnt = [StgEvent.GetToHKey, 10]
patternor.on_event(evnt, kclock)
'''