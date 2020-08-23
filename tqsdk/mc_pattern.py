#驱动kline产生pattern
from kpattern.kpattern_map import KPatternMap
from kclock import KClock
from param_defines import MyString

class McPattern(object):
    def __init__(self):
        self.pattern_list = []
        self.__load()
        self.cb = None

    def classic_pattern(self):
        #做大、逆小
        #strongUP and Wave
        pass

    def __load(self):
        kp_map = KPatternMap()
        pt_class_list = kp_map.pattern_list

        for PtClass in pt_class_list:
            pt = PtClass()
            pt.set_callback(self)
            self.pattern_list.append(pt)

    def set_callback(self, cb):
        self.cb = cb

    def on_bar(self, klines):
        for pt in self.pattern_list:
            if (pt.bar_type == 0):
                pt.drive(klines)

    def on_day_bar(self, dklines):
        for pt in self.pattern_list:
            if (pt.bar_type == 1):
                pt.drive(dklines)

    def on_kpattern_callback(self, pt, event, value):
        if (event == MyString.Match):
            pt_struct = pt.clone_struct()
            if (self.cb is not None):
                if (pt.bar_type == 0):
                    self.cb.on_kpattern(pt_struct)
                elif (pt.bar_type == 1):
                    self.cb.on_dkpattern(pt_struct)
                    
    def pt_ok(self, pt):
        pt_struct = pt.clone_struct()
        if (self.cb is not None):
            if (pt.bar_type == 0):
                self.cb.on_kpattern(pt_struct)
            elif (pt.bar_type == 1):
                self.cb.on_dkpattern(pt_struct)

    def __check(self):
        for pt in self.pattern_list:
            if (pt.isok()):
                self.pt_ok(pt)

    def drive_indicator(self, indor, value):
        for pt in self.pattern_list:
            pt.drive_indor(indor, value)