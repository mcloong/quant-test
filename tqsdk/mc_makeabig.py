import pandas as pd
import csv
import pplib
from datetime import datetime
import time
from tqsdk import TqApi, TargetPosTask
import strategy

start = False
aa = []
path = 'C:\TianQin\strategies\m2001_daily.csv'
#csv_data = pd.read_csv(path,header=None)
csv_data = pd.read_csv(path,header=None,sep=',',names=["date",'open','high','low','close','volume','open_oi','close_oi'])
#print(csv_data[1:]["open"])
#print(csv_data)
for index, row in csv_data.iterrows():
  #  print (row["date"], row["close"])
  #  if (row["date"] == "datetime"):
  #      continue
    dict = {'date': row["date"],'open':row["open"],'close': row["close"]} 
    aa.append(dict)
#print(csv_data.iloc[-1].open)
#for itor in csv_data:
#    print(itor)
 #   dict = {'date': i[0],'close': 'i["close"]'} 
 #   aa.append(dict)
#print(len(aa))
#print (aa)
#for i in range(1, csv_data.size):
 #   print(csv_data[i:]["open"])

'''
with open(path)as f:
    f_csv = csv.reader(f)
    for row in f_csv:
    print(row['close'])
'''
#high = pplib.Swing_High_Price()
#high = pplib.SwingHighPriceSeries(csv_data, 2, 30)
#print(high)
#low = pplib.SwingLowPriceSeries(csv_data, 2, 30)
#print(low)
#load_history()
#mae_postion()

SYMBOL = "SHFE.rb2005"  # 合约代码
CLOSE_HOUR, CLOSE_MINUTE = 14, 50  # 平仓时间
STOP_LOSS_PRICE = 10  # 止损点(价格)

api = TqApi()
serial = api.get_tick_serial(SYMBOL)
quote = api.get_quote(SYMBOL)
klinesDay = api.get_kline_serial(SYMBOL, 24 * 60 * 60, 3)
klines5Min = api.get_kline_serial(SYMBOL, 5 * 60)
klines5Sec = api.get_kline_serial(SYMBOL, 50) 
position = api.get_position(SYMBOL)


target_pos = TargetPosTask(api, SYMBOL)

swingHighs = {}
swingLows = {}
trendType = 0
target_pos_value = position.pos_long - position.pos_short  
open_position_price = position.open_price_long if target_pos_value > 0 else position.open_price_short 

def print_bars():
  print (" ")
  if len(serial) > 0:
    print("serial:average[-1]=%f average[-10]=%f"%(serial.iloc[-10].average, serial.iloc[-1].average)) 
   
  if len (klinesDay):
    print("klinesDay:open=%d"%(klinesDay.iloc[-1].open)) # -1 为当前
print (" ")

def get_index_line(klinesDay):
    high = klinesDay.high.iloc[-2]  
    low = klinesDay.low.iloc[-2] 
    close = klinesDay.close.iloc[-2] 
    pivot = (high + low + close) / 3 
    bBreak = high + 2 * (pivot - low) 
    sSetup = pivot + (high - low)  
    sEnter = 2 * pivot - low 
    bEnter = 2 * pivot - high  
    bSetup = pivot - (high - low) 
    sBreak = low - 2 * (high - pivot) 
    print("shuniu: %f, tupoBuy: %f, guanchaSell %f, fanzhanSell: %f, fanzhanBuy: %f, guanchaBuy: %f, guanchaSell: %f"
                % (pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak))
    return pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak

def wait_more_bar():
  if (target_pos_value > 0 and open_position_price - quote.last_price >= STOP_LOSS_PRICE) or \
    (target_pos_value < 0 and quote.last_price - open_position_price >= STOP_LOSS_PRICE):
    target_pos_value = 0 

  print("已计算新标志线, 枢轴点: %f, 突破买入价: %f, 观察卖出价: %f, 反转卖出价: %f, 反转买入价: %f, 观察买入价: %f, 突破卖出价: %f"
              % (pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak))

  if target_pos_value > 0:  
    if quote.highest > sSetup and quote.last_price < sEnter:
      print("duo chi")
      target_pos_value = -3 
      open_position_price = quote.last_price
    elif target_pos_value < 0: 
      if quote.lowest < bSetup and quote.last_price > bEnter:
        print("kong fan")
        target_pos_value = 3  
        open_position_price = quote.last_price

    elif target_pos_value == 0:  
      if quote.last_price > bBreak:
          print(" kai duo")
          target_pos_value = 1 
          open_position_price = quote.last_price
      elif quote.last_price < sBreak:
          print("kai kong")
          target_pos_value = -1  
          open_position_price = quote.last_price

def game_start():

  print(klines5Min)
  high = pplib.SwingHighPriceSeries(klines5Min, 2, 10)
  print(high)
  low = pplib.SwingLowPriceSeries(klines5Min, 2, 10)
  #print(Low)

  marketPosion = position.pos_long - position.pos_short
  trendType = strategy.parse_trend_type()
  if trendType == 2:
    target_pos_value = 1
  elif trendType ==1:
    target_pos_value = 0
 # elif trendType ==0:
 # elif trendType ==1:
 # elif trendType ==2:

#pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak = get_index_line(klinesDay) 

while True:
    if start == True:
      target_pos.set_target_volume(target_pos_value)
    api.wait_update()
   
    if api.is_changing(klinesDay.iloc[-1], "datetime"):  
      pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak = get_index_line(klinesDay)
      print_bars()
    if api.is_changing(quote, "datetime"):
        now = datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f")
        if now.hour == CLOSE_HOUR and now.minute >= CLOSE_MINUTE:  
            print("shoupan ping")
            target_pos_value = 0  
            pivot = bBreak = sSetup = sEnter = bEnter = bSetup = sBreak = float("nan") 

    if api.is_changing(quote, "last_price"):
        print("price: %f" % quote.last_price)
        print_bars()

        localtime = time.localtime(time.time())
        if((localtime.tm_hour == 9 and localtime.tm_min >=0 and localtime.tm_min <=30) or
            (localtime.tm_hour == 21 and localtime.tm_min >=0 and localtime.tm_min <=30)) :
          wait_more_bar()
        else:
          game_start()

      