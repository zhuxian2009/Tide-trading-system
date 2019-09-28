# coding=utf-8
import src.common.tools as tools
import os
import src.common.statistics as statistics
import datetime
import src.datamgr.dbadapter as dbadapter
import src.common.conf as conf
import src.stockselector.wbottom as wbottom

#策略
import src.strategy.strategymgr as strategymgr

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

        #策略
        self.strategy = strategymgr.CStrategyMgr(str_conf_path, log)
        self.strategy.start_day = '20190101'

        #self.m_statistics = statistics.CStatistics()


    #进程结束以后，进入回调函数
    def process_callback(self, x):
        pass

    '''# 根据sql语句的select内容，进行转换
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

        return trade_days'''

    #处理一支股票
    def __process(self, code):
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

            #2. 一个一个交易日加入到策略
            #self.wbottom.Init(10, self.start_day, today, self.selected_callback)
            #self.wbottom.ProcessEx(all_stock_kdata_part)
            #self.wbottom.UnInit()
            #3. 策略给出状态：需要下一个数据、持有、卖出、统计等

        #ret = self.cur_status.get_result()
        #self.statistics()

    #加入日K数据源
    def input_new_data(self, kdata):
        try:
            self.strategy.input_new_data(kdata)
        except Exception as e:
            print(e)


    #买入
    def buy(self, res):
        self.strategy.buy(res)

    #统计
    def statistics(self):
        self.strategy.statistics()

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
    start_day = '20180101'
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

