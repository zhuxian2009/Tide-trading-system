# coding=utf-8

from src.backtest.bt_base_status import CBT_Base_Status, status_type
import operator

''' 回测策略，具有选股状态，持股状态，卖出状态；每个策略算法的不同之处，主要体现在这三个状态的实现上
小步向前，尾盘突破前高，短线 '''

#选股状态
class CBT_LittleStepSelectStatus(CBT_Base_Status):
    def __init__(self, strategy, str_conf_path, log):
        #状态,区别于其他的状态
        self.status = status_type.STATUS_SELECT
        self.init(strategy, str_conf_path, log)

    def input_newkdata(self, kdata):
        # kdata表示回测日及之前的kdata
        # 需要的原始数据
        # 交易日期
        trade_day = kdata['trade_day']
        # 收盘价 最高价 最低价
        low_price = kdata['low']
        high_price = kdata['high']
        close_price = kdata['close']
        open_price = kdata['open']
        # 成交额
        amount = kdata['amount']
        vol = kdata['vol']
        ma5_vol = kdata['ma5vol']
        pct_chg = kdata['pct_chg']
        # macd指标
        macd = kdata['macd']
        dif = kdata['dif']
        dea = kdata['dea']
        # 当前被处理的股票代码
        code = kdata['code'].iloc[0]
        cur_close = close_price.iloc[-1]
        cur_open = open_price.iloc[-1]
        cur_low = low_price.iloc[-1]
        cur_trade_day = trade_day.iloc[-1]
        cur_pct_chg = pct_chg.iloc[-1]

        if code == '002013.SZ' and cur_trade_day == '20180827':
            print('pause')

        b_go = True
        count = 0
        #连续4个交易日小阳线
        for i in range(-2, -6, -1):
            #前N天的收盘价
            history_close = close_price.iloc[i]
            history_open = open_price.iloc[i]
            #前N+1天的收盘价
            #history_pre_close = close_price.iloc[i-1]

            #小于5个点的小阳线
            gain = pct_chg.iloc[i]
            if gain < 0.5 or gain > 6 or history_open > history_close:
                b_go = False
                return

            #至少1个交易日的量能大于ma5，温和放量更好
            history_vol = vol.iloc[i]
            history_ma_vol = ma5_vol.iloc[i]

            if history_vol > history_ma_vol:
                count = count + 1

        #回测日的收盘价，突破前期高点，且放量,且阳线
        gain = cur_pct_chg

        #计算前N天的极大值
        N=-13
        part_high = high_price[N:-1]
        part_trade_day = trade_day[N:-1]
        max_index, max_number = max(enumerate(part_high), key=operator.itemgetter(1))
        the_trade_day = part_trade_day.iloc[max_index]

        if b_go is True and count >= 2 and gain>0.5 and gain<9 and cur_close>=max_number:
            print('little step trade day =', cur_trade_day, '   code=', code, '  max_number=',max_number, '  the_trade_day=',the_trade_day)

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
class CBT_LittleStepHoldStatus(CBT_Base_Status):
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
class CBT_LittleStepSoldStatus(CBT_Base_Status):
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
