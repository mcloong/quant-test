# 模型 条件 状态 
# 模型预置几种情况的应对操作
# 条件 达到什么情况进行开平
# 状态：标明当前的情况
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
import abc
sys.path.append("..")
from param_defines import StgEvent, Indicator, MyString, MyDefaultValue
#import param_defines.StgEvent
from enum import Enum
import numpy as np
import pandas as pd
from kpattern.kcommon import CondtionSet, TradeCondition, UpperLimitCondition, LowerLimitCondition, RangeCondition
import random

class TradeTaskEnum(Enum):
    BreakUp = 1
    BreakDown = 2
    DoubleM = 3
    DoubleW = 4

class PatternBase(object):
    def __init__(self, stg):
        self.task_list = []
        self.stg = stg
        self.position = 0
        self.clock = None

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
                (itor.get_status() == itor.S_FINISHED or
                itor.get_status() == itor.S_FINISHED)):
                return

        self.task_list.append(task)

    def find_running_trade_task(self, name):
        for itor in self.task_list:
            if (name == itor.name and 
                (itor.get_status() == itor.S_FINISHED or
                itor.get_status() == itor.S_FINISHED)):

                return True

        return False

    def cb(self, operation, param):
        self.stg.cb(operation, param)
        #if (operation == "SetPosition"):

    def close(self):
        pass

    #===============if 事件处理===========================#
    def if_bigbangup(self, kstatus):
        #create_tradecondition()
        chsum_cond = RangeCondition(Indicator.SCheckSum, 1, -2, 2)
        task = TradeTask("WaitForBack", MyString.Buy, kstatus.cur_bar_id, 30, 200) #回调
        task.addEntryCond(chsum_cond)

        lowrange_cond = RangeCondition(Indicator.RangeHeight15, 1, 10, 20)
        task.addGainExitCond(lowrange_cond)

        loss_cond = UpperLimitCondition(StgEvent.Loss, 1, -200)
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

    def if_lowrange_in_top(self):
        pass

    def if_lowrange_in_bottom(self):
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
#================================================#

    def monitor_event(self):
        self.Buyevent = [StgEvent.BigBangBreakUp]
        pass
#================================================#
    def create_range_task(self):
        task = TradeTask("TradeRangeBuy", MyString.Buy, self.clock.cur_bar, 300, 300)
        #cksum = TradeCondition()
        #event = 

        pass

    def create_range_sell_task(self):
        task = TradeTask("TradeRangeSell", MyString.Sell, self.clock.cur_bar, 300, 300)

        range_l = self.stg.get_indor_value(Indicator.rangeHInDay)
        cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        if (range_l > cur_price):
            range_l = cur_price + random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50)
        #gain exit
        random.randint(MyDefaultValue.GainStd-2, MyDefaultValue.GainStd+5)
        price_cond = LowerLimitCondition(Indicator.CurPrice, 1, range_l)
        task.addGainExitCond(price_cond)
        target_gain_cond = UpperLimitCondition(StgEvent.Gain, 1, random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50))
        task.addGainExitCond(target_gain_cond)
        #loss exit
        self.add_default_exit_cond(task)

        self.addTradeTask(task) 

    def create_range_buy_task(self):
        task = TradeTask("TradeRangeBuy", MyString.Buy, self.clock.cur_bar, 300, 300)

        range_h = self.stg.get_indor_value(Indicator.rangeHInDay)
        cur_price = self.stg.get_indor_value(Indicator.CurPrice)
        if (range_h < cur_price):
            range_h = cur_price + random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50)
        #gain exit
        random.randint(MyDefaultValue.GainStd-2, MyDefaultValue.GainStd+5)
        price_cond = UpperLimitCondition(Indicator.CurPrice, 1, range_h)
        task.addGainExitCond(price_cond)
        target_gain_cond = UpperLimitCondition(StgEvent.Gain, 1, random.randint(MyDefaultValue.GainStd-20, MyDefaultValue.GainStd+50))
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

    def create_buy_task(self):
        pass

    def create_sell_task(self):
        pass

    def add_default_exit_cond(self, task):
        #
        target_loss_cond = LowerLimitCondition(StgEvent.Gain, 1, random.randint(MyDefaultValue.LossStd-20, MyDefaultValue.LossStd+50))
        task.addLossExitCond(target_loss_cond)

        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        task.addLossExitCond(checksum_cond)
       
        greater_cond = UpperLimitCondition(Indicator.GreaterContinuousCount, 3, 10)
        task.addLossExitCond(greater_cond)
        #===========================================#
        expired_cond = UpperLimitCondition(StgEvent.HoldExpire, 1, MyDefaultValue.ExpiredStd)
        task.add_expired_exit_cond(expired_cond)
        
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        task.add_expired_exit_cond(checksum_cond)
       
        greater_cond = UpperLimitCondition(Indicator.GreaterContinuousCount, 3, 10)
        task.add_expired_exit_cond(greater_cond)
#========================================================================#
class PatternDown(object):
    pass
        
