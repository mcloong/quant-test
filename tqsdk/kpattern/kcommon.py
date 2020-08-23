
from param_defines import StgEvent, Indicator, MyString, MyDefaultValue
import random
from logUtils import my_print

class TradeConditionType(object):
    def __init__(self):
        self.RangeCondition = 1
        self.UpperLimitCondition = 2
        self.LowerLimitCondition = 3
        self.EventCondition = 4
        self.EventValueCondition = 5
        self.EventFixBarCondition = 6
        self.EventRelativeBarCondition = 7
        self.EventSampleCondition = 8
        self.EventSampleValueCondition = 9

ConditionType = TradeConditionType()

class TradeCondition(object):
    def __init__(self, name , idx, t_type):
        self.p_type = t_type
        self.name = name
        self.idx = idx # 一个task中id相同的两个cond，有一个满足调价即可
        self.result = False
        self.last_ok_value = 0
        self.last_ok_bar = 0
        self.cur_bar = 0

    def drive_kclock(self, c_name, value, kclock):
        self.cur_bar = kclock.cur_bar

    def get_result(self):
        return self.result

    def ok(self):
        self.last_ok_bar = self.cur_bar
        self.result = True

class IndictorCondition(TradeCondition):
    def __init__(self, name , idx, t_type):
       
        self.max_val = 99999
        self.min_val = -99999

    def range_compare(self, value):
        #my_print(self.name , "range_compare value=%d min_val=%d max_val=%d"%(value, self.min_val, self.max_val))
        if (value >= self.min_val and value <= self.max_val):
            self.result = True
        else:
            self.result = False

    def upper_compare(self, value):
        #my_print(self.name , "upper_compare value=%d min_val=%d max_val=%d"%(value, self.min_val, self.max_val))
        if (value >= self.max_val):
            self.result = True
        else:
            self.result = False

    def lower_compare(self, value):
        #my_print(self.name , "upper_compare value=%d min_val=%d max_val=%d"%(value, self.min_val, self.max_val))
        if (value <= self.min_val):
            self.result = True
        else:
            self.result = False

    def drive(self, c_name, value):
        if (c_name != self.name):
            return

        #my_print("cond", " drive c_name=%s value=%d"%(c_name, value))
        if (self.p_type == ConditionType.RangeCondition):
            self.range_compare(value)
        elif (self.p_type == ConditionType.UpperLimitCondition):
            self.upper_compare(value)
        elif (self.p_type == ConditionType.LowerLimitCondition):
            self.lower_compare(value)

        if (self.result == True):
            self.last_ok_bar = self.cur_bar
            self.last_ok_value = value

    def drive_kclock(self, c_name, value, kclock):
        self.cur_bar = kclock.cur_bar

    def drive_with_kclock(self, c_name, value, kclock):
        if (c_name != self.name):
            return
        self.cur_bar = kclock.cur_bar
        self.drive(c_name, value)

    def drive_indicator_object(self, indor):
        if (self.name == indor.name):
            self.drive(indor.name, indor.value)
            if (self.result == True):
                self.last_ok_bar = indor.bar
                self.last_ok_value = indor.value
    
    #整个时间分几段
    def set_parts_of_trade_time(self, n):
        self.parts = n

    def random_start_end_bar(self):
        pass

    #0 无操作，1 开， 2 平
    def check_condition(self):
        pass

    def get_result(self):
        pass

class RangeCondition(IndictorCondition):
    def __init__(self, name, idx, min_val, max_val):
        TradeCondition.__init__(self, name, idx, ConditionType.RangeCondition)
        if (max_val < min_val):
            self.max_val = min_val
            self.min_val = max_val
        else:
            self.max_val = max_val
            self.min_val = min_val

class UpperLimitCondition(IndictorCondition):
    def __init__(self, name, idx, value):
        TradeCondition.__init__(self, name, idx, ConditionType.UpperLimitCondition)
        self.max_val = value

class LowerLimitCondition(IndictorCondition):
    def __init__(self, name, idx, value):
        TradeCondition.__init__(self, name, idx, ConditionType.LowerLimitCondition)
        self.min_val = value

