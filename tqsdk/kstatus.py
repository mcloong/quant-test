# k_parsr 日线级别的预处理,调度kpattern
# KStatus 日内级别实时的处理,驱动产生事件
# 注入走势和预期，当Status发生某事件和趋势匹配或相反时
#      比如，当创新高后出现BigbangDown时，
class KStatus(object): #叫Kdriver是不是更合适
    def __init__(self):
        self.price_pos = 0 # 顶部、底部...
        self.avg_pos = 1 # 上下
        self.ups = 0
        self.cur_bar = 0
        self.cur_bar_id = 0

        self.last_event = 0
        self.predict = 0
        
    def set_newday_barid(self):
        pass

    def generate_event(self):
        pass

    #状态和语义
    #前半段创新高达到boll_hh，后半场回落，代表反转，应该试试追空