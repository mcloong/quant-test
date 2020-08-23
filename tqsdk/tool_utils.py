from datetime import datetime
import time
from tqsdk.tafunc import time_to_s_timestamp, time_to_str

def time_diff_min(start_h, start_m, end_h, end_m):
    min_passed = (end_h - start_h) * 60
    min_passed += end_m - start_m

    return min_passed
'''
def get_current_bar(duration):
    if (duration < 60):
        print("不能小于1分钟")

    localtime = time.localtime(time.time())
    half_day_bars = (11-9)*60+30-15
    
    if (localtime.tm_hour >= 21 and localtime.tm_hour<=23) :
        min_passed = 0
    elif (localtime.tm_hour >= 9 and localtime.tm_hour<=15) :
        if (localtime.tm_hour >= 9 and localtime.tm_hour<=12) :
            min_passed = (localtime.tm_hour - 9)*60 + localtime.tm_min
            if (localtime.tm_hour == 10 and localtime.tm_min >=30):
                min_passed -= 15
            if (localtime.tm_hour == 11 and localtime.tm_min >=30):
                min_passed = half_day_bars
        elif (localtime.tm_hour >= 13 and localtime.tm_hour<=15):
            if (localtime.tm_hour == 13 and localtime.tm_min < 30):
                min_passed = half_day_bars
            else:
                min_passed = half_day_bars + (localtime.tm_hour - 13)*60 + localtime.tm_min
                min_passed -= 30 
    else:
        min_passed = 225
    dev = duration / 60
    return min_passed/dev
'''

#阳盘
def get_current_bar2(duration, tt):
    if (duration < 60):
        print("不能小于1分钟")

    localtime = time.localtime(tt)
    return get_current_bar_by_hour_min(localtime.tm_hour, localtime.tm_min, duration)

def get_current_bar_by_hour_min(tm_hour, tm_min, duration):
    half_day_bars = (11-9)*60+30-15
 
    if (tm_hour >= 21 and tm_hour<=23) :
        min_passed = 0
    elif (tm_hour >= 9 and tm_hour<=15) : 
        if (tm_hour >= 9 and tm_hour<=12) :
            min_passed = (tm_hour - 9)*60 + tm_min
            if ((tm_hour == 10 and tm_min >=30) or 
                    (tm_hour == 11 and tm_min <30)):
                min_passed -= 15
            if (tm_hour == 11 and tm_min >=30):
                min_passed = half_day_bars
        elif (tm_hour >= 13 and tm_hour<=15):
            if (tm_hour == 13 and tm_min < 30):
                min_passed = half_day_bars
            elif (tm_hour == 13 and tm_min > 30):
                min_passed = half_day_bars + tm_min - 30
            else:
                min_passed = half_day_bars + (tm_hour - 13)*60 + tm_min
                min_passed -= 30 
    else:
        min_passed = 225
    dev = duration / 60
    return min_passed/dev
#日+夜
def get_current_bar(duration, tt):
    if (duration < 60):
        print("不能小于1分钟")

    localtime = time.localtime(tt)
    half_day_bars = (11-9)*60+30-15
    
    min_passed = 0
    if (localtime.tm_hour >= 21):
        if (localtime.tm_hour <= 23):
            min_passed += time_diff_min(21, 0, localtime.tm_hour, localtime.tm_min)
        else:
            min_passed += time_diff_min(21, 0, 23, 0)
    
    #+夜
    if (localtime.tm_hour >= 0 and localtime.tm_hour<=15) :
        min_passed += time_diff_min(21, 0, 23, 0)
    #白
    if (localtime.tm_hour >= 9 and localtime.tm_hour<=12) :
        min_passed += time_diff_min(9, 0, localtime.tm_hour, localtime.tm_min)

        if ((localtime.tm_hour == 10 and localtime.tm_min >=30) or 
                (localtime.tm_hour == 11 and localtime.tm_min <30)):
            min_passed -= 15

        if (localtime.tm_hour == 11 and localtime.tm_min >=30):
            min_passed += half_day_bars

    elif (localtime.tm_hour >= 12 and localtime.tm_hour<=15):
        min_passed += half_day_bars
        
        if ((localtime.tm_hour == 13 and localtime.tm_min >= 30)
            or  localtime.tm_hour >= 14):
            min_passed += time_diff_min(13, 30, localtime.tm_hour, localtime.tm_min)
        
    
    dev = duration / 60
    return min_passed/dev

def get_current_bar_dt(duration, dt):
    tt = time_to_s_timestamp(dt)
    return get_current_bar(duration, tt)
#def time_to_bar(duration):
#    time_to_datetime(serial.iloc[-1].datetime)
def get_current_minute_bar():
    return int(get_current_bar(60, time.time()))

def get_current_minute_bar_tt(tt):
    return int(get_current_bar(60, tt))

def get_current_minute_bar_dt(dt):
    tt = time_to_s_timestamp(dt)
    return int(get_current_bar(60, tt))

def time_to_bar_index(time):
    pass

def get_minute():
    localtime = time.localtime(time.time())
    return localtime.tm_min

def get_second():
    localtime = time.localtime(time.time())
    return localtime.tm_sec
   
def time_to_minute_inday(hour, minute):
    return (hour)*60 + minute

def is_in_trade_time():
    lt = time.localtime(time.time())
    trade_time = [[21*60, 23*60], [9*60, 10*60+15], [10*60+35, 11*60+30], [13*60+30, 15*60]]
    now_min = lt.tm_hour*60 + lt.tm_min

    flag = False
    for a in trade_time:
        if (now_min >= a[0] and now_min < a[1]):
            flag = True
    return flag

def print_klines(klines, count):
    for i in range(1, count):
        print(time_to_str(klines.loc[i].datetime), klines.iloc[i].average)
        #lt = time.localtime(time_to_s_timestamp(cur_time))
        #print("%d-%d-%d %d:%d:%d"klines.iloc[-i])

def datetime_to_localtime(dt):
    return time.localtime(time_to_s_timestamp(dt))
#test
#print("tool_utils test")
#print(get_current_bar(60))
#print(is_in_trade_time())