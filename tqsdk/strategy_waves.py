#计算波峰、波谷，
#根据开口数目,梯度定趋势
#三段式，最长不超过三个浪；用ATR设置最高、最低，
#预设脚本、开仓
#相较于killer_tank,它注重于预测
#高度、浪数决定趋势
#m_opens 比 w_opens 多几个说明
'''
1. 排列上涨，横盘
2. 排列上涨，下跌
3. 下跌
'''

from strategy_base  import StrategyBase
import pplib
from datetime import datetime
import time
import tool_utils
from tqsdk.tafunc import time_to_s_timestamp,time_to_str
from param_defines import TradeDirection, StgEvent, Indicator

class StrategyWaves(StrategyBase):
    def __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "StrategyWaves", manager)
        self.TAG = "StrategyWaves"
        self.period = 1 #min
        self.MAX_HOLD = 55
        self.run_flag = True
        self.manager = manager

        self.position = 0
        self.trade_dir = 0

        self.init_flag = False
        self.hh = 0
        self.ll = 0

        self.w_checksum = 0
        self.m_checksum = 0

        self.ups_at_open = 0
        self.downs_at_open = 0

        self.swing_trade_dir = TradeDirection.BUYONLY
        print ("[%s] running....."%(self.TAG))

    def run(self, klines, ask_price, bid_price, quote_avg_price):
        # 前三十分钟过滤
        if (self.run_flag == False):
            return

        lt = time.localtime(time.time())
        if (lt.tm_hour==9 and lt.tm_min<=30):
            return

        if ((lt.tm_min%2==0 and lt.tm_sec==1) == False):
            return
        self.cur_price = ask_price
        self.ask_price = ask_price
        self.bid_price = bid_price
        self.avg_price = quote_avg_price

    def init_data(self, klines):
        self.open_price = pplib.get_open_today(klines, 1)
        self.hh = self.ask_price+self.get_atr_daily()-6
        self.ll = self.ask_price-self.get_atr_daily()+6
        self.init_flag = True
        self.debug("open=%d stg_hh=%d stg_ll=%d"%(self.open_price, self.hh, self.ll))

    def on_bar5(self, klines):
        # greate_hh_ll
        self.generate_hh_ll(klines)

    def on_bar(self, klines):
        if (self.run_flag == False):
            return
        StrategyBase.on_bar(self, klines)
        if (self.skip_open() == True):
            return
        
        if (self.init_flag == False):
            self.init_data(klines)
        lt = self.get_real_time()
        cur_bar = self.get_current_minute_bar()
        self.cur_bar =  cur_bar
        open_inday = klines.iloc[-cur_bar].open
        #print(time_to_str(klines.iloc[-cur_bar].datetime), klines.iloc[-cur_bar].open)
     
        #最近两个高点、低点
        m_opens = pplib.get_M_opens(klines, 20)
        w_opens = pplib.get_W_opens(klines,20)
        
        #高低点 差值
        m_size = 0
        if (m_opens is not None):
            m_size = len(m_opens)
        w_size = 0
        if (w_opens is not None):
            w_size = len(w_opens)

        #bar_id, count_of_nearest_less = pplib.get_count_of_nearest_less(klines, 5, cur_bar)
        #bar_id, count_of_nearest_greater = pplib.get_count_of_nearest_greater(klines, 5, cur_bar)
       
        self.w_size = w_size
        self.m_size = m_size
        self.w_opens = w_opens
        self.m_opens = m_opens
       
        if (lt.tm_min%15==0):
            self.analyze()
        
        if (lt.tm_min%5==0):
            self.on_bar5(klines)

        self.make_trade(klines)

        if (self.position != 0):
            self.monitor_position(klines)

    def make_trade(self, klines):
        #到达低点、高点
        #检测时候bigbang
        #ll_5 = pplib.get_lest_in_range(klines, 1, 11)
        #hh_5 = pplib.get_lest_in_range(klines, 1, 11)
        if (self.hh - self.ll < 20):
            self.debug("range too small, hh=%d ll=%d"%(self.hh, self.ll))
            if (self.manager.get_market_prediction() > 20):
                self.hh += 25
                self.ll -= 20
            elif (self.manager.get_market_prediction() < -20):
                self.hh += 20
                self.ll -= 25
            else:
                self.hh += 25
                self.ll -= 25

        if (self.position <= 0 and self.ask_price <= self.ll):
            self.debug("arrive ll, hh=%d ll=%d"%(self.hh, self.ll))
            self.set_position(1)
            # 急
            # 缓
        elif (self.position >= 0 and self.ask_price >= self.hh):
            self.debug("arrive ll, hh=%d ll=%d"%(self.hh, self.ll))
            self.set_position(-1)
    
    def monitor_position(self, klines):
        #平仓
        #时间过长
        if (self.position != 0 and self.get_bars_since_entry() >= self.MAX_HOLD):
            s_checksum = pplib.get_checksum(klines, 20, 1) # short
            if (self.position > 0 and abs(s_checksum) < 2):
                self.set_position(0)
                self.debug("持多时间过长")
            if (self.position < 0 and abs(s_checksum) < 2):
                self.set_position(0)
                self.debug("持空时间过长")          
    '''
    def top_open(self, klines, to_left):
        tmp_position = 0
        MIN_DIFF = 20
        if (self.m_size > 0):
            hh_6,hh_bar = pplib.get_hest_in_range2(klines, 1, 7)
            ll_today,ll_today_bar = pplib.get_lowest_bar_today2(klines)
            m_price = self.m_opens.loc[0].close
            if (self.m_size > 1):
                cur_id = klines.iloc[-1].id
                for i in range (1, self.m_size):
                    if (self.m_opens.iloc[-i].id - cur_id > to_left
                        and self.m_opens.iloc[-i].id - ll_today_bar > MIN_DIFF):
                        m_price = self.m_opens.iloc[-i].high
            print("w_price=", m_price)
            dif =  m_price - ll_today  
            adjust = 0
            if (dif < MIN_DIFF*1.5):
                adjust = -3
            elif  (dif < MIN_DIFF*2):
                adjust = -5
            if (hh_6 - m_price >= adjust and self.position != -1):
                s_checksum = pplib.get_checksum(klines, 5, 1)
                self.debug("top arrive m_price=%d adjust=%d"%(m_price, adjust))
                if (abs(s_checksum) <= 2):
                    tmp_position = -1
                    self.debug("top open m_price=%d adjust=%d"%(m_price, adjust))

        return tmp_position

    def bottom_open(self, klines, to_left):
        tmp_position = 0
        MIN_DIFF = 20
        if (self.w_size > 0):
            ll_6,ll_bar = pplib.get_lest_in_range2(klines, 1, 7)
            hh_today = pplib.get_highest_price_today(klines, 60)
            w_price = self.w_opens.loc[0].close
            if (self.w_size > 1):
                cur_id = klines.iloc[-1].id
                for i in range (1, self.w_size):
                    if (self.w_opens.iloc[-i].id - cur_id > to_left
                        and hh_today - self.w_opens.iloc[-i].id > MIN_DIFF):
                        w_price = self.w_opens.iloc[-i].low
            print("w_price=", w_price)
            dif =  hh_today  - w_price
            adjust = 0
            if (dif < MIN_DIFF*1.5):
                adjust = 3
            elif  (dif < MIN_DIFF*2):
                adjust = 5
            if (ll_6 - w_price <= adjust and self.position != 1):
                s_checksum = pplib.get_checksum(klines, 5, 1)
                if (abs(s_checksum) <= 2):
                    tmp_position = 1
                    self.debug("bottom open w_price=%d adjust=%d"%(w_price, adjust))

        return tmp_position
    '''
    def timer_task(self):
        pass


    #设置预演脚本，
    def set_script(self, id):
        pass

    def run_script(self, id):
        pass

    def collect_indictors(self, klines):
        #self.max_ = 
        pass

    def generate_hh_ll(self, klines):
        #开仓
        #排列
        swing_hh = self.hh
        swing_ll = self.ll
        hh_msg = "change swing_hh "
        ll_msg = "change swing_ll"
        if (self.m_size>0 and self.w_size>0):
            m_ret = self.check_open_queue("m_opens", self.m_opens)
            w_ret = self.check_open_queue("w_opens", self.w_opens)
            #swing_hh = self.m_opens.loc[0].high + 40
            #swing_ll = self.w_opens.loc[0].low - 40
            if (m_ret == 1 and w_ret == 1):
                #几浪
                if(self.m_size > 3):
                    swing_hh = self.m_opens.loc[0].high + 2
                    swing_ll = swing_hh - 30
                elif(self.m_size > 2):
                    swing_hh = self.m_opens.loc[0].high + 10
                    swing_ll = pplib.get_lest_in_range(klines, 1, 51)
                elif(self.m_size > 1):
                    swing_hh = self.m_opens.loc[0].high + 20
                    swing_ll = pplib.get_lest_in_range(klines, 1, 31)
                else:
                    swing_hh = self.m_opens.loc[0].high + 38
                    swing_ll = pplib.get_lest_in_range(klines, 1, 21)
                hh_msg = "排列多"
                ll_msg = "排列多"
            elif (m_ret == -1 and w_ret == -1):
                #几浪
                if(self.w_size > 3):
                    swing_ll = self.m_opens.loc[0].low - 2
                    swing_hh = swing_ll + 30
                elif(self.w_size > 2):
                    swing_ll = self.m_opens.loc[0].low - 10
                    swing_hh = pplib.get_hest_in_range(klines, 1, 51)
                elif(self.w_size > 1):
                    swing_ll = self.m_opens.loc[0].low - 20
                    swing_hh = pplib.get_hest_in_range(klines, 1, 31)
                else:
                    swing_ll = self.m_opens.loc[0].low - 38
                    swing_hh = pplib.get_hest_in_range(klines, 1, 21)
                hh_msg = "排列空"
                ll_msg = "排列空"
            else:
                #未突破
                hh_msg = "找swing_high"
                ll_msg = "找swing_low"
                range_heigh_8 = pplib.get_height_in_range(klines, 1, 8)
                l_cksum = pplib.get_checksum(klines, 10, 1)
                avg_price = pplib.get_average(klines, 6)
                if (self.w_opens.loc[0].lcount>60):
                    #突破
                    '''
                    swing_hh = self.w_opens.loc[0].close + 20
                    if(self.w_size > 2):
                        swing_ll = self.w_opens.loc[0].low-15
                    if (self.w_size >= 1):
                        swing_ll = self.w_opens.loc[0].low-25
                    '''
                    if (abs(avg_price-self.w_opens.loc[0].low)<3
                        and range_heigh_8<15 and l_cksum<0 and l_cksum > -15):
                        swing_ll = avg_price
                        ll_msg = "在上一个swing_low附近形成震荡"
                    #突破
                    else:
                        #偏空
                        if(self.w_size > 2):
                            swing_ll = self.w_opens.loc[0].low-8
                            ll_msg = "w_size>2 and ll=swing_low - 8"
                        if (self.w_size >= 1):
                            swing_ll = self.w_opens.loc[0].low-15
                            ll_msg = "w_size>2 and ll=swing_low - 15"
                        if (self.get_kpi_daily() > 10):
                            swing_ll += int(self.get_kpi_daily()/10)+1
                            ll_msg += "调整%d"%(int(self.get_kpi_daily()/10)+1)
                elif (self.w_opens.loc[0].lcount < 30 and self.w_opens.loc[0].lcount > 60):
                    if (avg_price < self.w_opens.loc[0].close - 8):
                        swing_hh = self.w_opens.loc[0].close
                        swing_ll = self.w_opens.loc[0].close- 28
                        ll_msg = "swing_low 大小桥 ll下移21"
                        hh_msg = "swing_low 大小桥 low变high 阻变支"
                    else:
                        swing_ll = self.w_opens.loc[0].close
                        ll_msg = "swing_low 大小桥 使用swing_low"
                    #突破跟进

                #突破
            if (self.m_opens.loc[0].lcount>60):
                    #突破
                    '''
                    swing_hh = self.w_opens.loc[0].close + 20
                    if(self.w_size > 2):
                        swing_ll = self.w_opens.loc[0].low-15
                    if (self.w_size >= 1):
                        swing_ll = self.w_opens.loc[0].low-25
                    '''
                    if (abs(avg_price-self.m_opens.loc[0].high)<3
                        and range_heigh_8 <15 and l_cksum>0 and l_cksum < 15):
                        swing_hh = avg_price
                        hh_msg = "swing_high 使用swing_high附件avg_price"
                    #突破
                    else:
                        #偏空
                        if(self.m_size > 2):
                            swing_hh = self.m_opens.loc[0].high+8
                            hh_msg = "m_size > 2 swing_high0+8"
                        if (self.m_size >= 1):
                            swing_hh = self.m_opens.loc[0].high+15
                            hh_msg = "m_size >= 1 swing_high0+15"
                        if (self.get_kpi_daily() < -10):
                            swing_hh += int(self.get_kpi_daily()/10)+1
                            hh_msg += "调整%d"%(int(self.get_kpi_daily()/10)+1)
            elif (self.m_opens.loc[0].lcount < 30 and self.m_opens.loc[0].lcount > 60):
                    if (avg_price > self.m_opens.loc[0].close + 5):
                        swing_ll = self.m_opens.loc[0].close-5
                        swing_hh = self.m_opens.loc[0].close + 25
                        hh_msg = "swing_high 上移21"
                        ll_msg = "swing_high0-5 变ll"
                    else:
                        swing_hh = self.m_opens.loc[0].high
                        hh_msg = "大小乔 使用swing_high"
        #
        elif (self.m_size > 0):
            #强升
            m_ret = self.check_open_queue("m_opens", self.m_opens)
            if (m_ret==1 and self.cur_bar<110 and self.get_kpi_daily() > 30):
                ll_10 = pplib.get_lest_in_range(klines, 1, 11)
                swing_ll = ll_10
                ll_msg = "强升，ll=ll_10"
            
        elif (self.w_size > 0):
            #强降
            m_ret = self.check_open_queue("w_opens", self.m_opens)
            if (m_ret==-1 and self.cur_bar<110 and self.get_kpi_daily() < -30):
                hh_10 = pplib.get_hest_in_range(klines, 1, 11)
                swing_hh = hh_10
                hh_msg = "强降，hh=hh_10"
        elif (self.cur_bar > 50):
            avg_price = pplib.get_average(klines, 5)
            open_p = self.get_open_price()
            if (avg_price > open_p):
                swing_ll = pplib.get_lest_in_range(klines, 1, 11)
                ll_msg = "流畅上升，ll=ll_10"
            elif (open_p > avg_price):
                swing_hh = pplib.get_hest_in_range(klines, 1, 11)
                hh_msg = "流畅下降，hh=hh_10"
        elif (self.cur_bar < 50):
            ups = pplib.get_count_of_greater(klines, self.cur_bar)
            downs = pplib.get_count_of_less(klines, self.cur_bar)
            if (ups > self.ups_at_open):
                self.ups_at_open = ups
            if (downs > self.downs_at_open):
                self.downs_at_open = downs
            if(self.cur_bar>25 and self.downs_at_open<10):
                avg_price = pplib.get_average(klines, 9)
                ll_msg = "未形成swing前强升，ll=lavg9"
                swing_ll = avg_price
            if(self.cur_bar>25 and self.downs_at_open<10):
                avg_price = pplib.get_average(klines, 9)
                hh_msg = "未形成swing前强降，hh=avg9"
                swing_hh = avg_price
        if(self.hh == 0):
            swing_hh = self.get_open_price + self.get_atr_daily()
            hh_msg = "hh=0, hh=open+atr"
        elif(self.hh < self.ask_price - 10):
            #突破
            avg_price = pplib.get_average(klines, 15)
            if (avg_price > self.hh+5):
                swing_ll = self.hh
                swing_hh = self.ask_price + 25
                hh_msg = "逃出区间, hh=cur_price+25"
                ll_msg = "逃出区间, ll = last_hh"
        
        if(self.ll == 0):
            swing_ll = self.get_open_price - self.get_atr_daily()
            ll_msg = "ll = 0, ll=open-atr"
        elif(self.ll > self.ask_price + 10):
            avg_price = pplib.get_average(klines, 15)
            if (avg_price < self.ll-5):
                swing_hh = self.ll
                swing_ll = self.ask_price - 23
                hh_msg = "逃出区间, hh=swing+25"
                ll_msg = "逃出区间, ll = cur_price-23"

        if (swing_hh != self.hh):
            self.change_hh(swing_hh, hh_msg)
        if (swing_ll != self.ll):
            self.change_ll(swing_ll, ll_msg)

    def check_w(self):

        pass

    def change_hh(self, swing_hh, msg):
        self.hh = swing_hh
        self.info("new hh=%d msg=%s"%(self.hh, msg))
    def change_ll(self, swing_ll, msg):
        #if (self.position < 0):
        self.info("new ll=%d msg=%s"%(self.ll, msg))
        self.ll = swing_ll
        pass

    def analyze(self):
        w_size = self.w_size
        m_size = self.m_size
        #===========checksum================
        w_checksum = 0
        m_checksum = 0
        if (w_size > 0):
            w_opens = self.w_opens
            i = 1
            open_inday = self.get_open_price()
            if (w_size >= 2):
                for i in range(0, w_size-1):
                    w_checksum +=  w_opens.loc[i].low- w_opens.loc[i+1].low
            w_checksum += w_opens.loc[w_size-1].low - open_inday # 错误
            if (w_size >= 2):
                avg_swing_low = (w_opens.loc[i].low + w_opens.loc[i+1].low)/2
                self.info("avg_swing_low=%d"%(avg_swing_low))
            last_swing_low = w_opens.loc[0].low
            swing_lowest = last_swing_low
            for i in range(0, w_size):
                if (w_opens.loc[i].low < swing_lowest):
                    swing_lowest = w_opens.loc[i].low

        if (m_size > 0):
            i = 1
            m_opens = self.m_opens
            open_inday = self.get_open_price()
            if (m_size > 0):
                for i in range(0, m_size-1):
                    m_checksum += m_opens.loc[i].high-m_opens.loc[i+1].high
            m_checksum += m_opens.loc[m_size-1].high - open_inday
            #m_checksum += m_opens.loc[m_size-1].high
            if (m_size >= 2):
                avg_swing_high = (m_opens.loc[i].high + m_opens.loc[i+1].high)/2
                self.info("avg_swing_high=%d"%(avg_swing_high))
            last_swing_high = m_opens.loc[0].high
            swing_highest = last_swing_high
            #print("[%s] m_opens 以下:"%(self.TAG))
            #print (m_opens)
            for i in range(0, m_size):
                if (m_opens.loc[i].high > swing_highest):
                    swing_highest = m_opens.loc[i].high

        self.w_checksum = w_checksum
        self.m_checksum = m_checksum
        #=============print===============================
        if (self.w_size > 0 or self.m_size > 0):
                self.debug("==========================================")
        if (self.w_size > 0):
            self.debug("w_opens:")
                #print(w_opens)
            self.print_opens("w_open",self.w_opens)
        if (self.m_size > 0):
            self.debug("m_opens:")
            #print(m_opens)
            self.print_opens("m_open",self. m_opens)
        if (self.w_size > 0 or self.m_size > 0):
            self.debug("==========================================")
        #if (self.w_size > 0):

        #出现顶、和底，选择最近的两个W、M
        #底不是最底，顶不是最顶

        #出现窄幅波动区间时

        #开仓及区间突破后

    def opens_min(self, name_str, df):
        pass

    def opens_max(self, name_str, df):
        pass

    def check_open_queue(self, open_name, o_df):
        o_size = len(o_df)
        flag = True
        if (open_name == "w_open" and o_size > 0): 
            
            if (o_size == 1):
                open_p = self.get_open_price()
                dif = open_p - self.w_opens.loc[0].low 
                if (dif > 18):
                    return -1
                elif(dif < 8):
                    return 1
                else:
                    return 0
            
            for i in range(0, o_size-1):
                if (o_df.loc[i].low >= o_df.loc[i+1].low):
                    flag = False
                    break
            if (flag == True):
                return -1
            flag = True
            for i in range(0, o_size-1):
                if (o_df.loc[i].low <= o_df.loc[i+1].low):
                    flag = False
                    break
            if (flag == True):
                return -1
            else:
                return 0
        elif (open_name == "m_open" and o_size > 0): 
            
            if (o_size == 1):
                open_p = self.get_open_price()
                dif = self.m_opens.loc[0].high - open_p
                if (dif > 18):
                    return 1
                elif(dif < 10):
                    return -1
                else:
                    return 0
            for i in range(0, o_size-1):
                if (o_df.loc[i].high >= o_df.loc[i+1].high):
                    flag = False
                    break
            if (flag == True):
                return -1
            flag = True
            for i in range(0, o_size-1):
                if (o_df.loc[i].high <= o_df.loc[i+1].high):
                    flag = False
                    break
            if (flag == True):
                return -1
            else:
                return 0

        return 0

    def print_opens(self, str_name, o_df):
        o_size = len(o_df)
        if (str_name == "w_open" and o_size>0):
            print ('%-5s%-10s%-10s%-10s%-10s%-10s' %("id","lcount","rcount", "close", "low", "datetime"))
            for i in range(0, o_size):
                #print(i, o_df.iloc[-i].lcount, o_df.iloc[-i].rcount, o_df.iloc[-i].close, o_df.iloc[-i].low, time_to_str(o_df.iloc[-i].time))
                print('%-5s%-10s%-10s%-10s%-10s%-10s' %(i, o_df.loc[i].lcount, o_df.loc[i].rcount, o_df.loc[i].close, o_df.loc[i].low, time_to_str(o_df.loc[i].time)))
        if (str_name == "m_open" and o_size>0):
            print ('%-5s%-10s%-10s%-10s%-10s%-10s' %("id", "lcount","rcount", "close", "high", "datetime"))
            for i in range(0, o_size):
                print('%-5s%-10s%-10s%-10s%-10s%-10s' %(i,o_df.loc[i].lcount, o_df.loc[i].rcount, o_df.loc[i].close, o_df.loc[i].high, time_to_str(o_df.loc[i].time)))

        print("hh=%d, ll=%d"%(self.hh, self.ll))
        print("w_check=%d, m_check=%d"%(self.w_checksum, self.m_checksum))

    def skip_open(self):
        lt = self.get_real_time()
        if ((lt.tm_hour == 21 and lt.tm_min < 30)
            or (lt.tm_hour == 9 and lt.tm_min <30)):
            return True
        else:
            return False

    def parse(self):
        '''
        开口数量分析强势方向
        反方向打破强势，并不一定说明要反方向做
        '''
        pass

    def on_event(self, event_name, e_param):
        if (event_name == StgEvent.DownTrendBreak):
            self.set_trade_direction(TradeDirection.BUYSELL)
        elif (event_name == StgEvent.UpTrendBreak):
            self.set_trade_direction(TradeDirection.BUYSELL)

    def generate_indor(self):
        self.set_indor_value(Indicator.RangeHInDay, self.hh)
        self.set_indor_value(Indicator.RangeLInDay, self.ll)
        self.set_indor_value(Indicator.MOpens, self.m_size)
        self.set_indor_value(Indicator.WOpens, self.w_size)