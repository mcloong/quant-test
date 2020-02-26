import time

STOP_LOSS_PRICE_L1 = 10 
STOP_LOSS_PRICE_L2 = 20

localtime = time.localtime(time.time())

#def swing_high_filter(highs, time, height):

#def swing_low_filter(lows, time, height):


def get_Rbreaker_line(klines):
    high = klines.high.iloc[-2] 
    low = klines.low.iloc[-2]  
    close = klines.close.iloc[-2]  
    pivot = (high + low + close) / 3  
    bBreak = high + 2 * (pivot - low)  
    sSetup = pivot + (high - low)  
    sEnter = 2 * pivot - low 
    bEnter = 2 * pivot - high  
    bSetup = pivot - (high - low)  
    sBreak = low - 2 * (high - pivot) 
    
    return pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak

def wait_market(curPrice, dayBars):
    high = klines.high.iloc[-2] 
    low = klines.low.iloc[-2]  
    close = klines.close.iloc[-2]  
    pivot = (high + low + close) / 3  
    bBreak = high + 2 * (pivot - low)  
    sSetup = pivot + (high - low)  
    sEnter = 2 * pivot - low 
    bEnter = 2 * pivot - high  
    bSetup = pivot - (high - low)  
    sBreak = low - 2 * (high - pivot)  


    if (target_pos_value > 0 and open_position_price - quote.last_price >= STOP_LOSS_PRICE) or \
                (target_pos_value < 0 and quote.last_price - open_position_price >= STOP_LOSS_PRICE):
        target_pos_value = 0 

        if target_pos_value > 0:  
            if quote.highest > sSetup and quote.last_price < sEnter:
               
                open_position_price = quote.last_price
        elif target_pos_value < 0:  
            if quote.lowest < bSetup and quote.last_price > bEnter:
                target_pos_value = 3  
                open_position_price = quote.last_price
        
        elif target_pos_value == 0: 
            if quote.last_price > bBreak:
                target_pos_value = 3 
                open_position_price = quote.last_price
            elif quote.last_price < sBreak:
                target_pos_value = -3 
                open_position_price = quote.last_price
'''
2 多排列
1 震荡多
-1 震荡空
-2 空排列
'''
def parse_trend_type(curPrice, highs, lows,dayBars, avgPrice):
    high_len = len(highs)
    low_len = len(lows)
    # day level

    # 当下
   # if (highs.iloc[-1]['price'] == ) :


     #   print("已计算新标志线, 枢轴点: %f, 突破买入价: %f, 观察卖出价: %f, 反转卖出价: %f, 反转买入价: %f, 观察买入价: %f, 突破卖出价: %f"
   #             % (pivot, bBreak, sSetup, sEnter, bEnter, bSetup, sBreak))