# coding=utf-8

from src.backtest.bt_base_status import CBT_Base_Status, status_type
import src.stockselector.wbottom as wbottom
''' 回测模块，状态模式 '''


#选股状态
class CBT_WBottomSelectStatus(CBT_Base_Status):
    def __init__(self, strategy, str_conf_path, log):
        #状态,区别于其他的状态
        self.status = status_type.STATUS_SELECT
        self.init(strategy, str_conf_path, log)
        self.wbottom = wbottom.CWBotton(self.dbadapter.db, log)
        self.reslut = None


    def input_newkdata(self, kdata):
        today = self.strategy.dbadapter.GetToday()
        # 2. 一个一个交易日加入到策略
        self.wbottom.Init(10, self.strategy.start_day, today, self.strategy.selected_callback)
        self.wbottom.ProcessEx(kdata)

    def buy(self, res):
        print('buy .... ')
        self.strategy.cur_status = self.strategy.status_hold
        self.strategy.cur_status.set_result(res)

    def hold(self):
        pass

    def sell(self, res):
        pass

    def statistics(self):
        pass

#股票持有状态
class CBT_WBottomHoldStatus(CBT_Base_Status):
    def __init__(self, strategy, str_conf_path, log):

        #状态
        self.status = status_type.STATUS_HOLD
        self.init(strategy, str_conf_path, log)


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
        result = self.strategy.cur_status.get_result()
        buy_price = result.buy_price

        # 盈利
        gain = (high-buy_price)/buy_price
        gain = gain * 100

        # 止损
        loss = (close - buy_price) / buy_price
        loss = loss * 100

        result = self.strategy.cur_status.get_result()
        result.duration = result.duration + 1

        # 止盈, 跌破五日均线
        '''if gain > 2:
            result.sell_price = high
            result.sell_date = trade_day
            self.strategy.cur_status.sell(result)'''
        if close < ma5:
            result.sell_price = close
            result.sell_date = trade_day
            self.strategy.cur_status.sell(result)

        #止损
        if loss < -2:
            result.sell_price = close
            result.sell_date = trade_day
            self.strategy.cur_status.sell(result)


    def buy(self, res):
        pass

    def hold(self):
        pass

    def sell(self, res):
        self.strategy.cur_status = self.strategy.status_sold
        self.strategy.cur_status.set_result(res)

    def statistics(self):
        pass
#卖出状态
class CBT_WBottomSoldStatus(CBT_Base_Status):
    def __init__(self, strategy, str_conf_path, log):
        #状态
        self.status = status_type.STATUS_SOLD
        self.init(strategy, str_conf_path, log)

    def input_newkdata(self, kdata):
        #write to mysql
        ret = self.reslut
        self.dbadapter.GetDB().add_bt_strategy(ret.code, ret.buy_date,
                                               ret.buy_price, ret.sell_date, ret.sell_price, ret.duration, 1)

        #sold to select
        self.strategy.cur_status = self.strategy.status_select
        self.strategy.cur_status.input_newkdata(kdata)

    def buy(self, res):
        pass

    def hold(self):
        pass

    def sell(self, res):
        pass

    def statistics(self):
        self.strategy.cur_status = self.strategy.status_select
