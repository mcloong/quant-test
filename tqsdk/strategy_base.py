import abc
from param_defines import TradeDirection
from tool_utils import get_current_minute_bar
import tool_utils
from pplib import get_avg_price ,get_checksum
import pplib
from datetime import datetime
import time
from param_defines import StrategyKpi,WalkPath,MyDefaultValue,Indicator
from tqsdk.tafunc import time_to_datetime, time_to_s_timestamp, time_to_str
from kclock import KClock
import random
 
#
class StrategyBase(object):
    def __init__(self, symbol, tag, manager):
        self.trade_dir = TradeDirection.BUYSELL
        self.MAX_LOSS = 25
        self.MAX_PROFIT = 50
        self.manager = manager
        self.symbol = symbol
        self.TAG = tag
        self.monitor_open = False
        self.keep_stg_logic = False #不考虑TradeDirection控制，保持策略自身逻辑
        self.forbid_trade = False
        self.kclock = KClock()

        self.task_list = []

        self.role = "strategy"##角色：Indicator EventRecord RiskManager

        self.new_data()

    def new_data(self):
        self.position = 0
        self.real_position = 0 #控制TradeDirection后的真实持仓
        self.cur_price = 0
        self.ask_price = 0
        self.bid_price = 0
        self.avg_price = 0
        self.entry_bar = 0
        self.entry_price = 0
        self.exit_pos = 0
        self.exit_bar = 0
        self.loss_mark_flag = 1
        self.loss_mark_bar = 999

        self.open_bar_id = 0
        self.cur_bar = 0#当天的bar值
        self.cur_bar_id = 0#klines中的id的值
        self.cur_bar_time = 0.0
        self.cur_tick_time = 0.0
        self.cur_day_barid = 0
        self.backtest_flag = False

        self.run_flag = False

        self.debug_level = 2 # 0 info , 1 debug , 2 err
        self.kpi = 0

        if (random.randint(0,9)%2 == 1):
            self.monitor_open = True
        else:
            self.monitor_open = False

    def stg_setting(self):
        pass

    def run(self, klines, bid_price, ask_price, avg_price):
        self.cur_bar_time = klines.iloc[-1].datetime

    def get_strategy_position(self):
        if (self.forbid_trade == True):
            return 0
        else:
            return self.real_position
    
    def reset(self):
        self.new_data()
        
    def start(self):
        self.run_flag = True
        self.debug("start.......")
        
    def stop(self):
        self.run_flag = False
        if (self.position != 0):
            self.set_position(0)
        self.debug("stop.......")

    #更新一个结构体
    def on_kindictor(self, kindictor):
        pass

    #更新单个指标
    def on_indicator(self, indictor, value):
        pass

    #更新单个指标
    def on_indicator_object(self, indictor, value):
        pass

    def on_event(self, event_name, e_param):
        #
        pass

    def on_command(self, cmd_name, c_param):
        #
        pass

    def on_kpattern(self, kpt):
        pass

    @abc.abstractmethod
    def timer_task(self):
        pass

    def get_name(self):
        return self.TAG

    def set_trade_direction(self, t_dir):
        self.debug("set_trade_direction dir=%s"%(t_dir))
        self.trade_dir = t_dir

    def get_trade_direction(self):
        return self.trade_dir

    def on_bar6(self, klines):
        self.base_monitor_position(klines)

    def on_bar10(self, klines):
        pass

    def on_bar30(self, klines):
        pass

    def on_bar(self, klines):
        self.cur_bar_time = klines.iloc[-1].datetime
        self.cur_bar_id = klines.iloc[-1].id
        if (self.open_bar_id == 0):
            self.open_bar_id = self.get_open_bar(klines)
        #print(self.TAG, self.cur_bar_time)
        if (self.bid_price == 0):
            self.bid_price = klines.iloc[-1].close
        if (self.ask_price == 0):
            self.ask_price = klines.iloc[-1].close
        if (self.avg_price == 0):
            self.avg_price = klines.iloc[-1].close

        self.cur_bar = self.get_current_minute_bar()

        self.update_kclock()

        if (self.cur_bar_id%6 == 6 and self.cur_bar>0):
            self.on_bar6(klines)
        
        if (self.cur_bar_id%10 == 6 and self.cur_bar>0):
            self.on_bar10(klines)

        if (self.cur_bar_id%30 == 6 and self.cur_bar>0):
            self.on_bar30(klines)

        if (self.backtest_flag == True):
            cur_price = klines.iloc[-1].close
            if (abs(self.ask_price - cur_price)>2):
                self.ask_price = cur_price
                leng = len(klines)
                if (leng > 30):
                    self.avg_price = pplib.get_avg_price(klines, 30)
            if (abs(self.bid_price - cur_price)>2):
                self.bid_price = cur_price

    def on_day_bar(self, dklines):
        self.cur_day_barid = dklines.iloc[-1].id
    
    def on_tick2(self, bid_price, ask_price, avg_price):
        pass

    def on_tick(self, serial):
        self.cur_tick_time = serial.iloc[-1].datetime
        self.bid_price = serial.iloc[-1].bid_price1
        self.ask_price = serial.iloc[-1].ask_price1
        self.avg_price = serial.iloc[-1].average
        self.cur_price = self.ask_price

    def set_keep_position(self, pos):
        pass

    def set_position(self, pos):
        self.real_position = self.set_position_internal(pos)
        if (self.keep_stg_logic):
            self.position = pos
 
    def set_position_internal(self, pos):
        #print("[%s] set_position pos=%d"%(self.TAG, pos))
        if (self.run_flag == False):
            return

        bk_position = self.position

        real_price = self.ask_price
        if (pos > 0):
            real_price = self.ask_price
        elif (pos < 0):
            real_price = self.bid_price
        else:
            if (self.position <0):
                real_price = self.ask_price
            else:
                real_price = self.bid_price

        if(pos > 0 and self.trade_dir == TradeDirection.SELLONLY):
            if (self.position !=0):
                if (self.position > 0):
                    msg = "多平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
                else:
                    msg = "空平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
                if (self.manager.set_position(self.TAG, 0) == True):
                    self.position = 0
                else:
                    self.my_print("set_position failed")
                self.logger.info(self.TAG, msg)
                self.my_print(msg)
        elif(pos < 0 and self.trade_dir == TradeDirection.BUYONLY):
            if (self.position !=0):
                if (self.manager.set_position(self.TAG, 0) == True):
                    self.position = 0
                else:
                    self.my_print("set_position failed")
                if (self.position > 0):
                    msg = "多平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
                else:
                    msg = "空平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
                self.logger.info(self.TAG, msg)
                self.my_print(msg)
        else:
            if (pos > 1):
                pos = 1
            elif (pos < -1):
                pos = -1
            if (pos != 0):
                self.entry_bar = self.get_current_minute_bar()
                self.entry_price = real_price
            if (pos > 0):
                msg = ""
                if (self.position < 0):
                    msg += "空平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
                msg += "多开(实) position=%d price=%d"%(pos, real_price)
            elif (pos < 0):
                msg = ""
                if (self.position > 0):
                    msg += "多平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
                msg = "空开(实) position=%d price=%d"%(pos, real_price)
            elif (pos == 0 and self.position > 0):
                msg = "多平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
            elif (pos == 0 and self.position < 0):
                msg = "空平(实) done_price=%d entry_bar=%d"%(real_price, self.entry_price)
            self.logger.info(self.TAG, msg)
            self.my_print(msg)
            
            if (self.manager.set_position(self.TAG, pos) == True):
                self.position = pos
            else:
                self.my_print("set_position failed")
        
        if (bk_position !=0 and self.position!=bk_position):
            if (bk_position>0):
                prof = self.ask_price - self.entry_price
                if (prof < -10):
                    self.loss_happend(1, prof)
                if (prof > 10):
                    self.gain_happend(1, prof)
       
            if (bk_position<0):
                prof = self.entry_price - self.ask_price
                if (prof < -10):
                    self.loss_happend(-1, prof)
                if (prof > 10):
                    self.gain_happend(-1, prof)

            self.exit_bar = self.get_current_minute_bar()
            self.exit_pos = bk_position

        return self.position
    
    def my_print(self, msg):
        lt = self.get_real_time()
        print("[%s] %d-%02d-%02d %02d:%02d:%02d - : %s"%(self.TAG, lt.tm_year,lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec, msg))
    
    def my_print_5(self, msg):
        lt = self.get_real_time()
        if (lt.tm_min % 5 == 0):
            self.my_print(msg)

    def set_logger(self,logger):
        self.logger = logger

    def open_backtest(self):
        self.backtest_flag = True
    
    def get_real_time(self):  
        '''
        if (self.backtest_flag == True):
            if (self.cur_tick_time != 0):
                return time.localtime(time_to_s_timestamp(self.cur_tick_time))
            elif (self.cur_bar_time != 0):
                return time.localtime(time_to_s_timestamp(self.cur_bar_time))
        
        return time.localtime(time.time())
        '''
        if (self.cur_tick_time != 0):
            return time.localtime(time_to_s_timestamp(self.cur_tick_time))
        elif (self.cur_bar_time != 0):
            return time.localtime(time_to_s_timestamp(self.cur_bar_time))
        else:
            return time.localtime(time.time())

    def get_current_minute_bar(self):
        '''
        if (self.backtest_flag == True and self.cur_bar_time != 0):
            return tool_utils.get_minute_bar_by_datetime(self.cur_bar_time)
        else:
            return get_current_minute_bar()
        '''
        '''
        if (self.backtest_flag == True and self.cur_bar_time != 0):
                return tool_utils.get_current_bar_dt(self.cur_bar_time)
            else:
                return get_current_minute_bar()
        else:
            return self.cur_bar
        '''
        '''
        前期设计弄复杂了
        找到当天开盘那根bar,并记录id，后边的bar与它相减就行
        '''
        if (self.open_bar_id != 0 and self.cur_bar_id!=0):
            cur_bar = self.cur_bar_id - self.open_bar_id
            if (cur_bar < 0):
                cur_bar = tool_utils.get_current_minute_bar_dt(self.cur_bar_time)
            return int(cur_bar)
        else:
            return tool_utils.get_current_minute_bar_dt(self.cur_bar_time)

    def set_log_level(self, level):
        pass

    def debug(self, msg):
        if (self.debug_level > 0):
            lt = self.get_real_time()
            #print("[%s] %s"%(self.TAG, msg))
            print("[%s] %d-%d %d:%d:%d(bar_id=%d) :%s"%(self.TAG,lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec, self.cur_bar_id, msg))

    def debug5(self, msg):
        if (self.cur_bar_id%5 == 0):
            self.debug(msg)

    def info(self, msg):
        self.logger.info(self.TAG, msg)

    def info5(self, msg):
        if (self.cur_bar_id%5 == 0):
            self.logger.info(self.TAG, msg)

    def set_indictor(self, indictor):
        self.indictor = indictor

    def close(self):
        self.run_flag = False
        self.position = 0
        self.debug("close...")
        self.open_bar_id = 0
        self.new_data()
    
    def in_open_30(self):
        lt = self.get_real_time()
        if (lt.tm_hour==9 and lt.tm_min<30):
            return True
        else:
            return False

    def get_bars_since_entry(self):
        
        if (self.indictor is None):
            self.cur_bar = self.get_current_minute_bar()
            return self.cur_bar - self.entry_bar
        self.cur_bar = self.indictor.get_cur_bar_internal()
        if (self.entry_bar > 0):
            return self.cur_bar - self.entry_bar
        else:
            return -999
        '''
        self.cur_bar = self.get_current_minute_bar()
        print("get_bars_since_entry", self.cur_bar , self.entry_bar)
        return self.cur_bar - self.entry_bar
        '''
    def get_open_bar(self, klines):
        cur_bar = tool_utils.get_current_minute_bar_dt(klines.iloc[-1].datetime)
        open_bar = klines.iloc[-1].id - cur_bar
        #self.debug("open_bar_id=%d k_id=%d time=%s"%(open_bar, klines.iloc[-cur_bar].id, time_to_str(klines.iloc[-cur_bar].datetime)))
        self.open_bar_id = open_bar
        return open_bar

    def convert_bar_inday(self, k_id):
        return k_id - self.open_bar_id

    def get_highest_bar_today(self):
        return self.indictor.get_highest_bar_today()
        
    def get_highest_today(self):
        return self.indictor.get_highest_today()

    def get_lowest_today(self):
        return self.indictor.get_lowest_today()

    def get_lowest_bar_today(self):
        return self.indictor.get_lowest_today()

    def to_hh_bars(self):
        pass

    def to_hh_diff(self):
        pass

    def to_ll_bars(self):
        pass

    def to_ll_diff(self):
        pass

    def get_avg_price(self):
        return self.indictor.get_avg_price_internal()

    def get_checksum_short(self):
        return self.indictor.get_checksum_short_internal()

    def preset_position(self, pos):
        if (self.position != pos):
            self.set_position(pos)

    def get_kpi(self):
        return self.kpi

    def get_atr_daily(self):
        return self.indictor.get_atr_daily()

    def report_trade_result(self):
        pass

    def loss_happend(self, t_dir, loss_p):
        if (t_dir > 0):
            msg = "多损：-%d"%(loss_p)
            self.loss_mark_bar = self.get_current_minute_bar()
        else:
            msg = "空损：-%d"%(loss_p)
        self.loss_mark_bar = self.get_current_minute_bar()
        self.info(msg)

    def gain_happend(self, t_dir, gain_p):
        if (t_dir > 0):
            msg = "多盈：-%d"%(gain_p)
            self.loss_mark_bar = self.get_current_minute_bar()
        else:
            msg = "空盈：-%d"%(gain_p)
        self.earn_mark_bar = self.get_current_minute_bar()
        self.info(msg)

    def get_status(self):
        if (self.run_flag == True):
            return 1
        else:
            return 0

    def check_less(self, left, val):
        if (left>0 and left<val):
            return True
        else:
            return False

    def check_greate(self, left, val):
        if (left>0 and left>val):
            return True
        else:
            return False

    def run_exit_smoothly(self, klines):
        #平滑止损出厂
        pass

    def to_cache(self):
        #keep_position
        pass

    def wait_open(self):
        lt = self.get_real_time()
        if ((lt.tm_hour==9 and lt.tm_min<5) or 
            (lt.tm_hour==21 and lt.tm_min<5)):
            return True
        return False

    #检查是否可以开仓
    def check_open_order(self, t_dir, skip_bar):
        #连续开,间隔
        if (self.exit_bar != 0 and
            t_dir == self.exit_pos and
            self.get_current_minute_bar() - self.exit_bar < skip_bar):
            return False

        #价格限制开仓
        return True

    def check_order(self, skip_bar):
         #连续开,间隔
        if (self.exit_bar != 0 and
            self.get_current_minute_bar() - self.exit_bar < skip_bar):
            return False
        if (self.entry_bar != 0 and
            self.get_current_minute_bar() - self.entry_bar < skip_bar):
            return False
        #价格限制开仓
        return True

    def get_open_price(self):
        return self.indictor.get_open_price()

    def get_kpi_daily(self):
        return self.manager.get_kpi_daily()

    def get_kpi_inday(self):
        if (self.indictor is None):
            return 0

        return self.indictor.get_kpi()

    def base_monitor_position(self, klines):
        if (self.monitor_open == False):
            return  
        if (self.position > 0 and self.cur_bar - self.entry_bar > 20):
            #hh, to_hh = pplib.get_hest_in_range2(klines, 1, self.cur_bar)
            #to_hh_height = 
            hest = self.get_highest_today()
            hest_bar = self.get_highest_bar_today()

            to_hest = hest - self.ask_price 

            if (hest_bar > 45 or to_hest>26):
                self.debug("monitor ping")
                self.set_position(0)
        if (self.position < 0 and self.cur_bar - self.entry_bar > 20):
            #hh, to_hh = pplib.get_hest_in_range2(klines, 1, self.cur_bar)
            #to_hh_height = 
            lest = self.get_lowest_today()
            lest_bar = self.get_lowest_bar_today()

            to_lest = self.ask_price - lest

            if (lest_bar > 45 or to_lest>26):
                self.debug("monitor ping")
                self.set_position(0)

    def get_avg_overs(self):
        return self.indictor.get_avg_overs()

    def get_avg_unders(self):
        return self.indictor.get_avg_unders()

    def get_last_avg_crossover(self):
        return self.indictor.get_last_avg_crossover()
    
    def get_last_avg_crossdown(self):
        return self.indictor.get_last_avg_crossdown()

    #判断高度
    def check_height_ok(self, height, length):
        pass

    def update_kclock(self):
        self.kclock.cur_bar_id = self.cur_bar_id
        self.kclock.cur_bar = self.cur_bar
        self.kclock.entry_bar = self.entry_bar
        self.kclock.exit_bar = self.exit_bar

    def get_profit(self):
        if (self.position > 0):
            return self.cur_price - self.entry_price
        elif (self.position < 0):
            return self.entry_price - self.cur_price
        else:
            return 0
    #角色：Indicator EventRecord RiskManager
    def get_role(self):
        return self.role

    def get_indor_value(self, name):
        '''
        indor_map = self.manager.get_indor_map()
        if (indor_map is None):
            return MyDefaultValue.InvalidInt
        return indor_map.get(name)
        '''
        if (name == Indicator.HoldProfit):
            self.debug("indicator HoldProfit should not be get")
            return 0
        return self.manager.get_indor_value(name)

    def set_indor_value(self, name, value):
        self.manager.drive_indicator(name, value)

    ##########产生本策略相关的指标，驱动给自己############        
    def generate_account_info(self):
        if(self.position == 0):
            return
        
        if (self.position > 0):
            HoldProfit = self.cur_price - self.entry_price
        elif (self.position < 0):
            HoldProfit = self.entry_price - self.cur_price
        self.on_indicator(Indicator.HoldProfit, HoldProfit)

        BarSinceEntry = self.cur_bar - self.entry_bar
        self.on_indicator(Indicator.BarSinceEntry, BarSinceEntry)

        BarsSinceLastExit = self.cur_bar - self.exit_bar
        self.on_indicator(Indicator.BarsSinceLastExit, BarsSinceLastExit)

    def addTradeTask(self, task):
        for itor in self.task_list:
            if (task.name == itor.name and 
                itor.get_status() != itor.S_FINISHED):
                self.debug("addTradeTask(%s) failed"%(task.name))
                return
        self.debug("addTradeTask(%s)"%(task.name))
        self.task_list.append(task)
