from param_defines import Indicator, MyDefaultValue

class KIndictor(object):
    def __init__(self, name, left, right):
        #self.kmap = []
        self.left_bar = 0
        self.right_bar = 0
        self.value = 0
        self.name = name
        self.bar = 0

    def defines(self):
        '''
        for tag in IndicatorEnum:
            self.kmap.append([tag, 0])
        '''

    def set(self, value, c_bar):
        self.name = value
        self.bar = c_bar

    def clone(self, indor):
        if (self.name != indor.name):
            return
        self.left_bar = indor.left_bar
        self.right_bar = indor.right_bar
        self.value = indor.value

class KIndictorSet(object):
    pass

class KIndictorRecorder(object):
    def __init__(self, name):
        self.name = name
        self.idor_list = []

    def add(self, indor):
        self.idor_list.append(indor)

class KIndictorFactory(object):
    def __init__(self):
        pass

    def on_bar(self, klines):
        pass

    def find_swing(self, klines):
        pass

    def create_checksum_idor(self, value, cur_bar):

        pass 

class KIndictorMap(object):
    def __init__(self):
        self.idor_list = []
        #self.interval = 

    def update(self, indor):
        '''
        ret = self.find(indor.name)
        if (ret is None):
            self.idor_list.append(indor)

        '''
        for itor in self.idor_list:
            if(indor.name == itor.name):
                itor.clone(indor)
                return

    def get(self, name):
        for itor in self.idor_list:
            if(name == itor.name):
                return itor.value

        return MyDefaultValue.InvalidInt
        