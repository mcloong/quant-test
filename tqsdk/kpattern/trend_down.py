#三种基本类型之一
from kpattern.kcommon import CondtionSet, TradeCondition, UpperLimitCondition, LowerLimitCondition, RangeCondition,TradeTask
from trade_factory import TradeFactory
from param_defines import StgEvent, Indicator, MyString, MyDefaultValue
from trend_base import TrendBase

class TrendDown(TrendBase):
    def __init__(self):
        self.default_strategy()

    def default_strategy(self):
        entry_timeout = 300
        hold_time = 300
        task = TradeTask("SellTest", MyString.Sell, 0, entry_timeout, hold_time)
        #entry
        open_price = 3730
        #price_cond = LowerLimitCondition(Indicator.CurPrice, 1, open_price)
        price_cond = UpperLimitCondition(Indicator.CurPrice, 1, open_price)
        task.addEntryCond(price_cond)
        #gain exit
        #price_cond = UpperLimitCondition(Indicator.CurPrice, 1, open_price-2)
        price_cond = LowerLimitCondition(Indicator.CurPrice, 1, open_price-2)
        task.addGainExitCond(price_cond)
        #loss exit
        TradeFactory.add_default_exit_cond(task)

        task.set_callbacker(self)
        self.addTradeTask(task) 

    def on_event(self, event):
        if (event == "bigbangUp"):
            pass

    def if_bigbangup(self):
        pass