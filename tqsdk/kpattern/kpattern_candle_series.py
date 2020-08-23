import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")

from kpattern.kpattern_base import KPattern, BarType
from param_defines import StgEvent, Indicator

class KPBigBang(KPattern):
    pass

# Cross Star
class KPRedDojiInBottom(KPattern):
    pass

class KPGreenDojiInTop(KPattern):
    pass