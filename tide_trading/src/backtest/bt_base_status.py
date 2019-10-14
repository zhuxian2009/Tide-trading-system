# coding=utf-8

import abc
from enum import Enum
import src.datamgr.dbadapter as dbadapter

''' 回测模块，状态模式的基类 '''

class status_type(Enum):
    STATUS_SELECT = 0
    STATUS_HOLD = 1
    STATUS_SOLD = 2

#策略类型
class strategy_type(Enum):
    STGY_WBOTTOM = 1
    STGY_STEP = 2


#抽象类，抽象方法
class CBT_Base_Status(metaclass=abc.ABCMeta):

    def init(self, strategy, str_conf_path, log):
        self.dbadapter = dbadapter.CDBAdapter(str_conf_path, log)
        self.strategy = strategy
        self.reslut = None

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def set_result(self, reslut):
        self.reslut = reslut

    def get_result(self):
        return self.reslut

    @abc.abstractmethod
    def input_newkdata(self, kdata):
        pass

    @abc.abstractmethod
    def buy(self, res):
        pass

    @abc.abstractmethod
    def hold(self):
        pass

    @abc.abstractmethod
    def sell(self, res):
        pass

    @abc.abstractmethod
    def statistics(self):
        pass