#绝对时间
class KEventCondition(TradeCondition):
    def __init__(self, name, idx, p_type, left_bar, right_bar, min_score, max_score):
        TradeCondition.__init__(self, name, idx, ConditionType.EventCondition)
        self.p_type = p_type

        self.left_bar = left_bar
        self.right_bar = right_bar

        self.min_score = min_score
        self.max_score = max_score

    def drive_event(self, kv):
        if (kv.name != self.name):
            return
        score = kv.score
        if (score > self.min_score and score < self.max_score):
            self.result = True

    def get_result(self):
        if (self.result == False):
            return False

        if (self.p_type == ConditionType.EventFixBarCondition):
            dif = self.cur_bar
        else:
            dif = self.cur_bar - self.last_ok_bar
        if (dif >= self.left_bar and dif <= self.right_bar):
            return True

class EventFixBarCondition(KEventCondition):
    def __init__(self, name, idx, left_bar, right_bar, min_score, max_score):
        KEventCondition.__init__(self, name, idx, ConditionType.EventFixBarCondition, left_bar, right_bar, min_score, max_score)

    def drive_event(self):
        pass

    def get_result(self):
        if (self.result == False):
            return False
            
        if (self.last_ok_bar >= self.left_bar and self.last_ok_bar <= self.right_bar):
            return True

class EventRelativeBarCondition(KEventCondition):
    def __init__(self, name, idx, left_bar, right_bar):
        KEventCondition.__init__(self, name, idx, ConditionType.EventFixBarCondition, left_bar, right_bar, -99999, 999999)

class EventSampleCondition(TradeCondition):
    def __init__(self, name , idx, min_score, max_score):
        TradeCondition.__init__(self, name , idx, ConditionType.EventSampleCondition)

    def drive_event(self, kv):
        if (kv.name == self.name):
            self.ok()

#Rl: relative
class EventSampleRlBarCondition(TradeCondition):
    def __init__(self, name , idx, min_bar, max_bar):
        TradeCondition.__init__(self, name , idx, ConditionType.EventSampleCondition)
        self.min_bar = min_bar
        self.max_bar = max_bar

    def drive_event(self, kv):
        if (kv.name != self.name):
            return
        self.ok()

    def get_result(self):
        if (self.result == False):
            return False
        dif = self.cur_bar - self.last_ok_bar
        if (dif > self.min_bar and dif < self.max_bar):
            return True

class EventSampleValueCondition(TradeCondition):
    def __init__(self, name , idx, min_score, max_score):
        TradeCondition.__init__(self, name , idx, ConditionType.EventSampleValueCondition)
        self.min_score = min_score
        self.max_score = max_score

    def drive_event(self, kv):
        if (kv.name != self.name):
            return

        if (kv.value >= self.min_score and kv.value <= self.max_score):
            self.ok()

class CondtionSet(object):
    def __init__(self, name):
        self.name = name
        self.cond_list = []

        self.last_ok_bar = 0
        self.cur_bar = 0
        self.index = 0 #编号，用于排序
        self.result = False

    def add_cond(self, cond):
        self.cond_list.append(cond)

    def check(self):
        pass

    def drive_cond(self, name, value):
        for cond in self.cond_list:
            cond.drive(name, value)

    def drive_kclock(self, kclock):
        self.cur_bar = kclock.cur_bar
        for cond in self.cond_list:
            cond.drive_kclock(kclock)
    
    def drive_cond_with_kclock(self, name, value, kclock):
        for cond in self.cond_list:
            cond.drive(name, value. kclock)

    def drive_indicator_object(self, indor):
        for cond in self.cond_list:
            cond.drive_indicator_object(indor)

    def is_ok(self):
        if (len(self.cond_list) == 0):
            return False
        ret_list = []
        for cond in self.cond_list:
            #print(self.name ,cond.name, cond.idx, cond.result)
            ret_list = self.result_record(ret_list, cond.idx, cond.get_result())
        ret = self.get_result_internal(ret_list)
        if (ret == True):
            self.last_ok_bar = self.mark_ok_bar

        return ret

    def get_result_internal(self, ret_list):
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
            if (itor[0] == new_idx):
                if (new_result==True):
                    itor[1] = new_result
                flag = False
            new_ret_list.append([itor[0], itor[1]])
            
        if (flag == True):
            new_ret_list.append([new_idx, new_result])

        return new_ret_list

    def mark_ok_bar(self):
        bar = 0
        for itor in self.cond_list:
            if (itor.last_ok_bar > bar):
                bar = itor.last_ok_bar
        return bar 

    def count(self):
        return len(self.cond_list)


