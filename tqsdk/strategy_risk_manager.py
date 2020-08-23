# 运行前预测
# 自动产生max_position

#二、运行中监控
#监控盈利、损失
#    监控资金曲线
#   损失：启动止损，逐步退出
#   盈利：
#监控count
#   顶部横盘（非突破） 限制仓数
#   lowrange 
#   day线 Bigbang面临回调
#监控k线状态和account匹配度
#
#
#


'''
#思路
1. 判断条件记录的问题：监控的指标放到event_record里，然后每次检测event_record里最近的更新
2. 账户监控调整和基于K线状态调整 可能会产生冲突，通过规范task行为解决
   比如klines马上要触及ma20，这时候止损要先等一等，或者本来止损两个，现在需要止损一个

   class TODOlist {
        initial_pos
        target_pos
        min_interval
        max_interval
        timeout
    
        priority = 0 #优先级，当另一个任务需要合并时做参考
        combine()
   }

'''
from tool_utils import get_minute
from strategy_base import StrategyBase
import pplib
from param_defines import StrategyKpi, TradeDirection, StgEvent
from indicator_recorder import IndicatorRecorder
from k_parser import KParser
from enum import Enum
import numpy as np
import pandas as pd
from event_recorder import EventRecorder
from kpattern_record import KPatternRecord
from kpattern.kpattern_back_series import KPBackFromKeySupportLine, KPBackFromKeyResistancePrice
from kpattern.kpattern_base import BarType

class StringStdClass(object):
    def __init__(self):
        self.LossExitTask = "LossExitTask"
SelfString = StringStdClass()

