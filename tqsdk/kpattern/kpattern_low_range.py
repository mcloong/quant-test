import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")

from kpattern.kpattern_base import KPattern, BarType
from param_defines import StgEvent, Indicator

class KPLowRange(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.LowRange, 0)
        self.std_range_height = 15
        self.std_range_width = 15
        self.indor = Indicator.PresetStdRangeWidth

        self.range_height = 0
        self.range_width = 0

    def drive_indor(self, indor, value):
        if (indor == self.indor):
            self.range_height = value
        if (indor == Indicator.StdRangeWidth):
            self.range_width = value
        if (self.range_height!=0 and self.range_width!=0):
            if (self.range_width >= self.std_range_width and self.range_height <= self.std_range_height):
                self.result = True
        
class KPLowRangeAtBottom(KPLowRange):
    def __init__(self):
        KPattern.__init__(self, StgEvent.LowRangeAtBottom, 0)
        self.pri_pos = 0

    def drive_indor(self, indor, value):
        KPLowRange.drive_indor(self, indor, value)
        if (indor == Indicator.PricePosition):
                self.pri_pos = value
        if (self.result):
            if (self.pri_pos != 0 and self.pri_pos <= 20):
                self.score = self.pri_pos
                self.ok()
            else:
                self.reset()
    
class KPLowRangeAtTop(KPLowRange):
    def __init__(self):
        KPattern.__init__(self, StgEvent.LowRangeAtTop, 0)
        self.pri_pos = 0

    def drive_indor(self, indor, value):
        KPLowRange.drive_indor(self, indor, value)
        if (indor == Indicator.PricePosition):
                self.pri_pos = value
        if (self.result):
            if (self.pri_pos != 0 and self.pri_pos >= 80):
                self.score = self.pri_pos
                self.ok()
            else:
                self.reset()
            
class KPLowRangeAtMiddle(KPLowRange):
    def __init__(self):
        KPattern.__init__(self, StgEvent.LowRangeAtTop, 0)
        self.pri_pos = 0

    def drive_indor(self, indor, value):
        KPLowRange.drive_indor(self, indor, value)
        if (indor == Indicator.PricePosition):
                self.pri_pos = value
        if (self.result):
            if (self.pri_pos != 0 and self.pri_pos >= 80):
                self.score = self.pri_pos
                self.ok()
            else:
                self.reset()