class TradeTask(object):
    def __init__(self, name, direction, start_bar, entry_timeout, hold_time):
        self.defines()

        self.name = name #"BigbangTrade"
        self.position = 0
        self.direct = direction #一个task对应一个方向的trade 只有open close
        self.status = self.S_CREATE
       
        self.monitor_start = 0  # -999表示无效
        self.monitor_timeout = 0

        self.hold_start = 0
        self.hold_timeout = 0
        self.term  = 10
        self.height = 10
        self.entry_status = 0
        self.exit_status = 0

        '''
        self.entry_cond = []
        self.entry_event = []
        self.gain_exit_cond = []
        self.loss_exit_cond = []
      #  self.gain_exit_event = [] #事件和条件和一
      #  self.loss_exit_event = []
      #  self.failure_event = []
        self.failure_cond = []
        '''
        self.entry_conds = CondtionSet("EntryConds")
        self.gain_exit_conds = CondtionSet("GainExitConds")
        self.loss_exit_conds = CondtionSet("LossExitConds")
        self.loss_exit_conds = CondtionSet("LossExitConds")
        self.expired_exit_conds = CondtionSet("ExpiredExitConds")
        self.kclock = None

    def defines(self):
        self.S_CREATE = 1
        self.S_DONE = 2
        self.S_FINISHED = 3
        
    def addEntryCond(self, cond):
        #self.entry_cond.append(cond)
        self.entry_conds.add_cond(cond)

    def addGainExitCond(self, cond):
        #self.gain_exit_cond.append(cond)
        self.gain_exit_conds.add_cond(cond)

    def addLossExitCond(self, cond):
        #self.loss_exit_cond.append(cond)
        self.loss_exit_conds.add_cond(cond)

    def add_expired_exit_cond(self, cond):
        self.expired_exit_conds.add_cond(cond)

    '''
    def drive_cond_list(self, name, idor, value):
        if (name == "entry"):
            for cond in self.entry_cond:
                cond.drive_indicator(idor, value)
        elif (name == "loss"):
            for cond in self.gain_exit_cond:
                cond.drive_indicator(idor, value)
        elif (name == "gain"):
            for cond in self.loss_exit_cond:
                cond.drive_indicator(idor, value)
    '''

    def drive_indicator(self, idor, value):
        if (self.status == self.S_CREATE):
            #self.drive_cond_list("entry", idor, value)
            self.entry_conds.drive_cond(idor, value)
        if (self.status == self.S_DONE):
            #self.drive_cond_list("gain", idor, value)
            self.gain_exit_conds.drive_cond(idor, value)
            self.loss_exit_conds.drive_cond(idor, value)
            self.expired_exit_conds.drive_cond(idor, value)
            #self.drive_cond_list("loss", idor, value)

    def drive_indicator_with_kclock(self, indor, value, kclock):
        self.kclock = kclock
        self.drive_indicator(indor, value)

    def drive_indicator_object(self, idor):
        pass

    def drive_clock(self, kclock):
        self.kclock = kclock
        pass

    def drive_event(self, event, param):
        if (event == StgEvent.CmdForbidBuy and self.direct == MyString.Buy):
            pass

    def drive(self, klines):
        #bars_since_entry = 0
        #self.event_drive("BarsSinceEntry")
        '''
        for cond in self.cond_list:
            cond.drive(klines)
        '''

        ret = self.check()
        if (self.direct == MyString.Buy):
            if (ret == MyString.Open):
                #cb.set_position(1)
                self.position = 1
            elif (ret == MyString.Close or ret == MyString.LossClose):
                #cb.set_position(-1)
                self.position = 0
        else:
            if (ret == MyString.Open):
                #cb.set_position(-1)
                self.position = -1
            elif (ret == MyString.Close or ret == MyString.LossClose):
                #cb.set_position(1)
                self.position = 0

    #0 nothing
    #1 open
    #2 close
    #3 止损
    def check(self):
        if (self.position == 0):
            if (self.entry_conds.count() == 0): #表示立即执行
                return MyString.Open
            ret = self.entry_conds.is_ok()
            if (ret == True):
                return MyString.Open
        else:
            ret = self.gain_exit_conds.is_ok()
            if (ret == True):
                return MyString.Close
            ret = self.loss_exit_conds.is_ok()
            if (ret == True):
                return MyString.LossClose
            ret = self.expired_exit_conds.is_ok()
            if (ret == True):
                return MyString.Close
        return MyString.Nothing

    '''
    def check_condition(self, cond_list):
        ret_list = []
        for cond in cond_list:
            ret_list = self.result_record(ret_list, cond.idx, cond.result)
        return self.get_result(ret_list)

    def get_result(self, ret_list):
        if (len(ret_list) == 0):
            return False
        for itor in ret_list:
            if (itor[1] == False):
                return False
        return True

    def result_record(self, ret_list, new_idx, new_result):
        new_ret_list = []
        flag = True
        for itor in ret_list:
            if (itor[0] == new_idx and new_result==True):
                itor[1] = new_result
            new_ret_list.append([itor[0], itor[1]])
            flag = False
        
        if (flag == True):
            new_ret_list.append([new_idx, new_result])

        return new_ret_list
    '''

    def get_position(self):
        return self.position

    def get_status(self):
        return self.status

    def on_exit_event(self):
        pass

    def destroy(self):
        pass