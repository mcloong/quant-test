import threading
import time
import os
from datetime import datetime
import time
from tool_utils import is_in_trade_time
import configparser
from param_defines import StrategyKpi, TradeDirection, TrendStatus, StgEvent, MyDefaultValue
import param_defines
from killer_rush import KillerRush
from strategy_avg_cross import StrategyAvgCross
from strategy_waves import StrategyWaves
from strategy_grid import StrategyGrid
from killer_tank import KillerTank
from killer_price_direct import KillerPriceDirect
from strategy_key_price import StrategyKeyPrice
from strategy_flow_stronger import StrategyFlowStronger
from strategy_risk_manager import RiskManager
from strategy_boll_daily import StrategyBollDaily
from strategy_event_drive import StrategyEventDrive
from script_bigsay import ScriptBigSay
from script_rebot import ScriptRebot
from killer_l import KillerL
from killer_s import KillerS
from killer_ninja import KillerNinja
import numpy as np
import pandas as pd
from tqsdk.tafunc import time_to_s_timestamp
from event_recorder import EventRecorder
from kpattern_record import KPatternRecord

class Setting(object):
    pass

class StrategyManager(object):
    def __init__(self, pos_manager, symbol):
    #def __init__(self):
        self.TAG = "StrategyManager"
        self.MAX_ORDERS = 10
        self.MAX_LONG_HOLD_POS = 3
        self.MAX_SHORT_HOLD_POS = -3
        self.MAX_LOSS = -200
        self.MAX_EARN = 500

        self.symbol = symbol
        c = ['who', 'result', 'open_barid', 'open_datetime', 'direction', 'open_price', 'close_barid', 'close_price']
        self.order_list = pd.DataFrame(columns=c)

        self.hold_position = 0

        self.stg_list = []
        self.order_count = 0
        self.run_flag = True
        self.shutdown_flag = False
        self.load_flag = False
        self.pos_manager = pos_manager
        lt = time.localtime(time.time())
        print("search mc_setting-%d%d.log"%(lt.tm_mon,lt.tm_mday))
        self.trade_time = [[21*60, 23*60], [9*60, 10*60+15], [10*60+35, 11*60+30], [13*60+30, 15*60]]

        #成交记录
        self.entry_time = 0
        self.entry_bar = 0
        self.entry_price = 0

        self.setting_flag = False
        self.inited = False
        self.risk_run_flag = False

        self.cur_price = 111
        self.cur_datetime = 0
        self.cur_bar_id = 0

        self.trade_dir = TradeDirection.BUYSELL
        self.run_backtest_enbale = False

        ##统计
        self.kpi_daily = 0
        self.kpi_inday = 0
        #
        self.event_recorder = EventRecorder("ManagerRecorder")
        #指标字典
        self.indor_map = {}

        #配置文件
        self.preset_prediction = 0
        self.force_direction = TradeDirection.BUYSELL
        self.max_buy_price = 0 #限价
        self.min_sell_price = 0
        self.cf_max_long_pos = 0
        self.cf_max_short_pos = 0

        #function
        self.risk_m = RiskManager(symbol, self)
        self.add(self.risk_m)
        self.stg_event = RiskManager(symbol, self)
        self.add(self.stg_event)

        #recorder
        self.kpattern_recorder = KPatternRecord("filter")

        self.start_process()
        #self.pos_manager.set_ma

    def new_day(self):
        if (self.is_setting_expired()):
            self.run_flag = False
            return
        self.run_flag = True
        for stg in self.stg_list:
            stg_name = stg.get_name()
            if (stg_name != "KillerPriceDirect"
               and stg_name != "StrategyWaves"):
                stg.reset()
                stg.start()

        self.new_day_prepare()
        
    def new_day_prepare(self):
        self.init()

    def start(self):
        self.run_flag = True
        for stg in self.stg_list:
            stg.start()
            
    def start_process(self):
        #args是关键字参数，需要加上名字，写成args=(self,)
        th1 = threading.Thread(target=StrategyManager.work_thread, args=(self,))
        th1.start()
    #th1.join()
        
    def add(self, strategy):
        for stg in self.stg_list:
            ret, stg = self.find_strategy(strategy.get_name())
            if (ret == True):
                return
        if (hasattr(self, 'logger') and self.logger is not None):
            strategy.set_logger(self.logger)
        if (hasattr(self, 'indictor') and self.indictor is not None):
            strategy.set_indictor(self.indictor)
        if (strategy.get_name() == "StrategyAvgCross" and self.avg_record is not None):
            strategy.set_avg_recorder(self.avg_record) 
        self.stg_list.append(strategy)

    def remove(self, strategy):
        self.stg_list.remove(strategy)

    def set_indictor(self, indictor):
        self.indictor = indictor
        if (indictor is not None):
            for stg in self.stg_list:
                stg.set_indictor(self.indictor)

    def get_indictor(self):
        return self.indictor

    def set_avg_record(self, record):
        self.avg_record = record

    #day
    def set_watcher(self, watcher):
        self.watcher = watcher

    def get_watcher(self, watcher):
        return self.watcher

    def update_indictor(self, klines):
        self.cur_bar_id = klines.iloc[-1].id
        #self.cur_price = klines.iloc[-1].ask_price1

    def on_tick(self, seriel):
        if (self.indictor is not None):
            self.indictor.on_tick(seriel)
        for stg in self.stg_list:
            stg.on_tick(seriel)

        self.cur_datetime = seriel.iloc[-1].datetime
        self.cur_price = seriel.iloc[-1].ask_price1

    def on_bar(self, klines):
        self.cur_bar_id = klines.iloc[-1].id
        self.update_indictor(klines)
        if (self.indictor is not None):
            self.indictor.on_bar(klines)
        for stg in self.stg_list:
            stg.on_bar(klines)
        
    def on_day_bar(self, dklines):
        if (self.indictor is not None):
            self.indictor.on_day_bar(dklines)
        for stg in self.stg_list:
            stg.on_day_bar(dklines)

    def drive_indicator_object(self, indor):
        #self.indor_map[indor.name]
        for stg in self.stg_list:
            stg.on_indicator_object(indor)

    def drive_indicator(self, name, value):
        self.indor_map[name] = value
        for stg in self.stg_list:
            stg.on_indicator(name, value)

    def drive_kpattern(self, kpt):
        ret = self.kpattern_recorder.add(kpt)
        if (ret == False):
            return
        for stg in self.stg_list:
            stg.on_kpattern(kpt)

    def broadcast_event(self, event_name, event_param):
        '''
        ret = self.event_recorder.add(event_name, event_param, self.cur_bar_id, self.cur_datetime)
        if (ret == False):
            return 
        '''
        self.my_print("event_name=%s"%(event_name))
        for stg in self.stg_list:
            stg.on_event(event_name, event_param)

    def run(self, klines, ask_price, bid_price, avg_price):
        for stg in self.stg_list:
            stg.run(klines, ask_price, bid_price, avg_price)
        
        self.cur_price = ask_price

    def load_setting(self):
        if(self.load_flag == True):
            return
        '''
        lt = time.localtime(time.time())
        #filename = "rb_setting-%d%d.ini"%(lt.tm_mon,lt.tm_mday)
        filename = "rb_setting.ini"#commands
        if (os.path.exists(filename)):
            pass
        
        '''
        lt = time.localtime(time.time())
        filename = "config/rb_setting.ini"#commands
        if (os.path.exists(filename) == False):
            return
        
        cp = configparser.ConfigParser()
        cp.read(filename)
        print(filename)
        print(cp.sections())

        if ("rb" not in cp):
            return
        if ("runable" in cp['rb']):
            runable =  cp['rb']['runable']
            if (runable == "false"):
                print ("rb runbale=false")
                return
            str_date = cp['rb']['date']
            year = int(str_date[0:4])
            mon = int(str_date[4:6])
            day = int(str_date[6:8])
            if (lt.tm_year != year or lt.tm_mon != mon or lt.tm_mday != day):
                print ("config is old")
                return
        self.setting_flag = True

        if ("stg_avg" in cp):
            self.load_stg_avg(cp)

        if ("stg_wave" in cp):
            self.load_stg_wave(cp)

        if ("stg_grid" in cp):
            self.load_stg_grid(cp)

        if ("killer_tank" in cp):
            self.load_killer_tank(cp)

        if ("price_direct" in cp):
            self.load_killer_price_direct(cp)

        if ("flow_stronger" in cp):
            self.load_stg_flow_stronger(cp)

        if ("key_price" in cp):
            self.load_stg_key_price(cp)

        if ("boll_daily" in cp):
            self.load_stg_boll_daily(cp)

        if ("killer_ninja" in cp):
            self.load_stg_killer_ninja(cp)

        if ("trade_script" in cp):
            if ("runable" in cp['trade_script']):
                runable =  cp['trade_script']['runable']
                if (runable == "false"):
                    pass

        if ("script_rebot" in cp):
            self.load_script_rebot(cp)

        if ("big_say" in cp):
            self.load_stg_big_say(cp)
            '''
            if ("script" in cp['trade_script']):
                script = cp['trade_script']['script']
                if(script == "OpenBuy"):
                    self.my_print("load KillerRush from trade_sc")
                    ret,stg = self.find_strategy("KillerRush")
                    if (ret == False):
                        stg = KillerRush(self.symbol, self)
                        self.add(stg)
                    #yestday_bar = self.indictor.get_lastday_quote()
                    yestday_bar = self.day_klines.iloc[-1]
                    #print (yestday_bar)
                    stg.set_hh(yestday_bar.close + 40)
                    stg.set_ll(yestday_bar.close)
                    stg.set_trade_direction(TradeDirection.BUYONLY)
                    stg.start()
                    
                elif(script == "SellBuy"):
                    pass
                
                    ret,stg = self.find_strategy("KillerRush")
                    if (ret == False):
                        stg = KillerRush(self.symbol, self)
                        self.add(stg)
                    yestday_bar = self.indictor.get_get_lastday_quote()
                    stg.set_hh(yestday_bar.close + 40)
                    stg.set_ll(yestday_bar.close-29)
                    stg.set_trade_direction(TradeDirection.SELLONLY)
                    stg.start()
                    
                '''

        self.load_rb_setting(cp)

        self.load_flag = True

    def is_setting_expired(self):
        lt = time.localtime(time.time())
        filename = "config/rb_setting.ini"#commands
        if (os.path.exists(filename) == False):
            return
        
        cp = configparser.ConfigParser()
        cp.read(filename)
        print(filename)
        print(cp.sections())

        if ("rb" not in cp):
            return
        if ("date" in cp['rb']):
            str_date = cp['rb']['date']
            year = int(str_date[0:4])
            mon = int(str_date[4:6])
            day = int(str_date[6:8])
            if (lt.tm_year == year or lt.tm_mon == mon or lt.tm_mday - day > 2): #超过两天算过期
                print ("config is expired1")
                return True
            if (lt.tm_year == year or lt.tm_mon != mon): #超过两天算过期
                print ("config is expired2")
                return True

        return False

    def load_runningtime_setting(self):
        filename = "config/rb_running.ini"#commands
        if (os.path.exists(filename) == False):
            return

        self.my_print(filename)
        cp = configparser.ConfigParser()
        cp.read(filename)
        print(cp.sections())
                
        if ("runable" in cp['rb']):
            runable =  cp['rb']['runable']
            if (runable == "false"):
                print("runable false")
                #self.pos_manager.close()
                self.close()
            elif (runable == "true"):
                print("runable true")

        if ("stg_grid" in cp):
            self.my_print("load grid.....")
            self.load_stg_grid(cp)
           
        if("avg_cross" in cp):
            print("avg_cross")

        if("killer_tank" in cp):
            self.my_print("load killer_tank......")
            self.load_killer_tank(cp)
        
        if("price_direct" in cp):
            self.load_killer_price_direct(cp)

        if ("key_price" in cp):
            self.load_stg_key_price(cp)
        
        if ("killer_rush" in cp):
            self.load_killer_rush(cp)
        
        if ("flow_stronger" in cp):
            self.load_stg_flow_stronger(cp)

        if ("boll_daily" in cp):
            self.load_stg_boll_daily(cp)

        if ("rb" in cp):
            self.load_rb_setting(cp)

        if ("script_rebot" in cp):
            self.load_script_rebot(cp)

        dstname = "%s.mark"%(filename)
        if (os.path.exists(dstname) == True):
            os.remove(dstname)
        os.rename(filename, dstname)

    def load_rb_setting(self, cp):
        if ("rb" in cp):
            '''
            if ("runable" in cp['rb']):
                runable =  cp['rb']['runable']
                if (runable == "false"):
                    print("runable false")
                    #self.pos_manager.close()
                    self.close()
                    return
                elif (runable == "true"):
                    print("runable true")
            '''
            self.my_print("==============rb setting==========")
            if ("direction" in cp['rb']):
                str_dir = cp['rb']['direction']
                tr_dir = TradeDirection.BUYSELL
                if (str_dir == "SellOnly"):
                    tr_dir = TradeDirection.SELLONLY
                elif (str_dir == "BuyOnly"):
                    tr_dir = TradeDirection.BUYONLY
                self.set_trade_direction(tr_dir)
        
            if ("preset_prediction" in cp['rb']):
                self.preset_prediction = int(cp['rb']['preset_prediction'])
                if ("force_direction" in cp['rb']):
                    trade_dir = cp['rb']['force_direction']
                    if (trade_dir == "BuySell"):
                        self.set_trade_direction(TradeDirection.BUYSELL)
                        self.force_direction = TradeDirection.BUYSELL
                    elif (trade_dir == "BuyOnly"):
                        self.set_trade_direction(TradeDirection.BUYONLY)
                        self.force_direction = TradeDirection.BUYONLY
                    elif(trade_dir == "SellOnly"):
                        self.set_trade_direction(TradeDirection.SELLONLY)
                        self.force_direction = TradeDirection.SELLONLY
                    print("force_direction=%s"%(self.force_direction))
                #self.my_print("=================================")
            
            if("max_buy_price" in cp['rb']):
                val = int(cp['rb']['max_buy_price'])
                if (val != 0):
                    self.max_buy_price = val
            if("min_sell_price" in cp['rb']):
                val = int(cp['rb']['min_sell_price'])
                if (val != 0):
                    self.min_sell_price = val
            if("max_long_pos" in cp['rb']):
                #self.cf_max_long_pos = int(cp['rb']['max_long_pos'])
                val = int(cp['rb']['max_long_pos'])
                if (val != 0):
                    self.MAX_LONG_HOLD_POS = val
            if("max_short_pos" in cp['rb']):
                #self.cf_max_short_pos = int(cp['rb']['max_short_pos'])
                val = int(cp['rb']['max_short_pos'])
                if (val != 0):
                    self.MAX_SHORT_HOLD_POS = val

    def load_stg_avg(self, cp):
        if ("stg_avg" in cp):
            ret , stg = self.find_strategy("StrategyAvgCross")
            if (ret == False):
                stg = StrategyAvgCross(self.symbol, self)
                self.add(stg)
            if ("runable" in cp["stg_avg"]):
                runable = cp["stg_avg"]["runable"]
                
                if (runable == "false"):
                    stg.stop()
                elif (runable == "true"):
                    stg.start()

    def load_stg_wave(self, cp):
        if ("stg_wave" in cp):
            ret, stg = self.find_strategy("StrategyWaves")
            runable = cp['stg_wave']['runable']
            if (runable == "false"):
                if (ret == True and stg is not None):
                    stg.stop()
            elif(runable == "true"):
                if (ret == False):
                    stg = StrategyWaves(self.symbol, self)
                    self.add(stg)
                stg.start()
    
    def load_stg_grid(self, cp):
        if ("stg_grid" in cp):
            runable = cp['stg_grid']['runable']
            h2 = int(cp['stg_grid']['high_level2'])
            h1 = int(cp['stg_grid']['high_level1'])
            l1 = int(cp['stg_grid']['low_level1'])
            l2 = int(cp['stg_grid']['low_level2'])
            print("runable=%s high_level2=%d high_level1=%d low_level1=%d low_level2=%d "%(runable, int(h2), int(h1), int(l1), int(l2)))
            ret , stg = self.find_strategy("StrategyGrid")
            if (ret == False):
                stg = StrategyGrid(self.symbol,self, h2, h1, l1, l2)
                self.add(stg)

            if (runable == "false"):
                stg.stop()
            elif (runable == "true"):
                stg.start()

    def load_stg_key_price(self, cp):
        ret, stg = self.find_strategy("StrategyKeyPrice")
        
        runable = cp['key_price']['runable']
        if (runable == "false"):
            if (ret == True and stg is not None):
                stg.stop()
        elif(runable == "true"):
            if (ret == False):
                stg = StrategyKeyPrice(self.symbol, self)
                self.add(stg)
            stg.start()
            if('key_price' in cp["key_price"]):
                key_price = int(cp["key_price"]["key_price"])
                if (key_price <= 0):
                    stg.set_key_price(key_price)

    def load_stg_flow_stronger(self, cp):
        ret, stg = self.find_strategy("StrategyFlowStronger")
        
        runable = cp['flow_stronger']['runable']
        if (runable == "false"):
            if (ret == True and stg is not None):
                stg.stop()
        elif(runable == "true"):
            if (ret == False):
                stg = StrategyFlowStronger(self.symbol, self)
                self.add(stg)
            
            stg.start()
            #key_price = int(cp["stg_flow_stronger"]["key_price"])

    def load_stg_boll_daily(self, cp):
        if ("boll_daily" in cp):
            ret,stg = self.find_strategy("StrategyBollDaily")
            runable = cp['boll_daily']['runable']
            if (runable == "false"):
                if (ret == True and stg is not None):
                    stg.stop()
            elif(runable == "true"):
                if (ret == False):
                    stg = StrategyBollDaily(self.symbol, self)
                    self.add(stg)
                stg.start()
    
    def load_stg_killer_ninja(self, cp):
        if ("killer_ninja" in cp):
            ret,stg = self.find_strategy("KillerNinja")
            runable = cp['killer_ninja']['runable']
            if (runable == "false"):
                if (ret == True and stg is not None):
                    stg.stop()
            elif(runable == "true"):
                if (ret == False):
                    stg = KillerNinja(self.symbol, self)
                    self.add(stg)
                stg.start()

    def load_killer_rush(self, cp):
        if ("killer_rush" in cp):
            ret,stg = self.find_strategy("KillerRush")
            runable = cp['killer_rush']['runable']
            if (runable == "false"):
                if (ret == True and stg is not None):
                    stg.stop()
            elif(runable == "true"):
                if (ret == False):
                    stg = KillerRush(self.symbol, self)
                    self.add(stg)

                hh = 0
                ll = 0
                if ("hh" in cp['killer_rush']):
                    hh = int(cp['killer_rush']['hh'])
                if ("ll" in cp['killer_rush']):
                    ll = int(cp['killer_rush']['ll'])
                if ("trade_dir" in cp['killer_rush'] ):
                    self.my_print(" trade_dir in cp['killer_rush']")
                    trade_dir = param_defines.trade_dir_string_to_std(cp['killer_rush']['trade_dir'])
                    stg.set_hh(hh)
                    stg.set_ll(ll)
                    stg.set_trade_direction(trade_dir)
                
                stg.start()

    def load_killer_tank(self, cp):
        if ("killer_tank" in cp):
            ret, stg = self.find_strategy("KillerTank")
            if (ret == False):
                stg = KillerTank(self.symbol, self)
                self.add(stg)
            up_count = 0
            down_count = 0
            if ("up_count" in cp["killer_tank"]):
                up_count = int(cp["killer_tank"]["up_count"])
            if ("down_count" in cp["killer_tank"]):
                down_count = int(cp["killer_tank"]["down_count"])
            if ("runable" in cp["killer_tank"]):
                runable = cp["killer_tank"]["runable"]
                if (runable == "true"):
                    if (up_count > 0):
                        stg.set_up_count(up_count)
                    if (down_count > 0):
                        stg.set_down_count(down_count)
                    stg.start()
                    if ("trade_dir" in cp['killer_tank'] ):
                        trade_dir = param_defines.trade_dir_string_to_std(cp['killer_tank']['trade_dir'])
                        stg.set_trade_direction(trade_dir)
                else:
                    stg.stop()


    def load_killer_price_direct(self, cp):
        if ("price_direct" in cp):
            if ("runable" not in cp['price_direct']):
                self.my_print("runable not in cp[price_direct]")
                return
            ret, stg = self.find_strategy("KillerPriceDirect")
            runable = cp['price_direct']['runable']
           
            if (runable == "false"):
                if (ret == True and stg is not None):
                    stg.stop()
            elif(runable == "true"):
                if (ret == False):
                    stg = KillerPriceDirect(self.symbol, self)
                    self.add(stg)
                hh = 0
                ll = 0
                if ("hh" in cp["price_direct"]):
                    hh = int(cp['price_direct']['hh'])
                if ("ll" in cp["price_direct"]):
                    ll = int(cp['price_direct']['ll'])
                if (hh==0 or ll==0):
                    return
                stg.set_hh(hh)
                stg.set_ll(ll)
                if ("trade_dir" in cp['price_direct']):
                    trade_dir = cp['price_direct']['trade_dir']
                    dir_val = param_defines.trade_dir_string_to_std(trade_dir)
                    stg.set_trade_direction(dir_val)
                stg.start()

    def load_stg_big_say(self, cp):
        if ("big_say" in cp):
            if ("runable" not in cp['big_say']):
                self.my_print("runable not in cp[price_direct]")
                return
            ret, stg = self.find_strategy("ScpBigSay")
            runable = cp['big_say']['runable']
           
            if (runable == "false"):
                if (ret == True and stg is not None):
                    stg.stop()
            elif(runable == "true"):
                if (ret == False):
                    stg = ScriptBigSay(self.symbol, self)
                    self.add(stg)
            stg.start()

    def load_script_rebot(self, cp):
        if ("script_rebot" in cp):
            if ("runable" not in cp['script_rebot']):
                self.my_print("runable not in cp[price_direct]")
                return
            ret, stg = self.find_strategy("ScpRebot")
            runable = cp['script_rebot']['runable']
           
            if (runable == "false"):
                if (ret == True and stg is not None):
                    stg.stop()
            elif(runable == "true"):
                if (ret == False):
                    stg = ScriptRebot(self.symbol, self)
                    self.add(stg)
            stg.start()

    def load_killer(self, kpi):
        if (kpi > 35):
            ret, stg = self.find_strategy("KillerL")
            if (ret == False):
                stg = KillerL(self.symbol, self)
                self.add(stg)
                self.my_print("add KillerL")
            if (kpi >= 55):
                stg.set_level(1)
            elif (kpi >= 47):
                stg.set_level(2)
            else:
                stg.set_level(3)
            stg.start()
        elif (kpi < -35):
            ret, stg = self.find_strategy("KillerS")
            if (ret == False):
                stg = KillerS(self.symbol, self)
                self.add(stg)
            if (kpi <= -55):
                stg.set_level(1)
            elif (kpi <= -47):
                stg.set_level(3)
            else:
                stg.set_level(3)
            stg.start()

    def create_killer_tank(self):
        ret, stg = self.find_strategy("KillerTank")
        if (ret == True):
            return stg
        stg = KillerTank(self.symbol, self)
                    
    def find_strategy(self, name):
        for stg in self.stg_list:
            if (stg.get_name() == name):
                return True, stg

        return False, None

    def set_position_direct(self, from_stg, pos):
        if (from_stg == "RiskManager"):
            self.hold_position += pos
            self.pos_manager.set_position(self.hold_position)
            self.my_print("set_position_direct from RiskManager pos=%d"%(self.hold_position))

        #self.hold_position = pos

    def set_position(self, from_stg, pos):
        if (self.run_flag == False and pos!=0):
            return False

        # 开仓方向可以在这里面进行限制
        if (pos > 0 and self.max_buy_price != 0 and self.cur_price > self.max_buy_price):
            self.my_print("开多限价......")
            return False

        if (pos < 0 and self.min_sell_price != 0 and self.cur_price < self.min_sell_price):
            self.my_print("开空限价......")
            return False

        if (self.order_count > self.MAX_ORDERS and pos != 0):
            print("[%s] [Worning] too much order, stop..."%(self.TAG))
            return False
        if (pos != 0):
            self.order_count = self.order_count + 1
        #tm = time.time()
        if (pos > 0):
            tdir = "BuyOpen" 
        elif (pos < 0):
            tdir = "SellOpen"
        else:
            tdir = "Close"
        #self.order_list.loc[len(self.order_list)] = [from_stg, self.cur_bar_id, self.cur_datetime, tdir,self.cur_price] 
        #['who', 'result', 'open_barid','open_datetime', 'direction', 'open_price', 'close_barid', 'close_price']
        self.order_list.loc[len(self.order_list)] = [from_stg, "true", self.cur_bar_id, self.cur_datetime, tdir, self.cur_price, "999", "0"] 
        real_pos = 0
        for stg in self.stg_list:
            if (stg.get_name() is not None and stg.get_name() != from_stg):
                sp = stg.get_strategy_position()
                real_pos = real_pos + sp
                if (sp != 0):
                    self.my_print("%s position=%d"%(stg.get_name(), sp))
        '''
        20200608 
        stg里的set_position在manager的set_position执行完才改变
        '''
        real_pos += pos

        tmp = self.risk_m.check_open_position(real_pos)
        if (pos > 0 and real_pos > 0 and tmp < real_pos):
            self.my_print("限制多开")
            return False
        if (pos < 0 and real_pos < 0 and tmp > real_pos):
            self.my_print("限制空开")
            return False

        if (real_pos > self.MAX_LONG_HOLD_POS):
            real_pos = self.MAX_LONG_HOLD_POS
            self.my_print("real_pos(%d) > self.MAX_LONG_HOLD_POS(%d)"%(real_pos, self.MAX_LONG_HOLD_POS))
        elif (real_pos < -abs(self.MAX_SHORT_HOLD_POS)):
            real_pos = -abs(self.MAX_SHORT_HOLD_POS)
            self.my_print("real_pos(%d) > self.MAX_SHORT_HOLD_POS(%d)"%(real_pos, self.MAX_SHORT_HOLD_POS))

        if (self.run_backtest_enbale == False):
            self.pos_manager.set_position(real_pos)

        self.hold_position = real_pos
        self.my_print("current position(%d)"%(real_pos))

        return True

    def get_position(self):
        real_pos = 0
        for stg in self.stg_list:
            if (stg.get_name() is not None):
                real_pos = real_pos + stg.get_strategy_position()
        
        return real_pos

    def import_time_inthread(self):
        pass

    def load_runningtime_setting_inthread(self):
        try:
            self.load_runningtime_setting()
        except Exception as e:
                print('Error:',e)
        finally:
            pass

    def risk_manager_inthread(self):
        profit = self.pos_manager.get_profit()
        hold_pos = self.pos_manager.get_hold_position()
        max_los = self.MAX_LOSS
        if (hold_pos >= 2):
            max_los = int(self.MAX_LOSS*1.5)
        if (profit is not None and profit < max_los): # 止损
            #self.pos_manager.set_position(0)
            self.my_print("max_loss hapanded")
            self.my_print("[%s] profit=%d"%(self.TAG, profit))
            '''
            real_pos = self.pos_manager.get_hold_position()
            ret, risk_m = self.find_strategy("RiskManager")
            if (ret == False):
                risk_m = RiskManager(self.symbol, self)
                self.add(risk_m)
            if (risk_m.get_status() == 1):
                return
            
            if (real_pos > 0):
                self.MAX_LONG_HOLD_POS = 1
            if (real_pos < 0):
                self.MAX_SHORT_HOLD_POS = -1
            risk_m.set_loss(real_pos, profit)
            risk_m.start()
            '''

    def print_position_inthread(self):
        #持仓
        position_profit = self.pos_manager.get_position_profit()
        #平 盈亏
        close_profit = self.pos_manager.get_close_profit()
        if ((int(close_profit)==0 and int(position_profit)==0) == False):
            self.my_print("position_profit=%d close_profit=%d"%(int(position_profit), int(close_profit)))

    def work_thread(self):
        #while(self.run_flag):
        while(self.shutdown_flag == False):
            lt = time.localtime(time.time())
            #test
            
            # 非运行时间
            if (is_in_trade_time() == False):
                time.sleep(5)
                #self.my_print("not _in_trade_time")
                continue

            # 每天初始化
            if (lt.tm_hour == 8 and lt.tm_min >=58 and self.inited == False):
                self.new_day_prepare()

            #加载中途的配置
            if (lt.tm_min%2 == 0):
                #self.my_print("load_runningtime_setting_inthread")
                self.load_runningtime_setting_inthread()

            #运行耗时任务       
            for stg in self.stg_list:
                stg.timer_task()

            #风险管理
            if (lt.tm_min%3==0 and lt.tm_sec == 5 and self.risk_run_flag == False):
                self.risk_manager_inthread()
                self.risk_run_flag = True

                if ((lt.tm_min%15==0) or (lt.tm_hour==14 and lt.tm_min==53) or (lt.tm_hour==23 and lt.tm_min==53)):
                    self.print_position_inthread()
            elif(lt.tm_min%3!=0):
                self.risk_run_flag = False

            if ((lt.tm_hour==14 and lt.tm_min==55 and lt.tm_sec==2) or (lt.tm_hour==23 and lt.tm_min==55 and lt.tm_sec==2)):
                self.print_position_inthread()

            #关键时间
            if (lt.tm_hour == 11 and lt.tm_min >= 20):
                pass
            elif (lt.tm_hour == 14 and lt.tm_min > 0 and lt.tm_min < 20):
                pass

            if (lt.tm_hour == 14 and lt.tm_min >= 58):
                self.close()

            time.sleep(1)

    def report_kpi(self, stg_name, kpi):
        if (stg_name == "StategyGrid"):
            if (kpi >= StrategyKpi.InEffective):
                print ("breaker next....")

    def report_walkpath(self, stg_name, direction):
        pass
        
    def report_key_price(self, stg_name, type, price):
        if (stg_name == "StategyGrid"):
            pass

    def sell(self, price):
        pass

    def sell_short(self, price):
        pass

    def buy(self, price):
        pass

    def buy_cover(self, price):
        pass

    def set_logger(self, logger):
        self.logger = logger
        for stg in self.stg_list:
            stg.set_logger(logger)

    #综合日线及日内
    def get_market_prediction(self):
        inday_kpi = 0
        longday_kpi = 0
        if (self.indictor is not None):
            inday_kpi = self.indictor.get_kpi()
            self.my_print("inday_kpi=%d"%(inday_kpi))

        ret, self.watcher = self.find_strategy("StrategyWatcher")
        if (ret == True and self.watcher is not None):
            longday_kpi = self.watcher.get_kpi()
            self.my_print("longday_kpi=%d"%(longday_kpi))

        if (abs(inday_kpi) >= 50):
            kpi = int(inday_kpi*0.8 + longday_kpi*0.24)
        elif (abs(inday_kpi) > 20):
            kpi = int(inday_kpi*0.6 + longday_kpi*0.4)
        else:
            kpi = int(inday_kpi*0.3 + longday_kpi*0.7)
            
        if (inday_kpi>10 and longday_kpi<-10):
            pass
        elif (inday_kpi<-10 and longday_kpi>10):
            pass
        else:
            pass

        return kpi

    #日线级别
    def get_market_prediction_daily(self):
        ret, self.watcher = self.find_strategy("StrategyWatcher")
        watcher_forecat = 0
        if (ret == True and self.watcher is not None):
            watcher_forecat = self.watcher.get_prediction_val()

        if (self.preset_prediction != 0):
            if (watcher_forecat == 0):
                self.my_print("use setting preset_prediction")
                return self.preset_prediction
        else:
            return watcher_forecat

        return 0

    # 开始前调用
    def trade_script(self):
        pass

    def trade_script_run(self):
        pass

    def close(self):
        if (self.run_flag == False):
            self.pos_manager.close()
            return
        self.inited = 0
        self.run_flag = False
        keep_pos = 0
        for stg in self.stg_list:
            stg.close()
            keep_pos += stg.get_strategy_position()

        self.pos_manager.set_keep_position(keep_pos)
        self.pos_manager.close()


    def shutdown(self):
        self.close()
        self.shutdown_flag = True

    def init(self):
        self.order_list = self.order_list.drop(index=self.order_list.index)
        self.order_count = 0

        #self.indictor.preparse_dayline_trend()
        self.load_setting()
        self.inited = True
    
    def update_day_klines(self, dklines):
        self.day_klines = dklines

    #应该用这个接口供外部调用
    def drive_event(self, who, event, event_param):
        ret = self.event_recorder.add(event, event_param, who, self.cur_bar_id, self.cur_datetime)
        if (ret == False):
            self.my_print("处在上条消息里")
            return 
        self.my_print("who=%s, event=%s, event_param=%s"%(who, event, event_param))
        if (event == StgEvent.LowRange):
            self.run_stg_wave()
        #参考日线，kpi>30,<-30
        elif (event == StgEvent.BigBangBreakUp):
            self.do_bigbang_break("Up")
        elif (event == StgEvent.BigBangBreakDown):
            self.do_bigbang_break("Down")
            #self.run_killer_rush(c_param)
            #self.do_bigbang_break
            #self.on_event()
        elif (event == StgEvent.BigBangUp):
            self.run_killer_rush("up")
        elif (event == StgEvent.BigBangDown):
            self.run_killer_rush("down")
        elif(event == StgEvent.GapUp):
            lt = self.get_real_time()
            if (lt.tm_wday == 0):
                self.set_trade_direction(TradeDirection.BUYONLY)
        elif(event == StgEvent.GapDown):
            lt = self.get_real_time()
            if (lt.tm_wday == 0):
                self.set_trade_direction(TradeDirection.SELLONLY)

        self.broadcast_event(event, event_param)

    def on_command(self, who, c_type, c_param):
        self.my_print("who=%s, c_type=%s, c_param=%s"%(who, c_type, c_param))
        ret = self.event_recorder.add(c_type, c_param, who, self.cur_bar_id, self.cur_datetime)
        if (ret == False):
            self.my_print("处在上条消息里")
            return 
        #print(type(c_param))
        '''
        if isinstance(c_param, int):
            self.my_print("who=%s, c_type=%s, c_param=%d"%(who, c_type, c_param))
        if isinstance(c_param, str):
            self.my_print("who=%s, c_type=%s, c_param=%s"%(who, c_type, c_param))
        '''
        if (c_type == "TradeDirection"):
            t_dir = c_param 
            if (who == "StrategyWatcher"):
                if (self.force_direction == TradeDirection.BUYONLY):
                    if (t_dir == TradeDirection.SELLONLY):
                        t_dir = TradeDirection.BUYSELL
                        self.my_print("trade direction 有歧义")
                    else:
                        t_dir = TradeDirection.BUYONLY
                elif (self.force_direction == TradeDirection.SELLONLY):
                    if (t_dir == TradeDirection.BUYONLY):
                        t_dir = TradeDirection.BUYSELL
                        self.my_print("trade direction 有歧义")
                    else:
                        t_dir = TradeDirection.BUYSELL
                self.set_trade_direction(t_dir)
                #for stg in self.stg_list:
                #    stg.set_trade_direction(t_dir)
        #日线级别只作用在开盘阶段，以及突破后是否跟进
        #开后半小时算起点，每个半小时报告kpi
        #比如日线做多，但是很快一步到位，后边横盘或者下跌，应该重新更新trade_direction
        elif (c_type == "ReportKpi"):
            if (who == "StrategyWatcher"):
                #print("c_param typr=", type(c_type))
                if isinstance(c_param, int):
                    kpi = c_param
                else:
                    kpi = int(c_param)
                self.kpi_daily = kpi
                if (abs(kpi) > 35):
                    self.my_print("load_killer ")
                    self.load_killer(kpi)
            elif (who == "McIndictors"):
                if isinstance(c_param, int):
                    kpi = c_param
                else:
                    kpi = int(c_param)
                self.kpi_inday = kpi
                if (kpi > 50):
                    self.my_print(" up.. inday ")
                    self.set_trade_direction(TradeDirection.BUYONLY)
                if (kpi > 30):
                    self.adjust_trade_dir()
                if (kpi < -50):
                    self.my_print(" down.. inday ")
                    self.set_trade_direction(TradeDirection.SELLONLY)
                if (kpi < -30):
                    self.adjust_trade_dir()
    
    def do_bigbang_break(self, direction):
        #update tank
        if (direction == "Down"):
            #限制方向
            if (self.trade_dir == TradeDirection.BUYONLY):
                self.set_trade_direction(TradeDirection.BUYSELL)
            #调用tank
            killer_tank = self.create_killer_tank()
            killer_tank.set_mode_wave_down()
            killer_tank.start()
            #trend_status = self.get_trend_status()
            kpi_daily = self.get_kpi_daily()
            if (kpi_daily < -25):# 震荡
                self.run_killer_rush("Down")
        elif (direction == "up"):
            #限制方向
            if (self.trade_dir == TradeDirection.SELLONLY):
                self.set_trade_direction(TradeDirection.BUYSELL)
            killer_tank = self.create_killer_tank()
            killer_tank.set_mode_wave_up()
            killer_tank.start()
            kpi_daily = self.get_kpi_daily()
            if (kpi_daily > 25):# 震荡
                self.run_killer_rush("Up")

    def do_bigbang(self, direction):
        pass

    def adjust_trade_dir(self):
        lt = self.get_real_time()
        if (lt.tm_hour > 9 and lt.tm_hour < 21):
            if (self.kpi_daily > 35 and self.kpi_inday < -30):
                self.broadcast_event(StgEvent.UpTrendBreak, "")
            if (self.kpi_daily < -35 and self.kpi_inday > 30):
                self.broadcast_event(StgEvent.DownTrendBreak, "")

    def run_stg_wave(self):
        #ret, watcher = self.find_strategy("StrategyWatcher")
        prediction_daily = self.get_market_prediction() 

        hh = self.indictor.get_highest_today()
        ll = self.indictor.get_lowest_today()

        hh1 = hh-5
        ll1 = ll-5
        hh2 = hh+18
        ll2 = ll-18

        ret, stg = self.find_strategy("StrategyGrid")
        if (ret == False):
            stg = StrategyGrid(self.symbol, self, hh2, hh1, ll1, ll2)
            self.add(stg)
        else:
            if (stg.get_status() == 1):
                sym = "%s-2"%(self.symbol)
                stg = StrategyGrid(sym, self, hh2, hh1, ll1, ll2)
                self.add(stg)
            else:
                stg.set_h2(hh2)
                stg.set_h1(hh1)
                stg.set_l2(ll2)
                stg.set_l1(ll1)
        stg.start()
        self.my_print("low_range，run stg_grid hh1=%d ll1=%d"%(hh1, ll1))

    def run_killer_rush(self, c_param):
        prediction_val = self.get_market_prediction_daily()
        if (prediction_val>0 and c_param == "Buy"):
            ret, stg = self.find_strategy("KillerRush")
            if (ret == False):
                stg = KillerRush(self.symbol, self)
                self.add(stg)
            stg.set_trade_direction(TradeDirection.BUYONLY)
            stg.start()
            self.my_print("BigBangBreak，run KillerRush")
        elif (prediction_val<0 and c_param == "Sell"):
            ret, stg = self.find_strategy("KillerRush")
            if (ret == False):
                stg = KillerRush(self.symbol, self)
                self.add(stg)
            stg.set_trade_direction(TradeDirection.SELLONLY)
            stg.start()
            self.my_print("BigBangBreak，run KillerRush")

    def my_print(self, msg):
        lt = time.localtime(time.time())
        print("%d-%d %d:%d:%d - [%s] - :%s"%(lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec, self.TAG, msg))

    def open_backtest(self):
        self.run_backtest_enbale = True
        for stg in self.stg_list:
            stg.open_backtest()

    def is_backtest(self):
        pass

    def set_trade_direction(self, tr_dir):
        self.trade_dir = tr_dir
        for stg in self.stg_list:
            stg.set_trade_direction(tr_dir)

    def get_trade_direction(self):
        return self.trade_dir

    def get_real_time(self):  
        if (self.run_backtest_enbale == True):
            if (self.cur_datetime != 0):
                return time.localtime(time_to_s_timestamp(self.cur_datetime))
            elif (self.cur_datetime != 0):
                return time.localtime(time_to_s_timestamp(self.cur_datetime))
        
        return time.localtime(time.time())

    def get_kpi_daily(self):
        return self.kpi_daily 

    def get_prediction_val_daily(self):
        return self.watcher.get_prediction_val()

    def get_trend_status(self):
        return self.watcher.get_trend_status()

    def get_profit(self):
        profit = self.pos_manager.get_profit()

        return profit

    def get_hold_pos(self):
        hold_pos = self.pos_manager.get_hold_position()
        
        return hold_pos 

    def get_balance(self):
        return self.pos_manager.get_balance()

    def set_max_long_pos(self, pos):
        self.MAX_LONG_HOLD_POS = pos

    def set_max_short_pos(self, pos):
        self.MAX_SHORT_HOLD_POS = pos

    def get_cfg_max_long_pos(self):
        return self.MAX_LONG_HOLD_POS

    def get_cfg_max_short_pos(self):
        return self.MAX_SHORT_HOLD_POS

    def get_order_list(self):
        return self.order_list

    def get_indor_value(self, name):
        if name in self.indor_map:
            return self.indor_map[name]
        else:
            return MyDefaultValue.InvalidInt

    def kevent_to_kpattern(self, event, value):
        pass
#test
'''
stg_manager = StrategyManager()
#stg_manager.start_process()
try:
    stg_manager.load_runningtime_setting()
except Exception as e:
    print('Error:',e)
finally:
    print('....')
'''