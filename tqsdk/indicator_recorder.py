#
import numpy as np
import pandas as pd
from  decimal import Decimal
import logUtils

#用于记录一个指标，name是指标的名字
class IndicatorRecorder(object):
    def __init__(self, name):
        self.TAG = "IndicatorRecorder"
        self.name = name
        #c = ['name', 'param', 'who', 'id', 'datetime']
        c = ['value', 'id', 'datetime']
        self.df = pd.DataFrame(columns=c)
        self.Interval = 10

    def set_interval(self, interval):
        self.Interval = interval
        
    #return True: 
    #return False: 失败，最近已经更新过
    def add(self, value, bar_id, datetime):
        df_len = len(self.df)
        if(df_len >= 1 and bar_id-self.df.loc[df_len-1].id<5):
            #考虑是否两条消息合并
            self.df.loc[df_len-1].id = bar_id
            self.df.loc[df_len-1].datetime = datetime
            self.df.loc[df_len-1].value = value
            logUtils.my_print(self.TAG, "last record does't timeout,combine")
            return False
        logUtils.my_print(self.TAG, "add one %s value=%d"%(value))
        self.df.loc[df_len] = [value, bar_id, datetime]
        return True

    #return barid
    def find(self, id):
        list_len = len(self.df)
    
        if (list_len >= id):
            return self.df[-id]

        return None

    def find_gt(self, val):
        list_len = len(self.df)
    
        bar_id = -1
        for i in range(1, list_len+1):
            if (val > int(self.df.iloc[-i].value)):
                bar_id = self.df.iloc[-i].id
                break
        return bar_id

    #通过事件分析行情
    def parse_market(self):
        pass

    def clear(self):
        pass

    ''''
    大于 -gt (greater than)
    小于 -lt (less than)
    大于或等于 -ge (greater than or equal)
    小于或等于 -le (less than or equal)
    不相等 -ne （not equal）
    '''

#成功
class IndicatorsMap(object):
    def __init__(self, name):
        self.name = name
        #passc = ['name', 'value', 'id', 'datetime']
        c = ['name', 'value', 'id']
        self.df = pd.DataFrame(columns=c)

    def add(self, name, value, barid):
        leng = len(self.df)
        
        for i in range(0, leng):
            if (self.df.loc[i].name == name):
                self.df.loc[i].value = value
                self.df.loc[i].id = barid
                return

        self.df.loc[leng] = [name, value, barid]
    
    def _find(self, name):
        for indor in self.df:
            if (indor.name == name):
                return True
        return False