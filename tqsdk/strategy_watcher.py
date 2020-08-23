# 高级别的监控和trade
from tqsdk import TqApi, TqSim,tafunc
from tqsdk.ta import RC
from tqsdk.ta import MA
from tqsdk.ta import ROC
from tqsdk.ta import ATR, BOLL
import pplib
from strategy_base import StrategyBase
from datetime import datetime
import time
from param_defines import WalkPath,TradeDirection, TrendStatus, StgEvent

class StrategyWatcher(StrategyBase):
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyWatcher", manager)
    #def __init__(self):

        self.TAG = "StrategyWatcher"
        self.MAX_LOSS = 25

        #self.manager = manager
        self.ATR_day = 60
        self.last_inrange_bar = 999
        self.last_inrange_height = 0
        self.last_inrange_high = 0
        self.last_inrange_low = 0
        self.last_big_red_candle = 999
        self.last_big_green_candle = 999
        self.last_break_bar = 999
        self.cur_price = 0

        self.trade_dir = TradeDirection.BUYSELL
        self.position = 0
        
        #preset
        self.preset_dir = TradeDirection.INVALID

        ##runing time##
        self.inited = False
        self.run_break_flag = 0

        self.entry_bar = 999
        self.entry_price = 0

        self.cond_flag = 0
        self.cond_mark_bar = 0

        self.BreakOut = 0
        self.TrendGoOn = 1
        self.GoBack = 2

        #parse
        self.trend_status =  TrendStatus.Unkown
        self.predict_walkpath = WalkPath.InRange

        self.my_print("running.......")

    def on_day_bar(self, klines):
        #三部曲：1. 综合得分; 2. 定义趋势; 3. 预测趋势；4. 提防关键位置
        #================score=================#
        lt = self.get_real_time()
        if (lt.tm_wday == 0):
            start_id = 1
        else:
            start_id = 2
        #self.get_daybar_score(klines, 1)
        self.get_daybar_score(klines, start_id)
        #self.backtest(klines)

        self.inited = True
        self.my_print("kpi=%d"%(self.kpi))

        if(self.kpi >= 35):
            self.manager.on_command(self.TAG, "TradeDirection", TradeDirection['BUYONLY'])
        elif(self.kpi <= -35):
            self.manager.on_command(self.TAG, "TradeDirection", TradeDirection['SELLONLY'])
        else:
            self.manager.on_command(self.TAG, "TradeDirection", TradeDirection['BUYSELL'])

        #if (abs(self.kpi) >= 10):
        self.manager.on_command(self.TAG, "ReportKpi", self.kpi)

        #===============trend status=======================#
        #
        self.parse_trend(start_id, klines)
        #==================================================#
        #self.make_prediction(1, klines)
        self.make_prediction(start_id, klines)

    def mc_set_trade_direction(self, dir):
        pass

    def mc_set_predict_walkpath(self, path):
        pass
    
    def get_trend_status(self):
        return self.trend_status

    def parse_trend(self, start_day, dklines):
        reds = pplib.get_reds_candle2(dklines, start_day, start_day+6)
        greens = pplib.get_greens_candle2(dklines, start_day, start_day+6)
        height_7 = pplib.get_height_in_range(dklines, start_day, start_day+7)
        cksum_8 = pplib.get_checksum2(dklines, start_day, 5, 1)
        last_crosdwn_bar = pplib.get_crossdown_ma_bar2(dklines, start_day, 10)
        last_crosovr_bar = pplib.get_crossover_ma_bar2(dklines, start_day, 10)
        hh_60, hh_60_bar = pplib.get_hest_in_range2(dklines, start_day,start_day+60)
        ll_60, ll_60_bar = pplib.get_lest_in_range2(dklines, start_day,start_day+60)
        self.debug("height_7=%d cksum_8=%d"%(height_7, cksum_8))
        self.debug("reds=%d green=%d"%(reds, greens))
        self.debug("ll_60_bar=%d hh_60_bar=%d"%(ll_60_bar, hh_60_bar))
        trend_type = 0
        if ((reds >= 4) or (ll_60_bar >= 2 and reds >=2)):
            trend_type += 1
        if (cksum_8>50 and height_7>70):
            trend_type += 1
        if (last_crosovr_bar > start_day+3):
            trend_type = 1

        if ((greens >= 4)or (hh_60_bar >= 2 and greens >=2)):
            trend_type -= 1
        if (cksum_8<-50 and height_7>70):
            trend_type -= 1
        if (last_crosdwn_bar > start_day+3):
            trend_type -= 1

        self.debug("trend_type score=%d"%(trend_type))
        self.trend_status =  TrendStatus.Unkown
        if (trend_type >= 2):
            self.debug("......trend up......")
            hh_12, hh_12_bar = pplib.get_hest_in_range2(dklines, start_day,start_day+12)
            if (hh_12_bar == 1):
                self.trend_status = TrendStatus.UpInUp
            if (hh_12_bar > start_day and hh_12_bar < start_day+5):
                self.trend_status = TrendStatus.WaveInUp

        elif (trend_type <= -2):
            ll_12, ll_12_bar = pplib.get_lest_in_range2(dklines, start_day,start_day+12)
            if (ll_12_bar == 1):
                self.trend_status = TrendStatus.DownInDown
            if (ll_12_bar > start_day and ll_12_bar < start_day+5):
                self.trend_status = TrendStatus.WaveInDown
        
        if (self.trend_status == TrendStatus.Unkown):
            hh_22, hh_22_bar = pplib.get_hest_in_range2(dklines, start_day,start_day+22)
            ll_22, ll_22_bar = pplib.get_lest_in_range2(dklines, start_day,start_day+22)
            if (hh_22_bar < ll_22_bar):
                self.trend_status = TrendStatus.WaveTop
            else:
                self.trend_status = TrendStatus.WaveBottom

        self.debug("trend_status=%s"%(self.trend_status))
    #
    # 5 不明确，1 强向上 -1 向下， 2 震荡向上，-2 震荡向下，0 上下震荡
    def get_prediction(self):
        return self.predict_walkpath 

    def make_prediction(self, start_day, dklines):
        self.watch_hh = dklines.iloc[-start_day].high + self.ATR_day
        self.watch_ll = dklines.iloc[-start_day].low - self.ATR_day
        walkpath = WalkPath.InRange
        if (self.trend_status.value >= TrendStatus.UpInUp.value):
            walkpath = WalkPath.Up
            self.watch_hh = dklines.iloc[-start_day].close + self.ATR_day
            self.watch_ll = (dklines.iloc[-start_day].low+dklines.iloc[-start_day].close)/2
            self.debug("WalkPath.Up1")

        elif (self.trend_status.value <= TrendStatus.DownInDown.value):
            walkpath = WalkPath.Down
            self.watch_ll = dklines.iloc[-start_day].close - self.ATR_day
            self.watch_hh = (dklines.iloc[-start_day].high+dklines.iloc[-start_day].close)/2
            self.debug("WalkPath.Down1")

        elif (self.trend_status.value >= TrendStatus.WaveBottom.value):
            ll_10, to_ll_bar = pplib.get_lest_in_range2(dklines, start_day, start_day+10)
            to_ll_height = dklines.iloc[-start_day].low - ll_10

            if (to_ll_bar>=start_day+2 and to_ll_bar<start_day+6 and to_ll_height<self.ATR_day): #
                bar_id = start_day + 1
                if (dklines.iloc[-bar_id].open > dklines.iloc[-bar_id].close):
                    walkpath = WalkPath.Up
                    self.debug("WalkPath.Up2")
                    self.watch_hh = pplib.get_avg_high2(dklines, start_day, 3) + 10
                    self.watch_ll = pplib.get_avg_low2(dklines, start_day, 3)
                else:
                    walkpath = WalkPath.Down
                    self.watch_hh = pplib.get_avg_high2(dklines, start_day, 3) - 10
                    self.watch_ll = pplib.get_avg_low2(dklines, start_day, 3) - 10
                    self.debug("WalkPath.Down2")
            else:
                walkpath = WalkPath.InRange
                self.debug("WalkPath.InRange2")
                boll=BOLL(dklines, 6, 1.5)
                self.watch_ll = list(boll["bottom"])[-start_day]
                self.watch_hh = list(boll["top"])[-start_day]

        elif (self.trend_status.value <= TrendStatus.WaveTop.value):
            hh_10, to_hh_bar = pplib.get_hest_in_range2(dklines, start_day, start_day+10)
            to_hh_height = hh_10 - dklines.iloc[-start_day].high

            if (to_hh_bar>=start_day+2 and to_hh_bar<start_day+6 and to_hh_height<self.ATR_day): #
                bar_id = start_day + 1
                if (dklines.iloc[-bar_id].open > dklines.iloc[-bar_id].close):
                    walkpath = WalkPath.Up
                    self.debug("WalkPath.Up3")
                else:
                    walkpath = WalkPath.Down
                    self.watch_hh = pplib.get_avg_high2(dklines, start_day, 3) + 10
                    self.watch_ll = pplib.get_avg_low2(dklines, start_day, 3)
                    self.debug("WalkPath.Down3")
            else:
                walkpath = WalkPath.InRange
                self.debug("WalkPath.InRange3")
                boll=BOLL(dklines, 6, 1.5)
                self.watch_ll = list(boll["bottom"])[-start_day]
                self.watch_hh = list(boll["top"])[-start_day]
        else:
            self.debug("WalkPath.InRange4")
            walkpath = WalkPath.InRange
            self.watch_hh = pplib.get_avg_high2(dklines, start_day, 3)
            self.watch_ll = pplib.get_avg_low2(dklines, start_day, 3)
        
        self.predict_walkpath = walkpath
        
        self.debug("forecast walkpath=%s self.watch_hh=%d self.watch_ll=%d"%(walkpath, self.watch_hh, self.watch_ll))

    def walkpath_to_val(self, wp):
        val = 0
        if (wp == WalkPath.Down):
            val = -30
        elif (wp == WalkPath.Up):
            val = 30
        else:
            val = 0
        return val

    def get_prediction_val(self):
        prediction_val = self.walkpath_to_val(self.predict_walkpath)

        real_val = int(prediction_val*0.4 + self.kpi*0.6)

        return real_val
        '''
        if (self.to_top == 1):
            hest_inday = self.indictor.get_highest_inday()
            if(self.hh_20 - self.cur_price < self.ATR_day):
                pass
            #标志性情况
            #冲高回落
        elif(self.to_bottom == 1):
            pass
            #赶底拉回
        else:
            #幅度
            range_score = 0
            atr = self.indictor.get_atr_daily()
            d_v = (self.hh_5 - self.ll_5)/atr
            if (d_v > 4.0):
                range_score = 2
            elif (d_v > 3.0):
                pass
            elif (d_v > 2.0):
                pass
            else:
                reds = 0
                green = 0

        #l_cksum_daily = 
        #s_cksum_daily = 

        self.prediction_val = 0

        return self.prediction_val
        '''

    def backtest(self, klines):
        for i in range(1, 10):
            print("==========[%s]==============="%(tafunc.time_to_str(klines.iloc[-i].datetime)))
            self.get_daybar_score(klines, i)

    def get_degree_daily(self):
        return self.kpi

    def check_risk(self, klines):
        #跳空
        pass

    def get_daybar_score(self, klines, id):
        self.debug("======analyze [%s] daybar========="%(tafunc.time_to_str(klines.iloc[-id].datetime)))
        self.debug("当日：open=%d close=%d"%(klines.iloc[-1].open, klines.iloc[-1].close))
        self.debug("昨日：open=%d close=%d"%(klines.iloc[-id].open, klines.iloc[-id].close))
        #突破+40
        #Bigbang30
        #连续+10
        #震荡上一个绿+10
        #底部+10
        BreakScore=30
        BigBangScore=20
        CheckSumScore=20
        ContinueScore=10
        InRangeAdjust=10
        TopBomScore=10
        RED_GREEN_SCORE= 10
        
        self.kpi = 0
        self.cur_day_bar = id
        if (self.cur_price == 0):
            self.cur_price = klines.iloc[-id].close
        #常用数据
        atr = ATR(klines, 30)
        self.ATR_day = int(atr.atr.iloc[-id])
        print("[%s] self.ATR_day=%d"%(self.TAG, self.ATR_day))
       
        # big bang find
        self.last_big_green_candle,self.last_big_green_candle_hight = pplib.find_big_green_candle(klines, 1, id, id+20, atr.atr.iloc[-id]*1.5)
        self.last_big_red_candle, self.last_big_red_candle_height= pplib.find_big_red_candle(klines, 1, id, id+20, atr.atr.iloc[-id]*1.5)
         # big bang score
        if (self.last_big_red_candle-id < 10 and self.last_big_red_candle < self.last_big_green_candle):
            self.kpi = self.kpi + (11-(self.last_big_red_candle-id))*(BigBangScore/10) + int((self.last_big_red_candle - atr.atr.iloc[-id]*1.5)/50)*5
        if (self.last_big_green_candle-id < 10 and self.last_big_red_candle < self.last_big_green_candle):
            self.kpi = self.kpi - (11-(self.last_big_green_candle-1))*(BigBangScore/10) - int((self.last_big_red_candle - atr.atr.iloc[-id]*1.5)/50)*5
        print("[%s] self.last_big_red_candle=%d, self.last_big_green_candle=%d"%(self.TAG, self.last_big_red_candle, self.last_big_green_candle))
        print("[%s] kpi=%d"%(self.TAG, self.kpi))
        
        #continue find
        self.last_continue_up_bar = 999
        self.last_continue_down_bar = 999
        for i in range(id, id+6):
            count = 0
            for j in range(0, 3):
                if (klines.iloc[-(i+j)].open < klines.iloc[-(i+j)].close):
                    count = count + 1
                else:
                    count = count - 1
            if (count >= 3):
                self.last_continue_up_bar = i
                break
            elif(count <= -3):
                self.last_continue_down_bar = i
                break
        #连续
        if (self.last_continue_up_bar-id<=1):
            self.kpi = self.kpi + ContinueScore
        if (self.last_continue_down_bar-id<=1):
            self.kpi = self.kpi - ContinueScore
        print("[%s] self.last_continue_up_bar=%d self.last_continue_down_bar=%d"%(self.TAG, self.last_continue_up_bar, self.last_continue_down_bar))
        print("[%s] kpi=%d after ContinueScore"%(self.TAG, self.kpi))
        #checksum
        self.day_checksum_4 = pplib.get_checksum(klines,5, 1)
        cks_ret = abs(self.day_checksum_4)/self.ATR_day
        print("[%s] self.day_checksum_4=%d cks_ret=%f"%(self.TAG, self.day_checksum_4, cks_ret))
        cks_score = 0
        cks_weight = 0.2
        if (cks_ret > 1.5):
            cks_weight = 1
        elif (cks_ret > 1):
            cks_weight = 0.7
        elif (cks_ret > 0.5):
            cks_weight = 0.5
        else:
            cks_weight = 0.2
        if (self.day_checksum_4 > 0):
            cks_score = int(CheckSumScore*cks_weight)
        if (self.day_checksum_4 < 0):
            cks_score = -int(CheckSumScore*cks_weight)
        print("[%s] cks_score=%d"%(self.TAG, cks_score))
        # inrange find
        heightest = 1000
        heightest_bar = 1
        '''
        for i in range(id, id+2):
            height = pplib.get_height_in_range(klines, i, i+3)
            if (height > heightest):
                heightest = height
                heightest_bar = i
        '''
        heightest = pplib.get_height_in_range(klines, id, id+5)
        result = heightest/atr.atr.iloc[-i]
        print("[%s] result=%f"%(self.TAG, result))
        if (result < 1.5):
            self.last_inrange_bar = heightest_bar
        self.last_inrange_height = heightest
        self.last_inrange_high = pplib.get_hest_in_range(klines, id, id+5)
        self.last_inrange_low = pplib.get_lest_in_range(klines, id, id+5)
        
        #inrange score
        if (self.last_inrange_bar-id < 2 and self.last_continue_up_bar-id>3 
            and self.last_continue_down_bar-id>3):
            if (klines.iloc[-id].close > klines.iloc[-id].open):
                self.kpi = self.kpi - InRangeAdjust
            else:
                self.kpi = self.kpi - InRangeAdjust
        print("[%s] last_inrange_bar=%d"%(self.TAG, self.last_inrange_bar))
        self.debug("last_inrange_high=%d last_inrange_low=%d last_inrange_height=%d"%(self.last_inrange_high, self.last_inrange_low, self.last_inrange_height))
        print("[%s] kpi=%d"%(self.TAG, self.kpi))
        #===================================================#
        # break find
        self.last_break_up_bar = 999
        self.last_break_down_bar = 999
        for i in range(id, id+6):
            tmp = pplib.get_hest_in_range(klines, i+1, i+1+4)
            if (klines.iloc[-i].close > tmp):
                self.last_break_up_bar = i
                break
        for i in range(id, id+6):
            tmp = pplib.get_lest_in_range(klines, i+1, i+1+4)
            if (klines.iloc[-i].close < tmp):
                self.last_break_down_bar = i
                break
        #break
        if (self.last_break_up_bar-id==0):
            self.kpi = self.kpi + BreakScore
        elif (self.last_break_up_bar-id==1):
            self.kpi = self.kpi + int(BreakScore/2)
        elif (self.last_break_up_bar-id==2):
            self.kpi = self.kpi + int(BreakScore/3)
        if (self.last_break_down_bar-id==0):
            self.kpi = self.kpi - BreakScore
        elif (self.last_break_down_bar-id==1):
            self.kpi = self.kpi - int(BreakScore/2)
        elif (self.last_break_down_bar-id==2):
            self.kpi = self.kpi - int(BreakScore/3)
        print("[%s] self.last_break_up_bar=%d self.last_break_down_bar=%d "%(self.TAG, self.last_break_up_bar, self.last_break_down_bar))
        print("[%s] kpi=%d"%(self.TAG, self.kpi))
        #=====================================#
        # price pos find
        self.hh_100,self.hh_100_bar = pplib.get_hest_in_range2(klines, id, id+100)
        self.ll_100,self.ll_100_bar = pplib.get_lest_in_range2(klines, id, id+100)
        price_pos_ratio = (self.cur_price-self.ll_100)/(self.hh_100-self.ll_100)
        if (price_pos_ratio <= 0.5):
            self.kpi = self.kpi + (5 - int(price_pos_ratio*TopBomScore))*2
        else:
            self.kpi = self.kpi - (int(price_pos_ratio*TopBomScore) - 5)*2
        print("[%s] price_pos_ratio=%f"%(self.TAG, price_pos_ratio)) 
        print("[%s] kpi=%d"%(self.TAG, self.kpi))
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
       
        #修正
        if (self.last_break_up_bar-id <= 2 and self.last_big_red_candle-id < 6):
            print ("last_break_up_bar=%d last_big_red_candle=%d  "%(self.last_break_up_bar-id <= 2 ,self.last_big_red_candle-id))
            self.kpi += 20
        if (self.last_break_down_bar-id <= 2 and self.last_big_green_candle-id < 6):
            self.kpi -= 20 
        if (self.last_break_up_bar-id <= 2 and price_pos_ratio <0.6):
            self.kpi += 20
            print ("last_break_up_bar=%d price_pos_ratio=%d  "%(self.last_break_up_bar-id <= 2 ,price_pos_ratio))
        if (self.last_break_down_bar-id <= 2 and self.last_big_green_candle-id < 6):
            self.kpi -= 20 
        #print ("height=%d atr=%d wave ratio=%f "%(height, atr.atr.iloc[-i], height/atr.atr.iloc[-i]))
        print("[%s] kpi=%d"%(self.TAG, self.kpi))
        #=====================================================================#
        # 距离底、顶的距离
        self.hh_20,self.hh_20_bar = pplib.get_hest_in_range2(klines, id, id+20)
        self.ll_20,self.ll_20_bar = pplib.get_lest_in_range2(klines, id, id+20)
        self.hh_10,self.hh_10_bar = pplib.get_hest_in_range2(klines, id, id+10)
        self.ll_10,self.ll_10_bar = pplib.get_lest_in_range2(klines, id, id+10)
        self.hh_5,self.hh_5_bar = pplib.get_hest_in_range2(klines, id, id+6)
        self.ll_5,self.ll_5_bar = pplib.get_lest_in_range2(klines, id, id+6)
        dif = self.hh_10_bar -id
        if (dif == 0):
            self.kpi += TopBomScore
        if (dif == 1):
            self.kpi += int(TopBomScore/2)
        elif (dif == 2):
            self.kpi -= TopBomScore
        elif (dif == 3):
            self.kpi += TopBomScore
        elif (dif>3 and dif<=5):
            self.kpi -= TopBomScore
        self.to_top = dif

        dif = self.ll_10_bar -id
        if (dif == 0):
            self.kpi -= TopBomScore
        if (dif == 1):
            self.kpi -= int(TopBomScore/2)
        elif (dif == 2):
            self.kpi += TopBomScore
        elif (dif == 3):
            self.kpi -= TopBomScore
        elif (dif>3 and dif<=5):
            self.kpi += TopBomScore 
        self.to_bottom = dif
        print("[%s] to top=%d, to bottom=%d "%(self.TAG, self.hh_10_bar -id, self.ll_10_bar - id))
        print("[%s] kpi=%d"%(self.TAG, self.kpi))
        #==============================================================#
        # 红绿数量
        red_gre_score = 0
        self.reds = pplib.get_reds_candle(klines, 6)
        self.greens = pplib.get_greens_candle(klines, 6)
        if (self.greens > 0):
            red_gre_score -= self.greens*20
        if (self.reds > 0):
            red_gre_score += self.reds*20
        self.kpi += red_gre_score*(RED_GREEN_SCORE/100)
        #跳空
        print("[%s] greens=%d reds=%d"%(self.TAG, self.greens, self.reds))
        gap_v = klines.iloc[-id].open - klines.iloc[-(id+1)].close
        if (gap_v > 10):
            print("[%s] 高跳"%(self.TAG))
            self.manager.drive_event(self.TAG, StgEvent.GapUp, gap_v)
            self.kpi += 10
        gap_v = klines.iloc[-(id+1)].close - klines.iloc[-id].open
        if (gap_v > 10):
            print("[%s] 低跳"%(self.TAG))
            self.manager.drive_event(self.TAG, StgEvent.GapDown, gap_v)
            self.kpi -= 10
        
        print("[%s] kpi=%d"%(self.TAG, self.kpi))

    def run(self, klines, bid_price, ask_price, avg_price):
        # only support and break
        self.cur_price = ask_price
        if (self.inited == False):
            return
        self.on_bar(klines)

    def out_trend(self, klines):
        if (self.ma5 > self.last_inrange_high): 
            self.ma50 = pplib.get_average(klines,50)
            if(self.ma50 > self.last_inrange_high):
                return 1
            elif (self.ma5 > self.last_inrange_high+30):
                return 1
            else:
                return 0
        elif (self.ma5 > self.last_inrange_low):
            self.ma50 = pplib.get_average(klines,50)
            if(self.ma50 < self.last_inrange_low):
                return -1
            elif (self.ma5 < self.last_inrange_low-30):
                return -1
            else:
                return 0
        else:
            return 0

    def find_trend(self, klines):
        if (self.reds > 2 and self.kpi > 20):
            return self.out_trend(klines)
        elif (self.greens > 2 and self.kpi < -20):
            return self.out_trend(klines)
        else:
            return 0

    def find_breakout(self, klines):
        if (self.last_inrange_height > 2*self.ATR_day or
            self.day_checksum_4 > self.ATR_day*1.5):
            return 0
        '''
        ret = self.out_trend(klines)
        if (ret == 1):
            if (self.hh_inday_bar>45):
                ret = 0
        elif (ret == -1):
            if (self.ll_inday_bar>45):
                ret = 0
        return ret
        '''
        if (self.ma5 > self.last_inrange_high): 
            self.ma50 = pplib.get_average(klines,50)
            if(self.ma50 > self.last_inrange_high):
                self.info5("find breakout hh by height")
                return 1
            elif (self.ma5 > self.last_inrange_high+20):
                self.info5("find breakout hh by height")
                return 1
            else:
                return 0
        elif (self.ma5 > self.last_inrange_low):
            self.ma50 = pplib.get_average(klines,50)
            if(self.ma50 < self.last_inrange_low):
                self.info5("find breakout ll by height")
                return -1
            elif (self.ma5 < self.last_inrange_low-30):
                self.info5("find breakout ll by height")
                return -1
            else:
                return 0
        else:
            return 0

        return 0

    def find_goback(self, klines):
        #强趋势下 回调
        #突破失败
        if (abs(self.hh_inday-self.hh_10) < 15
            and (self.hh_10_bar > 30 or self.hh_10-self.ma5 > 20)):
            self.info5("find  goback from hh")
            return -1
        elif (abs(self.ll_inday-self.ll_10) < 15
            and (self.ll_10_bar > 30 or self.ma5 - self.ll_10 > 20)):
            self.info5("find  goback from ll")
            return 1
        else:
            return 0

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        
        cur_bar = self.get_current_minute_bar()
        s_checksum = pplib.get_checksum(klines,10, 1)
        l_checksum = pplib.get_checksum(klines,50, 0)
        self.ma5 = pplib.get_avg_price(klines, 6)
        tmp_position = self.position
        self.hh_inday, self.hh_inday_bar = pplib.get_highest_bar_today2(klines) #可以不用替换_fix
        self.ll_inday, self.ll_inday_bar = pplib.get_lowest_bar_today2(klines)
        
        # big bang + top、bottom
        #long top、bottom
        if (abs(self.hh_inday - self.hh_100)<20 and self.position >= 0):
            #if (cur_bar - self.hh_inday_bar > 30):
            if (self.hh_inday_bar > 30):
                tmp_position = -1
            if (self.hh_inday - self.ma5 > 30):#bigbang
                tmp_position = -1
        if (abs(self.ll_inday - self.ll_100)<20 and self.position <=0):
            #if (cur_bar - self.ll_inday_bar > 30):
            if (self.ll_inday_bar > 30):
                tmp_position = 1
            if (self.ma5 - self.ll_inday > 30): #bigbang
                tmp_position = 1

        #######################
        # 突破
        tmp =self.find_breakout(klines)
        if (tmp != 0):
            tmp_position = tmp
        else:
            tmp = self.find_goback(klines)
            if (tmp != 0):
                tmp_position = tmp
        '''
        tmp_cond_flag = self.cond_flag
        ret = self.find_trend(klines)
        if (ret == 1): # 趋势
            tmp_cond_flag = 1
        elif(ret == -1):
            tmp_cond_flag = -1
        else:
            ret = self.find_breakout(klines)
            if (ret != 0): #突破
                tmp_cond_flag = ret
            else:
                ret = self.find_goback(klines) #回归
                pass

        if (self.cond_flag != tmp_cond_flag):
            self.cond_flag = tmp_cond_flag
            self.cond_mark_bar = cur_bar

        if (self.cond_flag != 0 and (cur_bar - self.cond_mark_bar > 3)):
            if (abs(s_checksum)):
                if (self.cond_flag > 0 and self.position <= 0):
                    tmp_position = 1
                elif (self.cond_flag < 0 and self.position >=0):
                    self.debug("")
                    tmp_position = -1
        '''

        # ping
        if (self.position > 0):
            if (self.entry_price - self.ma5 > abs(self.MAX_LOSS)):
                self.debug("多止....")
                tmp_position = 0
            elif (cur_bar - self.entry_bar > 120 and abs(s_checksum) < 5):
                ups = pplib.get_count_of_greater(klines,cur_bar)
                if (ups > 30):
                    self.debug("时间止")
                    tmp_position = 0
            elif (self.ask_price - self.entry_bar > self.MAX_PROFIT and abs(s_checksum) < 5):
                tmp_position = 0
                self.debug("止盈。。。。")
        elif (self.position < 0):
            if (self.ma5 - self.entry_price > abs(self.MAX_LOSS)):
                self.debug("空止....")
                tmp_position = 0
            elif (cur_bar - self.entry_bar > 120 and abs(s_checksum) < 5):
                downs = pplib.get_count_of_less(klines,cur_bar)
                if (downs > 30):
                    self.debug("时间止")
                    tmp_position = 0
            elif (self.entry_bar - self.ask_price > self.MAX_PROFIT and abs(s_checksum) < 5):
                tmp_position = 0
                self.debug("止盈。。。。")

        if (tmp_position != self.position):
            if (tmp_position > 0 and self.check_open_order(1, 20)):
                self.info5("开仓间隔控制")
            elif (tmp_position < 0 and self.check_open_order(-1, 20)):
                self.info5("开仓间隔控制")
            else:
                self.set_position(tmp_position)

    def timer_task(self):
        pass

    def get_kpi(self):
        return self.kpi

    def close(self):
        self.run_flag = False

    # 发现重要模式
    #
    def find_key_mode(self):
        pass

