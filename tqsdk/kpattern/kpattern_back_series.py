#BackFrom 系列

#以下三个没调整 20200718
# resistance
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")

from kpattern.kpattern_base import KPattern, BarType
from param_defines import StgEvent

class KPBackFromKeySupportLine(KPattern):
    def __init__(self, bar_type):
        KPattern.__init__(self, StgEvent.BackFromKeyResistanceLine, bar_type)
        self.level = 1 #最高
        self.score = 0
        self.from_last_cross = 0
        self.back_bar = 0
        self.key_price = 0

    def cacl_score(self):
        #距离
        dist_score = 0
        if (self.back_bar <= 1):
            self.score = 100
        elif (self.back_bar <= 2):
            self.score = 80
        elif (self.back_bar <= 3):
            self.score = 40
        #上一个的距离

# resistance
class KPBackFromKeySupportPrice(KPattern):
    def __init__(self, bar_type):
        KPattern.__init__(self, StgEvent.BackFromKeySupportPrice, bar_type)
        self.level = 1 #最高
        self.score = 0
        self.from_last_cross = 0
        self.back_bar = 0
        self.key_price = 0

    def cacl_score(self):
        #距离
        dist_score = 0
        if (self.back_bar <= 1):
            self.score = 100
        elif (self.back_bar <= 2):
            self.score = 80
        elif (self.back_bar <= 3):
            self.score = 40
        #上一个的距离

# resistance
class KPBackFromKeyResistancePrice(KPattern):
    def __init__(self, bar_type):
        KPattern.__init__(self, StgEvent.BackFromKeyResistancePrice, bar_type)
        self.level = 1 #最高
        self.score = 0
        self.from_last_cross = 0
        self.back_bar = 0
        self.key_price = 0

    def cacl_score(self):
        #距离
        dist_score = 0
        if (self.back_bar <= 1):
            self.score = 100
        elif (self.back_bar <= 2):
            self.score = 80
        elif (self.back_bar <= 3):
            self.score = 40
        #上一个的距离

# resistance
#复制与KPBackFromKeyResistanceLine未计算 20200819
class KPBackFromKeyResistanceLine(KPattern):
    def __init__(self, bar_type):
        KPattern.__init__(self, StgEvent.BackFromKeyResistancePrice, bar_type)
        self.level = 1 #最高
        self.score = 0
        self.from_last_cross = 0
        self.back_bar = 0
        self.key_price = 0

    def cacl_score(self):
        #距离
        dist_score = 0
        if (self.back_bar <= 1):
            self.score = 100
        elif (self.back_bar <= 2):
            self.score = 80
        elif (self.back_bar <= 3):
            self.score = 40
        #上一个的距离