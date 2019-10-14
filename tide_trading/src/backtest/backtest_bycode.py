# coding=utf-8
import src.common.tools as tools
import os
import src.common.statistics as statistics
import datetime
import src.datamgr.dbadapter as dbadapter
import src.common.conf as conf
#import src.stockselector.wbottom as wbottom
from multiprocessing import Pool #导入进程池

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
        #仓位
        self.position = 0.5

class CBackTestBycode:
    def __init__(self, str_conf_path, log):
        self.dbadapter = dbadapter.CDBAdapter(str_conf_path, log)
        self.log = log
        self.start_day = ''
        #self.wbottom = wbottom.CWBotton(self.dbadapter.db, log)

        #策略
        self.strategy = strategymgr.CStrategyMgr(str_conf_path, log)
        self.strategy.start_day = '20171201'

        #self.m_statistics = statistics.CStatistics()

        #调试单个，不删除结果
        self.debug_one = False

    #处理一支股票
    def __process(self, code):

        #test
        if self.debug_one is True and code != '002409.SZ':
            return

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

    #加入日K数据源
    def input_new_data(self, kdata):
        try:
            self.strategy.input_new_data(kdata)
        except Exception as e:
            print(e)

    #多进程处理
    def process(self, start_day, process_cnt, cur_idx):
        self.start_day = start_day
        print("start=", self.start_day, ' process_cnt=', process_cnt, '  cur_idx=', cur_idx)
        self.log.info("start=" + self.start_day)

        #首先从mysql删除双底策略的结果
        #1 双底，2 小阳
        if self.debug_one is False:
            self.dbadapter.GetDB().delete_bt_strategy(2)

        #获取股票列表
        df_stock_basic = self.dbadapter.GetStockBasic()
        list_code = list(df_stock_basic['ts_code'])

        ###########################################################
        count_codes = len(list_code)
        # python中的除法运算,向上取整
        average = (count_codes + process_cnt) // process_cnt

        # 给每个进程，分配N个股票任务
        left_idx = average * cur_idx
        right_idx = left_idx + average

        if right_idx >= count_codes:
            right_idx = -1

        part_list_code = list_code[left_idx:right_idx]
        print('left=', left_idx, '  right=', right_idx, ' cur_idx=', cur_idx)

        # 不使用多进程
        for code in part_list_code:
            self.__process(code)

        #self.strategy.statistics()

#统计
def statistics():
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

    backtest = CBackTestBycode(str_conf_path, log)
    backtest.strategy.statistics()

#进程结束以后，进入回调函数
def process_callback(x):
    pass

def process(process_cnt, cur_idx):
    print(cur_idx)
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

    backtest = CBackTestBycode(str_conf_path, log)
    #回测时间范围：起始日期到最近一个交易日
    start_day = '20180101'
    backtest.process(start_day, process_cnt, cur_idx)

def main():
    # 进程池里进程个数,大于1：多进程
    process_cnt = 4

    starttime = datetime.datetime.now()
    ##############################################################################################
    start_idx = 0
    end_idx = 3000
    # 使用多进程
    if process_cnt > 1:
        process_pool = Pool(process_cnt)

        for cur_idx in range(0, process_cnt):
            process_pool.apply_async(process, (process_cnt, cur_idx,), callback=process_callback)

        process_pool.close()
        process_pool.join()
    else:
        # 不使用多进程
        process(start_idx, end_idx)
    ##################################################################
    '''backtest = CBackTestBycode(str_conf_path, log)
    #回测时间范围：起始日期到最近一个交易日
    start_day = '20180101'
    backtest.process(start_day)'''

    endtime = datetime.datetime.now()
    print('回测用时(秒)：', (endtime - starttime).seconds)

    # 最后统计
    statistics()
    #backtest.log.info('回测用时(秒)：'+ str((endtime - starttime).seconds))

def shutdown(sec):
    # N秒后关机
    cmd = 'shutdown -s -t ' + str(sec)
    os.system(cmd)

if __name__ == '__main__':
    main()
    #shutdown(10)

