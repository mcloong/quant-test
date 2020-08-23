#类似killer rusher
# 短平快
# 追涨、杀跌
# 横盘时预埋
#参考长线趋势和短方向

#横盘预埋、突破跟进
# trend > 35，avg以下横盘
# trend > 35, 突破

#后半场不受kpi_daily约束

#计划：
# 寻找lowrange 20200817

from param_defines import TradeDirection
from pplib import get_avg_price ,get_checksum
from datetime import datetime
import time
from param_defines import StrategyKpi,WalkPath,RecordEvent,Indicator
from strategy_base import StrategyBase
import pplib
from event_recorder import EventRecorder
from kindictor import KIndictorRecorder
#
class KillerNinja(StrategyBase):
    def  __init__(self, symbol, manager):
        StrategyBase.__init__(self, symbol, "KillerNinja", manager)
        self.TAG = "KillerNinja"
        self.MAX_EARN = 25
        self.MAX_TRADE_TERM =20 #最长交易时间
        self.BREAK_PROFIT2 = 25
        self.BREAK_PROFIT2 = 20
        self.BREAK_PROFIT1 = 13
        self.RUSH_PROFIT = 15
        self.trade_dir = TradeDirection.BUYSELL

        self.hh = 0
        self.ll = 0
        self.event_recorder = EventRecorder("NinjaRecorder") #记录传入的event
        self.idor_record = KIndictorRecorder("idor_rd") #内部记录

        self.last_greaters = 0
        self.last_greaters_mark_bar = 0
        self.last_lesses = 0
        self.last_lesses_mark_bar = 0
        self.greaters = 0
        self.lesses = 0

        self.step = 0
        self.make_type = 0 # 1 overs and downs; 2 break flow; 3 break opposite; 4 open
        print("........[%s] running..........."%(self.TAG))

    def set_hh(self, hh):
        self.hh = hh

    def set_ll(self, ll):
        self.ll = ll

    def on_day_bar(self, klines):
        #3 day
        pass

    def on_bar(self, klines):
        StrategyBase.on_bar(self, klines)
        #if (self.run_flag == False or self.hh <= 0 or self.ll <= 0):
        self.generate_indicator(klines)

        if (self.run_flag == False):
            return
        if (self.cur_bar < 10):
            return

        height8 = pplib.get_height_in_range(klines, 1, 10)
        cksum = pplib.get_checksum(klines, 10, 1)

        l_height = pplib.get_height_in_range(klines, 1, 30)
        l_cksum = pplib.get_checksum(klines, 30, 1)

        pre_height8 = pplib.get_height_in_range(klines, 4, 4+8)

        overs = self.get_avg_overs()
        unders = self.get_avg_unders()
        greaters = pplib.get_count_of_greater(klines, self.cur_bar)
        lesses = pplib.get_count_of_less(klines, self.cur_bar)
        self.greaters = greaters
        self.lesses = lesses

        if (height8 < 15 and abs(cksum) < 3):
            self.debug("height8=%d cksum=%d"%(height8, cksum))
        if (l_height< 20 and abs(l_cksum) < 5):
            self.debug("l_height=%d l_cksum=%d"%(l_height, l_cksum))
        '''
        if (greaters > 30):
            self.last_greaters = overs
        else:
            if (self.last_greaters > 60):
                self.last_lesses = lesses
                if (self.last)
                self.add_event()

        if (downs > 30):
            self.last_downs = downs
        else:
            if (self.last_downs>60 and overs > 5):
                self.last_downs = 
        
        if (overs > 2 and self.last_downs > 30):
            pass
        if (downs > 2 and self.last_overs > 30):
            pass
        '''

        lt = self.get_real_time()
        tmp_position = self.position
        
        #===============make==================#
        #一、根据均线上线
        if (self.ask_price<self.avg_price and self.position <= 0):
            kpi_daily = self.get_kpi_daily()
            cond = False
            if (unders > 15 and overs/unders > 1.3):
                cond = True
            if (kpi_daily > 10):
                cond = True
            else:
                cond = False

            if (abs(cksum) < 4 and self.avg_price-self.ask_price<20):
                if (cond == True):
                    self.debug("under avg open......")
                    tmp_position = 1
                    self.make_type = 1
                    self.hh = self.ask_price + self.RUSH_PROFIT
                elif(self.position<0):
                    tmp_position = 0 #有漏洞
        elif (self.ask_price > self.avg_price and self.position >=0):
            kpi_daily = self.get_kpi_daily()
            cond = False
            if (unders > 15 and overs/unders > 1.3):
                cond = True
            if (kpi_daily < -10):
                cond = True
            else:
                cond = False

            if (abs(cksum) < 4 and self.ask_price-self.avg_price<20):
                if (cond == True):
                    self.debug("over avg open......")
                    tmp_position = -1
                    self.make_type = 1
                    self.ll = self.ask_price - self.RUSH_PROFIT
                elif(self.position>0):
                    tmp_position = 0 #有漏洞

        #二、根据突破
        last_cru_avg = self.get_last_avg_crossdown()
        last_cro_avg = self.get_last_avg_crossover()
        kpi_daily = self.get_kpi_daily()
        if (((last_cro_avg > 38 and last_cro_avg<last_cru_avg) 
            or(kpi_daily > 35 and greaters > 120))
            and self.position <=0):
            if (self.last_greaters > 60 and greaters > 4 and self.cur_bar_id - self.last_greaters_mark_bar < 30):
                
                my_kpi = self.get_kpi_myself()
                dist = self.cur_bar_id - self.last_greaters_mark_bar
                #短 连续
                if (kpi_daily > 35 and greaters>self.last_greaters and dist>3 and dist<10):
                    self.hh = self.ask_price + self.BREAK_PROFIT2
                    tmp_position = 1
                    self.make_type = 2
                    self.debug("连续。。。。")
                if (tmp_position != 1 and kpi_daily>30 and dist>15):
                    height12 = 100
                    rang = self.cur_bar_id - self.last_greaters_mark_bar
                    if (rang > 2):
                        height12 = pplib.get_height_in_range(klines, 1, 15)
                    if (height12<14 and abs(cksum)<3):
                        self.hh = self.ask_price + self.BREAK_PROFIT1
                        tmp_position = 1
                        self.make_type = 2
                        self.debug("横盘 等待 break...")
                if (tmp_position != 1 and self.last_greaters > 240):
                    if (greaters > self.last_greaters and greaters > 5 and greaters < 30):
                        tmp_position = 1
                        self.make_type = 2
                        self.debug("长突破。。")
                        
        if (((last_cro_avg > 38 and last_cro_avg<last_cru_avg) #条件1
            or (kpi_daily<-35 and lesses > 120))
            and self.position >=0):
            if (self.last_lesses > 60 and lesses > 4 and self.cur_bar_id - self.last_lesses_mark_bar < 30):
                
                my_kpi = self.get_kpi_myself()
                dist = self.cur_bar_id - self.last_lesses_mark_bar
                #短 连续
                if (kpi_daily < -35 and lesses>self.last_lesses and dist>3 and dist<10):
                    self.ll = self.ask_price - self.BREAK_PROFIT2
                    tmp_position = -1
                    self.make_type = 2
                    self.debug("连续。。。。")
                if (tmp_position != 1 and kpi_daily>30 and dist>15):
                    height12 = 100
                    rang = self.cur_bar_id - self.last_greaters_mark_bar
                    if (rang > 2):
                        height12 = pplib.get_height_in_range(klines, 1, 15)
                    if (height12<14 and abs(cksum)<3):
                        self.ll = self.ask_price - self.BREAK_PROFIT1
                        tmp_position = -1
                        self.make_type = 2
                        self.debug("横盘 等待 break...")
                if (tmp_position != 1 and self.last_lesses > 240):
                    if (lesses > self.last_greaters and greaters > 5 and greaters < 30):
                        tmp_position = -1
                        self.make_type = 2
                        self.debug("长突破。。")
                        self.ll = self.ask_price - self.BREAK_PROFIT1
                
                #长 高度小

        #三、出现长横盘

        #四、开盘来一发
        if (self.cur_bar < 30):
            if (kpi_daily > 35 and self.position <=0):
                open_p = self.get_open_price()

                if (open_p-self.ask_price >= 10):
                    tmp_position = 1
                    self.make_type = 4
                    self.debug("开盘  enter.....")
                    self.hh = self.ask_price+self.RUSH_PROFIT
                elif (self.cur_bar>10 and lesses > 9):
                    tmp_position = 1
                    self.make_type = 4
                    self.debug("开盘  超时enter.....")
                    self.hh = self.ask_price+self.RUSH_PROFIT
            if (kpi_daily < -35 and self.position >=0):
                open_p = self.get_open_price()

                if (self.ask_price- open_p>= 10):
                    tmp_position = -1
                    self.make_type = 4
                    self.ll = self.ask_price - self.RUSH_PROFIT
                    self.debug("开盘  enter.....")
                elif (self.cur_bar>10 and lesses > 9):
                    tmp_position = -1
                    self.make_type = 4
                    self.ll = self.ask_price - self.RUSH_PROFIT
                    self.debug("开盘  超时enter.....")
        #==================exit===========================#
        if (self.position > 0 and self.ask_price>=self.hh):
            tmp_position = 0
            self.debug("arrive hh")
        if (self.position < 0 and self.ask_price<=self.ll):
            tmp_position = 0
            self.debug("arrive ll")

        if (self.position == 1):
            if (self.cur_bar - self.entry_bar > 5 and self.bid_price-self.entry_price >= self.MAX_EARN):
                tmp_position = 0
        if (self.position == -1):
            if (self.cur_bar - self.entry_bar > 5 and self.entry_price-self.bid_price >= self.MAX_EARN):# 达到最大profit
                tmp_position = 0
        
        if (self.position !=0 and self.make_type == 0):
            self.monitor_position(klines, 30)
        elif (self.position !=0 and self.make_type == 1):
            self.monitor_position(klines, 40)
        elif (self.position !=0 and self.make_type == 2):
            self.monitor_position(klines, 50)
        elif (self.position !=0 and self.make_type == 2):
            self.monitor_position(klines, 30)
        
        #===============================================#
        #更新放后
        if (self.last_greaters>40):
            if (greaters == 0):
                self.add_event(RecordEvent.Up, self.last_greaters, self.cur_bar_id, self.cur_bar_time)
            if (self.cur_bar_id - self.last_greaters_mark_bar < 20 and lesses >5):
                self.add_event(RecordEvent.DownAfterUp, lesses, self.cur_bar_id, self.cur_bar_time)
        if (self.last_lesses>40):
            if (lesses == 0):
                self.add_event(RecordEvent.Down, self.last_lesses, self.cur_bar_id, self.cur_bar_time)
            if (self.cur_bar_id - self.last_lesses_mark_bar < 20 and greaters > 5):
                self.add_event(RecordEvent.UpAfterDown, greaters, self.cur_bar_id, self.cur_bar_time)

        if (greaters > 30):
            self.last_greaters = greaters
            if (greaters > 60):
                self.last_greaters_mark_bar = self.cur_bar_id

        if (lesses > 30):
            self.last_lesses = lesses
            if (lesses > 60):
                self.last_lesses_mark_bar = self.cur_bar_id

        #===================================#
        if (tmp_position != self.position):
            if (self.check_order(5)):
                self.set_position(tmp_position)
            else:
                self.debug("间隔检测 false")

    def monitor_position(self,klines, bars):
        if (self.cur_bar - self.entry_bar > bars):
            sum_range = 8
            std_count = 7
            if (bars > 20):
                sum_range = 11
                std_count = 14
            else:
                sum_range = 8
            cksum = pplib.get_checksum(klines, 1, sum_range)
            
            if (self.position > 0 and self.greaters>std_count and abs(cksum)<4):
                self.set_position(0)
            if (self.position < 0 and self.lesses>std_count and abs(cksum)<4):
                self.set_position(0)

        ##################################
        #盈利快出
        #损失快出

    def add_event(self, name, value, bid, dt):
        self.event_recorder.add(name, value, self.TAG, bid, dt)
        pass

    def timer_task(self):
        pass

    def breakup_mode(self):
        pass

    def get_kpi_myself(self):
        overs = self.get_avg_overs()
        unders = self.get_avg_unders()
        my_kpi = 0
        if (self.cur_bar < 90):
            #kpi_daily = self.get_kpi_daily()
            dif = overs - unders
            if (abs(dif) > 50):
                my_kpi = 80
            elif (abs(dif) > 30):
                my_kpi = 60
            elif (abs(dif) > 10):
                my_kpi = 20
            else:
                my_kpi = 10
            if (dif < 0):
                my_kpi = -my_kpi
        elif (self.cur_bar >= 90):
            last_cru_avg = self.get_last_avg_crossdown()
            last_cro_avg = self.get_last_avg_crossover()

            if (last_cro_avg < last_cru_avg):
                if (last_cro_avg > 240):
                    my_kpi = 10
                if (last_cro_avg >160):
                    my_kpi = 20
                if (last_cro_avg >120):
                    my_kpi = 80
                elif (last_cro_avg > 30):
                    my_kpi = 10
                else:
                    my_kpi = 5

            if (last_cru_avg < last_cro_avg):
                if (last_cru_avg > 240):
                    my_kpi = -10
                if (last_cru_avg >160):
                    my_kpi = -20
                if (last_cru_avg >120):
                    my_kpi = -80
                elif (last_cru_avg > 30):
                    my_kpi = 10
                else:
                    my_kpi = -5
        
        return my_kpi

    def find_pattern(self, klines):
        #find break failed or success 
        if (self.cur_bar < 60):
           return
        
        up_idx = self.find_event(RecordEvent.Up, 1)
        down_idx = self.find_event(RecordEvent.Down, 1)
        if (up_idx>down_idx and down_idx!=-1):
            self.find_up_mode(klines)
        elif (down_idx<up_idx and up_idx!=-1):
            self.find_down_mode(klines)
    
    #strong_up_mode and rushup_and_down
    def find_up_mode(self, klines):
        mode_type = 0
        up_idx1 = self.find_event(RecordEvent.Up, 1)
        up_idx2 = self.find_event(RecordEvent.Up, 2)
        up_down_idx1 = self.find_event(RecordEvent.DownAfterUp, 1)
        down_idx1 = self.find_event(RecordEvent.Down, 1)
        sr_event1 = self.get_event_iloc(up_idx1)
        ups1 = int(sr_event1.param)
        sr_event2 = self.get_event_iloc(up_idx2)
        ups2 = int(sr_event2.param)
        sr_event3 = self.get_event_iloc(down_idx1)
        downs = int(sr_event3.param)
        if (ups1>110 and ups2>110 and up_idx1-up_idx2<20):
            #if (up_down_idx1 > ):
            self.debug("strong_up_mode")
            mode_type = 2
            
        if (ups2>110 and ups2>10 and up_idx1-up_idx2<50):
            start_bar = self.cur_bar_id - up_idx1
            end_bar = self.cur_bar_id - up_idx2
            range_height = pplib.get_height_in_range(klines, start_bar, end_bar)
            if (range_height < 15):
                self.debug("strong_up_mode")
                mode_type = 2
            else:
                self.debug("rushup_and_down_mode")
                mode_type = -1
        elif (ups1>110 and downs>30 and up_idx1<down_idx1):
            start_bar = self.cur_bar_id - up_idx1
            end_bar = self.cur_bar_id - up_idx2
            range_height = pplib.get_height_in_range(klines, start_bar, end_bar)
            if (range_height > 20):
                self.debug("rushup_and_down")
                mode_type = -1

    #strong_up_mode and rushup_and_down
    def find_down_mode(self, klines):
        mode_type = 0
        down_idx1 = self.find_event(RecordEvent.Down, 1)
        down_idx2 = self.find_event(RecordEvent.Down, 2)
        down_up_idx1 = self.find_event(RecordEvent.UpAfterDown, 1)
        up_idx1 = self.find_event(RecordEvent.Up, 1)
        sr_event1 = self.get_event_iloc(down_idx1)
        down1 = int(sr_event1.param)
        sr_event2 = self.get_event_iloc(down_idx2)
        down2 = int(sr_event2.param)
        sr_event3 = self.get_event_iloc(up_idx1)
        ups = int(sr_event3.param)
        if (down1>110 and down2>110 and down_idx1-down_idx2<20):
            #if (up_down_idx1 > ):
            self.debug("strong_down_mode")
            mode_type = -2
            
        if (down1>110 and down2>10 and down_idx1-down_idx2<50):
            start_bar = self.cur_bar_id - down_idx1
            end_bar = self.cur_bar_id - down_idx2
            range_height = pplib.get_height_in_range(klines, start_bar, end_bar)
            if (range_height < 15):
                self.debug("strong_down_mode")
                mode_type = -2
            else:
                self.debug("rushup_and_down_mode")
                mode_type = 1
        elif (down1>110 and ups>30 and up_idx1>down_idx1):
            start_bar = self.cur_bar_id - down_idx1
            end_bar = self.cur_bar_id - down_idx2
            range_height = pplib.get_height_in_range(klines, start_bar, end_bar)
            if (range_height > 20):
                self.debug("rushdown_and_up")
                mode_type = 1

    def find_event(self, event, idx):
        return self.event_recorder.find_event(event, idx)

    def get_event_iloc(self, idx):
        return self.event_recorder.get_event_iloc(idx)

    def generate_indicator(self, klines):
        RANGE = 10
        LENGTH = 60
        if (self.cur_bar < RANGE):
            return
        if (self.cur_bar < LENGTH):
           LENGTH = self.cur_bar

        swinghighs = pplib.SwingHighPriceSeries(klines, RANGE, 1, LENGTH)
        swinglows = pplib.SwingHighPriceSeries(klines, RANGE, 1, LENGTH)

        swing_h_bar = 0
        swing_l_bar = 0
        if (len(swinghighs) > 0):
            swing_h = swinghighs[0]['price']
            swing_h_bar = swinghighs[0]['bar']
        else:
            swing_h = self.cur_bar
        if (len(swinglows) > 0):
            swing_l = swinglows[0]['price']
            swing_l_bar = swinglows[0]['bar']
        else:
            swing_l = self.cur_bar

        if (swing_h_bar == 0 or swing_l_bar == 0):
            return

        if (swing_h_bar > swing_l_bar):
            swing_height = swing_h - swing_l
            swing_width = swing_h_bar - swing_l_bar
        else:
            swing_height = swing_l - swing_h
            swing_width =  swing_l_bar - swing_h_bar

        if (abs(swing_height) > 15):
            self.manager.drive_indrcator(Indicator.LastSwingHeightShort, swing_height)
            self.manager.drive_indrcator(Indicator.LastSwingWidthShort, swing_width)
        else:
            pass

        #根据价格产生次峰、次谷

    def generate_event(self):
        #基于数量和幅度
        pass