'''
#from back_test import StrategyManagerTest

api = TqApi()
klines = api.get_kline_serial("SHFE.rb2010", 24*60*60)
atr = ATR(klines, 10)
#print(atr.tr)  # 真实波幅
#print(atr.atr)  # 平均真实波幅
print (tafunc.time_to_str(klines.iloc[-1].datetime))
#print (klines.iloc[-1])
#'''
#for i in range(1, 10):
#    print(atr.tr.iloc[-i], atr.atr.iloc[-i])


'''
for i in range(1, 4):
    height = pplib.get_height_in_range(klines, i, i+3)
    print ("height=%d atr=%d wave id=%f "%(height, atr.atr.iloc[-i], height/atr.atr.iloc[-i]))

i,val = pplib.find_big_green_candle(klines, 1, 20, atr.atr.iloc[-1]*1.5)
if (i > 0):
    print(i, klines.iloc[-i])
else:
    print(i)



i,val = pplib.find_big_red_candle(klines, 1, 1, 20, atr.atr.iloc[-1]*1.5)
if (i > 0):
    print(i, klines.iloc[-i])
else:
    print(i)

manager = StrategyManagerTest()
watcher = StrategyWatcher(manager)
watcher.update_day_klines(klines)

while True:
    ma = tafunc.ma(klines.close, 20)
    print("=========start===============")
    #ma = MA(klines, 20)
    #print(list(ma))
    print(ma.iloc[-1])
#    print(list(ma.tail(1)["ma"]))
    print("=========end===============")
    api.wait_update()
'''