class RiskManager(StrategyBase):
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "RiskManager", manager)
        self.TAG = "RiskManager"
        self.update_interval = 5
        self.trade_dir = TradeDirection.BUYSELL
        self.hold_pos = 0
        self.mark_price = 0
        self.ABS_MAX_LOSS = 20
        self.hold_profit = 0

        self.filter_head_bar = 5
        self.bar_count = 0

        self.exit_internal = 0

        self.last_bigbang_up_id = 99
        self.last_bigbang_down_id = 99

        self.lastday_bar = 2
        self.hh_50 = 0
        self.ll_50 = 0
        self.to_hh_50_bar = 0
        self.to_ll_50_bar = 0

        self.key_hh = 0
        self.key_ll = 0
        self.key_mark_bar = 0
        self.key_mark_flag = 0

        self.dklines = []
        self.account_recorder = IndicatorRecorder("account")
        self.account_recorder.set_interval(1)

        self.capital_record = CapitalRecord(0)

        #key_price = 
        self.kp = KParser()
        self.kpt_record = KPatternRecord("RiskHave")
        self.task_list = []

        #c = ['id', 'account']
        #self.df_profit = pd.DataFrame(columns=c)
        
        self.controler_manager = ControlerManager()
        
        #self.this_new_data()
        print("[RiskManager] running .....................")
    
        self.define_data()

    def define_data(self):
        self.INVALID_POS_MARK = 999
        self.INVALID_PROFIT_MARK = 999

        self.MAX_LOSS = -200
        self.MAX_SHORT_POS = -3
        self.MAX_LONG_POS = 3
        self.MAX_GAIN = 450

    def start(self):
        StrategyBase.start(self)
        self.mark_price = 0

    def stop(self):
        StrategyBase.stop(self)
        self.mark_price = 0
        self.position = 0
        self.hold_pos = 0

    def set_trade_direction(self, t_dir):
        StrategyBase.set_trade_direction(self, t_dir)
        '''
        if (如果有相反方向，在合适位置退出)

        '''

    def time_to_update(self):
        if (get_minute()%self.update_interval == 0):
            return True
        else:
            return False

    def set_loss(self, hold_pos, hold_loss):
        self.hold_loss = hold_loss
        self.hold_pos = hold_pos
        self.debug("hold_loss=%d hold_pos=%d"%(self.hold_loss, self.hold_pos))

    def update_loss(self):
        '''
        self.hold_loss = self.manager.get_profit()
        tmp_pos = self.manager.get_hold_pos()

        if (tmp_pos != self.hold_pos+self.position):
            self.hold_pos = tmp_pos
        self.debug("hold_loss=%d hold_pos=%d"%(self.hold_loss, self.hold_pos))
        '''

    def on_day_bar(self, dklines):
        self.dklines = dklines

        max_short_pos = 0
        max_long_pos = 0

        last_close = dklines.iloc[-1].close
        lastday_bar = self.lastday_bar

        price_flag = 0
        bigbang_flag = 0
        #控制仓位
        hh_50, to_hh_50_bar = pplib.get_hest_in_range2(dklines, 2, 50)
        ll_50, to_ll_50_bar = pplib.get_lest_in_range2(dklines, 2, 50)
        
        #顶不追，底不追
        to_hh_50 = dklines.iloc[-lastday_bar].high - hh_50
        if (to_hh_50_bar >= 4 and to_hh_50 < 30):
            price_flag = 1
            self.to_hh_50_bar = self.lastday_bar
        to_ll_50 = dklines.iloc[-lastday_bar].low - ll_50
        if (to_ll_50_bar >= 4 and to_ll_50 < 30):
            price_flag = -1
            self.to_ll_50_bar = self.lastday_bar
        self.hh_50 = hh_50
        self.ll_50 = ll_50
        self.to_hh_50_bar = to_hh_50_bar
        self.to_ll_50_bar = to_ll_50_bar
        #大涨、大跌后不追
        if (dklines.iloc[-lastday_bar].close-dklines.iloc[-lastday_bar].open > 45):# big up
            self.last_bigbang_up_id = lastday_bar
            bigbang_flag = 1
        elif (dklines.iloc[-lastday_bar].open-dklines.iloc[-lastday_bar].close > 45):# big down
            self.last_bigbang_down_id = lastday_bar
            bigbang_flag = -1

        if (bigbang_flag ==1 and price_flag== 1):
            if (to_hh_50_bar > 6):
                max_long_pos = 2
            else:
                max_long_pos = 1
        elif (bigbang_flag==-1 and price_flag==-1):
            if (to_ll_50_bar > 6):
                max_short_pos = 2
            else:
                max_short_pos = 1
        elif (bigbang_flag == -1 and price_flag== 1):
            max_long_pos = 1
        elif (bigbang_flag == 1 and price_flag== -1):
            max_short_pos = 1
        elif (price_flag == 1):
            max_long_pos = 1
        elif (price_flag == -1):
            max_short_pos = -1
        elif (bigbang_flag == 1):
            max_long_pos = 1
        elif (bigbang_flag == -1):
            max_short_pos = 1

        if(max_long_pos > 0 and self.manager.get_cfg_max_long_pos() > max_long_pos):
            self.manager.set_max_long_pos(max_long_pos)
            self.debug("set_max_long_pos(%d)"%(max_long_pos))
        if(max_short_pos > 0 and self.manager.get_cfg_max_short_pos() > max_short_pos):
            self.manager.set_max_short_pos(max_short_pos)
            self.debug("set_max_short_pos(%d)"%(max_short_pos))

        #关键价格
        self.kp.on_bar(dklines)
        #如果key_hh存在，代表是阻力线
        self.key_ll = self.kp.get_last_key_ll_price(dklines.iloc[-1].close, 3)
        #如果key_ll存在，代表是支撑线
        self.key_hh = self.kp.get_last_key_hh_price(dklines.iloc[-1].close, 3)

    def onCreate_event(self, event_name, event_value):
        pass

    def on_bar2(self, klines):

        pass

    def on_bar10(self, klines):
        if (self.exit_bar != 0
            and klines.iloc[-1].id - self.exit_bar > 0):
            self.update_loss()
        self.risk_monitor(klines)
    
    # loss
    # gain
    # count
    # direction
    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        #特殊

        #self.monitor_open = False
        #self.on_run(klines) #会产生order
        #盈利与损失

        #klines转态与account 是否匹配
        self.update_data(klines)
        profit = self.hold_pos
        pos = self.hold_pos
        balance = self.manager.get_balance()

        #account 监控
        if (profit < self.calc_max_loss(pos)):
            self.create_loss_exit_task()
        elif (profit > self.calc_max_gain(pos)):
            self.create_profit_exit_task()
        #监控 数量
        if (abs(pos) > abs(self.calc_max_postion(pos))):
            self.create_monitor_position_task()

        #监控资金曲线
        self.monitor_capital_curve(klines)
        self.monitor_key_price(klines)
        self.monitor_key_hour(klines)
        self.monitor_event(klines)
        self.monitor_limiter(klines)
        #实时调整
        self.monitor_trade_direction(klines)
        self.monitor_trade_price(klines)

        self.run_task(klines)

    def update_data(self, klines):
        self.update_profit()
        self.update_balance()

    def update_profit(self):
        self.profit = self.manager.get_profit()
        self.hold_pos = self.manager.get_hold_pos()

    def update_balance(self):
        balance = self.manager.get_balance()
        self.capital_record.add(self.cur_bar_id, self.hold_pos, balance)
        self.capital = balance
        #self.df_profit.loc[len(self.df_profit)] = [self.cur_bar_id, profit]

    def create_profit_exit_task(self):
        name = "GainExitTask"
        ret = self.find_runing_task(name)
        if (ret == True):
            return
        profit = self.manager.get_profit()
        pos = self.manager.get_hold_pos()

        init_pos = pos
        init_profit = profit

        target_profit = -100
        target_pos = pos - 1

        timeout_bar = 30

        if (pos > 0):
            target_pos = pos - 1
        if (pos < 0):
            target_pos = pos + 1
            
        exit_task = ExitTask (name, self, self.cur_bar_id, timeout_bar, init_pos, init_profit, target_pos, target_profit)
        #self.task_list.append(exit_task)
        self.add_task(exit_task)

    def create_loss_exit_task(self):
        name = "LossExitTask"
        ret = self.find_runing_task(name)
        if (ret == True):
            return
        profit = self.manager.get_profit()
        pos = self.manager.get_hold_pos()

        init_pos = pos
        init_profit = profit

        #target_profit = self.INVALID_PROFIT_MARK
        #target_pos = self.INVALID_POS_MARK

        target_profit = -100
        
        if (pos > 0):
            target_pos = pos - 1
            limit_buy_open = Controler(ControlerEnum.CtrlLimitBuyCount, self.cur_bar, 70, 1, 1)
            self.add_controler(limit_buy_open)
        if (pos < 0):
            target_pos = pos + 1
            limit_sell_open = Controler(ControlerEnum.CtrlLimitSellCount, self.cur_bar, 70, 1, 1)
            self.add_controler(limit_sell_open)
        timeout_bar = 30

        if (pos > 0):
            pass
            #bbd = find_event("BigbangDown")
            #bk = find_event("Break")
            #if (bbd == True and bk == True):
            #   timeout_bar = 20

        #if (profit)
        exit_task = ExitTask (name, self, self.cur_bar_id, timeout_bar, init_pos, init_profit, target_pos, target_profit)
        #self.task_list.append(exit_task)
        self.add_task(exit_task)

    def create_monitor_position_task(self):
        pos = self.manager.get_hold_pos()
        std_pos = self.calc_max_postion(pos)
        if (pos > 0 and pos > std_pos):
            self.limit_long_pos(std_pos)
        if (pos < 0 and pos < std_pos):
            self.limit_short_pos(std_pos)

    def monitor_key_price(self, klines):
        #if (cur_price > )
        #到达
        self.cur_bar = self.get_current_minute_bar()
        hh_list = self.kp.get_hh_list()
        ll_list = self.kp.get_ll_list()
        #if (self.ask_price >= hh_list.loc[0].value):
        if (self.ask_price >= self.key_hh):
            self.getto_key_price(1)
        #if (self.ask_price <= ll_list.loc[0].value):
        if (self.ask_price <= self.key_ll):
            self.getto_key_price(-1)

        # 远离key_price
        hh_inday = self.get_highest_today()
        hh_inday_bar = self.get_highest_bar_today()
        ll_inday = self.get_lowest_today()
        ll_inday_bar = self.get_lowest_bar_today()
        #到达阻力线，又折回
        if (hh_inday > self.key_hh and self.ask_price < self.key_hh):
            if (self.cur_bar - hh_inday_bar > 30):
                self.back_from_key_price("hh")
        #曾靠近，又折回
        if (self.key_hh - hh_inday < 15 and self.cur_bar - hh_inday_bar > 40):
            #判断波动够大
            if(hh_inday-ll_inday > self.get_atr_daily()-10):
                self.back_from_key_price("hh")
        #########################################
        #到达支撑线，又折回
        elif (ll_inday < self.key_ll and self.ask_price > self.key_ll):
            if (self.cur_bar - hh_inday_bar > 30):
                self.back_from_key_price("ll")
        #靠近支撑线，又折回
        elif (ll_inday -self.key_ll < 20 and self.cur_bar - ll_inday_bar > 40):
            #判断波动够大
            if(hh_inday-ll_inday > self.get_atr_daily()-10):
                self.back_from_key_price("ll")

        ''''
        diff = ll - key_ll
        if (diff < 30):
            printf()

        '''

        # self.manager.oncommand()

    #曲线
    #def monitor_profit_curve(self, klines):
    def monitor_capital_curve(self, klines):
        if (self.hold_pos == 0):
            return

        if (self.cur_bar_id%5 == 0):
            if (self.hold_pos != 0):
                self.debug("pos=%d profit=%d"%(self.hold_pos, self.profit))
            '''   
            if (self.capital >= target_capital)

            '''
            if (self.capital_record.status == self.capital_record.S_DOWN_DOWN):
                self.debug("capital down down, run exit task...")
                name = "RushDownExit"
                timeout_bar = 5
                init_pos = self.hold_pos
                init_profit = self.hold_profit
                target_pos = 1
                target_profit = self.INVALID_PROFIT_MARK
                exit_task = ExitTask (name, self, self.cur_bar_id, timeout_bar, init_pos, init_profit, target_pos, target_profit)
                #self.task_list.append(exit_task)
                self.add_task(exit_task)
                
            elif (self.capital_record.status == self.capital_record.S_UP_LOWRANGE):
                name = "S_UP_LOWRANGE"
                timeout_bar = 15
                init_pos = self.hold_pos
                init_profit = self.hold_profit
                target_pos = 1
                target_profit = self.INVALID_PROFIT_MARK
                self.debug("太久......")
                exit_task = ExitTask (name, self, self.cur_bar_id, timeout_bar, init_pos, init_profit, target_pos, target_profit)
                #self.task_list.append(exit_task)
                self.add_task(exit_task)
                '''
                if (弱势)：
                    ExitTask
                '''
        #监控盈利 
        #positive return
        #self.monitor_profit()

    def monitor_key_hour(self, klines):
        lt = self.get_real_time()
        if ((lt.tm_hour == 21 or lt.tm_hour == 9) and lt.tm_min < 10):
            diff = klines.iloc[-(self.cur_bar-1)].low-klines.iloc[-(self.cur_bar-1)].close
            if (self.cur_bar>1 and diff>15):
                gap_ctrl = Controler(ControlerEnum.CtrlOpenGapBarLimt, self.cur_bar, 73, 0, 1)
                self.add_controler(gap_ctrl)
        pass

    def monitor_event(self, klines):
        pass

    def monitor_limiter(self, klines):
        pass

    #调整
    def monitor_trade_direction(self, klines):
        #ToDo:
        #   1. 缺少中途调整
        #   2. 

        # abs(kpi) > 35 but 达到key_price
        # kpi计算得到的方向较慢，趋势往往被几个特征模式改变
        if (self.cur_bar == 6):
            #标志事件
            self.find_key_line_pattern() #line and price
            #处理前半天把行情走完的情况


    def monitor_trade_price(self, klines):
        # abs(kpi) > 35 but 达到key_price
        pass
        #处理前半天把行情走完的情况

    def set_position(self, pos):
        #self.manager.set_position(self.TAG, pos)
        self.manager.set_position_direct(pos)

    def risk_monitor(self, klines):
        #关键时刻
        hh_inday = self.get_highest_today()
        hh_inday_bar = self.get_highest_bar_today()
        if (self.hh_50-hh_inday < 30 and hh_inday_bar < 60):
            if (self.to_hh_50_bar < 6):
                max_long_pos = 2
            else:
                max_long_pos = 1
            if(max_long_pos > 0 and self.manager.get_cfg_max_long_pos() > max_long_pos):
                self.manager.set_max_long_pos(max_long_pos)
                self.debug("set_max_long_pos(%d)"%(max_long_pos))
        
        ll_inday = self.get_lowest_today()
        ll_inday_bar = self.get_lowest_bar_today()
        if (ll_inday - self.ll_50 < 30 and ll_inday_bar < 60):
            if (self.to_ll_50_bar < 6):
                max_short_pos = 2
            else:
                max_short_pos = 1
            if(max_short_pos > 0 and self.manager.get_cfg_max_short_pos() > max_short_pos):
                self.manager.set_max_long_pos(max_short_pos)
                self.debug("set_max_short_pos(%d)"%(max_short_pos))

        #tm_hour = 9 or 13:30
        #关键位置
        if (self.key_hh != 0 ):
            if (self.key_mark_flag == 0):
                hh_5 = pplib.get_hest_in_range(klines, 1, 6)
                if (hh_5 >= self.key_hh):
                    self.key_mark_bar = self.cur_bar_id
                    self.key_mark_flag = 1
                    self.position -= 1
                    self.set_position(self.position)
            elif (self.key_mark_flag == 1):
                if (self.cur_bar_id - self.key_mark_bar> 25):
                    self.key_mark_flag = 2
            elif (self.key_mark_bar==2):
                self.position += 1
                self.set_position(self.position)

        if (self.key_ll != 0 ):
            if (self.key_mark_flag == 0):
                ll_5 = pplib.get_lest_in_range(klines, 1, 6)
                if (ll_5 <= self.key_ll):
                    self.key_mark_bar = self.cur_bar_id
                    self.key_mark_flag = 1
                    self.position += 1
                    self.set_position(self.position)
            elif (self.key_mark_flag == 1):
                if (self.cur_bar_id - self.key_mark_bar> 25):
                    self.key_mark_flag = 2
            elif (self.key_mark_bar==2):
                self.position -= 1
                self.set_position(self.position)

    def find_key_line_pattern(self):
        impt_kpt_down = [StgEvent.BackFromKeyResistanceLine, StgEvent.BackFromKeyResistancePrice]   
        ret_barid = -1
        leng = len(impt_kpt_down)
        for i in range(0, leng):
            pt = self.kpt_record.get_by_name(impt_kpt_down[i])
            if (pt is None):
                #找到一个就走？
                ret_barid = pt.bar
                break
                    #if (ret_id )
        if (ret_barid != -1):
            if (self.cur_day_barid - ret_barid < 3): #或者score
                self.set_trade_direction(TradeDirection.SELLONLY)
                return -1

        impt_kpt_up = [StgEvent.BackFromKeySupportLine, StgEvent.BackFromKeySupportPrice]
        ret_barid = -1
        leng = len(impt_kpt_up)
        for i in range(0, leng):
            pt = self.kpt_record.get_by_name(impt_kpt_up[i])
            if (pt is None):
                #找到一个就走？
                ret_barid = pt.bar
                break
                    #if (ret_id )
        if (ret_barid != -1):
            if (self.cur_day_barid - ret_barid < 3): #或者score
                self.set_trade_direction(TradeDirection.BUYONLY)
                return 1

        return 0


    def getto_key_price(self, direct):
        if (direct > 0):
            index = self.kp.get_last_key_hh_index(self.ask_price, 3)
            if (index >= 0):
                ctror = Controler(ControlerEnum.CtrlLimitBuyPrice, self.cur_bar_id, 60, self.ask_price, 1)
                self.add_controler(ctror)
                self.limit_long_pos(1)
        else:
            index = self.kp.get_last_key_ll_index(self.ask_price, 3)
            if (index >= 0):
                ctror = Controler(ControlerEnum.CtrlLimitSellPrice, self.cur_bar_id, 60, self.ask_price, 1)
                self.add_controler(ctror)
                self.limit_short_pos(1)

    def back_from_key_price(self, which):
        if (which == "hh"):
            ctror = Controler(ControlerEnum.CtrlLimitSellPrice, self.cur_bar_id, 300, self.ask_price, 1)
            self.add_controler(ctror)
            ctror = Controler(ControlerEnum.CtrlSellOnly, self.cur_bar_id, 300, self.ask_price, 1)
            self.add_controler(ctror)
            #20200808 generate event
            kpbk = KPBackFromKeyResistancePrice(BarType.DAY)
            kpbk.bar = self.cur_bar
            kpbk.key_price = self.key_hh
            self.manager.drive_kpattern(kpbk)

        if (which == "ll"):
            ctror = Controler(ControlerEnum.CtrlLimitBuyPrice, self.cur_bar_id, 300, self.ask_price, 1)
            self.add_controler(ctror)
            ctror = Controler(ControlerEnum.CtrlBuyOnly, self.cur_bar_id, 300, self.ask_price, 1)
            self.add_controler(ctror)
            #20200808 generate event
            kpbk = KPBackFromKeySupportLine(BarType.MIN)
            kpbk.bar = self.cur_bar
            kpbk.key_price = self.key_ll
            self.manager.drive_kpattern(kpbk)

    def check_lowrange(self, klines):
        pass

    def check_trend_reverse(self, klines):
        pass

    def adjust_pos(self, klines):
        pass

    def get_strategy_position(self):
        return 0
    
    def check_open_position(self,pos):
        lt = self.get_real_time()
        if (lt.tm_hour==9 and lt.tm_min<=5 and lt.tm_wday==0):
            return 0
        #从价格和数量上限定
        # 比如分前后两个半场
        # 比如除非突破，否则两个空间时间上不能太接近
        #permit_pos = 0 #self.limiter
        tmp = self.controler_manager.get_open_position_limit(self.cur_bar, pos)

        return tmp

    def check_open_price(self, t_dir):
        return True

    def get_order_list(self):
        self.manager.get_order_list()

    def run_task(self, klines):
        for task in self.task_list:
            if (task.get_status == task.S_RUNING):
                task.drive(klines)

    def on_event(self, name, param):
        pass

    def on_kpattern(self, kpt):
        self.kpt_record.add(kpt)

    def task_callback(self, who, action, param):
        if (action == "adjust_position"):
            self.set_position(param)

    def limit_open_time(self, gapbar):
        pass

    def limit_long_pos(self, limit_pos):
        profit = self.manager.get_profit()
        pos = self.manager.get_hold_pos()

        if (pos > limit_pos):
            name = "LimitLongPos"
            ret = self.find_runing_task(name)
            if (ret == False):
                limit_task = ExitTask(name, self, self.cur_bar_id, 20, pos, profit, limit_pos, self.INVALID_PROFIT_MARK)
                self.add_task(limit_task)

    def limit_short_pos(self, limit_pos):
        profit = self.manager.get_profit()
        pos = self.manager.get_hold_pos()

        if (pos < limit_pos):
            name = "LimitShortPos"
            ret = self.find_runing_task(name)
            if (ret == False):
                limit_task = ExitTask(name, self, self.cur_bar_id, 20, pos, profit, limit_pos, self.INVALID_PROFIT_MARK)
                self.add_task(limit_task)

    def add_controler(self, ctor):
        #self.controler_mappend(ctor) 
        self.controler_manager.add(ctor)

    def add_task(self, task):
        #todo list
        # 过滤同类型的task,比如都是建仓
        # 如果上一个也是同类型可以合并
        for itor in self.task_list:
            if (task.name == itor.name and task.get_status != task.S_FINISHED):
                return
        self.task_list.append(task)
    #==================tool================================#
    def calc_max_loss(self, pos):
        if (pos <= 0):
            return -300
        
        return -300

    def calc_max_gain(self, pos):
        if (pos <= 0):
            return 500
        
        return 500

    def calc_max_postion(self, t_dir):
        if (t_dir < 0):
            return -2
        else:
            return 3

    def find_runing_task(self, name):
        flag = False
        for task in self.task_list:
            if (task.name == name):
                if (task.get_status() == task.S_RUNING):
                    flag = True
        return flag

