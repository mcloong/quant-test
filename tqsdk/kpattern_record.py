#默认时间最近最靠前

from param_defines import TrendType, MyString
from kpattern.kpattern_base import BarType

class KPatternRecord(object):
    def __init__(self, name):
        self.pattern_list = [] # 最近的在最前
        self.interval = 10 #
        self.name = name
        self.t_type = TrendType.WAVE
        self.ClassName = MyString.KPatternRecord

    def add(self, pattern):
        flag = True
        pt = self.find(pattern.name, pattern.bar_type)
        if (pt is not None):
            pattern = pt.combine(pattern)
            self.pattern_list.remove(pt)
            #间隔 过滤
            if (pt.bar_type == BarType.MIN):
                interval = self.interval
                if (pt.interval > self.interval):
                    interval = pt.interval
                if (pattern.bar - pt.bar > interval):
                    flag = False
        i = 0
        '''
        第一个
        leng = len(self.pattern_list)
        if (leng == 0):
            self.pattern_list.append(pattern)
            return
        '''
        #找到顺序位置
        for pt in self.pattern_list:
            if (pt.bar < pattern.bar):
                i += 1

        self.pattern_list.insert(i, pattern)
        return flag

    def get_pattern_list(self):
        return self.pattern_list

    def get_by_index(self, idx):
        leng = len(self.pattern_list)
        if (leng == 0 or leng-1 < idx):
            return None
        
        return self.pattern_list[idx]

    def get_by_name(self, name):
        '''
        leng = len(self.pattern_list)
        if (leng == 0):
            return None
        '''
        for pt in self.pattern_list:
            if (pt.name == name):
                return pt

        return None

    #查找有没有
    def find(self, name, bar_type):
        size = len(self.pattern_list)

        i = 0
        if (size == 0):
            return -1
        
        for i in range(0, size):
            if (self.pattern_list[i].name == name and
                self.pattern_list[i].bar_type == bar_type):
                return i
        
        return -1

    def parse(self):
        pass

    def find_kpattern_by_level(self, level):
        pass

    def get_level_score(self, level):
        score = 0
        for pt in self.pattern_list:
            if (pt.level == level):
                score += pt.score*pt.trend
        return score
        
    def find_pattern_set(self, sets): #集合
        step = 0
        for pt in self.pattern_list:
            if (step == 0 and pt.name == sets[1]):
                step = 1
            elif (step == 1 and pt.name == sets[0]):
                step = 2
                break
        if(step == 2):
            return True
        else:
            return False

    def find_up_pattern_sets(self):
        pass

    def find_down_pattern_sets(self):
        pass

    def find_wave_pattern_sets(self):
        pass

    def get_inday_score(self):
        score_1 = self.get_level_score(1) # 50
        score_2 = self.get_level_score(2) # 30
        score_3 = self.get_level_score(3) # 20

        score = score_1*0.5 + score_2*0.3 + score_3*0.2

        return score

    def find_long_trend(self):

        pass

    def find_strong_mode(self):
        return True, TrendType.StrongUp

    def find_trend_mode(self):
         return True, TrendType.TrendUp

    def parse_pattern(self):
        ret, t_type = self.find_strong_mode()
        if (ret == True):
            return t_type
        ret, t_type = self.find_trend_mode()
        if (ret == True):
            return t_type

    def get_trend_type(self, bar_type):
        return self.parse_pattern()

    def clear(self):
        self.pattern_list.clear()