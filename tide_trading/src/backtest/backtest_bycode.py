# coding=utf-8
#import strategy01
#import strategybase as sttbase
#import strategy02
#import strategy04
#import strategy05
import src.strategy.strategy06 as strategy06
import statistics as st
import h5py  #导入工具包
import src.common.tools as tools
import sys
import os
import src.common.statistics as statistics
import datetime
import src.datamgr.dbadapter as dbadapter
import matplotlib.pyplot as plt
#导入中文字体，避免显示乱码
import pylab as mpl
import numpy as np
from multiprocessing import Pool #导入进程池

import src.datamgr.dbmgr as dbmgr
import pandas as pd
import src.common.conf as conf
import src.stockselector.wbottom as wbottom
import src.backtest.backtest_bycode_status as backtest_bycode_status
''' 回测模块，每次回测一支股票的所有日期，k线数据 '''


#回测结果
class CBT_Result:
    def __init__(self):
        # 买卖信息
        self.buy_price = 0.0
        self.buy_date = ''
        self.sell_price = 0.0
        self.sell_date = ''
        self.code = ''
        self.duration = 0

class CBackTestBycode:
    def __init__(self, str_conf_path, log):
        self.dbadapter = dbadapter.CDBAdapter(str_conf_path, log)
        self.log = log
        self.start_day = ''
        self.wbottom = wbottom.CWBotton(self.dbadapter.db, log)

        #状态：选股状态  持股状态  卖出状态
        self.status_select = backtest_bycode_status.CBT_SelectStatus(self, str_conf_path, log)
        self.status_hold = backtest_bycode_status.CBT_HoldStatus(self, str_conf_path, log)
        self.status_sold = backtest_bycode_status.CBT_SoldStatus(self, str_conf_path, log)
        self.cur_status = self.status_select

        self.m_statistics = statistics.CStatistics()

    #进程结束以后，进入回调函数
    def process_callback(self, x):
        pass

    # 根据sql语句的select内容，进行转换
    def QueryAllTradeDays(self):
        result = self.db.query_tradeday()

        df = pd.DataFrame(list(result), columns=['trade_day'])
        # print(df)
        return df

    # 获取所有离线的交易日期，mysql
    def GetOfflineTradeDays(self):
        trade_days = []
        # 离线数据
        data = self.QueryAllTradeDays()
        for i in data['trade_day']:
            trade_days.append(i)

        return trade_days

    #处理一支股票
    def __process(self, code):

        self.cur_status = self.status_select
        #print('backtest_bcode::__process  ... code=', code)
        today = self.dbadapter.GetToday()
        all_stock_kdata = self.dbadapter.QueryRangeKData(code, self.start_day, today)

        # 交易日小于60日，不处理
        if all_stock_kdata is None or len(all_stock_kdata) < 60:
            print(code, 'is empty! --- wbottom.py Process')
            return

        min_base_count = 60
        max_count = len(all_stock_kdata)
        #1. 先取最前N个交易日的Kdata，作为基础数据
        for i in range(min_base_count, max_count, 1):
            all_stock_kdata_part = all_stock_kdata[0:i]

            self.input_new_data(all_stock_kdata_part)

            '''
            #卖出状态，写数据库
            if self.cur_status.get_status() is self.status_sold.get_status():
                ret = self.cur_status.get_result()
                if ret is not None:
                    #写mysql
                    self.dbadapter.GetDB().add_bt_strategy(ret.code, ret.buy_date,
                                                           ret.buy_price, ret.sell_date, ret.sell_price, ret.duration, 1)
                    #print(ret_tmp.sell_date)
                    gain = (ret.sell_price - ret.buy_price) / ret.buy_price
                    gain = round(gain * 100, 2)
                    if gain > 0:
                        print(code,'  buy date=',ret.buy_date," 盈利：",gain, '  sell date=',ret.sell_date)
                    else:
                        print(code,'  buy date=', ret.buy_date, " 亏损：", gain, '  sell date=', ret.sell_date)
            '''
            #2. 一个一个交易日加入到策略
            #self.wbottom.Init(10, self.start_day, today, self.selected_callback)
            #self.wbottom.ProcessEx(all_stock_kdata_part)
            #self.wbottom.UnInit()
            #3. 策略给出状态：需要下一个数据、持有、卖出、统计等

        #ret = self.cur_status.get_result()
        self.cur_status.statistics()

    #加入日K数据源
    def input_new_data(self, kdata):
        self.cur_status.input_newkdata(kdata)

    #买入
    def buy(self, res):
        self.cur_status.buy(res)

    #统计
    def statistics(self):
        #1. 从mysql读取数据
        #"ts_code", "buydate", "buyprice", "selldate", "sellprice", "duration", "strategyid"
        df = self.dbadapter.QueryBTStrategy(id=1)

        #2. 统计某一个卖出时间，对应的涨跌幅平均值
        list_selldate = list()
        list_gain = list()

        selldate=''
        gain = 0
        count = 1
        for row in df.values:
            buyprice = row[2]
            sellprice = row[4]
            #涨跌幅
            cur_gain = self.m_statistics.calc_gain(sellprice, buyprice)

            #第一次，直接赋值
            if selldate == '':
                selldate = row[3]

            try:
                #相同日期，取涨跌幅的平均值
                if selldate == row[3]:
                    count = count + 1
                    gain = gain + float(cur_gain)
                    continue
                else:
                    #日期发生变化，统计前一个交易日的卖出
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

            #print(row[0], '  ', row[1], '  ', row[2], '  ', row[3])
        print(list_selldate)
        print(list_gain)

        self.draw(list_selldate, list_gain)

    def draw(self, list_date, list_y):
        mpl.rcParams['font.sans-serif'] = ['simhei']
        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['axes.unicode_minus'] = False

        # 生成figure对象,相当于准备一个画板
        fig = plt.figure(figsize=(8, 3))

        # 生成axis对象，相当于在画板上准备一张白纸，111，11表示只有一个表格，第3个1，表示在第1个表格上画图
        ax = fig.add_subplot(111)
        plt.title('双底策略')
        plt.xlabel(u'交易日')
        plt.ylabel(u'盈亏百分比')

        # 将字符串的日期，转换成日期对象
        xs = [datetime.datetime.strptime(d, '%Y%m%d').date() for d in list_date]

        # 日期对象作为参数设置到横坐标,并且使用list_date中的字符串日志作为对象的标签（别名）
        # x坐标的刻度值
        ar_xticks = np.arange(1, len(list_date) + 1, step=1)
        plt.xticks(ar_xticks, list_date, rotation=90, fontsize=10)
        plt.yticks(np.arange(0, 30, step=2), fontsize=10)
        ax.plot(ar_xticks, list_y, color='r')

        # 下方图片显示不完整的问题
        plt.tight_layout()

        # 在点阵上方标明数值
        for x, y in zip(ar_xticks, list_y):
            plt.text(x, y + 0.3, str(y), ha='center', va='bottom', fontsize=10)

        plt.show()


    # 选股成功，满足策略， 买买买
    def selected_callback(self, code, bottom1, bottom2, trade_day_b1, trade_day_b2, cur_trade_day, min_interval, price):
        print(code, '   ', cur_trade_day)
        cur_day = datetime.datetime.now().strftime('%Y%m%d')
        cur_time = datetime.datetime.now().strftime('%H:%M:%S')

        #每个状态对象都持有一个结果数据，在一次完整的买卖策略过程中，每个状态的结果相互传递，保持一致
        res = CBT_Result()
        res.buy_price = price
        res.buy_date = cur_trade_day
        res.code = code
        self.buy(res)

    def process(self, start_day):
        self.start_day = start_day
        print("start=", self.start_day)
        self.log.info("start=" + self.start_day)

        #首先从mysql删除双底策略的结果
        self.dbadapter.GetDB().delete_bt_strategy(1)

        #获取股票列表
        df_stock_basic = self.dbadapter.GetStockBasic()
        list_code = list(df_stock_basic['ts_code'])
        for code in list_code:
            self.__process(code)

        self.statistics()


def main():
    ##############################################################################################
    # 配置文件路径
    cur_path = os.getcwd()
    print(cur_path)
    str_conf_path = cur_path + '/../../conf/conf.ini'

    # 日志唯一
    g_conf = conf.CConf(str_conf_path)
    filename_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    log_filename = cur_path + '/../../' + g_conf.log_dir + '/backtest_' + filename_time + '.log'
    log = tools.CLogger(g_conf.app_name, log_filename, 1).getLogger()
    ##############################################################################################

    starttime = datetime.datetime.now()
    backtest = CBackTestBycode(str_conf_path, log)
    #回测时间范围：起始日期到最近一个交易日
    start_day = '20190115'
    backtest.process(start_day)

    endtime = datetime.datetime.now()
    print('回测用时(秒)：', (endtime - starttime).seconds)
    backtest.log.info('回测用时(秒)：'+ str((endtime - starttime).seconds))

def shutdown(sec):
    # N秒后关机
    cmd = 'shutdown -s -t ' + str(sec)
    os.system(cmd)

if __name__ == '__main__':
    main()
    #shutdown(10)

