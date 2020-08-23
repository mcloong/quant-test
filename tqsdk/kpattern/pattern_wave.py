#
#预置该模型下，出现某些情况的处理机制 
#波动较大
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
from kpattern.pattern_base import PatternBase
from param_defines import StgEvent
from kclock import KClock

#class PatternStrongUpLowRange(PatternBase):
class PatternWave(PatternBase):
    def __init__(self):
        PatternBase.__init__(self, "PatternWave")
        self.PatternLowRange = 0

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