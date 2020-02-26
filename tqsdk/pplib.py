'''
def Swing_High_Price(KS, index, NumOfSideBar, fromWhere):
    cutIndex = 0;
   
    swingHigh_ = -1
    if (KS.length < NumOfSideBar):
        return -1
    length = KS.length;
    for i in range(NumOfSideBar, length):
        continueflag = True
      #  print("====KS.iloc[-"+str(i)+"].close"+str(KS.iloc[-i].close))
        for j in range(1, NumOfSideBar):
            print("KS.iloc[-"+str(i-j)+"].close="+str(KS.iloc[-(i-j)].close));
            if(KS.iloc[-i].close < KS.iloc[-(i-j)].close):
                continueflag = False
                break
        if (continueflag == False):
            continue
        print("=====left=========")
        for k in range(1, countOfLeft+1):
            print("KS.iloc[-"+str(i+k)+"].close="+str(KS.iloc[-(i+k)].close));
            if(KS.iloc[-i].close < KS.iloc[-(i+k)].close):
                continueflag = False
                break
        if (continueflag == True):
            print("HighPrice = "+str(KS.iloc[-i].close))
            print("HighPriceBar = "+str(i))
            swingHigh_ = KS.iloc[-i].close
            break
    return swingHigh_

def Swing_Low_Price(KS, SwingNum):
    countOfRight = int(SwingNum/2)
    countOfLeft = int(SwingNum/2)
    if (SwingNum%2 != 0):
        print("coutOfRight="+str(countOfRight)+" countOfLeft="+str(countOfLeft))
        countOfRight += 1
    
    swingLow_ = -1
    if (currentBar < SHORT):
        return -1
    for i in range(countOfRight+1, SHORT-countOfLeft):
        continueflag = True
        print("=====KS.iloc[-"+str(i)+"].close"+str(KS.iloc[-i].close))
        for j in range(1, countOfRight+1):
            print("KS.iloc[-"+str(i-j)+"].close="+str(KS.iloc[-(i-j)].close));
            if(KS.iloc[-i].close > KS.iloc[-(i-j)].close):
                continueflag = False
                break
        if (continueflag == False):
            continue
        print("=====left=========")
        for k in range(1, countOfLeft+1):
            print("KS.iloc[-"+str(i+k)+"].close="+str(KS.iloc[-(i+k)].close));
            if(KS.iloc[-i].close > KS.iloc[-(i+k)].close):
                continueflag = False
                break
        if (continueflag == True):
            print("LowPrice = "+str(klines.iloc[-i].close))
            print("LowPriceBar = "+str(i))
            swingLow_ = KS.iloc[-i].close
            break
    return swingLow_
    '''
def SwingHighPriceSeries(ks, numBarsOfSwig, fromWhere):
    highs = []
    length = len(ks)
    if (numBarsOfSwig*2 > length):
        print ('SwingHighPriceSeries')
        return
    print("length="+str(length))
    for i in range(numBarsOfSwig, length):
        elem = {}
        flag = True
        for j in range(1, numBarsOfSwig) :
            if (ks.iloc[-i].high<ks.iloc[-(i+1)].high or ks.iloc[-i].high<ks.iloc[-(i-1)].high) :
                flag = False; 
                break
        if (flag == True):
            elem['price'] = ks.iloc[-i]['high']
            elem['datetime'] = ks.iloc[-i]['datetime']
            highs.append(elem)
    
    return highs

def SwingLowPriceSeries(ks, numBarsOfSwig, fromWhere):
    lows = []
    length = len(ks)
    if (numBarsOfSwig*2 > length):
        print ('SwingHighPriceSeries')
        return
    print("length="+str(length))
    for i in range(numBarsOfSwig, length):
        elem = {}
        flag = True
        for j in range(1, numBarsOfSwig) :
            if (ks.iloc[-i].low>ks.iloc[-(i+1)].low or ks.iloc[-i].low>ks.iloc[-(i-1)].low) :
                flag = False; 
                break
        if (flag == True):
            elem['price'] = ks.iloc[-i]['high']
            elem['datetime'] = ks.iloc[-i]['datetime']
            lows.append(elem)
    
    return lows

#波峰波谷差值
def getSwingHighLowDev(highs, lows, num):
    if (num <= 0):
        return

    sumval = 0
    for i in num:
        sumval += highs[i] - lows[i]
    return round(sumval/num)

#
def checksumOfTickSerial(tserial, count):
    sumval = 0
    countOfUp = 0
    for i in range(0, count):
        if (tserial.iloc[i].average < tserial.iloc[i].bid_price):
            countOfUp += 1
        sumval = tserial.iloc[i].bid_price - tserial.iloc[i].average
    return sumval, countOfUp

def searchBigCandle(Klines, atr, fromWhere):
    elem = {}
    lists = []
    maxVal = 0
    for i in range(1,fromWhere):
        if tserial.iloc[-i].