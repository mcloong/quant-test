
#!/usr/bin/python
import urllib
import json
import time
 
data={}
data['word']='Jecvay Notes'
 
#url_values=urllib.parse.urlencode(data)
url="http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol=RB1801"
full_url=url
 
data=urllib.urlopen(full_url).read()
data=data.decode('UTF-8')
#print(data)

bars = json.loads(data)

print len(bars)
minBar = bars[0];
maxBar = bars[1];
peak = []
valley = []
peak_temp = []
valley_temp = []
num_of_peak = 100
index = []
index_tmp = []

def bar_cmp(x, y):
    return x[4]<y[4]

def myKey(a):
    return a[4]

def date_trans(str):
    #basetime = "2017-08-01 00:00:00"
    #y = (int(str[0:4]) - 2017)*60*60*24*365;
    #m = (int(str[0:4]) - 2017)*60*60*24*365;
    localtime=time.strptime(str,'%Y-%m-%d %H:%M:%S')
    ltime= time.mktime(localtime)
    print ltime
    return ltime
def date_cmp(time1, time2):
    return date_trans(time1) - date_trans(time2)
    
print date_trans("2017-08-01 00:04:12")- date_trans("2017-08-01 00:00:00")

for i in range(1, len(bars)-1,1):
    if(bars[i][4] > bars[i-1][4] and bars[i][4] >= bars[i+1][4]):
        peak.append(bars[i])
    elif(bars[i][4] < bars[i-1][4] and bars[i][4] <= bars[i+1][4]):
        valley.append(bars[i])
            
print peak
peak.sort(cmp=None, key=myKey, reverse=True)
print peak

print valley
valley.sort(cmp=None, key=myKey, reverse=False)
print valley

num_of_peak = len(peak)

k = 0
while k > 5:
    for i in range(0, len(peak)-1, 1):
        val = abs(date_cmp(peak[i], peak[i+1]))
        if(val < 60*20):#20s
            k = k+1
            peak.remove(i+1)
            break;
        
k = 0
while k > 5:
    for i in range(0, len(valley)-1, 1):
        val = abs(date_cmp(valley[i], valley[i+1]))
        if(val < 60*20):#20s
            k = k+1
            valley.remove(i+1)
            break;        

#while 1:
    
#for i in range(0, len(bars),1):
    #index.append(i)
    
#while 1:
    #peak = []
    #valley= []    
    #if(bars[index[0]][4] < bars[index[1]][4]):
        #valley.append(bars[index[0]])
        #index_tmp.append(index[0])
    #elif((bars[index[0]][4] > bars[index[1]][4])):
        #peak.append(bars[index[0]])    
        #index_tmp.append(index[0])
         
       
    #for i in range(1, len(index)-1,1):
        #if(bars[index[i]][4] > bars[index[i-1]][4] and bars[index[i]][4] >= bars[index[i+1]][4]):
            #peak.append(bars[index[i]])
            #index_tmp.append(index[i])
        #elif(bars[index[i]][4] < bars[index[i-1]][4] and bars[index[i]][4] <= bars[index[i+1]][4]):
            #valley.append(bars[index[i]])
            #index_tmp.append(index[i])
            
    #print str(len(peak))+" peaks "+str(len(valley))+" valleys"

    ##if(bars[index[len(index)-1]][4] < bars[index[len(index)-2]][4]):
        ##valley.append(bars[index[len(index)-1]])
        ##index_tmp.append(index[len(index)-1])
    ##elif(bars[index[len(index)-1]][4] > bars[index[len(index)-2]][4]):
         ##peak.append(bars[index[len(index)-1]])   
         ##index_tmp.append(index[len(index)-1])
         

         
    #num_of_peak = len(index_tmp)
    #if(num_of_peak <= 20):
        #break;
    #else:
        #index = index_tmp;
        #index_tmp = []
    
##num_of_peak = len(peak)
##num_of_valley = len(valley)
##tmp = []
##while num_of_peak > 4:
    ##tmp = peak;
    ##peak = []
    ##for i in range(1, len(tmp)-1, 1):
        ##if(bars[i][4] >= bars[i-1][4] and bars[i][4] > bars[i+1][4]):
    

for elem in peak[0:5]:
    print elem[0], elem[4]
print "==========================="
for elem in valley[0:5]:
    print elem[0], elem[4]    
    
print str(len(peak))+" peaks "+str(len(valley))+" valleys"

#震荡 箱体交易

# 过滤波峰波谷思想
# 第一遍过滤出来所有的波峰波谷
# 第二遍按照第一遍再过滤一次，过滤出符合数量要求的波峰波谷。
 
    