from kpattern.kcommon import LowerLimitCondition, RangeCondition, UpperLimitCondition, TradeTask
from param_defines import StgEvent, Indicator, MyDefaultValue, MyString
import random

class TradeFactoryClass(object):
    def goback_from_l_key(self):
        pass

    def add_default_exit_cond(self, task):
        if (task.direct ==  MyString.Buy):
            self.add_default_buy_exit_cond(task)
        else:
            self.add_default_sell_exit_cond(task)

    def add_default_buy_loss_exit_cond(self, task):
        #价格
        target_loss_cond = LowerLimitCondition(Indicator.HoldProfit, 1, random.randint(MyDefaultValue.LossStd-20, MyDefaultValue.LossStd+50))
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        greater_cond = UpperLimitCondition(Indicator.GreaterContinuousCount, 3, 10)
        task.addLossExitCond(target_loss_cond)
        task.addLossExitCond(checksum_cond)
        task.addLossExitCond(greater_cond)

    def add_default_buy_expired_exit_cond(self, task):
        #时间
        expired_cond = UpperLimitCondition(StgEvent.HoldExpire, 1, MyDefaultValue.ExpiredStd)
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        greater_cond = UpperLimitCondition(Indicator.GreaterContinuousCount, 3, 10)
        task.add_expired_exit_cond(greater_cond)
        task.add_expired_exit_cond(expired_cond)
        task.add_expired_exit_cond(checksum_cond)

    def add_default_buy_exit_cond(self, task):
        #价格
        self.add_default_buy_loss_exit_cond(task)
        #时间
        self.add_default_buy_expired_exit_cond(task)

    def add_target_gain_exit_cond(self, task,target_profit):
        target_cond = UpperLimitCondition(Indicator.HoldProfit, 1, target_profit)
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        task.addGainExitCond(target_cond)
        task.addGainExitCond(checksum_cond)

    def add_default_sell_exit_cond(self, task):
        #价格
        target_loss_cond = LowerLimitCondition(Indicator.HoldProfit, 1, random.randint(MyDefaultValue.LossStd-20, MyDefaultValue.LossStd+50))
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        lesser_cond = UpperLimitCondition(Indicator.LessContinuousCount, 3, 10)
        task.addLossExitCond(target_loss_cond)
        task.addLossExitCond(checksum_cond)
        task.addLossExitCond(lesser_cond)
        #时间
        expired_cond = UpperLimitCondition(StgEvent.HoldExpire, 1, MyDefaultValue.ExpiredStd)
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        lesser_cond = UpperLimitCondition(Indicator.LessContinuousCount, 3, 10)
        task.add_expired_exit_cond(checksum_cond)
        task.add_expired_exit_cond(expired_cond)
        task.add_expired_exit_cond(lesser_cond)

    def add_default_buy_entry_cond(self, task, downs, end_bar):
        #task = TradeTask("SellTest", MyString.Sell, 0, entry_timeout, hold_time)
       
        #price_cond = UpperLimitCondition(Indicator.CurPrice, 1, open_price)
        cksum_cond = RangeCondition(Indicator.SCheckSum, 1, -3, 1)
        height8_cond = LowerLimitCondition(Indicator.RangeHeight15, 2, 10)
        height15_cond = LowerLimitCondition(Indicator.RangeHeight15, 3, 16)
        #二选一
        downs_cond = RangeCondition(Indicator.Downs, 4, downs, downs+20)
        #or
        expired_cond = UpperLimitCondition(Indicator.CurBar, 4, end_bar)

        task.addEntryCond(cksum_cond)
        task.addEntryCond(height8_cond)
        task.addEntryCond(height15_cond)
        task.addEntryCond(downs_cond)
        task.addEntryCond(expired_cond)

    def add_default_sell_entry_cond(self, task, ups, end_bar):
        #task = TradeTask("SellTest", MyString.Sell, 0, entry_timeout, hold_time)
       
        #price_cond = UpperLimitCondition(Indicator.CurPrice, 1, open_price)
        cksum_cond = RangeCondition(Indicator.SCheckSum, 1, 0, 4)
        height8_cond = LowerLimitCondition(Indicator.RangeHeight15, 2, 10)
        height15_cond = LowerLimitCondition(Indicator.RangeHeight15, 3, 16)
        #二选一
        downs_cond = RangeCondition(Indicator.Downs, 4, ups, ups+20)
        #or
        expired_cond = UpperLimitCondition(Indicator.CurBar, 4, end_bar)

        task.addEntryCond(cksum_cond)
        task.addEntryCond(height8_cond)
        task.addEntryCond(height15_cond)
        task.addEntryCond(downs_cond)
        task.addEntryCond(expired_cond)

    def add_default_sell_loss_exit_cond(self, task):
        #价格
        target_loss_cond = LowerLimitCondition(Indicator.HoldProfit, 1, random.randint(MyDefaultValue.LossStd-20, MyDefaultValue.LossStd+50))
        checksum_cond = RangeCondition(Indicator.SCheckSum, 2, -3, 3)
        lesses_cond = UpperLimitCondition(Indicator.LessContinuousCount, 3, 10)
        task.addLossExitCond(target_loss_cond)
        task.addLossExitCond(checksum_cond)
        task.addLossExitCond(lesses_cond)
        
    def create_random_loss(self):
        pass

    def create_random_gain(self):
        pass

    def create_target_buy_task(self, name, target_profit):
        buy_task = TradeTask(name, MyString.Buy, 0, 300, 300)
        self.add_default_buy_entry_cond(buy_task, 10, 100)
        self.add_target_gain_exit_cond(buy_task, target_profit)
        self.add_default_buy_loss_exit_cond(buy_task)
        return buy_task

    def create_target_sell_task(self, name, target_profit):
        buy_task = TradeTask(name, MyString.Sell, 0, 300, 300)
        self.add_default_sell_entry_cond(buy_task, 10, 100)
        self.add_target_gain_exit_cond(buy_task, target_profit)
        self.add_default_sell_loss_exit_cond(buy_task)
        return buy_task


TradeFactory = TradeFactoryClass()