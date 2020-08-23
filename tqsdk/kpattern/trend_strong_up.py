#强势上涨
'''
条件
1. 支撑线
2. 回调横盘的底部，特别要抓住急调
出
1. 升上平台后， 2~5个bar，高点出，低点接回来
#找支持，找
'''
from kpattern.trend_base import TrendBase
from param_defines import StgEvent, MyString, Indicator
from kpattern.kcommon import TradeTask, EventSampleCondition, UpperLimitCondition, RangeCondition

class TrendStrongUp(TrendBase):
    def __init__(self):
        gain_cond = self.create_default_gain_exit_cond()

        # over avg and in range bottom
        up_task1 = TradeTask("OverAvgInRgeBot", MyString.Buy, self.clock.cur_bar, 300, 300)
        avg_cond = EventSampleCondition(StgEvent.OverAvgLineAtOpen, 1, 0,60)
        btm_cond = EventSampleCondition(StgEvent.InRangeBottom, 2, 0, 100)

        up_task1.addEntryCond(avg_cond)
        up_task1.addEntryCond(btm_cond)
        up_task1.addGainExitCond(gain_cond)
        self.add_default_exit_cond(up_task1)
        #v and inrange bottom
        up_task2 = TradeTask("VInRgeBot", MyString.Buy, self.clock.cur_bar, 300, 300)
        avg_cond = EventSampleCondition(StgEvent.RushBottomAndBack, 1, 10, 360)
        btm_cond = EventSampleCondition(StgEvent.InRangeBottom, 2, 0, 100)
        up_task2.addEntryCond(avg_cond)
        up_task2.addEntryCond(btm_cond)
        up_task2.addGainExitCond(gain_cond)
        self.add_default_exit_cond(up_task2)
        # far from day_bottom and in range bottom
        up_task3 = TradeTask("farFromLL", MyString.Buy, self.clock.cur_bar, 300, 300)
        away_cond = EventSampleCondition(StgEvent.FarFromLL, 1, 0, 500)
        downs_cond = UpperLimitCondition(Indicator.Downs, 2, 20)
        ck = RangeCondition(Indicator.CheckSum15, 3, -6, 6)
        up_task3.addEntryCond(away_cond)
        up_task3.addEntryCond(downs_cond)
        up_task3.addEntryCond(ck)
        up_task3.addGainExitCond(gain_cond)
        self.add_default_exit_cond(up_task3)
    #对应20200725
    def if_over_avgline_at_open(self):
        pass
        #self.create_buy_task()

    def if_faraway_bottom(self):
        pass

    def if_in_range_bottom(self):
        pass

    def if_(self):
        pass