class TradeTask(object):
    def __init__(self, name, direction, start_bar, entry_timeout, hold_time):
        self.defines()

        self.name = name #"BigbangTrade"
        self.position = 0
        self.direct = direction #一个task对应一个方向的trade 只有open close
        self.status = self.S_CREATE

        self.priority = 0 #
       
        self.monitor_start = 0  # -999表示无效
        self.monitor_timeout = 0

        self.hold_start = 0
        self.hold_timeout = 0
        self.term  = 10
        self.height = 10
        self.entry_status = 0
        self.exit_status = 0

        self.callbacker = None
        self.userdata = None

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
        self.entry_conds = CondtionSet("EntryConds") # 如果为空，表示立即执行
        self.gain_exit_conds = CondtionSet("GainExitConds")
        self.loss_exit_conds = CondtionSet("LossExitConds")
        self.expired_exit_conds = CondtionSet("ExpiredExitConds")
        self.canle_event_conds = CondtionSet("CanleEventConds") #遇此事件，取消
        self.kclock = None

        self.backup_task = None#name

    def set_callbacker(self, cb):
        self.callbacker = cb

    def defines(self):
        self.S_Standby = 0 #等待，当做备份时才用到
        self.S_CREATE = 1
        self.S_DONE = 2 #成交
        self.S_FINISHED = 3

    def set_priority(self, prio):
        self.priority = prio
        
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
        if (self.status == self.S_FINISHED):
            return
        elif (self.status == self.S_CREATE):
            #self.drive_cond_list("entry", idor, value)
            self.entry_conds.drive_cond(idor, value)
        elif (self.status == self.S_DONE):
            #self.drive_cond_list("gain", idor, value)
            self.gain_exit_conds.drive_cond(idor, value)
            self.loss_exit_conds.drive_cond(idor, value)
            self.expired_exit_conds.drive_cond(idor, value)
            #self.drive_cond_list("loss", idor, value)

        self.drive()

    def drive_indicator_with_kclock(self, indor, value, kclock):
        self.kclock = kclock
        self.drive_indicator(indor, value)

    def drive_indicator_object(self, idor):
        pass

    def drive_clock(self, kclock):
        self.kclock = kclock
        pass

    def drive_event(self, event, param):
        if (self.status == self.S_FINISHED):
            return

        if (event == StgEvent.CmdForbidBuy and self.direct == MyString.Buy):
            pass

    #def drive(self, klines):
    def drive(self):
        if (self.status == self.S_FINISHED):
            return
        #bars_since_entry = 0
        #self.event_drive("BarsSinceEntry")
        '''
        for cond in self.cond_list:
            cond.drive(klines)
        '''
        ret = self.check()
        if (self.direct == MyString.Buy):
            if (ret == MyString.Open):
                self.set_position(1)
                self.position = 1
                self.status = self.S_DONE
            elif (ret == MyString.Close or ret == MyString.LossClose):
                self.set_position(0)
                self.position = 0
                self.status = self.S_FINISHED
        else:
            if (ret == MyString.Open):
                self.set_position(-1)
                self.position = -1
                self.status = self.S_DONE
            elif (ret == MyString.Close or ret == MyString.LossClose):
                self.set_position(0)
                self.position = 0
                self.status = self.S_FINISHED

    def set_position(self, pos):
        if (self.callbacker is not None):
            self.callbacker.set_task_position(self.name, pos)
    
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
                my_print(self.name, "gain_exit_conds")
                return MyString.Close
            ret = self.loss_exit_conds.is_ok()
            if (ret == True):
                my_print(self.name, "loss_exit_conds")
                return MyString.LossClose
            ret = self.expired_exit_conds.is_ok()
            if (ret == True):
                my_print(self.name, "expired_exit_conds")
                return MyString.Close
        return MyString.Nothing

    def set_userdata(self, userdata):
        self.userdata = userdata
        
    def get_userdata(self):
        return self.userdata
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

    def finish(self):
        self.status = self.S_FINISHED
        if (self.callbacker is None):
            self.callbacker.task_event(MyString.Finished, "")
            if (self.backup_task is not None):
                self.callbacker.task_event(MyString.NextTask, self.backup_task)
            
    def get_trade_direction(self):
        return self.direct