# coding=utf-8

import src.common.tools as tools
import sys
import os
import src.backtest.backtest_bycode
import datetime
import src.datamgr.dbadapter as dbadapter
from multiprocessing import Pool #导入进程池

import src.datamgr.dbmgr as dbmgr
import pandas as pd
import src.common.conf as conf
import src.stockselector.wbottom as wbottom
import abc
from enum import Enum

''' 回测模块，状态模式 '''

class status_type(Enum):
    STATUS_SELECT = 0
    STATUS_HOLD = 1
    STATUS_SOLD = 2

#抽象类，抽象方法
class CBackTestBycodeStatus(metaclass=abc.ABCMeta):

    def init(self, backtest, str_conf_path, log):
        self.dbadapter = dbadapter.CDBAdapter(str_conf_path, log)
        self.backtest = backtest
        self.wbottom = wbottom.CWBotton(self.dbadapter.db, log)
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
    def statistics(self, res):
        pass

#选股状态
class CBT_SelectStatus(CBackTestBycodeStatus):
    def __init__(self, backtest, str_conf_path, log):
        #状态,区别于其他的状态
        self.status = status_type.STATUS_SELECT
        self.init(backtest, str_conf_path, log)

    def input_newkdata(self, kdata):
        today = self.backtest.dbadapter.GetToday()
        # 2. 一个一个交易日加入到策略
        self.wbottom.Init(10, self.backtest.start_day, today, self.backtest.selected_callback)
        self.wbottom.ProcessEx(kdata)

    def buy(self, res):
        print('buy .... ')
        self.backtest.cur_status = self.backtest.status_hold
        self.backtest.cur_status.set_result(res)

    def hold(self):
        pass

    def sell(self, res):
        pass

    def statistics(self):
        pass

#股票持有状态
class CBT_HoldStatus(CBackTestBycodeStatus):
    def __init__(self, backtest, str_conf_path, log):
        #状态
        self.status = status_type.STATUS_HOLD
        self.init(backtest, str_conf_path, log)

    def input_newkdata(self, kdata):
        #找卖点
        newest = kdata[-1:]
        code = newest['code'].iloc[-1]
        close = newest['close'].iloc[-1]
        ma5 = newest['ma5'].iloc[-1]

        high = newest['high'].iloc[-1]
        trade_day = newest['trade_day'].iloc[-1]
        print('close=', close, 'high=', high)
        #卖出条件
        result = self.backtest.cur_status.get_result()
        buy_price = result.buy_price

        # 盈利
        gain = (high-buy_price)/buy_price
        gain = gain * 100

        # 止损
        loss = (close - buy_price) / buy_price
        loss = loss * 100

        result = self.backtest.cur_status.get_result()
        result.duration = result.duration + 1

        # 止盈, 跌破五日均线
        '''if gain > 2:
            result.sell_price = high
            result.sell_date = trade_day
            self.backtest.cur_status.sell(result)'''
        if close < ma5:
            result.sell_price = close
            result.sell_date = trade_day
            self.backtest.cur_status.sell(result)

        #止损
        if loss < -2:
            result.sell_price = close
            result.sell_date = trade_day
            self.backtest.cur_status.sell(result)


    def buy(self, res):
        pass

    def hold(self):
        pass

    def sell(self, res):
        self.backtest.cur_status = self.backtest.status_sold
        self.backtest.cur_status.set_result(res)

    def statistics(self):
        pass
#卖出状态
class CBT_SoldStatus(CBackTestBycodeStatus):
    def __init__(self, backtest, str_conf_path, log):
        #状态
        self.status = status_type.STATUS_SOLD
        self.init(backtest, str_conf_path, log)

    def input_newkdata(self, kdata):
        #write to mysql
        ret = self.reslut
        self.dbadapter.GetDB().add_bt_strategy(ret.code, ret.buy_date,
                                               ret.buy_price, ret.sell_date, ret.sell_price, ret.duration, 1)

        #sold to select
        self.backtest.cur_status = self.backtest.status_select
        self.backtest.cur_status.input_newkdata(kdata)

    def buy(self, res):
        pass

    def hold(self):
        pass

    def sell(self, res):
        pass

    def statistics(self):
        self.backtest.cur_status = self.backtest.status_select