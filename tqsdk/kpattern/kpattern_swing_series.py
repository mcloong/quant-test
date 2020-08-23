import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")

from kpattern.kpattern_base import KPattern, BarType
from param_defines import StgEvent, Indicator

class KPDoubleM(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.LowRange, 0)

class KPDoubleW(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.LowRange, 0)

class KPSwingHigh(KPattern):
    pass

class KPSwingLow(KPattern):
    pass