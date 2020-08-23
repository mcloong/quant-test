'''
Name: average record
Desc: 用于记录当日均线
'''
import numpy as np
import pandas as pd
from  decimal import Decimal
from tool_utils import get_current_minute_bar
import logUtils

def date_convert(time):
    return int(time/(1000000000*60))

class AvgRecorder(object):
    def __init__(self, symbol,duration):
        self.name = symbol

        self.TAG = "AvgRecorder"
        self.run_flag = True
        self.duration = duration
        #self.last_minute = Decimal(0.0)
        self.initData()

        self.average = 0
        self.count = 0
        print("[%s] runing............"%(self.TAG))
    
    def initData(self):
        self.average = 0
        self.count = 0
        self.count_of_over = 0
        self.count_of_under = 0
        self.last_minute = 0
        self.init_count_of_under = 0
        self.init_count_of_over = 0
        c = ['id', 'time', 'avg']
        self.df = pd.DataFrame(columns=c)
        
        self.cross_list = []

    def set_logger(self, logger):
        self.logger = logger

    def start(self, ):
        self.initData()
        self.run_flag = True

    def stop(self):
        self.run_flag = False

    def close(self):
        self.initData()

    def bars_of_over(self, klines):
        overs = self.count_of_over + self.init_count_of_over
        return overs 

    def bars_of_under(self, klines):
        unders = self.count_of_under + self.init_count_of_under
        return unders

    def set_bars_of_over(self, count):
        self.init_count_of_over = count

    def set_bars_of_under(self, count):
        self.init_count_of_under = count

    def print(self):
        #self.count_of_under = count
        print(self.df)

    def info(self, msg):
        if (self.logger is not None):
            self.logger.info(self.TAG, msg)

    def get_last_cross_over(self, klines, skip_bars):
        if (skip_bars < 1):
            skip_bars = 1
        cur_bar = get_current_minute_bar()
        if (cur_bar < 10):
            return 0
        df_len = len(self.df)
        if (df_len < skip_bars*2):
            return 0
        for i in range(skip_bars, df_len):
            '''
            if (klines.iloc[-(i+1)].low <= self.df.iloc[-(i+1)].avg
               and klines.iloc[-i].low > self.df.iloc[-i].avg):
                return i
            '''
            avg = self.df.loc[df_len-i].avg
            if (klines.iloc[-(i+1)].low <= avg
               and klines.iloc[-i].low > avg):
                return i

        return df_len

    def get_last_cross_under(self, klines, skip_bars):
        if (skip_bars < 1):
            skip_bars = 1
        cur_bar = get_current_minute_bar()
        df_len = len(self.df)
        if (df_len < skip_bars*2):
            return 0
        if (cur_bar < 10):
            return 0
        
        for i in range(skip_bars, df_len):
            '''
            if (klines.iloc[-(i+1)].high >= self.df.iloc[-(i+1)].avg
               and klines.iloc[-i].high < self.df.iloc[-i].avg):
                return i
            '''
            avg = self.df.loc[df_len-i].avg
            if (klines.iloc[-(i+1)].high >= avg
               and klines.iloc[-i].high < avg):
                return i
        return df_len
        
    def on_tick(self, serial):
        self.average = serial.iloc[-1].average

    def on_bar(self, klines):
        self.df.loc[len(self.df)] = [klines.iloc[-1].id, klines.iloc[-1].datetime, self.average]
        if (klines.iloc[-1].low > self.average):
            self.count_of_over += 1
        if (klines.iloc[-1].high < self.average):
            self.count_of_under += 1
        
        if (self.count > 2 and klines.iloc[-2].high >= self.df.iloc[-2].avg
            and klines.iloc[-1].high < self.average):
            logUtils.my_print(self.TAG, "crossunder cross_count=%d"%(len(self.cross_list)))
            self.cross_list.append([klines.iloc[-1].id, self.average])
        if (self.count > 2 and klines.iloc[-2].low <= self.df.iloc[-2].avg
            and klines.iloc[-1].low > self.average):
            logUtils.my_print(self.TAG, "crossover cross_count=%d"%(len(self.cross_list)))
            self.cross_list.append([klines.iloc[-1].id, self.average])
        self.count += 1
    #不用
    def update_tick(self, id, time, average):
        minute = int(time/(1000000000*60))
        #print("minute=%d last_minute=%d"%(minute,self.last_minute))
        if (self.last_minute != minute):
            self.df.loc[len(self.df)] = [id, time, average]
            
        self.last_minute = minute
        #print(type(minute))
    #不用
    def update_klines(self, klines):
    
        avg_len = len(self.df)
        #avg_len = self.df.shape[0]
        kli_len = len(klines)
        leng = 0 #变量名和函数名不能一样
        #print(avg_len, kli_len)
        if (avg_len < kli_len):
            leng = avg_len 
        else:
            leng = kli_len
        i = 1
        j = 1
        count_of_up = 0
        count_of_down = 0
        while(i < leng and j < leng):
            avg_time_i = date_convert(self.df.iloc[-i].time)
            kli_time_i = date_convert(klines.iloc[-i].datetime)
            #print(avg_time_i, kli_time_i)
            if (avg_time_i < 1000):
                i += 1
                continue
            if (avg_time_i < kli_time_i):
                j += 1
                continue
            elif (avg_time_i > kli_time_i):
                i += 1
                continue
            #print(klines.iloc[-i].low , self.df.iloc[-i].avg)
            if (klines.iloc[-i].low >= self.df.iloc[-i].avg):
                count_of_up = count_of_up+1
            elif(klines.iloc[-i].high <= self.df.iloc[-i].avg):
                count_of_down = count_of_down+1

            i = i+1
            j = j+1

        #print(self.TAG, count_of_up, count_of_down)
        self.count_of_over = count_of_up
        self.count_of_under = count_of_down

    def get_cross_list(self):
        return self.cross_list
'''
from tqsdk import TqApi, TqSim
#test
api = TqApi()
klines = api.get_kline_serial("SHFE.rb2005", 60)
serial = api.get_tick_serial("SHFE.rb2005")
record = AvgRecorder("SHFE.rb2005", 60)
count = 0
mini = 324567.23567898045456
print(len(klines))
print (int(mini))

while True:
    api.wait_update()
   #record.update_tick(serial[-1].id,serial[-1].time,serial[-1].average)
    record.update_tick(serial.iloc[-1].id, serial.iloc[-1].datetime, serial.iloc[-1].average)
    count = count + 1
    #if (count%5 == 0):
    #    record.print()
    if (count %60 == 0):
        record.update_klines(klines)
'''