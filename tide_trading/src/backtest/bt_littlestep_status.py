# coding=utf-8

from src.backtest.bt_base_status import CBT_Base_Status, status_type
import operator
from src.backtest.backtest_bycode import CBT_Result as CBT_Result

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
        #ma值
        ma60 = kdata['ma60']
        # 当前被处理的股票代码
        code = kdata['code'].iloc[0]
        cur_close = close_price.iloc[-1]
        cur_open = open_price.iloc[-1]
        cur_low = low_price.iloc[-1]
        cur_high = high_price.iloc[-1]
        cur_trade_day = trade_day.iloc[-1]
        cur_pct_chg = pct_chg.iloc[-1]
        cur_ma60 = ma60.iloc[-1]
        cur_vol = vol.iloc[-1]
        cur_ma5_vol = ma5_vol.iloc[-1]
        cur_macd = macd.iloc[-1]

        if code == '002409.SZ' and cur_trade_day == '20190924':
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

        #最后一个交易日是真阳线
        if cur_close < cur_open:
            b_go = False

        #计算前N天的极大值
        N = -13
        last_high = 0
        the_trade_day = None
        higt_point_macd=0
        for i in range(-13,-20,-2):
            N = i
            part_high = high_price[N:-1]
            part_trade_day = trade_day[N:-1]
            part_macd = macd[N:-1]
            max_index, max_number = max(enumerate(part_high), key=operator.itemgetter(1))

            #往前两格，依然是相同的高点，则认为找到了高点
            if last_high == max_number:
                break

            #每次下标会变化，所以保存位置没有意义
            the_trade_day = part_trade_day.iloc[max_index]
            higt_point_macd = part_macd.iloc[max_index]

            last_high =max_number

        #macd大于前高点的macd
        if cur_macd < higt_point_macd:
            b_go = False

        #MA60向上
        if cur_ma60 < ma60.iloc[-2] or ma60.iloc[-2] <= ma60.iloc[-4]:
            b_go = False

        #上证指数在ma10上
        sh000001 = self.strategy.get_sh000001(the_trade_day)
        sh000001_close = float(sh000001['close'].iloc[0])
        sh000001_ma10 = float(sh000001['ma10'].iloc[0])
        if sh000001_close < sh000001_ma10:
            b_go = False

        #成交量不能大于ma5的两倍
        if cur_vol > cur_ma5_vol * 2:
            b_go = False

        #不能有超过4个点的长上引线
        up_shadow = (cur_high-cur_close)*100/cur_close
        if up_shadow > 4:
            b_go = False

        if b_go is True and count >= 2 and gain>0.5 and gain<9 and cur_close >= max_number:
            print('little step trade day =', cur_trade_day, '   code=', code, '  max_number=',max_number, '  the_trade_day=',the_trade_day)
            res = CBT_Result()
            #收盘价作为买点
            res.buy_price = cur_close
            res.buy_date = cur_trade_day
            res.code = code
            self.strategy.buy(res)

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
        ma10 = newest['ma10'].iloc[-1]

        high = newest['high'].iloc[-1]
        low = newest['low'].iloc[-1]
        trade_day = newest['trade_day'].iloc[-1]
        #print('close=', close, 'high=', high)

        result = self.strategy.cur_status.get_result()
        result.duration = result.duration + 1
        self.strategy.cur_status.set_result(result)

        #到ma10(一个点的范围)，补半仓，补一次；
        # 大盘跌破ma10，不补（未实现）
        if result.position < 1.0 and float(low) <= (float(ma10)+float(ma10)*0.01):
            result.position = 1.0
            result.buy_price = result.buy_price - (result.buy_price-ma10)/2
            self.strategy.cur_status.set_result(result)
            print('add position')
            return

        #卖出条件
        #result = self.strategy.cur_status.get_result()
        buy_price = result.buy_price

        # 盈利
        gain = (high-buy_price)/buy_price
        gain = gain * 100

        # 止损
        loss = (low - buy_price) / buy_price
        loss = loss * 100

        result = self.strategy.cur_status.get_result()
        #result.duration = result.duration + 1

        # 止盈, 4个点 or 跌破五日均线
        if gain > 4:
            result.sell_price = float(buy_price)*1.04#high
            result.sell_date = trade_day
            self.strategy.cur_status.sell(result)
        '''if close < ma5:
            result.sell_price = close
            result.sell_date = trade_day
            self.strategy.cur_status.sell(result)'''

        #止损,跌破ma10
        if loss < -3 and close<ma10:
            result.sell_price = float(buy_price)*0.97
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
        self.title = '步步高升'

    def input_newkdata(self, kdata):
        #write to mysql
        ret = self.reslut
        self.dbadapter.GetDB().add_bt_strategy(ret.code, ret.buy_date,
                                               ret.buy_price, ret.sell_date, ret.sell_price, ret.duration, 2)

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
