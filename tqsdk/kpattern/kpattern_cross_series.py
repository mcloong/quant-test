from kpattern.kpattern_base import KPattern
from param_defines import StgEvent

class KPCrossOverAvgLine(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.CrossOverAvgLine, 0)

class KPCrossUnderAvgLine(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.CrossUnderAvgLine, 0)