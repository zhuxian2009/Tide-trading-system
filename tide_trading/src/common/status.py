#coding=utf-8
from enum import Enum

''' 观察点，观察中，买入点，持有中，卖出点，等状态 '''
class State(Enum):
    #无状态
    none = 0
    #进入观察点
    view = 1
    # 正在观察
    viewing = 2
    # 退出观察
    out_view = 3
    #买入
    buy = 10
    #持股
    hold = 11
    #卖出
    sell = 20

class CStatus(object):
    def __init__(self):
        self.enState = State.none

    def getState(self):
        return self.enState

    def setState(self, enState):
        self.enState = enState

    def toNone(self):
        self.enState = State.none

    def View(self):
        if self.enState is State.view:
            self.enState = State.viewing
        elif self.enState is State.none:
            self.enState = State.view

    def Buy2Hold(self):
        if self.enState is State.buy:
            self.enState = State.hold
