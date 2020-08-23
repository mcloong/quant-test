# 模型 条件 状态 
# 模型预置几种情况的应对操作
# 条件 达到什么情况进行开平
# 状态：标明当前的情况
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
import abc
sys.path.append("..")
from param_defines import StgEvent, Indicator, MyString, MyDefaultValue, TrendType
from enum import Enum
import numpy as np
import pandas as pd
from kpattern.kcommon import CondtionSet, TradeCondition, UpperLimitCondition, LowerLimitCondition, RangeCondition, EventSampleCondition,TradeTask
from kpattern.kcommon import EventRelativeBarCondition, EventSampleRlBarCondition, EventSampleRlBarCondition
import random

class TradeTaskEnum(Enum):
    BreakUp = 1
    BreakDown = 2
    DoubleM = 3
    DoubleW = 4

class TrendBase(object):
    def __init__(self, stg):
        self.trend_type = TrendType.WAVE
        self.task_list = []
        self.beware_event = [] #提防
        self.stg = stg
        self.position = 0
        self.clock = None
        self.keep_one_task = False #同时只能一个任务
        self.map_define()

    def map_define(self):
        self.func_map = []
        self.func_map.append([StgEvent.BigBangBreakDown, self.if_bigbangup])
        self.func_map.append([StgEvent.GetToHKey, self.if_getto_Hkey])
        
        #print(type(self.func_map.loc[1].event, type(self.func_map.loc[1].func))

    def on_event(self, event_dict, kclock):
        for itor in self.func_map:
            if (itor[0] == event_dict[0]):
                itor[1](event_dict[1])

    def on_kindictor(self, kindicator):
        pass

    #结果
    def on_indicator(self, indicator, value):
        for task in self.task_list:
            if (task.get_status == task.S_FINISHED):
                continue
            task.drive_indicator(indicator, value)

    def on_indicator_with_kclock(self, name, value, kclock):
        self.clock = kclock

    def on_indicator_object(self, indor_obj):
        pass

    def on_clock(self, kclock):
        self.clock = kclock

    def addTradeTask(self, task):
        for itor in self.task_list:
            if (task.name == itor.name and 
                itor.get_status() != itor.S_FINISHED):
                return

        self.task_list.append(task)

    def get_current_task(self):
        pass

    def find_running_trade_task(self, name):
        for itor in self.task_list:
            if (name == itor.name and 
                itor.get_status() != itor.S_FINISHED):
                return True

        return False

    def cb(self, operation, param):
        self.stg.cb(operation, param)
        #if (operation == "SetPosition"):

    def close(self):
        pass

    def check_run(self):
        #检查是否继续可以运行
        #如果有多个，并且高优先级的执行完了

        return True

    #tradetask的回调
    def task_event(self, event, param):
        if (event == MyString.Finished):
            pass
        elif (event == MyString.NextTask):
            pass

    #===============if 事件处理===========================#
    #===============if系列用于处理意外====================#
    def if_bigbangup(self, kstatus):

        #create_tradecondition()
        chsum_cond = RangeCondition(Indicator.SCheckSum, 1, -2, 2)
        task = TradeTask("WaitForBack", MyString.Buy, kstatus.cur_bar_id, 30, 200) #回调
        task.addEntryCond(chsum_cond)

        lowrange_cond = RangeCondition(Indicator.RangeHeight15, 1, 10, 20)
        task.addGainExitCond(lowrange_cond)

        loss_cond = UpperLimitCondition(Indicator.HoldProfit, 1, -200)
        task.addLossExitCond(loss_cond)

        #task.add_gain_exit_event(StgEvent.Loss200)

        self.addTradeTask(task)
        
    @abc.abstractmethod
    def if_breakup(self):
        pass

    def if_avg_crossover(self):
        pass

    def if_avg_crossdown(self):
        pass

    def if_lowrange(self):
        pass

    def if_lowrange_in_top(self, kp):
        if(self.trend_type <= 0):
            task = self.create_classic_sell_task(5)
            self.addTradeTask(task)
        # sell task

    def if_lowrange_in_bottom(self):
        if(self.trend_type >= 0):
            # buy  task
            pass

    def if_up_to_key(self):
        pass

    def if_getto_Hkey(self, value):
        print("pattern_base: getto_Hkey value=%d"%(value))
        pass

    def if_check_position(self):
        tmp_position = 0
        for task in self.task_list:
            tmp_position += task.get_position()

        if (self.position != tmp_position):
            self.stg.get_position(tmp_position)
            self.position = tmp_position

    def if_gap_up(self):
        pass

    def if_gap_down(self):
        pass

    def if_close_is_high_yestday(self): #前几日
        pass

    def if_close_is_low(self):
        pass

    #日线级别
    def if_bigbangup_daily(self, kp):
        cur_day_bar = 1
        event_bar = 1
        dif = cur_day_bar - event_bar
        if(dif > 0 and dif < 2):
            pass
        
        if (kp.guild_price != 0):
            self.create_buy_task_by_price(kp.guild_price)

    def if_bigbangdown_daily(self):
        pass

    def if_over_avgline_at_open(self):
        pass
