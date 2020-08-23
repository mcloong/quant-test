'''
分析，匹配模型
'''
import numpy as np
import pandas as pd
from  decimal import Decimal
from tqsdk import tafunc
from tqsdk.ta import ATR, BOLL
#from kpattern.kpattern_map import KPattern, KPBackFromKeyResistanceLine, KPBackFromKeySupportLine
from kpattern.kpattern_base import KPattern
from kpattern.kpattern_back_series import KPBackFromKeyResistancePrice, KPBackFromKeySupportLine, KPBackFromKeyResistanceLine

class KParser(object):
    def __init__(self):
        self.BOLL_TERM = 26
        self.BOLL_DIF = 2
        #c = ['name', 'value', 'relative_position', 'last_cross', 'id', 'backid','datetime']
        #c = ['name', 'value', 'relative_position', 'last_crossup_bkid', 'last_crossdown_bkid']
        c = ['name', 'value', 'relative_position', 'last_crossup', 'last_crossdown']
        self.key_ll = pd.DataFrame(columns=c)
        self.key_hh = pd.DataFrame(columns=c)
        self.keys = pd.DataFrame(columns=c)
        

    def on_bar(self, klines):
        #ma 5, 10, 20, 30
        self.get_ma_key(klines)
        self.get_boll_key(klines)
        
        self.sort_ll_by_price()
        self.sort_hh_by_price()
        
        print("========key_hh=============")
        print(self.key_hh)
       
        print("========key_ll=============")
        print(self.key_ll)
        #print("first=%d last=%d", self.key_ll.loc[0], self.key_ll.loc[5])
        #print(self.key_ll.iloc[0,:])
        #print(self.key_ll.iloc[5,:])
        '''
        print("========after adjust=============")
        print(self.key_ll)
        print("===========ma==================")
        print(self.key_ma)
        #print("=============================")
        '''

    def get_ma_key(self, klines):
        ma_list = [5, 10, 20, 30, 40, 60]
        list_len = len(ma_list)

        for i in range(0, list_len):
            ma = tafunc.ma(klines.close, ma_list[i])
            name = "ma%d"%(ma_list[i])
            relative_position = "cross" #above、below、cross
            last_crossup = 60
            last_crossdown = 60
            if (klines.iloc[-1].low > ma.iloc[-1]):
                relative_position = "above"
            elif (klines.iloc[-1].high < ma.iloc[-1]):
                relative_position = "below"
            
            # last_crossup
            for j in range(1, 100):
                if (klines.iloc[-j].low >= ma.iloc[-j] and klines.iloc[-(j+1)].low <= ma.iloc[-(j+1)]):
                    last_crossup = j
                    break
            #last_crossdown
            for j in range(1, 100):
                if (klines.iloc[-j].high <= ma.iloc[-j] and klines.iloc[-(j+1)].high >= ma.iloc[-(j+1)]):
                    last_crossdown = j
                    break
            '''
            if (relative_position == "above"):
                self.key_ll.loc[len(self.key_ll)] = [name, ma.iloc[-1], relative_position, last_crossup, last_crossdown]
            elif (relative_position == "below"):
                self.key_hh.loc[len(self.key_hh)] = [name, ma.iloc[-1], relative_position, last_crossup, last_crossdown]
            '''
            self.keys.loc[len(self.keys)] =  [name, ma.iloc[-1], relative_position, last_crossup, last_crossdown]
        
        #boll 

        #pre_high、ll
        #support、

    def find_boll_daily(self, start_id, dklines):
        p = 1
        n = 5
        new_df = pd.DataFrame()
        mid = tafunc.ma(dklines["close"], n)
        std = dklines["close"].rolling(n).std()
        new_df["mid"] = mid
        new_df["top"] = mid + p * std
        new_df["bottom"] = mid - p * std

        boll = new_df
        ma_ck = 0
        j = 1
        for i in range(j+1, j+3+1):
            ma_ck += list(boll["mid"])[-i] - list(boll["mid"])[-(i+1)]
        #print(ma_ck)
        if (ma_ck > 0):
            self.boll_top = int(list(boll["mid"])[-(j+1)] + std.iloc[-(j+1)]*1.3)
            self.boll_bottom = int(list(boll["mid"])[-(j+1)] - std.iloc[-(j+1)])
            
        elif (ma_ck < 0):
            self.boll_top = int(list(boll["mid"])[-(j+1)] + std.iloc[-(j+1)])
            self.boll_bottom = int(list(boll["mid"])[-(j+1)] - std.iloc[-(j+1)]*1.3)
            #self.boll_trade_dir = TradeDirection.SELLONLY
            
        #self.debug("boll_top=%d boll_bottom=%d direction=%s"%(self.boll_top, self.boll_bottom, self.boll_trade_dir))

    def get_boll_key(self, klines):
        key_name = ["bottom", "top", "mid"]
        boll=BOLL(klines, self.BOLL_TERM, self.BOLL_DIF)

        for i in range(0, 3):
            name = key_name[i]
            boll_value = list(boll[key_name[i]])[-1]
            relative_position = "cross"
            if (klines.iloc[-1].low >= boll_value):
                relative_position = "above"
            elif (klines.iloc[-1].high <= boll_value):
                relative_position = "below"
            last_crossdown, last_crossup =  self.generate_about_cross(list(boll[key_name[i]]), klines)
            if (relative_position == "above"):
                self.key_hh 
            '''
            if (relative_position == "above"):
                self.key_ll.loc[len(self.key_ll)] = [name, boll_value, relative_position, last_crossup, last_crossdown]
            elif (relative_position == "below"):
                self.key_hh.loc[len(self.key_hh)] = [name, boll_value, relative_position, last_crossup, last_crossdown]
            '''
            self.keys.loc[len(self.keys)] =  [name, boll_value, relative_position, last_crossup, last_crossdown]

    
    def generate_about_cross(self, b_list, klines):
        crossup = 60
        crossdown = 60

        #crossup
        for i in range(1, 60):
            if (klines.iloc[-i].low >= b_list[-i] and klines.iloc[-(i+1)].low <= b_list[-(i+1)] ):
                crossup = i
                break
        #crossdown
        for i in range(1, 60):
            if (klines.iloc[-i].high <= b_list[-i] and klines.iloc[-(i+1)].high >= b_list[-(i+1)] ):
                crossdown = i
                break
        return crossdown, crossup

    def sort_hh_by_price(self):
        #self.key_hh.sort_values(['value'], ascending = True)# 升序
        self.tmp = self.keys.sort_values(['value'], ascending = True)# 升序
        for index, row in self.tmp.iterrows():
            if (row['relative_position'] == "below"):
                self.key_hh.loc[len(self.key_hh)] = [row['name'], row['value'], row['relative_position'], 
                                                    row['last_crossup'], row['last_crossdown']]

    def sort_ll_by_price(self):
        #print(self.key_ll.sort_values(['value'], ascending = True))# 升序
        self.tmp = self.keys.sort_values(['value'], ascending = False)

        for index, row in self.tmp.iterrows():
            if (row['relative_position'] == "above"):
                self.key_ll.loc[len(self.key_ll)] = [row['name'], row['value'], row['relative_position'], 
                                                    row['last_crossup'], row['last_crossdown']]

    def sort_by_barid(self):
        pass

    def get_hh_list(self):
        return self.key_hh

    def get_ll_list(self):
        return self.key_ll

    def get_last_key_hh_index(self, price, gapbar):
        leng = len(self.key_hh)
        for i in range(0, leng):
            if (price >= self.key_hh.loc[i].value and 
                self.key_hh.loc[i].last_crossdownd >= gapbar):
                return i
        return -1

    def get_last_key_ll_index(self, price, gapbar):
        leng = len(self.key_ll)
        for i in range(0, leng):
            if (price <= self.key_ll.loc[i].value and 
                self.key_ll.loc[i].last_crossup >= gapbar):
                return i
        return -1

    def get_last_key_hh_price(self, price, gapbar):
        index = self.get_last_key_hh_index(price, gapbar)
        if (index == -1):
            return 9999
        return self.key_hh.loc[index].value

    def get_last_key_ll_price(self, price, gapbar):
        index = self.get_last_key_ll_index(price, gapbar)
        if (index == -1):
            return -9999
        return self.key_ll.loc[index].value

    def get_last_key_hh_name(self, price, gapbar):
        index = self.get_last_key_hh_index(price, gapbar)
        if (index == -1):
            return None
        return self.key_hh.loc[index].name

    def get_last_key_ll_name(self, price, gapbar):
        index = self.get_last_key_ll_index(price, gapbar)
        if (index == -1):
            return None
        return self.key_ll.loc[index].name

    def two_crossover(self, ls, klines):
        idx = 0
        first_bar = 100
        send_bar = 100
        for i in range(1, 100):
            if (ls[-i] <= klines.iloc[-i].low and
                ls[-(i+1)] >= klines.iloc[-(i+1)].low):
                idx += 1
                if (idx == 1):
                    first_bar = i
                elif (idx == 2):
                    send_bar = i
                    break
        return first_bar, send_bar

    def two_crossdown(self, ls, klines):
        idx = 0
        first_bar = 100
        send_bar = 100
        for i in range(1, 100):
            if (ls[-i] >= klines.iloc[-i].high and
                ls[-(i+1)] <= klines.iloc[-(i+1)].high):
                idx += 1
                if (idx == 1):
                    first_bar = i
                elif (idx == 2):
                    send_bar = i
                    break
        return first_bar, send_bar
    '''
    def stick(self, klines):
        idx = 0
        first_bar = 100
        send_bar = 100
        for i in range(1, 100):
            if (ls[-i] >= klines.iloc[-i].high and
                ls[-(i+1)] <= klines.iloc[-(i+1)].high):
                idx += 1
                if (idx == 1):
                    first_bar = i
                elif (idx == 2):
                    send_bar = i
                    break
        return first_bar, send_bar
    '''
    #crossup、crossdown、反复触及
    def generate_event(self, klines):
        #key_len = len(self.key_ll)
        #for ll in self.key_ll:
        #c = ['tag', 'title', 'first', 'second']
        c = ['tag', 'first_crossover', 'send_crossover', 'first_crossdown', 'send_crossdown', 'first_stick', 'send_stick']
        self.cross = pd.DataFrame(columns=c)
        kpattern_list = [] #KPattern

        ma_list = [5, 10, 20, 30, 40, 60]
        list_len = len(ma_list)

        for i in range(0, list_len):
            ma = tafunc.ma(klines.close, ma_list[i])
            name = "ma%d"%(ma_list[i])
            first_cd, send_cd = self.two_crossdown(list(ma),klines)
            #self.cross.loc[len(self.cross)] = [name, "two_crossdown", first_bar, send_bar]
            print("two_crossdown",name, first_cd, send_cd)
            first_cu, send_cu = self.two_crossover(list(ma),klines)
            self.cross.loc[len(self.cross)] = [name, first_cd, send_cd, first_cu, send_cu, 100, 100]
            print("two_crossdown",name, first_cu, send_cu)

        key_name = ["bottom", "top", "mid"]
        boll=BOLL(klines, self.BOLL_TERM, self.BOLL_DIF)
        for i in range(0, 3):
            name = key_name[i]
            first_cd, send_cd = self.two_crossdown(list(boll[key_name[i]]), klines)
            #self.cross.loc[len(self.cross)] = [name, "two_crossdown", first_bar, send_bar]
            print("two_crossdown",name, first_cd, send_cd)
            first_cu, send_cu = self.two_crossover(list(boll[key_name[i]]), klines)
            self.cross.loc[len(self.cross)] = [name, first_cd, send_cd, first_cu, send_cu, 100, 100]
            print("two_crossover",name, first_cu, send_cu)

        for index, row in self.cross.iterrows():
            first_cu = row['first_crossover']
            send_cu = row['send_crossover']
            first_cd = row['first_crossdown']
            send_cd = row['send_crossdown']
            
            #print(row['first_bar'], row['send_bar'])
           
            if (first_cu < 4 and first_cd > 5 and send_cu - first_cu > 15):
                #key_price 支撑
                print("StdCrossGoBack up") 
                print(row)
                #====
                kpt = KPBackFromKeySupportLine(1)
                kpt.bar = first_cu
                kpattern_list.append(kpt)
            if (first_cu > 5 and first_cd < 4 and send_cd - first_cd < 15):
                #key_price 反转
                print("StdCrossReverse")
                print(row)
                #=========
                kpt = KPBackFromKeyResistanceLine(1)
                kpt.bar = first_cd
                kpattern_list.append(kpt)
        return kpattern_list

    def generate_indicator(self):
        pass

'''
from tqsdk import TqApi, TqSim, tafunc

api = TqApi(TqSim())
klines = api.get_kline_serial("SHFE.rb2010", 24 * 60 * 60)

kp = KParser()

kp.on_bar(klines)
kp.generate_event(klines)

while True:
    api.wait_update()
'''