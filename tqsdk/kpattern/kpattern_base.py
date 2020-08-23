#一、分为TrendMode和KMode，分别为趋势模型、K线模型
#预置K线模式：检测当前处于哪个阶段，预判下一个阶段
#适用决策树
#大涨后高位横盘、大跌后被拉涨（易涨难跌）
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from kpattern.kcommon import CondtionSet, UpperLimitCondition, LowerLimitCondition, RangeCondition
from param_defines import StgEvent, Indicator, MyString, MyDefaultValue, BarType

#废弃不用
class KPatternTrendTypeClass(object):
    def __init__(self):
        #===UpPatternAllDay=====
        self.UpAllDay = 1 #用于分隔
        self.UpPatternHalfDay = 2
        self.RangePattern = 0
        self.DownPatternAllDay = -1
        self.DownPatternHalfDay = -2
        
        '''
        self.KBackFromKeySupportLine = 1
        self.KBackFromKeyResistanceLine = 2
        self.KBackFromKeySupportPrice = 3
        self.KBackFromKeyResistancePrice = 4
        self.ThreeReds = 5
        self.TreeGreens = 6
        self.RedInGreens = 7 
        self.GreenInReds = 8
        self.BoxWithStrongBottom = 9
        self.BoxWithStrongTop = 10
        '''
KPatternTrendType = KPatternTrendTypeClass()

#此处定义是为了全局浏览，或者临时小调整
#每个pattern在定义时会设置默认值
#上涨的模式

#ClassicUpMode = [[]]

#趋势


class StrongUpLowRange(object):
    pass

'''
class StrongUpUp
    StrongDownLowRange
    StrongDownDown
'''

#代表着冲击失败
class TopDoubuleMDown(object):
    pass
    '''
    BottomDoubleWUp
    TopBigbangDown

    WideRange

    '''

    #self.

    '''
    MODE1 = "Bottom-Up-Wave-Top"

    #最有效突破
    #趋势-lowrange(均线附近)-突破


    #解析K线
    1. 由swing_low 和 high 构成的阶梯线
    2. 更具强势程度判断是否会初级下线
    
    swing_ll: 
    swing_high
    '''
class KPGuildTypeStruct(object):
    def __init__(self):
        self.Price = 1
        self.Event = 2

#继承KPattern模式的类相当于Pattern的产生器
#模式的纯数据形式为KPatternStruct，对外广播的也应该是Struct
class KPatternStruct(object):
    def __init__(self):
        self.name = None
        self.bar_type = 0 # 1 日，0 分钟
        self.trend = 0 # 趋向
        self.level = 3 # 优先级 1~3，等级1 具有决定性，2、3需要多个条件结合
        self.interval = 10 # 控制间隔和检测周期
        self.bar = 0 # bar、bar_inday 为0，说明没有符合过
        self.bar_inday = 0
        self.left_bar = 0
        self.right_bar = 0
        self.valid = False #是否生效
        self.kclock = None
        self.result = True #是否匹配
    
#条件->指标->组合->模式->趋势
#山峰、契形
class KPattern(object):
    def __init__(self, name, ktype):
        self.name = name
        self.bar_type = ktype # 0 minbar, 1 daybar
        self.level = 3 # 优先级 1~3，等级1 具有决定性，2、3需要多个条件结合
        self.interval = 10 # 控制间隔和检测周期
        self.bar = 0 # bar、bar_inday 为0，说明没有符合过
        self.bar_inday = 0
        self.left_bar = 0
        self.right_bar = 0
        self.valid = False #是否生效
        self.kclock = None
        self.result = True #是否匹配
        self.trend = 0 #趋向
        self.parts = 3

        #self.cond_set = CondtionSet(name) #
        self.indor_sets = []
        self.cur_step = 1
        self.score = 0

        self.callback = None #用于匹配成功通知上一级

        #对应策略
        self.guild_type = 0
        self.guild_price = 0
        self.target_profit = 0
        self.match_event = [] #匹配的事件
        self.watcher_event = []

        #可能用不到
        self.author = "default"

    def cond_define(self, cond):
        pass

    def drive_cond(self, cond):
        pass

    def add_sets(self, indor_set):
        self.indor_sets.append(indor_set)

    def get_steps(self):
        return len(self.indor_sets)
    
    def drive(self, klines):
        pass

    def drive_kclock(self, kclock):
        self.kclock = kclock

    def drive_indor(self, indor, value):
        pass

    def drive_indicator_class(self, indor):
        for itor in self.indor_sets:
            if (itor.index == self.cur_step):
                itor.drive_indicator(indor)
                if (itor.is_ok()):
                    self.cur_step += 1
                else:
                    #self.cur_step = 1
                    self.reset()
        count = self.get_steps()
        if (self.cur_step == count):
            if (self.check_gap()):
                self.result = True
            return True
        else:
            return False

    def drive_event(self, event_name, event_value):
        pass

    def reset(self):
        self.cur_step = 1
        self.result = False

    def get_score(self):
        return self.score

    #一个模式分多个部分，每部分之间设定间隔，超出模式无效
    def set_setp_gap(self, bars):
        self.gaps = bars
        pass
    
    def check_gap(self):
        leng = len(self.indor_sets)
        for i in range(0, leng-1):
            if (self.indor_sets[i+1].lask_ok_bar - self.indor_sets[i+1].lask_ok_bar > self.gaps):
                return False

        return True

    def match(self):
        self.result = True
        if (self.kclock is not None):
            if (self.bar_type == 0):
                self.bar = self.kclock.bar
                self.bar_inday = self.kclock.bar_inday
            else:
                self.bar = self.kclock.day_bar
        if (self.callback is not None):
            self.callback.on_kpattern_callback(self, MyString.Match, 0)
        

    def check(self):
        return self.result

    #存储用
    def clone_struct(self):
        kp = KPatternStruct()
        kp.name = self.name
        kp.bar_type = self.bar_type
        kp.level = self.level
        kp.interval = self.interval
        kp.bar = self.bar
        kp.bar_inday = self.bar_inday
        kp.left_bar = self.left_bar
        kp.right_bar = self.right_bar
        kp.valid = self.valid
        kp.kclock = self.kclock
        kp.result = self.result

    #合并用
    #bar要保持最新的
    def combine(self, pt):
        return pt

    def ok(self):
        self.result = True

    def isok(self):
        return self.result

    def set_callback(self, cb):
        self.callback = cb

