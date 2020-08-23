# 指标
# 分析方向，被强力拉回的方向
from pplib import get_checksum,get_hest_in_range,get_ll_price_bar,get_hh_price_bar,\
    get_support_line, get_resistance_line,get_sensitive_hh,get_sensitive_ll,\
        get_count_of_nearest_greater,get_count_of_nearest_less
import pplib
from tool_utils import get_minute,get_second
import tool_utils
from tqsdk.ta import ATR
from tqsdk import tafunc
from datetime import datetime
import time
from strategy_base import StrategyBase
from param_defines import TradeDirection, Indicator, StgEvent, ParamUnion
from kpattern.kpattern_cross_series import KPCrossOverAvgLine, KPCrossUnderAvgLine

class McIndictors(StrategyBase):
    def __init__(self, symbol,manager):
        StrategyBase.__init__(self, symbol, "McIndictors", manager)
        self.TAG = "McIndictors"
        self.symbol = symbol
        self.UPDATE_INTERVAL = 2 # minute

        self.trade_dir = TradeDirection.INVALID

        self.init_flag = False

        self.init_var()

    def new_day(self):
        #当天的情况
        self.init_var()

    def init_var(self):
        self.UpdateTradeInterval = 5
        self.short_term = 8
        self.long_term = 90

        self.avg_overs = 0
        self.avg_unders = 0
        self.last_crossdown_bar = 0
        self.last_crossover_bar = 0
        self.atr_5 = 0

        self.ma10 = 0
        #
        self.cur_price = 0
        # data record
        self.lastday_quote = []

        #当天的情况
        self.hest_inday = 0
        self.lest_inday = 0
        self.open_price = 0
        self.hest_bar_inday = 0
        self.lest_bar_inday = 0
        self.gap_height = 0
        self.range_height_30 = 0 #30分钟高度
        
        #控制
        self.run_flag = True
        self.day_record = {}

        #find strong
        self.strong_direction = 0
        self.strong_type = 0
        self.strong_start_bar = 0
        self.strong_end_bar = 999
        self.last_fit_less_bar = 999
        self.last_fit_greater_bar = 999
        self.strong_result = 0
        #break
        self.last_break_down_bar = 0
        self.last_break_up_bar = 999
        self.last_inrange_ll = 0
        self.last_inrange_hh = 0
        self.last_after_break_ll = 0
        self.last_after_break_hh = 0
        self.last_inrange_end_bar = 999
        self.csum_12 = 0
        self.height_12 = 0
        self.last_bigbang_up = 999
        self.last_bigbang_down= 999

        self.open_score = 0
        self.atr_daily = 60

        self.score = 0
        self.hh_100_daily = 0
        self.ll_100_daily = 0

    def init_data(self, klines):
        self.init_flag = True
        cur_bar = self.get_current_minute_bar()
        if (cur_bar > 2):
            self.open_price = pplib.get_open_today(klines, 1)
            self.lest_inday = pplib.get_lest_in_range(klines, 1, cur_bar)
            self.hest_inday = pplib.get_hest_in_range(klines, 1, cur_bar)
        else:
            self.open_price = klines.iloc[-1].open
            self.lest_inday = klines.iloc[-1].open
            self.hest_inday = klines.iloc[-1].open

    def start(self):
        self.run_flag = True

    def stop(self):
        self.run_flag = False

    def set_avg_recorder(self, avg_recorder):
        self.avg_recorder = avg_recorder

    def set_stg_manager(self, manager):
        self.manager = manager

    def get_strong(self):
        return self.strong_result

    #重要时间的变化，具有趋势性
    def monitor_key_time(self):
        lt = time.localtime(time.time())
        if(lt.tm_hour == 21 and lt.tm_min <= 30): 
            pass
            #参考日内，判断今天的情况
        elif(lt.tm_hour == 9 and lt.tm_min <= 30): 
            #是否出现异动
            #周五回来后，跳空？
            #前期已经涨幅过大？

            pass
        elif(lt.tm_hour == 11 and lt.tm_min >= 15):
            pass
        elif(lt.tm_hour == 13 and lt.tm_min <= 50):
            #下午，行情的突破与拉回
            pass

    def find_strong(self, klines):
        #===============================================#  
        if (self.downs_of_this > 100):
            self.last_fit_less_bar = self.get_current_minute_bar()
        if (self.overs_of_this > 100):
            self.last_fit_greater_bar = self.get_current_minute_bar()
        
        #range break
        #last 5 break last 120
        # 
        hh_5 = pplib.get_hest_in_range(klines, 1, 6)
        ll_5 = pplib.get_lest_in_range(klines, 1, 6)
        range_width = 120
        if (self.cur_bar < 120):
            range_width = self.cur_bar
        if (range_width <= 6):
            return
        hh_120 = pplib.get_hest_in_range(klines, 6, range_width)
        ll_120 = pplib.get_lest_in_range(klines, 6, range_width)

        bk_last_break_down_bar = self.last_break_down_bar
        bk_last_break_up_bar = self.last_break_up_bar
        if (hh_120 - ll_120 < 30):
            if (ll_120 - ll_5 > 10):
                self.last_break_down_bar = self.get_current_minute_bar()
                self.last_after_break_ll = ll_5
            elif (hh_5 - hh_120 > 10):
                self.last_break_up_bar = self.get_current_minute_bar()
                self.last_after_break_hh = hh_5
            self.last_inrange_end_bar = self.get_current_minute_bar() - 5

        #突破、拉回、反向创新高
        #突破,判断回调、再突破
        if (self.last_break_down_bar<150 and 
            self.cur_bar - self.last_break_down_bar < 20+6 and self.ma5 > self.last_inrange_ll
            ):# 折回
            pass
        elif (self.last_break_down_bar > 10 and self.ma5 < self.last_after_break_ll ): # 连续突破
            self.strong_result = -1
            self.strong_direction = -1
        # 多
        if (self.last_break_up_bar<150 and 
            self.cur_bar - self.last_break_up_bar < 20+6 and self.ma5 > self.last_inrange_hh
            ): # 折回
            self.strong_result = 1
            self.strong_direction = 1
        elif (self.last_break_down_bar > 10 and self.ma5 < self.last_after_break_ll ): # 连续突破
            self.strong_result = 1
            self.strong_direction = 1

        #突破、反向创新高
        if (self.cur_price > hh_120 and (self.cur_bar - self.last_break_up_bar < 30+6) and 
            (self.cur_bar - self.last_break_down_bar < 120 and self.last_break_down_bar > 20)):
            self.strong_result = 2
            self.strong_direction = 2
        if (self.cur_price < ll_120 and self.cur_bar - self.last_break_down_bar < 30+6
            and (self.last_break_up_bar > 20 and self.cur_bar - self.last_break_up_bar < 120)):
            self.strong_result = -2
            self.strong_direction = -2

        height_12 = pplib.get_height_in_range(klines, 1, 13)
        csum = pplib.get_checksum(klines, 13, 1)
        if (csum > 25 or (csum>0 and height_12>18)):
            self.debug("strong up chsum=%d height_12=%d"%(csum, height_12))
            self.info("strong up chsum=%d height_12=%d"%(csum, height_12))
            self.csum_12 = csum
            self.height_12 = height_12
            self.last_bigbang_up = self.cur_bar
        if (csum < -25 or (csum<0 and height_12>18)):
            self.debug("strong down chsum=%d height_12=%d"%(csum, height_12))
            self.info("strong down chsum=%d height_12=%d"%(csum, height_12))
            self.csum_12 = csum
            self.height_12 = height_12
            self.last_bigbang_down=self.cur_bar
    
        #连续 达到一定高度
    
    def run(self, klines, bid_price, ask_price, avg_price):
        self.cur_price = ask_price
        self.bid_price = bid_price
        self.ask_price = ask_price
        self.avg_price = avg_price
        self.on_bar(klines)

    def on_tick(self, serial):
        StrategyBase.on_tick(self, serial)

    def make_prediction(self):
        pass

    def get_score_inday(self, klines):
        #======================================================#
        #计算得分
        open_score = 0
        trend_score = 0
        o_d_score = 0
        self.score = 0

        lt = self.get_real_time()
        cur_bar = self.get_current_minute_bar()
        #前日高低
        #开仓判断
        if (((lt.tm_hour == 21 or lt.tm_hour == 9) and lt.tm_min < 30 and lt.tm_min > 5)
            or (self.open_score == 0 and cur_bar > 30)):
            #跳空 50
            if (cur_bar < 2):
                open_ma5 = klines.iloc[-1].close
            elif (cur_bar < 7):
                open_ma5 = pplib.get_average2(klines, 1, cur_bar-1)
            else:
                open_ma5 = pplib.get_average2(klines, cur_bar-6, 6)
            #================================#
            if (lt.tm_hour == 21 and lt.tm_min<7):
                self.gap_height = open_ma5 - self.lastday_quote[1].close
            elif (lt.tm_hour == 9 and lt.tm_min<7):
                pre_ma5 = pplib.get_average2(klines, cur_bar+6, 6)
                self.gap_height = open_ma5 - pre_ma5

            if (self.open_score == 0 and cur_bar > 30):
                 open_ma5 = pplib.get_average2(klines, cur_bar-6, 6)
                 self.gap_height = open_ma5 - self.lastday_quote[1].close

            gap_height = self.gap_height

            if(abs(gap_height) > 30):
                open_score = 50
                self.debug("gap_height=%d"%(gap_height))
            elif(abs(gap_height) > 20):
                open_score = 40
                self.debug("gap_height=%d"%(gap_height))
            elif(abs(gap_height) > 15):
                open_score = 25
                self.debug("gap_height=%d"%(gap_height))
            elif(abs(gap_height) > 5):
                open_score = 10
                self.debug("gap_height=%d"%(gap_height))
            elif(abs(gap_height) > 0):
                open_score = 5
                self.debug("gap_height=%d"%(gap_height))
            else:
                open_score = 0
            
            if (gap_height < 0):
                open_score = -open_score

            #================================#
            #冲高回落50
            hh = pplib.get_highest_price_today(klines)
            ll = pplib.get_lowest_price_today(klines)
            open_p = pplib.get_open_today(klines, 0)

            if (hh > open_p + 15 and hh-self.ask_price> 15):
                open_score = open_score - 30
            if (hh > open_p + 15 and hh-self.ask_price> 15):
                open_score = open_score - 30
            
            #连续性
            trend_score = 0
            ma5 = pplib.get_average(klines, 6)
            dif = ma5 - open_p
            d_v = int((abs(dif)/35)*50)
            if (dif > 0):
                trend_score = d_v
            else:
                trend_score = -d_v
            open_score += trend_score
            
            self.open_score = open_score
            return self.open_score
        else:
            pass
        #波峰、波谷计算趋势性
        if (cur_bar > 60):
            open_p = pplib.get_open_today(klines, 60)
            m_opens = pplib.get_M_opens(klines, 10)
            m_len = 0
            #===========向下开口得分==============#
            if (m_opens is not None):
                m_len = len(m_opens)
            m_difsum = 0
            if (m_len >= 2):
                for i in range(0, m_len-1):
                    m_difsum += m_opens.loc[i].high - m_opens.loc[i+1].high
            if (m_len >= 1):
                m_difsum += m_opens.loc[m_len-1].high - open_p
            #==========向上开口得分===============#
            w_difsum = 0
            w_opens = pplib.get_W_opens(klines,20)
            w_len = 0
            if (w_opens is not None):
                w_len = len(w_opens)
            if (w_len >= 2):
                for i in range(0, w_len-1):
                    w_difsum += w_opens.loc[i].low - w_opens.loc[i+1].low
            if (w_len >= 1):
                w_difsum += w_opens.loc[w_len-1].low - open_p
            #=============综合计算===================#
            #是否一致性
            if (self.atr_daily <40):
                self.atr_daily = 50
            if (w_difsum > 0 and m_difsum > 0):
                a_sum = w_difsum+m_difsum
                '''
                if (w_difsum+m_difsum > self.atr_daily):
                    trend_score = 70
                if (w_difsum+m_difsum > self.atr_daily/2):
                    trend_score = 40
                '''
                a_sum = w_difsum+m_difsum
                ret = abs(a_sum) / self.atr_daily
                if (ret > 1):
                    ret = 1
                trend_score = ret*100
                trend_score = trend_score+30
                if (trend_score > 100):
                    trend_score = 100
            elif (w_difsum < 0 and m_difsum < 0):
                a_sum = w_difsum+m_difsum
                ret = abs(a_sum) / self.atr_daily
                if (ret > 1):
                    ret = 1
                trend_score = -ret*100
                trend_score = trend_score-30
                if (trend_score < -100):
                    trend_score = -100
            else:
                a_sum = w_difsum+m_difsum
                ret = abs(a_sum) / self.atr_daily
                if (ret > 1):
                    ret = 1
                if (a_sum > 0):
                    trend_score = ret*100
                else:
                    trend_score = -ret*100

                if (trend_score < -100):
                    trend_score = -100
                if (trend_score > 100):
                    trend_score = 100

        if (trend_score == 0):#未形成开口
            l_chsum = pplib.get_checksum(klines, cur_bar, 1)
            hour_pass = (cur_bar/60)+1
            d_v = int(abs(l_chsum)/hour_pass)
            if (d_v > 35):
                trend_score = 50
            elif (d_v > 20):
                trend_score = 40
            elif (d_v > 10):
                trend_score = 20
            elif (d_v > 5):
                trend_score = 10

            if (l_chsum < 0):
                trend_score = -trend_score

            self.info("get_score_inday: trend_score=%d"%(trend_score))
        # avg overs、Downs
        # 数量和占比得分
        if (self.avg_overs > self.avg_unders and self.cur_bar > 0):
            if (self.avg_overs > 110 and self.avg_unders < 9):
                o_d_score = 100
            elif (self.avg_overs - self.avg_unders<20):
                o_d_score = 10
            elif (self.avg_overs/self.cur_bar > 0.9):
                o_d_score = 90
            elif (self.avg_overs/self.cur_bar > 0.8):
                o_d_score = 80
            elif (self.avg_overs/self.cur_bar > 0.7):
                o_d_score = 60
            elif (self.avg_overs/self.cur_bar > 0.6):
                o_d_score = 30
            elif (self.avg_overs/self.cur_bar > 0.5):
                o_d_score = 10
        elif (self.avg_overs < self.avg_unders and self.cur_bar > 0):
            if (self.avg_unders > 110 and self.avg_overs < 9):
                o_d_score = -100
            elif (self.avg_unders - self.avg_overs <20):
                o_d_score = -10
            elif (self.avg_unders/self.cur_bar > 0.9):
                o_d_score = -90
            elif (self.avg_unders/self.cur_bar > 0.8):
                o_d_score = -80
            elif (self.avg_unders/self.cur_bar > 0.7):
                o_d_score = -60
            elif (self.avg_unders/self.cur_bar > 0.6):
                o_d_score = -30
            elif (self.avg_unders/self.cur_bar > 0.5):
                o_d_score = -10
        #bigbang_down
        if ((self.cur_bar-self.last_bigbang_down < 10) and (self.last_bigbang_down<self.last_bigbang_up)):
            #pass
            bar_len = self.get_current_minute_bar()
            if (bar_len > 100):
                bar_len = 100
            #break
            ll_100, ll_100_bar = pplib.get_lest_in_range2(klines, 1, bar_len)
            #高度
            height_100 = pplib.get_height_in_range(klines, 1, bar_len)
            param = ParamUnion()
            param.put_param("height", self.height_12)
            if (ll_100_bar<10 or height_100>45):
                self.manager.drive_event(self.TAG, StgEvent.BigBangBreakDown, param)
            else:
                self.manager.drive_event(self.TAG, StgEvent.BigBangDown, param)

        if ((self.cur_bar-self.last_bigbang_up < 10) and (self.last_bigbang_up<self.last_bigbang_down)):
            #pass
            bar_len = self.get_current_minute_bar()
            if (bar_len > 100):
                bar_len = 100
            #break
            hh_100, hh_100_bar = pplib.get_hest_in_range2(klines, 1, bar_len)
            #高度
            height_100 = pplib.get_height_in_range(klines, 1, bar_len)
            param = ParamUnion()
            param.put_param("height", self.height_12)
            if (hh_100_bar<10 or height_100>45):
                self.manager.drive_event(self.TAG, StgEvent.BigBangBreakUp, param)
            else:
                self.manager.drive_event(self.TAG, StgEvent.BigBangUp, param)

        #脱离顶底部得分
        distance_score = 0
        hh_inday, hh_inday_bar= pplib.get_highest_bar_today2(klines)#不用替换成_fix
        ll_inday, ll_inday_bar = pplib.get_lowest_bar_today2(klines)
        self.debug("hh_inday=%d hh_inday_bar=%d cur_bar=%d"%(hh_inday, hh_inday_bar, cur_bar))
        self.debug("ll_inday=%d ll_inday_bar=%d"%(ll_inday, ll_inday_bar))
        if (hh_inday_bar < ll_inday_bar and hh_inday_bar > 110):
            distance_score = -30
        elif (hh_inday_bar < ll_inday_bar):
            avg_p = pplib.get_average(klines, 6)
            if (hh_inday_bar<20):
                if (hh_inday - avg_p < 15):
                    distance_score += 100
                else:
                    distance_score += 60
            elif(hh_inday_bar>25 and hh_inday_bar<55):
                
                if (hh_inday - avg_p < 15):
                    distance_score += 15
                elif (hh_inday - avg_p > 25):
                    distance_score -= 30
                elif (hh_inday - avg_p > 30):
                    distance_score -= 50
            else:
                distance_score -= 30
        elif (hh_inday_bar < ll_inday_bar and ll_inday_bar > 110):
            distance_score = 30
        else:
            avg_p = pplib.get_average(klines, 6)
            if (ll_inday_bar<20):
                if (avg_p - ll_inday < 15):
                    distance_score -= 100
                else:
                    distance_score -= 60
            elif(ll_inday_bar>25 and ll_inday_bar<55):
                if (avg_p-ll_inday < 15):
                    distance_score -= 15
                elif (avg_p-ll_inday>25):
                    distance_score += 30
                elif (avg_p - ll_inday>30):
                    distance_score += 50
            else:
                distance_score += 30
            #新高

        #key hour
        if (lt.tm_hour==9 and lt.tm_min < 20):
            self.key_hour_score = 0
            pass

        if (lt.tm_hour==13 and lt.tm_min < 40):
            pass
        #根据运行过程
        self.debug("open_score=%d trend_score=%d o_d_score=%d distance_score=%d"%(open_score,trend_score,o_d_score,distance_score))
        if (lt.tm_hour==21):
            self.score = int(self.open_score*0.3+o_d_score*0.6+distance_score*0.1)
        else:
            self.score = int(self.open_score*0.1+trend_score*0.3+o_d_score*0.5+distance_score*0.2)
        self.kpi = self.score

    def on_bar_5(self, klines):
        self.find_strong(klines)
        self.get_score_inday(klines)

        self.generate_indicator_event5()

        if (self.kpi > 50):
            self.debug("=====up up inday!!!!!!!======")
            self.manager.on_command(self.TAG, "ReportKpi", self.kpi)
        if (self.kpi > 30):
            self.debug("=====report kpi_inday !!!!!!!======")
            self.manager.on_command(self.TAG, "ReportKpi", self.kpi)
        if (self.kpi < -50):
            self.debug("=====down down inday!!!!!!!======")
            self.manager.on_command(self.TAG, "ReportKpi", self.kpi)
        if (self.kpi < -30):
            self.debug("=====report kpi_inday!!!!!!!======")
            self.manager.on_command(self.TAG, "ReportKpi", self.kpi)
    
    def on_bar_10(self, klines):
        self.range_height_30 = pplib.get_height_in_range(klines, 1, 31)
        if (self.range_height_30 < 20):
            hh = pplib.get_hest_in_range(klines, 1, 30)
            ll = pplib.get_lest_in_range(klines, 1, 30)
            bars = pplib.get_continus_bars_in_height(klines, 1, self.cur_bar, hh, ll) #在区间范围内的bar数
            range_inday = self.hest_inday - self.lest_inday
            if (range_inday > 30):
                # todo: 排除个别 
                param = ParamUnion()
                param.put_param("bars", bars)
                param.put_param("height", self.range_height_30)
                avg_10 = pplib.get_avg_price(klines, 11)
                if (self.hest_inday - avg_10 < (avg_10 - self.lest_inday)):
                    self.manager.drive_event(self.TAG, StgEvent.LowRangeAtTop, range_inday)
                else:
                    self.manager.drive_event(self.TAG, StgEvent.LowRangeAtBottom, range_inday)
            else:
                self.manager.drive_event(self.TAG, StgEvent.LowRange, range_inday)
        self.generate_price_action()
        

    def on_bar_30(self, klines):
        lt = self.get_real_time()
        if (lt.tm_hour >= 10):
            rg = self.hest_inday - self.lest_inday
            if (rg < 40):
                param = ParamUnion()
                param.put_param("int", rg)
                self.manager.drive_event(self.TAG, StgEvent.LowRange, param)
        self.range_height_30
                
    def on_bar(self,klines):
        StrategyBase.on_bar(self, klines)
        lt = self.get_real_time()
        self.cur_bar_time = klines.iloc[-1].datetime
        self.cur_bar = self.get_current_minute_bar()
        #==================================#
        if (self.init_flag == False):
            self.init_data(klines)
        #================test==============#
        '''
        self.debug("cur_bar=%d"%(self.cur_bar))
        if (klines.iloc[-1].id - klines.iloc[-33].id > 30):
            self.debug(">30")
        else:
            self.debug("<30")
        '''
        self.avg_overs = self.avg_recorder.bars_of_over(klines)
        self.avg_unders = self.avg_recorder.bars_of_under(klines)
        tmp_last_crossdown_bar = self.last_crossdown_bar
        self.last_crossdown_bar = self.avg_recorder.get_last_cross_under(klines, 2)
        if (tmp_last_crossdown_bar != self.last_crossdown_bar):
            kp = KPCrossUnderAvgLine()
            kp.bar = self.cur_bar
            kp.score = self.last_crossover_bar
        tmp_last_crossover_bar = self.last_crossover_bar
        self.last_crossover_bar = self.avg_recorder.get_last_cross_over(klines, 2)
        if (tmp_last_crossover_bar != self.last_crossover_bar):
            kp = KPCrossOverAvgLine()
            kp.bar = self.cur_bar
            kp.score = self.last_crossdown_bar
        self.s_checksum = get_checksum(klines, self.short_term, 1)
        self.l_checksum = get_checksum(klines, self.long_term, 1)
        self.hh_long = get_hest_in_range(klines, 0, 60) #长期的高
        self.hh_shor = get_hest_in_range(klines,0, 30) #短期的高
        self.ma5 = pplib.get_avg_price(klines, 5)

        #更新 最高最低
        if (klines.iloc[-1].close > self.hest_inday):
            self.hest_inday = klines.iloc[-1].close
            self.hest_bar_inday = self.get_current_minute_bar()
        if (klines.iloc[-1].close < self.lest_inday):
            self.lest_inday = klines.iloc[-1].close
            self.lest_bar_inday = self.get_current_minute_bar()

        if (self.open_price == 0 and self.cur_bar > 1):
            self.open_price = pplib.get_open_today(klines,1)

        if (self.UpdateTradeInterval >=1 and lt.tm_min % self.UpdateTradeInterval == 0):
            self.update_trand_indictor()
        elif(self.UpdateTradeInterval == 0):
            self.update_trand_indictor()

        self.count_of_nearest_less = pplib.get_count_of_nearest_less(klines, 5, 50)
        self.count_of_nearest_greater = pplib.get_count_of_nearest_greater(klines, 5, 50)
        self.downs_of_this = pplib.get_count_of_less(klines, self.cur_bar)
        self.overs_of_this = pplib.get_count_of_greater(klines, self.cur_bar)

        if (self.hest_bar_inday < 60): #近期新高
            if (self.Long_HH < self.hest_inday):
                self.trade_worning = 0

        if (lt.tm_min %4 == 0 and lt.tm_sec == 0):
            self.my_print("kpi=%d"%(self.score))

        #==============================================#
        self.generate_indicator_event(klines)

        #==============================================#
        if (lt.tm_min % 5 == 0 and self.cur_bar > 0):
            self.on_bar_5(klines)
        
        if (self.cur_bar_id % 10 == 0 and self.cur_bar > 0):
            self.on_bar_10(klines)

        if (lt.tm_min % 30 == 0 and lt.tm_min == 1 and self.cur_bar > 60):
            self.on_bar_30(klines)

    def monitor_key_price(self):
        # 
        pass

    def update_trand_indictor(self):
        self.trade_indicate = 0
        pass

    def update_long_term_indictors(self):
        
        pass

    def update_short_term_indictors(self):
        pass

    def get_lest_inday(self):
        return self

    def get_hh_long_term(self):
        return self.hh_long

    def update_record_daily(self, dklines):
        self.ll_100_daily = pplib.get_lest_in_range(dklines, 1, 100)
        self.hh_100_daily = pplib.get_hest_in_range(dklines, 1, 100)
        self.debug("ll_100_daily=%d hh_100_daily=%d"%(self.ll_100_daily, self.hh_100_daily))

    def on_day_bar(self, dklines):
        self.preparse_dayline_trend(dklines)
        self.generate_day_indicator()

    def get_lastday_quote(self):
        return self.lastday_quote

    def parse(self):
        pass

    def parse_trade(self, klines):
        pass

    def get_high_key_price(self):
        return 0

    def get_low_key_price(self):
        return 0

    def find_bigbang(self, klines):
        #速度
        ck_sum_10 = pplib.get_checksum(klines, 11, 1)
        if (abs(ck_sum_10) > 10):    
            msg = "ck_sum_10=%d"%(ck_sum_10)
            self.info(msg)
        '''
        if (ck_sum_10 > self.max_ck_sum):
            self.max_ck_sum = ck_sum_10
        if (ck_sum_10 < self.min_ck_sum):
            self.min_ck_sum = ck_sum_10
        '''
        # 高度
        # cksum 和 height有重复
        height_10 = pplib.get_height_in_range(klines, 1, 11)
        if (height_10 > 20):
            msg = "height_10=%d"%(height_10)
            self.info(msg)
            self.debug("bigbang")
        
        if (ck_sum_10 > 20 or (height_10> 20 and ck_sum_10>10)):
            self.last_bigbang_up = self.get_current_minute_bar()
        if (ck_sum_10 < -20 or (height_10> 20 and ck_sum_10<-10)):
            self.last_bigbang_down = self.get_current_minute_bar()

    #每天执行一次
    #-10 ~ 10
    # 幅度和数量各站一半
    def preparse_hourline_trend(self, d_klines):
        self.strong_direction = 0
        self.strong_hh = 0
        self.strong_ll = 0
        pass

    def preparse_dayline_trend(self, d_klines):
        back_count  = 6
        red_count = 0
        checksum = 0
        atr = ATR(d_klines, 30)
        self.atr_daily = int(atr.atr.iloc[-1])
        #print(self.TAG, self.atr_daily)  # 平均真实波幅
        for i in range(1, back_count):
            if (d_klines.iloc[-i].open - d_klines.iloc[-i].close > 0):
                red_count = red_count + 1
            checksum = checksum + (d_klines.iloc[-i].close - d_klines.iloc[-i].open)
            
        weight = tafunc.abs(checksum)/atr.atr.iloc[-i]
        print("[%s] parse_dayline_trend checksum=%d weight=%f "%(self.TAG, checksum, weight))
        #if (checksum > 0 and checksum > back_count*atr.atr):
        
        self.day_trend = red_count - (back_count - red_count)
        if (float(weight) > float(0.001) and checksum>0):
            self.day_trend = self.day_trend + weight
        if (float(weight) > float(0.001) and checksum<0):
            self.day_trend = self.day_trend - weight

        # 关键
    
        #range_H = tafunc.hhv(klines.high, 5)
        #range_L = tafunc.llv(klines.low, 5)
        self.Long_HH = pplib.get_hest_in_range(d_klines, 1, 50)
        self.Long_LL = pplib.get_lest_in_range(d_klines, 1, 50)
        self.range_HH, self.hh_day_bar = get_hh_price_bar(d_klines, 5)
        self.range_LL, self.ll_day_bar = get_ll_price_bar(d_klines, 5)
        print("[%s] Long_HH=%d Long_LL=%f "%(self.TAG,self.Long_HH, self.Long_LL))
        # 大小口 配合
        self.support_line = get_support_line(d_klines, 1, 2, 10)
        self.resistance_line = get_resistance_line(d_klines, 1, 2, 10)
        # 敏感价格基于前长周期的波峰波谷，后期被打破或形成支撑阻力
        self.sensitive_hh_bar,self.sensitive_hh = get_sensitive_hh(d_klines, 2)
        self.sensitive_ll_bar,self.sensitive_ll = get_sensitive_ll(d_klines, 2)

        self.debug("support_line=%d resistance_line=%d"%(
            self.support_line,self.resistance_line
            ))

        self.debug("sensitive_hh_bar=%d sensitive_hh=%d sensitive_ll_bar=%d sensitive_ll=%d"%(
            self.sensitive_hh_bar,self.sensitive_hh,
            self.sensitive_ll_bar,self.sensitive_ll
            ))

        if (self.sensitive_hh != 0):
            self.set_indor_value(Indicator.RangeHDaily, self.sensitive_hh)
        if (self.sensitive_ll != 0):
            self.set_indor_value(Indicator.RangeLDaily, self.sensitive_ll)
        # 关键，需手动录入

        '''
        self.key_hh = 
        self.key_ll = 
        '''

        '''
        日线级别的均线值
        '''
        self.ma10 = 0
        self.ma20 = 0

        '''
        预估
        '''
        self.forecast = 0

        for i in range(1, 5):
            self.lastday_quote.append(d_klines.iloc[-i])
            
        self.debug("last_day: open=%d close=%d high=%d low=%d"%(self.lastday_quote[1].open, 
                   self.lastday_quote[1].close, self.lastday_quote[1].high, self.lastday_quote[1].low))

        return self.day_trend

    #综合当下
    def get_trade_indicate(self):
        return self.trade_indicate

    #基于历史
    def get_market_forecast(self):
        return self.forecast

    def get_count_of_nearest_greater_less(self):
        return self.count_of_nearest_greater
        
    def get_count_of_nearest_less(self):
        return self.count_of_nearest_less

    #def get_current_minute_bar(self):
    #    self.cur_bar = tool_utils.get_current_minute_bar_dt(self.cur_bar_time)
    #    return self.cur_bar

    def my_print(self, msg):
        lt = time.localtime(time.time())
        print("[%s] %d-%d %d:%d:%d - :%s"%(self.TAG, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec, msg))

    def get_highest_today(self):
        return self.hest_inday

    def get_highest_bar_today(self):
        return self.hest_bar_inday

    def get_lowest_today(self):
        return self.lest_inday

    def get_lowest_bar_today(self):
        return self.lest_bar_inday

    def get_cur_bar_internal(self):
        return self.cur_bar

    def get_checksum_short_internal(self):
        return self.s_checksum

    def get_ma_short_internal(self):
        if (self.ma10 == 0):
            return self.avg_price
        return self.ma10

    def get_open_price(self):
        return self.open_price
    
    def get_atr_daily(self):
        return self.atr_daily

    def get_avg_overs(self):
        return self.avg_overs

    def get_avg_unders(self):
        return self.avg_unders

    def get_last_avg_crossover(self):
        return self.last_crossover_bar
    
    def get_last_avg_crossdown(self):
        return self.last_crossdown_bar

    def generate_indicator_event(self, klines):
        if (self.cur_bar < 2):
            return
        idor_list = []

        idor_list.append([Indicator.SCheckSum, self.s_checksum])
        idor_list.append([Indicator.CurPrice, self.cur_price])
        idor_list.append([Indicator.CurBar, self.cur_bar])
        #idor_list.append([Indicator.SCheckSum, self.s_checksum])
        idor_list.append([Indicator.LCheckSum, self.l_checksum])
        idor_list.append([Indicator.GreaterContinuousCount, self.overs_of_this]) 
        idor_list.append([Indicator.LessContinuousCount, self.downs_of_this])
        idor_list.append([Indicator.Ups, self.overs_of_this]) # 和GreaterContinuousCount重复
        idor_list.append([Indicator.Downs, self.downs_of_this])

        idor_list.append([Indicator.UndersAvg, self.avg_unders])
        idor_list.append([Indicator.OversAvg, self.avg_overs])
        avg_overs_per = int((self.avg_overs / self.cur_bar)*100)
        avg_unders_per = int((self.avg_unders / self.cur_bar)*100)
        idor_list.append([Indicator.UndersAvgPer, avg_unders_per])
        idor_list.append([Indicator.OversAvgPer, avg_overs_per])
        idor_list.append([Indicator.AvgLine, self.avg_price])

        idor_list.append([Indicator.HestInDay, self.hest_inday])
        idor_list.append([Indicator.LestInDay, self.lest_inday])
        
        idor_list.append([Indicator.CheckSum12, self.csum_12])
        csum6 = pplib.get_checksum(klines, 6, 1)
        idor_list.append([Indicator.CheckSum5, csum6])
        csum12 = pplib.get_checksum(klines, 12, 1)
        idor_list.append([Indicator.CheckSum12, csum12])
        csum15 = pplib.get_checksum(klines, 16, 1)
        idor_list.append([Indicator.CheckSum15, csum15])
        csum45 = pplib.get_checksum(klines, 45, 1)
        idor_list.append([Indicator.LCheckSum, csum45])
        idor_list.append([Indicator.SCheckSum, csum15])

        height_8 = pplib.get_height_in_range(klines, 1, 8)
        idor_list.append([Indicator.RangeHeight8, height_8])
        height_10 = pplib.get_height_in_range(klines, 1, 11)
        idor_list.append([Indicator.RangeHeight10, height_10])
        height_15 = pplib.get_height_in_range(klines, 1, 16)
        idor_list.append([Indicator.RangeHeight15, height_15])
        height_30 = pplib.get_height_in_range(klines, 1, 30)
        idor_list.append([Indicator.RangeHeight30, height_30])
        height_50 = pplib.get_height_in_range(klines, 1, 50)
        idor_list.append([Indicator.RangeHeight50, height_50])

        idor_list.append([Indicator.OpenPrice, self.open_price])
        idor_list.append([Indicator.LestInDay, self.lest_inday])
        idor_list.append([Indicator.HestInDay, self.hest_inday])

        idor_list.append([Indicator.HestBarInDay, self.hest_bar_inday])
        idor_list.append([Indicator.LestBarInDay, self.lest_bar_inday])
    
        for idor in idor_list:
            self.manager.drive_indicator(idor[0], idor[1])

    def generate_indicator_event5(self):
        idor_list = []

        atr_inday = self.get_highest_today() - self.get_lowest_today()
        idor_list.append([Indicator.AtrInday, atr_inday])

        for idor in idor_list:
            self.manager.drive_indicator(idor[0], idor[1])

    def generate_day_indicator(self): 
        idor_list = []

        idor_list.append([Indicator.AtrDaily, self.atr_daily])

        for idor in idor_list:
            self.manager.drive_indicator(idor[0], idor[1])

    def generate_price_action(self):
        height_inday = self.hest_inday - self.lest_inday
        if (height_inday < 2):
            return
        rel_price = self.cur_price - self.lest_inday
        price_pos = int((rel_price / height_inday)*100)
        if (height_inday < 12):
            if (price_pos > 80):
                price_pos = 50
            elif (price_pos < 20):
                price_pos = 50
        self.manager.drive_indicator(Indicator.PricePosition, price_pos)
'''
from tqsdk import TqApi, TqSim,tafunc
api = TqApi()
klines = api.get_kline_serial("SHFE.rb2010", 60, 300)
atr = ATR(klines, 10)
'''