#================================================#

    def monitor_event(self):
        self.Buyevent = [StgEvent.BigBangBreakUp]
        pass
#================================================#
    def create_buy_task_by_price(self, entry_price):
        task = TradeTask("DefaultBuyPirce", MyString.Buy, self.clock.cur_bar, 300, 300)

        #cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        price_cond = UpperLimitCondition(Indicator.CurPrice, 1, entry_price)
        task.addEntryCond(price_cond)
        back_rest_event = EventSampleRlBarCondition(StgEvent.StdBackRestOfDown, 2, 0, 10)
        task.addEntryCond(back_rest_event)
        #gain exit
        target_profit = self.stg.get_indor_value(Indicator.PreBuyProfit)
        target_cond = UpperLimitCondition(Indicator.HoldProfit, 1, target_profit)
        task.addGainExitCond(target_cond)
        
        #loss exit
        self.add_default_exit_cond(task)

        self.addTradeTask(task) 

    def create_buy_task_by_price_only(self, entry_price):
        task = TradeTask("DefaultBuyPriceOnly", MyString.Buy, self.clock.cur_bar, 300, 300)

        #cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        price_cond = UpperLimitCondition(Indicator.CurPrice, 1, entry_price)
        task.addEntryCond(price_cond)
        #gain exit
        target_profit = self.stg.get_indor_value(Indicator.PreBuyProfit)
        target_cond = UpperLimitCondition(Indicator.HoldProfit, 1, target_profit)
        task.addGainExitCond(target_cond)
        
        #loss exit
        self.add_default_exit_cond(task)

        self.addTradeTask(task) 

    #基于回调或者叫downs
    def create_buy_task_by_back(self, downs): 
        task = TradeTask("DefaultBuy", MyString.Buy, self.clock.cur_bar, 300, 300)

        #cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        price_cond = UpperLimitCondition(Indicator.Downs, 1, downs)
        task.addEntryCond(price_cond)
        #gain exit
        target_profit = self.stg.get_indor_value(Indicator.PreBuyProfit)
        target_cond = UpperLimitCondition(Indicator.HoldProfit, 1, target_profit)
        task.addGainExitCond(target_cond)
        
        #loss exit
        self.add_default_exit_cond(task)

        self.addTradeTask(task) 

    def create_classic_sell_task(self, overs):
        task = TradeTask("ClassicSell", MyString.Sell, self.clock.cur_bar, 300, 300)

        #cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        overs_cond = UpperLimitCondition(Indicator.Downs, 1, overs)
        task.addEntryCond(overs_cond)
        #gain exit
        target_profit = self.stg.get_indor_value(Indicator.PreBuyProfit)
        if (target_profit < 100):
            target_profit = 100
        target_cond = UpperLimitCondition(Indicator.HoldProfit, 1, target_profit)
        task.addGainExitCond(target_cond)
        
        #loss exit
        self.add_default_sell_exit_cond(task)
        return task
        #self.addTradeTask(task) 

    #基于回调
    #可以用于错过时机未执行任务的补充任务
    def create_classic_buy_task(self, unders):
        task = TradeTask("ClassicBuy", MyString.Buy, self.clock.cur_bar, 300, 300)

        #cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        downs_cond = UpperLimitCondition(Indicator.Downs, 1, unders)
        task.addEntryCond(downs_cond)
        #gain exit
        target_profit = self.stg.get_indor_value(Indicator.PreBuyProfit)
        if (target_profit > 10):
            target_profit = 10
        target_cond = UpperLimitCondition(Indicator.HoldProfit, 1, target_profit)
        task.addGainExitCond(target_cond)
        
        #loss exit
        self.add_default_exit_cond(task)
        return task
        #self.addTradeTask(task) 
    
    def create_range_task(self):
        task = TradeTask("TradeRangeBuy", MyString.Buy, self.clock.cur_bar, 300, 300)
        #cksum = TradeCondition()
        #event = 
        pass

    def create_range_sell_task(self):
        task = TradeTask("TradeRangeSell", MyString.Sell, self.clock.cur_bar, 300, 300)
        #entry
        range_h = self.stg.get_indor_value(Indicator.RangeHInDay)
        if (range_h < 100):
            return
        range_l = self.stg.get_indor_value(Indicator.RangeLInDay)
        cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        if (range_l > cur_price):
            range_l = cur_price + random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50)
        price_cond = UpperLimitCondition(Indicator.CurPrice, 1, range_h)
        task.addGainExitCond(price_cond)
        #gain exit
        price_cond = LowerLimitCondition(Indicator.CurPrice, 1, range_l)
        task.addGainExitCond(price_cond)
        target_gain_cond = UpperLimitCondition(Indicator.HoldProfit, 1, random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50))
        task.addGainExitCond(target_gain_cond)
        #loss exit
        self.add_default_exit_cond(task)

        self.addTradeTask(task) 

    def create_range_buy_task(self):
        task = TradeTask("TradeRangeBuy", MyString.Buy, self.clock.cur_bar, 300, 300)

        range_h = self.stg.get_indor_value(Indicator.RangeHInDay)
        cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        if (range_h < cur_price):
            range_h = cur_price + random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50)
        #gain exit
        random.randint(MyDefaultValue.GainStd-2, MyDefaultValue.GainStd+5)
        price_cond = UpperLimitCondition(Indicator.CurPrice, 1, range_h)
        task.addGainExitCond(price_cond)
        target_gain_cond = UpperLimitCondition(Indicator.HoldProfit, 1, random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50))
        task.addGainExitCond(target_gain_cond)
        #loss exit
        self.add_default_exit_cond(task)

        self.addTradeTask(task) 

    def create_range_task_with_strong(self, tdir):
        if (tdir == "buy"):
            pass

    def create_break_task(self):
        pass

    #突破跳空等强趋势
    def create_strong_up(self):
        pass

    def create_strong_down(self):
        pass

    def add_default_exit_cond(self, task):
        #价格
        target_loss_cond = LowerLimitCondition(Indicator.HoldProfit, 1, random.randint(MyDefaultValue.LossStd-20, MyDefaultValue.LossStd+50))
        task.addLossExitCond(target_loss_cond)

        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        task.addLossExitCond(checksum_cond)
       
        greater_cond = UpperLimitCondition(Indicator.GreaterContinuousCount, 3, 10)
        task.addLossExitCond(greater_cond)
        #时间
        expired_cond = UpperLimitCondition(StgEvent.HoldExpire, 1, MyDefaultValue.ExpiredStd)
        task.add_expired_exit_cond(expired_cond)
        
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        task.add_expired_exit_cond(checksum_cond)
       
        greater_cond = UpperLimitCondition(Indicator.GreaterContinuousCount, 3, 10)
        task.add_expired_exit_cond(greater_cond)

    def add_default_sell_exit_cond(self, task):
        #价格
        target_loss_cond = LowerLimitCondition(Indicator.HoldProfit, 1, random.randint(MyDefaultValue.LossStd-20, MyDefaultValue.LossStd+50))
        task.addLossExitCond(target_loss_cond)

        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        task.addLossExitCond(checksum_cond)
       
        lesser_cond = UpperLimitCondition(Indicator.LessContinuousCount, 3, 10)
        task.addLossExitCond(lesser_cond)
        #时间
        expired_cond = UpperLimitCondition(StgEvent.HoldExpire, 1, MyDefaultValue.ExpiredStd)
        task.add_expired_exit_cond(expired_cond)
        
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        task.add_expired_exit_cond(checksum_cond)
       
        greater_cond = UpperLimitCondition(Indicator.GreaterContinuousCount, 3, 10)
        task.add_expired_exit_cond(greater_cond)
    
    def create_default_gain_exit_cond(self):
        #gain exit
        target_profit = self.stg.get_indor_value(Indicator.PreBuyProfit)
        target_cond = UpperLimitCondition(Indicator.HoldProfit, 1, target_profit)
        return target_cond

    def create_over_avgline_in_range_bottom_task(self, prior):
    # over avg and in range bottom
        gain_cond = self.create_default_gain_exit_cond()
        up_task1 = TradeTask("OverAvgInRgeBot", MyString.Buy, self.clock.cur_bar, 300, 300)
        avg_cond = EventRelativeBarCondition(StgEvent.OverAvgLineAtOpen, 1, 0,60)
        btm_cond = EventRelativeBarCondition(StgEvent.InRangeBottom, 2, 0, 100)

        up_task1.addEntryCond(avg_cond)
        up_task1.addEntryCond(btm_cond)
        up_task1.addGainExitCond(gain_cond)
        self.add_default_exit_cond(up_task1)
        up_task1.set_priority(prior)

        return up_task1

    # for wave
    def create_in_range_bottom_buy_task(self, prior):
        gain_cond = self.create_default_gain_exit_cond()
        up_task3 = TradeTask("farFromLL", MyString.Buy, self.clock.cur_bar, 300, 300)
        away_cond = EventRelativeBarCondition(StgEvent.FarFromLL, 1, 0, 500)
        downs_cond = UpperLimitCondition(Indicator.Downs, 2, 20)
        ck = RangeCondition(Indicator.CheckSum15, 3, -6, 6)
        price_pos = LowerLimitCondition(Indicator.DistanceAvgLine, 3, -10) #均线以下
        up_task3.addEntryCond(away_cond)
        up_task3.addEntryCond(downs_cond)
        up_task3.addEntryCond(ck)
        up_task3.addEntryCond(price_pos)
        up_task3.addGainExitCond(gain_cond)
        self.add_default_exit_cond(up_task3)
        return up_task3

#========================================================================#
class TrendDown(object):
    pass
        
