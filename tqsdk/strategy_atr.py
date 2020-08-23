#区间与ATR
#如果lastday bigbang atr大的概率小；
#如果前两天atr的幅度小，atr超常的概率变大
#如果区间底部 开仓徘徊在avg之上
from strategy_base import StrategyBase
from kpattern_record import KPatternRecord
from param_defines import Indicator, TrendType, StgEvent, WalkStep
import pplib
from kpattern.trade_factory import TradeFactory

class StrategyAtr(StrategyBase):
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyAtr", manager)

    def on_bar(self, klines):
        self.walk_path()
        self.atr_break(klines)

    def atr_break(self, klines):
        if (self.lowrange_back_bar == 0):
            return

        h10_day_bar = 0
        l10_day_bar = 0

        flag = 0
        if (h10_day_bar >= self.lowrange_back_bar and 
            l10_day_bar <= self.lowrange_back_bar + self.lowrange_bars+1):
            flag = 1
        if (l10_day_bar >= self.lowrange_back_bar and 
            l10_day_bar <= self.lowrange_back_bar + self.lowrange_bars+1):
            flag = -1
        if (flag == 0):
            return
        #速度和高度

        h3_day = 0
        l3_day = 0
        avg5 = pplib.get_average(klines, 7)
        if (flag == -1):
            if (avg5 <= l3_day):
                # sell task
                task = TradeFactory.create_target_sell_task
                self.addTradeTask(task)

        if (flag == 1):
            if (avg5 >= h3_day):
                task = TradeFactory.create_target_buy_task
                self.addTradeTask(task)

    #to bottom -> in bottom -> far away bottom -> to top -> in top -> far away top
    def walk_path(self):
        atr_daily = self.get_indor_value(Indicator.AtrDaily)
        atr_inday = self.get_indor_value(Indicator.AtrInday)
       
        avg_overs_per = self.get_indor_value(Indicator.OversAvgPer)
        avg_downs_per = self.get_indor_value(Indicator.UndersAvgPer)
        atr_score = (atr_inday/atr_daily)*100
        #常规
        if (atr_score < 60):
            if (avg_overs_per > 50):
                #to top
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.ToTop)
                pass
            elif (avg_downs_per > 50):
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.ToBottom)
                # to bottom
                pass
            else:
                # wave
                pass
        else:
            self.wait_path_out_1hour()
            pass

        #特例

    def wait_path_out_1hour(self):
        hest_bar = self.get_indor_value(Indicator.HestBarInDay)
        lest_bar = self.get_indor_value(Indicator.LestBarInDay)
        farfrom_top = self.cur_bar - hest_bar
        farfrom_bottom = self.cur_bar - lest_bar
        farfrom_h_height = self.get_indor_value(Indicator.HestInDay) - self.cur_price
        farfrom_l_height = self.cur_price - self.get_indor_value(Indicator.LestInDay)
        trend_daily = self.get_indor_value(Indicator.TrendTypeDaily)
        if (farfrom_top < 40 and farfrom_h_height < 16):
            if (trend_daily == TrendType.StrongUp):
                #to top
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.ToTop)
                pass
            else:
                #in top
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.InTop)
                pass
        elif (farfrom_bottom < 40 and farfrom_l_height < 16): 
            if (trend_daily == TrendType.StrongDown):
                #to bottom
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.ToBottom)
                pass
            else:
                #in bottom
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.InBottom)
                pass
        elif (farfrom_top > 40 and 
            farfrom_bottom > 40):
            
            if (farfrom_top > farfrom_bottom):
                #far away bottom
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.FarAwayBottom)
                pass
            else:
                #far away top
                self.manager.drive_event(StgEvent.WalkStep, WalkStep.FarAwayTop)
                pass

        '''
        '''
    def on_day_bar(self, dklines):
        back_bar = 0
        count = 0

        for i in range(1, 6):
            hl = dklines.iloc[-i].high - dklines.iloc[-i].low
            oc = dklines.iloc[-i].open - dklines.iloc[-i].close
            if (hl < 10): #说明是当天
                continue
            if (hl < 30 or oc < 20):
                if (back_bar == 0):
                    back_bar = i
                    count += 1
                else:
                    if (i == back_bar+1): #说明连续
                        count+=1
                    else:
                        break

        if (count > 0):
            self.lowrange_back_bar = back_bar
            self.lowrange_bars = count
