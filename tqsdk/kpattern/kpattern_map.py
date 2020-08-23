import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from kpattern.kcommon import CondtionSet, UpperLimitCondition, LowerLimitCondition, RangeCondition
from param_defines import StgEvent, Indicator, MyString, MyDefaultValue, BarType
from kpattern.kpattern_base import KPOverAvgLineAtOpen,StdBackResetOfUp
from kpattern.kpattern_low_range import KPLowRange, KPLowRangeAtBottom, KPLowRangeAtTop, KPLowRangeAtMiddle

UpPatternAllDay = [StgEvent.BreakUpLongBottom]
StrongUpMode = [StgEvent.BackFromKeySupportLine, StgEvent.BackFromKeySupportPrice]
StrongDownMode = [StgEvent.BackFromKeyResistanceLine, StgEvent.BackFromKeyResistancePrice]
#涨半天
UpPatternHalfDay = []
RangePattern = []
DownPatternAllDay = []
DownPatternHalfDay = []

class TrendMap(object):
    def __init__(self):
        #长周期
        self.StrongUp = "bottom-BreakUp-LowRange-BreakUp-Wave-Top-DoubleM-Down" #踩到30均线
        self.WaveUp = "bottom-Up-MidDown-support-up-wave-M-Down" #踩到60均线
        self.StrongDown = "top-break-down-lowrange-break-down-wave-W-Up" 
        self.WaveDown = ""
        self.InRange = "LongUp-Wave-Bigbang-break" #顶部平台期
        #短周期
        self.S_WaveUp = "Low-Go-Up"
        self.S_WaveDown = "High-Go-Down"
        self.S_InRange = "Top-Mid-Bottom"

    def set_start_barid(self, barid):
        self.bar = barid

    def drive(self, klines):
        pass

class KPatternMap(object):
    def __init__(self):
        self.pattern_list = []
        self.pattern_list.append(KPOverAvgLineAtOpen)
        self.pattern_list.append(StdBackResetOfUp)
        self.pattern_list.append(KPLowRange)
        self.pattern_list.append(KPLowRangeAtBottom)
        self.pattern_list.append(KPLowRangeAtTop)
        self.pattern_list.append(KPLowRangeAtMiddle)

    #理论上在mc_pattern.py上产生
    '''
    #回调用于告知 新模式产生
    def set_callback(self):
        pass

    def drive_kline(self):
        pass

    def drive_event(self):
        for pt in self.pattern_list:
            pt.drive_indor

    def drive_indor(self, indor,value):
        pass

    def get_up_pattern(self):
        pass
    '''