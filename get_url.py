
import urllib
#import urllib.request
 
data={}
data['word']='Jecvay Notes'
 
#url_values=urllib.parse.urlencode(data)
url="http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol=RB1801"
full_url=url
 
data=urllib.urlopen(full_url).read()
data=data.decode('UTF-8')
print(data)