class TaskUnit(object):
    def __init__(self):
        pass

class TodoTask(object):
    def __init__(self, name):
        self.param_defines()

        self.name = name
        self.start_barid = 0 #开始的bar
        self.timeout_bar = 0 #start_barid+timeout_bar

        self.run_flag = True
        self.status = self.S_INIT

       
    def param_defines(self):
        self.S_INIT = 1
        self.S_RUNING = 2
        self.S_FINISHED = 3

    def drive(self, klines):
        pass

    def update_account(self, pos, profit):
        pass

    def start(self):
        self.run_flag = True

    def stop(self):
        self.run_flag = False

    def doit(self):
        self.status = self.S_RUNING

    def done(self):
        self.status = self.S_FINISHED

    def get_status(self):
        return self.status

class ExitTask(TodoTask):
    def __init__(self, name, callback, cur_bar, timeout_bar, init_pos, init_profit, target_pos, target_profit):
        TodoTask.__init__(self, name)
        self.init_pos = target_pos
        self.init_profit = init_profit
        self.target_pos = target_pos #9999
        self.target_profit = target_pos #9999 表示不调整

        self.time_slice = []

        self.position = init_pos
        self.mark_price = 0
        self.cur_step = 0
        self.exit_bar = 0

        self.callback = callback

        #分解
        dif = init_pos - target_pos
        absdif = abs(dif)
        if (self.target_pos != 9999 and absdif >= 2):
            self.time_slice.append([0, 5])
            gap = (timeout_bar - 5)/(absdif-1)
            last_bar = 6

            if (absdif > 2):
                for j in range(2, absdif):
                    self.time_slice.append([last_bar, last_bar+gap])
                    last_bar += gap
            
            self.time_slice.append([last_bar, timeout_bar])
        else:
            self.time_slice.append([0, timeout_bar])

    def set_init_pos(self):
        pass

    def set_init_profit(self):
        pass


    def set_target_pos(self):
        pass

    def set_target_profit(self):
        pass

    def drive(self, klines):
        if (self.mark_price == 0):
            self.mark_price = klines.iloc[-1].close

        bar_pas = klines.iloc[-1].id - self.start_barid
        '''

        '''
        dif = self.target_pos - self.init_pos
        cksum_bar = 10
        c_sum = pplib.get_checksum(klines, cksum_bar, 1)
        ma10 = pplib.get_average(klines, 10)

        #监控损失 monitor_loss
        if (self.target_pos == self.position):
            self.run_flag = False
            print("%s finish....."%(self.name))

        #间隔限制
        if (klines.iloc[-1].id - self.exit_bar < 5):
            print("%s gap limit....."%(self.name))
            return
        slice_start = self.time_slice[self.cur_step]
        if (bar_pas < slice_start-4):
            print("%s time slice limit....."%(self.name))
            return

        if (dif > 0):
            tmp_pos = 0
            if (ma10 > self.mark_price):
                tmp_pos = 1
            if (bar_pas > self.time_slice[self.cur_step][1]):#超时
                tmp_pos = 1   
            if (tmp_pos != 0):
                self.callback.task_callback(self.name, "adjust_position", 1)
                self.exit_bar = klines.iloc[-1].id
                self.position += 1
                self.doit()
        else:
            tmp_pos = 0
            if (ma10 > self.mark_price):
                tmp_pos = -1
            if (bar_pas > self.time_slice[self.cur_step][1]):#超时
                tmp_pos = -1   
            if (tmp_pos != 0):
                self.callback.task_callback(self.name, "adjust_position", -1)
                self.exit_bar = klines.iloc[-1].id
                self.position -= 1
                self.doit()

    def update_hold_pos(self, pos):
        if (self.target_pos == pos):
            self.run_flag = False
            self.done()
    
    def update_hold_profit(self, profit):
        if (abs(profit) <= abs(self.target_profit)):
            self.run_flag = False
            self.done()

    def combine(self, other_task):
        if (self.name == other_task.name and self.status != self.S_FINISHED):
            if (self.name == SelfString.LossExitTask):
                pass
                

