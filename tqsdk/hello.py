#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

'''

'''
from tqsdk import TqApi, TqSim, TargetPosTask
from tqsdk.tafunc import ma
from datetime import datetime, date
from contextlib import closing
from tqsdk.tools import DataDownloader

SHORT = 10  # 短周期
LONG = 60  # 长周期
SYMBOL = "DCE.m2001"  # 合约代码

api = TqApi()
print("策略开始运行")

data_length = LONG + 2  # k线数据长度
# "duration_seconds=60"为一分钟线, 日线的duration_seconds参数为: 24*60*60
klines = api.get_kline_serial(SYMBOL, duration_seconds=60, data_length=data_length)
target_pos = TargetPosTask(api, SYMBOL)
currentBar = 0
###################################
high_price_list = []
low_price_list = []

###################################
download_tasks = {}
#download_tasks["m_daily"] = DataDownloader(api, symbol_list="DCE.m2001", dur_sec=24*60*60,
#                    start_dt=date(2019, 10, 1), end_dt=date(2019, 11, 20), csv_file_name="m2001_daily.csv")
download_tasks["rb2005_10sec"] = DataDownloader(api, symbol_list="SHFE.rb2005", dur_sec=10,
          start_dt=date(2020, 1, 15), end_dt=date(2020, 1, 20), csv_file_name="rb2005_10sec.csv")

def load_history():
    while not all([v.is_finished() for v in download_tasks.values()]):
        api.wait_update()
        print("progress: ", { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() })

#def parse_trend_type():

'''
def Swing_High_Price(KS, SwingNum):
    global currentBar
    countOfRight = int(SwingNum/2)
    countOfLeft = int(SwingNum/2)
    if (SwingNum%2 != 0):
        countOfRight += 1
   
    swingHigh_ = -1
    if (currentBar < SHORT):
        print("coutOfRight="+str(countOfRight)+" countOfLeft="+str(countOfLeft))
        return -1
    for i in range(countOfRight+1, SHORT-countOfLeft):
        continueflag = True
        print("====KS.iloc[-"+str(i)+"].close"+str(KS.iloc[-i].close))
        for j in range(1, countOfRight+1):
            print("KS.iloc[-"+str(i-j)+"].close="+str(KS.iloc[-(i-j)].close));
            if(KS.iloc[-i].close < KS.iloc[-(i-j)].close):
                continueflag = False
                break
        if (continueflag == False):
            continue
        print("=====left=========")
        for k in range(1, countOfLeft+1):
            print("KS.iloc[-"+str(i+k)+"].close="+str(KS.iloc[-(i+k)].close));
            if(KS.iloc[-i].close < KS.iloc[-(i+k)].close):
                continueflag = False
                break
        if (continueflag == True):
            print("HighPrice = "+str(klines.iloc[-i].close))
            print("HighPriceBar = "+str(i))
            swingHigh_ = KS.iloc[-i].close
            break
    return swingHigh_

def Swing_Low_Price(KS, SwingNum):
    countOfRight = int(SwingNum/2)
    countOfLeft = int(SwingNum/2)
    if (SwingNum%2 != 0):
        print("coutOfRight="+str(countOfRight)+" countOfLeft="+str(countOfLeft))
        countOfRight += 1
    
    swingLow_ = -1
    if (currentBar < SHORT):
        return -1
    for i in range(countOfRight+1, SHORT-countOfLeft):
        continueflag = True
        print("=====KS.iloc[-"+str(i)+"].close"+str(KS.iloc[-i].close))
        for j in range(1, countOfRight+1):
            print("KS.iloc[-"+str(i-j)+"].close="+str(KS.iloc[-(i-j)].close));
            if(KS.iloc[-i].close > KS.iloc[-(i-j)].close):
                continueflag = False
                break
        if (continueflag == False):
            continue
        print("=====left=========")
        for k in range(1, countOfLeft+1):
            print("KS.iloc[-"+str(i+k)+"].close="+str(KS.iloc[-(i+k)].close));
            if(KS.iloc[-i].close > KS.iloc[-(i+k)].close):
                continueflag = False
                break
        if (continueflag == True):
            print("LowPrice = "+str(klines.iloc[-i].close))
            print("LowPriceBar = "+str(i))
            swingLow_ = KS.iloc[-i].close
            break
    return swingLow_
'''

while True:
    if (currentBar == 0):
        load_history()
        parse_trend_type()
    api.wait_update()
    
'''
while True:
    if (currentBar == 0):
        load_history()
        parse_trend_type()
    api.wait_update()
    currentBar = currentBar+1
    print("========"+str(currentBar)+"========")
  #  print("HighPrice = ")
    print("HighPrice ="+str(Swing_High_Price(klines, 4)))
   # print("LowPrice ="+str(Swing_Low_Price(klines, 4)))
    #print(klines.iloc[-1].close)
    if api.is_changing(klines.iloc[-1], "datetime"):  # 产生新k线:重新计算SMA
        short_avg = ma(klines["close"], SHORT)  # 短周期
        long_avg = ma(klines["close"], LONG)  # 长周期

        # 均线下穿，做空
        if long_avg.iloc[-2] < short_avg.iloc[-2] and long_avg.iloc[-1] > short_avg.iloc[-1]:
            target_pos.set_target_volume(-3)
            print("均线下穿，做空")

        # 均线上穿，做多
        if short_avg.iloc[-2] < long_avg.iloc[-2] and short_avg.iloc[-1] > long_avg.iloc[-1]:
            target_pos.set_target_volume(3)
            print("均线上穿，做多")

'''