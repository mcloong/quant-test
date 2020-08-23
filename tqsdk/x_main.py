'''
云中漫步
（9:00,13:00，21:00 这几个关键时间点，比如上午涨，13:30半开盘后回调，没如果没涨上来 趋势改变了方向，跟进，如果涨上来了，再会调时跟进）
'''

from param_defines import TradeDirection
from position_manager import PositionManger
from datetime import datetime
import time
from tqsdk import TqApi, TqAccount, TargetPosTask, TqSim
from avg_record import AvgRecorder
from logUtils import mylog
from strategy_grid import StrategyGrid
from mc_indictors import McIndictors
from strategy_avg_cross import StrategyAvgCross
from strategy_manager import StrategyManager
from killer_tank import KillerTank
from strategy_watcher import StrategyWatcher
import signal

#********************** params **********
#自然灾害（5），趋势影响（4），政策影响（3）

# 止损区间，突破HH2和LL2，如果持仓方向不对，坚决出厂
# LL1 和 HH 2 安全区间

BAR_LENGTH = 380
#************************ var ****************************

#/************************init***********************************/

mylog.info("walkswing", "game begin")
SYMBOL = "SHFE.rb2010"
api = TqApi(TqSim())
klines = api.get_kline_serial(SYMBOL, 60, BAR_LENGTH)
day_klines = api.get_kline_serial(SYMBOL, 24*60*60)
serial = api.get_tick_serial(SYMBOL)
# 账户情况
account = api.get_account()
print(account)

# 运行时记录
avg_recorder = AvgRecorder("AvgRecord", 60) 
pos_manage = PositionManger(api, SYMBOL)

strage_manager = StrategyManager(pos_manage, SYMBOL)
mc_indictor = McIndictors(SYMBOL, strage_manager)
mc_indictor.set_avg_recorder(avg_recorder)
strage_manager.set_indictor(mc_indictor)
strage_manager.set_avg_record(avg_recorder)
pos_manage.set_logger(mylog)
strage_manager.set_logger(mylog)
strage_manager.set_indictor(mc_indictor)
mc_indictor.set_logger(mylog)
avg_recorder.set_logger(mylog)
strage_manager.update_day_klines(day_klines)
strage_manager.load_setting()

# 策略
stg_watcher = StrategyWatcher(SYMBOL, strage_manager)
strage_manager.add(stg_watcher)
'''
stg_avg = StrategyAvgCross(strage_manager)
stg_avg.set_avg_recorder(avg_recorder)
killer_tank = KillerTank(strage_manager)

strage_manager.add(stg_avg)
strage_manager.add(killer_tank)
'''
#/**********************function****************************/
# 自定义信号处理函数
def my_handler(signum, frame):
    print("进程被终止")
    global strage_manager
    strage_manager.shutdown()
    exit()
 
# 设置相应信号处理的handler
signal.signal(signal.SIGINT, my_handler)
signal.signal(signal.SIGTERM, my_handler)

init_flag = False

#mc_indictor.on_day_bar(day_klines)
#stg_watcher.on_day_bar(day_klines)
strage_manager.on_day_bar(day_klines)

while True:
    api.wait_update()
    
    lt = time.localtime(time.time())      
    #if (((lt.tm_hour == 9 and lt.tm_min <= 1) or (lt.tm_hour==21 and lt.tm_min <= 1)) and init_flag == False):
    if (((lt.tm_hour==21 and lt.tm_min <= 1) or (lt.tm_wday == 4 and lt.tm_hour == 0 and lt.tm_min <= 1)) and init_flag == False):
        print("new day begining")
        pos_manage.new_day()
        avg_recorder.start()
        strage_manager.new_day()
        init_flag = True
    elif ((lt.tm_hour == 14 and lt.tm_min >= 55 and lt.tm_min <= 58) 
        or (lt.tm_wday == 4 and lt.tm_hour == 22 and lt.tm_min >= 55 and lt.tm_min <= 58)): # 周五 night
        #pos_manage.close()
        strage_manager.close()
        #pos_manage.close()
        init_flag = False
        continue
    elif (lt.tm_hour == 14 and lt.tm_min == 59 and lt.tm_sec ==1):
        #mc_indictor.on_day_bar(day_klines)
        #stg_watcher.on_day_bar(day_klines)
        continue

    #stg_grid.run(klines, serial.iloc[-1].ask_price1, serial.iloc[-1].bid_price1)
    #stg_avg.run(klines, serial.iloc[-1].ask_price1, serial.iloc[-1].bid_price1)
    # bid_price 买价，ask_price 卖价
    if api.is_changing(day_klines.iloc[-1], "datetime"):
        print(".................on day bar....................")
        #mc_indictor.on_day_bar(day_klines)
        #stg_watcher.on_day_bar(day_klines)
        strage_manager.on_day_bar(day_klines)

    if api.is_changing(klines.iloc[-1], "datetime"):
        #strage_manager.run(klines, serial.iloc[-1].ask_price1, serial.iloc[-1].bid_price1, serial.iloc[-1].average)
        strage_manager.on_bar(klines)
        avg_recorder.on_bar(klines)
        #print("lt.tm_min=%d lt.tm_sec=%d"%(lt.tm_min, lt.tm_sec))
    
    strage_manager.on_tick(serial)
    avg_recorder.on_tick(serial)
    
 #   pos_manage.check()
 #   avg_recorder.update_tick(serial.iloc[-1].id, serial.iloc[-1].datetime, serial.iloc[-1].average)

    #mc_indictor.run(klines, serial.iloc[-1].ask_price1, serial.iloc[-1].bid_price1, serial.iloc[-1].average)