class ControlerEnum(Enum):
    CtrlDoNot = 90
    CtrlDontOpen = 91

    CtrlBuyOnly = 1
    CtrlSellOnly = 2
    CtrlBuySell = 3
    CtrlNone = 3

    CtrlLimitSellCount = 10
    CtrlLimitBuyCount = 11
    CtrlLimitSellPrice = 12
    CtrlLimitBuyPrice = 13
    CtrlOpenGapBarLimt = 14 #开仓间隔，比如允许5分钟后才能开仓
    CtrlOpenGapPriceLimit = 15

#管理者指令
class Controler(object):
    def __init__(self, order, start_barid, timeout, param, prio):
        self.order = order
        self.start_bar = 0 #基于日内计数的bar,如果基于klines没法表示日内
        self.timeout = 0

        self.order_param = param#指令的参数
        self.priority = prio#优先级

        self.func_mode = 0#使用哪个函数模型
        self.func_mode = 0#失效模型

        self.int_param1 = 0

        self.timeout_cb = 0 #

    def update(self, ctrlor):
        self.timeout = (ctrlor.start_bar+ctrlor.start_bar)-self.start_bar

class ControlerManager(object):
    def __init__(self):
        self.ctler_list = [] #指令队列 

    def add(self, ctor):
        # 和上一个对比
        index = self.find(ctor.name, ctor.start_bar)
        if (index == 1):
            #del self.ctler_list[-1]
            self.ctler_list[index].update(ctor)
        else:
            self.ctler_list.append(ctor)

    def get_cur_controler(self):
        pass 

    def find(self, name, cur_bar):
        leng = len(self.ctler_list)
        for i in range(1, leng):
            ctrlor = self.ctler_list[-1]
            if (ctrlor.order == name
                and self.check_timeout(ctrlor, cur_bar) == True):
                return leng - i
        return -1


    #def get_open_limit(self, start_bar, timeout):
    # true: 有限制
    # false: 没有限制
    def get_open_limit(self, cur_bar, timeout):
        for ctler in self.ctler_list:
            if (self.check_timeout(ctler, cur_bar) == True):
                continue
            if (ctler.order == ControlerEnum.CtrlDontOpen):
                return True
                
        return False

    def get_open_position_limit(self, cur_bar, pos):
        ret = pos
        for ctler in self.ctler_list:
            if (self.check_timeout(ctler, cur_bar) == True):
                continue
            if (ctler.order == ControlerEnum.CtrlDoNot):
                ret = 0
                break
            if (pos > 0 and ctler.order == ControlerEnum.CtrlLimitBuyCount):
                limit_cnt = int(ctler.order_param)
                if (limit_cnt < ret):
                    ret = limit_cnt
                continue
            if (pos < 0 and ctler.order == ControlerEnum.CtrlLimitSellCount):
                limit_cnt = int(ctler.order_param)
                if (limit_cnt > ret):
                    ret = limit_cnt
                continue

        return ret

    def check_open_price_limit(self, cur_bar, pos, price):
        ret = price
        for ctler in self.ctler_list:
            if (self.check_timeout(ctler, cur_bar) == True):
                continue
            if (pos > 0 and ctler.order == ControlerEnum.CtrlLimitBuyPrice):
                limit_price = int(ctler.order_param)
                if (limit_price > price):
                    return False
            if (pos < 0 and ctler.order == ControlerEnum.CtrlLimitSellPrice):
                limit_price = int(ctler.order_param)
                if (limit_price < price):
                    return False

        return True
    
    def drive(self, klines):
        #k 驱动
        pass

    def check_timeout(self, ctler, cur_bar):
        if (ctler.start_bar<=cur_bar
            and ctler.start_bar+ctler.timeout>cur_bar):
            return False

        return True
        
