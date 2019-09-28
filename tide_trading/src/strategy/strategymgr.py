#coding=utf-8
from src.strategy.strategybase import CStrategyBase as strategybase
import src.datamgr.dbadapter as dbadapter
from src.backtest.backtest_bycode import CBT_Result as CBT_Result
import src.common.statistics as statistics
import datetime

'''
#双底
from src.backtest.bt_wbottom_status import CBT_WBottomSelectStatus as CBT_SelectStatus
from src.backtest.bt_wbottom_status import CBT_WBottomHoldStatus as CBT_HoldStatus
from src.backtest.bt_wbottom_status import CBT_WBottomSoldStatus as CBT_SoldStatus
'''

#小阳线
from src.backtest.bt_littlestep_status import CBT_LittleStepSelectStatus as CBT_SelectStatus
from src.backtest.bt_littlestep_status import CBT_LittleStepHoldStatus as CBT_HoldStatus
from src.backtest.bt_littlestep_status import CBT_LittleStepSoldStatus as CBT_SoldStatus

'''
策略管理者
管理具体的策略，策略的切换，是回测模块与策略算法的桥梁
'''
class CStrategyMgr(strategybase):
    def __init__(self, str_conf_path, log):
        self.dbadapter = dbadapter.CDBAdapter(str_conf_path, log)
        self.log = log
        self.start_day = ''

        #状态：选股状态  持股状态  卖出状态
        self.status_select = CBT_SelectStatus(self, str_conf_path, log)
        self.status_hold = CBT_HoldStatus(self, str_conf_path, log)
        self.status_sold = CBT_SoldStatus(self, str_conf_path, log)
        self.cur_status = self.status_select

        self.m_statistics = statistics.CStatistics()

    def get_status(self):
        return self.cur_status

    # 加入日K数据源
    def input_new_data(self, kdata):
        self.cur_status.input_newkdata(kdata)

    # 买入
    def buy(self, res):
        self.cur_status.buy(res)

    # 选股成功，满足策略， 买买买
    def selected_callback(self, code, bottom1, bottom2, trade_day_b1, trade_day_b2, cur_trade_day, min_interval,
                          price):
        print(code, '   ', cur_trade_day)
        cur_day = datetime.datetime.now().strftime('%Y%m%d')
        cur_time = datetime.datetime.now().strftime('%H:%M:%S')

        # 每个状态对象都持有一个结果数据，在一次完整的买卖策略过程中，每个状态的结果相互传递，保持一致
        res = CBT_Result()
        res.buy_price = price
        res.buy_date = cur_trade_day
        res.code = code
        self.buy(res)

    # 统计
    def statistics(self):
        # 1. 从mysql读取数据
        # "ts_code", "buydate", "buyprice", "selldate", "sellprice", "duration", "strategyid"
        df = self.dbadapter.QueryBTStrategy(id=1)

        # 2. 统计某一个卖出时间，对应的涨跌幅平均值
        list_selldate = list()
        list_gain = list()

        selldate = ''
        gain = 0
        count = 1
        for row in df.values:
            buyprice = row[2]
            sellprice = row[4]
            # 涨跌幅
            cur_gain = self.m_statistics.calc_gain(sellprice, buyprice)

            # 第一次，直接赋值
            if selldate == '':
                selldate = row[3]

            try:
                # 相同日期，取涨跌幅的平均值
                if selldate == row[3]:
                    count = count + 1
                    gain = gain + float(cur_gain)
                    continue
                else:
                    # 日期发生变化，统计前一个交易日的卖出
                    if count > 0:
                        list_gain.append(round(gain / count, 2))
                        list_selldate.append(selldate)

                    count = 1
                    gain = float(cur_gain)
            except Exception as e:
                print(e)

            #            list_gain.append(gain/count)
            #            list_selldate.append(selldate)
            selldate = row[3]

            # print(row[0], '  ', row[1], '  ', row[2], '  ', row[3])
        print(list_selldate)
        print(list_gain)

        self.draw(list_selldate, list_gain)





