from kpattern.trend_base import TrendBase
from param_defines import StgEvent, MyString, Indicator
from kpattern.kcommon import TradeTask, EventSampleCondition, UpperLimitCondition, RangeCondition

class TrendWaveInStrongUp(TrendBase):
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
        up_task2 = TradeTask("OverAvgInRgeBot", MyString.Buy, self.clock.cur_bar, 300, 300)
        avg_cond = EventSampleCondition(StgEvent.RushBottomAndBack, 1, 10, 360)
        btm_cond = EventSampleCondition(StgEvent.InRangeBottom, 2, 0, 100)
        up_task2.addEntryCond(avg_cond)
        up_task2.addEntryCond(btm_cond)
        up_task2.addGainExitCond(gain_cond)
        self.add_default_exit_cond(up_task2)