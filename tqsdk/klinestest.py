'''
klines
'''
from tqsdk import TqApi, TqSim, tafunc
from tqsdk.tafunc import time_to_datetime

api = TqApi()
klines = api.get_kline_serial("SHFE.rb2005", 60)
serial = api.get_tick_serial("SHFE.rb2005")
#print(time_to_datetime(serial.iloc[-1].datetime))
#llv = tafunc.llv(klines.low, 5)  # 求5根k线最低点(包含当前k线)
#print(list(llv))
while True:
    api.wait_update()
    print(serial.iloc[-1].bid_price1)