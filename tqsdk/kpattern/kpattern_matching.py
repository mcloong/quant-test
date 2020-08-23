import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
from param_defines import StgEvent
import numpy as np
import pandas as pd
from  decimal import Decimal

class MatchingTypeClass(object):
    def __init__(self):
        self.Day2Day = 1
        self.Day2InDay = 2
        self.InDay2InDay = 3
MatchingType = MatchingTypeClass()

#多个次级别的模式组成一个高级别
#多个模式组合成一个确定性高的机会

class KPActionClass(object):
    def __init__(self):
        self.NoAction = "NoAction"
        self.OpenAtOpenTime60 = "OpenAtOpenTime60" #前60分钟内开仓,必须开仓
        self.OpenAtOpenTime20 = "OpenAtOpenTime20" #前60分钟内开仓,必须开仓
        self.WaitOpenAtOpenTime60 = "WaitOpenAtOpenTime60" #等待合适条件开仓
        self.MakeWave = "MakeWave" #震荡
        self.BuyAtBottom = "BuyAtBottom" #
        self.QuickBuyAtOpen = "QuickBuyAtOpen" #
KPAction = KPActionClass()

#基类
class KPatternMatching(object):
    def __init__(self, m_type):
        self.kp_base = None #哪个模式发起的
        self.kp_bar_type = 1 # 0 minbar 1 daybar
        self.name = ""
        self.kaction = KPAction.NoAction
        #包含，存在
        # action 取决于最后一个
        # start 基于回溯
        c = ['id', 'bartype', 'start', 'end', 'kpattern', 'include', 'action']
        self.pairs = pd.DataFrame(columns=c)

    #注入的是kpattern list
    def drive(self, kp_list, kclock):
        pair_size = len(self.pairs)
        if (pair_size == 0):
            return KPAction.NoAction
        flag = self.check_bar_type(kp_list, 1, kclock) #day
        if (flag == True):
            return KPAction.NoAction

        flag = self.check_bar_type(kp_list, 0, kclock) #min
        if (flag == True):
            return KPAction.NoAction

        return KPAction.NoAction

    def check_bar_type(self, kp_list, bartype, kclock):
        pair_size = len(self.pairs)
        last_index = 0
        for i in range(0, pair_size):
            if (bartype != self.pairs.loc[i].bartype):
                continue
            kp = self.pairs.loc[i].kpattern
            tmp = kp_list.find(kp)
            if (self.pairs.loc[i].include == False):
                if (tmp == -1 or tmp < last_index):
                    return False
            else:
                kp = self.pairs.loc[i].kpattern
                tmp = kp_list.find(kp)
                if (tmp == -1):
                    return False
                #找得到
                if (last_index > 0 and tmp > last_index): #顺序不对
                    return False
                backbar = kclock.dar_bar - kp.day
                if(backbar > self.pairs.loc[i].end):
                    return False
                last_index = tmp #正确
        return True
    '''
    def check_day_type(self, kp_list):
        pair_size = len(self.pairs)
        last_index = 0
        for i in range(0, pair_size):
            kp = self.pairs.loc[i].kpattern
            tmp = kp_list.find(kp)
            if (self.pairs.loc[i].include == False):
                if (tmp == -1 or tmp < last_index):
                    return False
            else:
                kp = self.pairs.loc[i].kpattern
                tmp = kp_list.find(kp)
                if (tmp == -1):
                    return False
                #找得到
                if (last_index > 0 and ltmp > ast_index): #顺序不对
                    return False
                last_index = tmp #正确
        return True
    '''

class BigUpMatching(object):
    def __init__(self):
        self.kp_base = StgEvent.BigUp
        pair = []
        pair.append([1, MatchingType.Day2InDay, StgEvent.LowAtrDaily, True, KPAction.BuyAtBottom])
        pair.append([2, MatchingType.Day2InDay, StgEvent.UpRelayYDAtOpen, True, KPAction.QuickBuyAtOpen])

class BigDownMatching(object):
    def __init__(self):
        pass

class BigBangUpMatching(object):
    def __init__(self):
        pass

class KpatternMatchingModule(object):
    def __init__(self):
        self.loaded = False
        self.kpm_list = []
        pass

    def load_kp_matching(self):
        if (self.loaded == True):
            return

        matchings = []
        match = BigUpMatching()
        matchings.append(match)

        return matchings

    #return action
    def drive_kp_record(self, kp_record):
        for kpm in self.kpm_list:
            ret = kp_record.find(kpm.name)
            if (ret >= 0):
                pass

    def find_and_get_action(self, kp_name, kp_record):
        actions = []

        idx = kp_record.find(kp_name)
        if (idx < 0):
            return None

        #kpm = kp_record.get_by_index(idx)
        kpm = self.get_kpm(kp_name)
        for e_a in kpm.pairs:
            idx = kp_record.find(e_a[1], e_a[0])
            if (idx < 0):
                continue
            actions.append(e_a[2])

        return actions

    def get_kpm(self, name):
        for m in self.kpm_list:
            if (m.name == name):
                return m
                
        return None