class UpFlatDown(KPattern):
    def __init__(self, strId):
        self.TAG = "UpFlatDown"
        KPattern.__init__(self, self.TAG, BarType.DAY)
        
        self.default_params()
    
    def default_params(self):
        '''
        up_h_cond = UpperLimitCondition("UpH", 1, 15)
        up_wide_cond = RangeCondition("UpW", 2, 1, 10)

        flat_h_cond = UpperLimitCondition("UpH", 1, 8)
        flat_wide_cond = RangeCondition("UpW", 2, 1, 10)

        down_h_cond = LowerLimitCondition("DownH", 1, -15)
        down_wide_cond = RangeCondition("DownW", 2, 1, 10)
        '''
        up_h_cond = UpperLimitCondition(Indicator.LastSwingHeightShort, 1, 15)
        up_w_cond = RangeCondition(Indicator.LastSwingWidthShort, 2, 1, 10)
        setp1 = CondtionSet("up")
        setp1.index = 1
        setp1.add_cond(up_h_cond)
        setp1.add_cond(up_w_cond)
        self.add_sets(setp1)

        flat_h_cond = UpperLimitCondition("UpH", 1, 8)
        flat_w_cond = RangeCondition("UpW", 2, 1, 10)
        setp2 = CondtionSet("flat")
        setp2.index = 2
        setp2.add_cond(flat_h_cond)
        setp2.add_cond(flat_w_cond)
        self.add_sets(setp2)

        down_h_cond = LowerLimitCondition("DownH", 1, -15)
        down_wide_cond = RangeCondition("DownW", 2, 1, 10)
        setp3 = CondtionSet("down")
        setp3.index = 3
        setp3.add_cond(down_h_cond)
        setp3.add_cond(down_wide_cond)
        self.add_sets(setp3)

#
class KSanMountain(KPattern):
    pass

#长板坡
class LongSlope(object):
    pass

# resistance
class KPBackFromKeyResistanceLine(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.BackFromKeyResistanceLine, BarType.DAY)
        self.level = 1 #最高
        self.score = 0
        self.from_last_cross = 0
        self.back_bar = 0

    def cacl_score(self):
        #距离
        dist_score = 0
        if (self.back_bar <= 1):
            self.score = 100
        elif (self.back_bar <= 2):
            self.score = 80
        elif (self.back_bar <= 3):
            self.score = 40
        #上一个的距离

#冲高回落
class KRushTopAndBack(KPattern):
    def __init__(self):
        pass

    def param(self):
        width = 10
        height = 20
        dif_of_two_side = 10
'''
        self.RushBottomAndBack = "RushBottomAndBack" # V型
        self.LowRangeInTop = "LowRangeInTop"
        self.LowRangeInBottom = "LowRangeInBottom"
'''

class KGapUp(KPattern):
    def __init__(self):
        pass

class KPOverAvgLine(KPattern):
    def __init__(self):
        pass

class KPOverAvgLineAtOpen(KPOverAvgLine):
    def __init__(self):
        self.name = StgEvent.OverAvgLineAtOpen
        self.default = 30

    def drive_indicator(self, indor, value):
        if (indor != Indicator.OversAvg):
            return
        
        if (self.kclock is None):
            return
        cur_bar = self.kclock.cur_bar

        overs = int(value)
        if (cur_bar>self.default and overs > int(cur_bar*0.9)):
            self.match()

   
    def check(self):
        pass

'''
上涨过程中的回调
1. 40分钟高和20分钟高相同
2. 10分钟高比20分钟高低10个点
3. 出现10分钟级别的lowrange
4. 注意与lowrange区分
'''
class StdBackRestOfUp(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.StdBackRestOfUp, 0)
        self.std_height10 = 10
        self.std_lowrange_height = 15
        self.std_lowrange_width = 10
        
        # 记录当前指标
        self.height10 = 0
        self.height30 = 0
        self.height20 = 0
        self.height15 = 0
        self.hh30 = 0
        self.hh10 = 0

    def drive_indicator(self, indor):
        if (indor.name == Indicator.RangeHeight10):
            self.height = indor.value
        if (indor.name == Indicator.RangeHeight30):
            self.height30 = indor.value
        if (indor.name == Indicator.RangeHeight50):
            self.height50 = indor.value

        if (indor.name == Indicator.RangeHeight10):
            self.hh10 = indor.value
        
        if (self.height30!=0 and self.height30==self.height50):#确定增长趋势
            self.height = 0

        pass

    def drive_kline(self, kline):
        pass

class StdBackResetOfDown(KPattern):
    def __init__(self):
        KPattern.__init__(self, StgEvent.StdBackRestOfDown, 0) 

    def drive_indicator(self):
        pass