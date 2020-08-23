from tqsdk import TqApi, TqAccount, TargetPosTask
from tool_utils import get_current_minute_bar
from datetime import datetime
import time
import threading
import time
import numpy as np

class PositionManger(object) :
    def __init__(self, api, symbol):
        self.api = api
        self.symbol = symbol
        self.account_position = self.api.get_position(self.symbol)
        self.target_pos = TargetPosTask(self.api, self.symbol)
        self.TAG = "PositionManager"

        self.bid_price = 0
        self.ask_price = 0

        self.MAX_POS = 2

        self.init_data()

    def init_data(self):
        self.runing_pos = 0
       # self.account_hold_pos = self.target_pos.pos_long + self.target_pos.pos_short
        self.account_hold_pos = self.account_position.pos_long_today + self.account_position.pos_short_today

        self.run_flag = True
        self.entry_time = 0
        self.exit_time = 0

        self.strategy_pos = 0

        self.keep_pos = 0

        self.count_limit_flag = False
        
        #不确定set_position 会不会取消order
        self.close_setup = 0 # 0 撤掉order；平仓

    def init(self, pos):
        self.strategy_pos = pos
        has_pos = self.get_hold_position()
        if (has_pos != self.strategy_pos):
            self.target_pos.set_target_volume(self.strategy_pos)

    def run(self):
        if self.api.is_changing(self.account_position):
            print("今多头: %d 手" % (self.account_position.pos_long_today))
            print("今空头: %d 手" % (self.account_position.pos_short_today))

    def new_day(self):
        self.init_data()

    def get_hold_position(self):
        position = self.api.get_position(self.symbol)
        pos_1 = position.pos_long - position.pos_short
        pos_2 = position.pos
        if (pos_1 != pos_2):
            print("[%s] pos_long=%d pos_short=%d pos=%d"%(self.TAG, position.pos_long , position.pos_short,pos_2))

        return pos_2
    '''
    def get_runing_position(self):
        position = self.api.get_position(self.symbol)
        return position.pos_long + position.pos_short
    '''
    def refresh(self):
        #position = self.api.get_position("SHFE.rb2005")
        if (self.run_flag == False):
            return
    def buy(self):
        if (self.run_flag == False):
            return
        self.entry_time = get_current_minute_bar()

    def buy_to_cover(self):
        if (self.run_flag == False):
            return

    def sell_to_short(self):
        if (self.run_flag == False):
            return
        self.entry_time = get_current_minute_bar()

    def sell(self):
        if (self.run_flag == False):
            return
    def order_buy(self):
        if (self.run_flag == False):
            return
    def order_buy_to_cover(self):
        if (self.run_flag == False):
            return
    def order_sell_to_short(self):
        if (self.run_flag == False):
            return

    def order_sell(self):
        if (self.run_flag == False):
            return
        
    def get_entry_time(self):
        return get_current_minute_bar - self.entry_time

    def get_trade_done_time(self):
        #trade = self.api.get_trade()
        pass
    #position = api.get_position("DCE.m1809")
    def get_profit(self):
        self.account_position = self.api.get_position(self.symbol)
        profit = self.account_position.float_profit_long + self.account_position.float_profit_short
        #print(profit)
        if (profit != profit):
            return 0
        else:
            return int(profit)

    def get_balance(self):
        account = self.api.get_account()
        balance = account.balance
        
        return int(balance)

    #持仓盈亏
    def get_position_profit(self):
        #self.account_position = self.api.get_position(self.symbol)
        #return self.account_position.position_profit
        account = self.api.get_account()
        return int(account.position_profit)

    #本交易日内平仓盈亏
    def get_close_profit(self):
        #self.account_position = self.api.get_position(self.symbol)
        #return self.account_position.close_profit
        account = self.api.get_account()
        return int(account.close_profit)
        
    def get_last_trade_type(self):
        pass

    def get_exit_time(self):
        pass

    def cancel_all_orders(self):
        orders = self.api.get_order()
        print(orders)
        if (orders):
            for oid, order in orders.items():
                if (order.status == "ALIVE"):
                    self.api.cancel_order(order)
    
    def start(self):
        self.run_flag = True
        th1 = threading.Thread(target=PositionManger.monitor_thread, args=(self,))
        th1.start()

    def stop(self):
        self.run_flag = False

    def close(self):
        if (self.run_flag == True):
            if (self.close_setup == 0):
                print("[%s] cancel all_orders", self.TAG)
                self.cancel_all_orders()
                self.close_setup = 1
                return
            else:
                print("[%s] close.....", self.TAG)
                self.target_pos.set_target_volume(self.keep_pos)
                self.run_flag = False
                self.strategy_pos = 0
                self.logger.info(self.TAG, "close....self.keep_pos=%d"%(self.keep_pos))
                print("[%s] close self.keep_pos=%d"%(self.TAG, self.keep_pos))
        else:
            return 

    def close2(self):
        if (self.run_flag == True):
            print("[%s] cancel all_orders", self.TAG)
            self.cancel_all_orders()
            self.target_pos.set_target_volume(0)
            self.run_flag = False
            self.strategy_pos = 0
            self.logger.info(self.TAG, "close2....")
            print("[%s] close2", self.TAG)
        else:
            return 

    def set_position(self,pos):
        lt = time.localtime(time.time())
        if (((lt.tm_hour == 14 and lt.tm_min>=56) or self.run_flag == False) and pos != 0):   
            return

        self.strategy_pos = pos

        if (self.count_limit_flag == False):
            self.target_pos.set_target_volume(self.strategy_pos)
        else:
            if (self.strategy_pos >= self.MAX_POS):
                self.target_pos.set_target_volume(self.MAX_POS)
            elif (self.strategy_pos <= -self.MAX_POS):
                self.target_pos.set_target_volume(-self.MAX_POS)
            else:
                self.target_pos.set_target_volume(0)

    def check(self):
        localtime = time.localtime(time.time())
        if (self.close_setup >= 1):
            return
        if (localtime.tm_min%5 == 0):
             account_position = self.api.get_position()
             if (account_position.pos_long + account_position.pos_short != self.strategy_pos):
                 self.target_pos.set_target_volume(self.strategy_pos)
        
        if (localtime.tm_hour == 14 and localtime.tm_min >=58):
            self.shutdown_flag = True
            account_position = self.api.get_position()
            if (account_position.pos_long != 0):
                 self.target_pos.set_target_volume(0)
            self.strategy_pos = 0

    def set_keep_position(self, pos):
        self.keep_pos = pos

    def set_logger(self, logger):
        self.logger = logger

    def init_trade_orders(self, direction, pos, trade_date):
        pass
    
    def monitor_thread(self):
        pass

'''
position = api.get_position("SHFE.rb2005")
#print(position.float_profit_long + position.float_profit_short)
print(position.pos_long)
#while api.wait_update():
#    print(position.float_profit_long + position.float_profit_short)
 #   print(position.pos_long)
'''