#
import numpy as np
import pandas as pd
from  decimal import Decimal
import logUtils
#用于事件或者下单
class EventRecorder(object):
    def __init__(self, tag_n):
        self.TAG = tag_n
        c = ['name', 'param', 'who', 'id', 'datetime']
        self.df = pd.DataFrame(columns=c)
    
        self.Interval = 10

    def set_interval(self, interval):
        self.Interval = interval

    #return True: 
    #return False: 失败，最近已经更新过
    def add(self, event_name, event_param, who, bar_id, datetime):
        return self.add_with_interval(event_name, event_param, who, bar_id, datetime, self.Interval)

    def add_with_interval(self, event_name, event_param, who, bar_id, datetime, interval):
        ret_id = self.find_event(event_name, 1)
        df_len = len(self.df)
        if(df_len >= 1 and ret_id!=-1 and bar_id-ret_id<interval):
            #考虑是否两条消息合并
            self.df.loc[df_len-1].id = bar_id
            self.df.loc[df_len-1].datetime = datetime
            self.df.loc[df_len-1].param = event_param
            logUtils.my_print(self.TAG, "last record does't timeout,combine")
            return False
        if isinstance(event_param, int):    
            logUtils.my_print(self.TAG, "add event=%s event_param=%d from=%s "%(event_name, event_param, who))
        elif isinstance(event_param, str): 
            logUtils.my_print(self.TAG, "add event=%s event_param=%s from=%s "%(event_name, event_param, who))
        self.df.loc[len(self.df)] = [event_name, event_param, who, bar_id, datetime]
        return True

    def add_with_merge(self, event_name, event_param, who, bar_id, datetime):
        ret_id = self.find_event(event_name, 1)
        if(ret_id!=-1 and bar_id-ret_id<5):
            self.df.iloc[-1].param = event_name
            self.df.iloc[-1].id = bar_id
            self.df.iloc[-1].datetime = datetime
            return False
        logUtils.my_print(self.TAG, "add event:%s from=%s"%(event_name, who))
        self.df.loc[len(self.df)] = [event_name, event_param, who, bar_id, datetime]
        return True

    #return barid
    def find_event(self, name, id):
        list_len = len(self.df)
        if (list_len == 0):
            return -1
        count = 0
        for i in range(1, list_len):
            if (self.df.iloc[-i].name == name):
                count += 1
                if (count == id):
                    return self.df.iloc[-i].id
                    #return i
        return -1

    #通过事件分析行情
    def parse_market(self):
        pass

    def get_event_iloc(self, idx):
        return self.df.iloc[-idx]


class StgEvent(object):
    def __init__(self):
        self.name = ""
        pass

class EventRecorder2(object):
    def __init__(self):
        pass