#可以记录收益和资金曲线两种
class CapitalRecord(object):
    def __init__(self, r_type):
        self.UPUP = 0
        self.downdown = 0
        self.status = 0

        self.hest_bar = 0
        self.hest = 0
        self.lest_bar = 0
        self.lest = 0
        self.save_pos = 0 #

        self.MARK_VALUE = 999
        self.mark_change = 0

        self.r_type = r_type
        if (r_type == 0):
            print("CapitalRecord")
        else:
            print("ProfitRecord")

        c = ['barid', 'pos', 'profit']
        self.df = pd.DataFrame(columns=c)
        self.event_record = EventRecorder("CapitalRecord")

        self.param_defines()

    def param_defines(self):
        self.S_NONE = 0
        self.S_LOWRANGE = 1
        self.S_UP_UP = 2
        self.S_DOWN_DOWN = 3
        self.S_UP_LOWRANGE = 4
        self.S_DOWN_LOWRANGE = 5

    def reset(self):
        self.df = self.df.drop(index=self.df.index)

    def add(self, barid, pos, profit):
        self.df.loc[len(self.df)] = [barid, pos, profit]

        if (profit >= self.hest):
            self.hest = profit
            self.hest_bar = barid
        if (profit <= self.lest):
            self.lest = profit
            self.lest_bar = barid

        if (self.df.iloc[-1].pos != pos):
            self.position_change(barid, pos)

        #if (barid%)
        self.update_status()

    def position_change(self, barid, pos):
        self.save_pos = pos
        self.mark_change = barid
      

    '''
    0: lowrange
    : bigbangUp
    : bigbangDown
    : too long
    '''
    def get_status(self):
        return self.status

    def update_status(self):
        if (len(self.df) > 5):
            self.status = self.S_NONE
        cur_id = self.df.iloc[-1].barid
        cksum = self.get_checksum(1, 6)
        '''
        if (cur_id-self.hest_bar > ):
            pass
        '''
        backid = 5
        status = 0

        height5 = self.get_height_in_range(1, 6)
        height10 = self.get_height_in_range(1, 11)
        height15 = self.get_height_in_range(1, 16)
        height30 = self.get_height_in_range(1, 31)

        if (self.r_type == 0): #CapitalRecord
            if (height15 > 20):
                status = 0
                if (height30 > 300 and height10 < 200):
                    status = self.S_UP_LOWRANGE

                if ((height5>100 or height10>150) and cksum>0):
                    status = self.S_UP_UP
                elif ((height5>100 or height10>150) and cksum<0):
                    status = self.S_DOWN_DOWN
            else:
                status = self.S_LOWRANGE
        else:
            if (height15 > 20 and cur_id-self.mark_change>15):
                status = 0
                if (height30 > 300 and height10 < 200):
                    status = self.S_UP_LOWRANGE

        self.status = status
    
    def get_checksum(self, start_id, num):
        leng = len(self.df)
        if (num >= leng):
            num = leng-1
        if (leng < 2):
            return 0
        csum = 0
        for i in range(start_id, start_id + num):
            csum = self.df.iloc[-i].profit - self.df.iloc[-(i+1)].profit
        return csum

    def get_greaters(self):
        pass

    def get_lesses(self):
        pass

    def get_hold_pos(self):
        return self.df.iloc[-1].pos

    def get_hold_profit(self):
        return self.df.iloc[-1].profit

    def smoothness(self):
        pass

    def get_score(self):
        pass

    def get_height_in_range(self, start_id, num):
        lengh = len(self.df)
        if  (lengh < num):
            num = lengh

        index, hh = self.get_hest_in_range2(start_id, num)
        index, ll = self.get_lest_in_range2(start_id, num)

        return hh-ll

    def get_lest_in_range2(self, start_id, num):
        lengh = len(self.df)
        if  (lengh < num):
            num = lengh

        ll = self.df.iloc[-start_id].profit
        i = start_id
        for i in range(start_id, start_id+num):
            if (self.df.iloc[-i].profit <= ll):
                ll = self.df.iloc[-i].profit

        return i, ll

    def get_hest_in_range2(self, start_id, num):
        lengh = len(self.df)
        if  (lengh < num):
            num = lengh

        hh = self.df.iloc[-start_id].profit
        i = start_id
        for i in range(start_id, start_id+num):
            if (self.df.iloc[-i].profit >= hh):
                hh = self.df.iloc[-i].profit

        return i, hh

    def get_highest(self):
        pass

    def get_lowest(self):
        pass

    def get_lowest_bar(self):
        pass

    def bigbang_up(self):
        pass

    def bigbang_down(self):
        pass


class Limiter(object):
    def __init__(self):

        pass

    def set_max_long_pos(self, who, pos):
        pass

class Risk(object):
    pass