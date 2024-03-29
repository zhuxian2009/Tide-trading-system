# coding=utf-8
import src.common.tools as tools
import os
import datetime
from multiprocessing import Pool #导入进程池
import src.datamgr.dbmgr as dbmgr
import pandas as pd
import src.stockselector.wbottom as wbottom

''' 回测模块：回测一天中，所有股票在该日期中的表现; 横向回测，不支持多进程 '''

class CBackTestBydate:
    def __init__(self):
        self.log_name = '../../log/backtest_log'
        self.use_mul_process = 0
        # 进程池里进程个数
        self.process_cnt = 3
        self.db = dbmgr.CDBMgr('localhost', 'root', '123', 'kdata')


        #以时间命名日志文件
        cur_time = datetime.datetime.now()
        log_filename = datetime.datetime.strftime(cur_time, '%Y%m%d_%H%M%S')
        my_log_filename = self.log_name + log_filename + ".txt"
        self.log = tools.CLogger('backtest', my_log_filename, 1)



    #进程结束以后，进入回调函数
    def process_callback(self,x):
        pass

    # 根据sql语句的select内容，进行转换
    def QueryAllStockBasic(self):
        result = self.db.query_allstockbasic()

        try:
            df = pd.DataFrame(list(result), columns=["ts_code", "symbol", "name", "area", "market", "list_status"])
        except Exception as e:
            print(e)
        # df = pd.DataFrame(list(result))
        # print(df)
        return df

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

    def process(self, start_day, end_day):
        print("start=", start_day, " end=", end_day)
        self.log.getLogger().info("start=" + start_day + " end=" + end_day)

        #if os.path.exists(my_log_filename):
        #    os.remove(my_log_filename)

        #首次投入基础数据的数量
        base_count = 60

        #获取交易日期列表
        list_trade_day = self.GetOfflineTradeDays()

        #获取股票列表
        #list_stock_basic = self.QueryAllStockBasic()
        #for code in list_stock_basic['ts_code']:
        temp = base_count

        #从设定的开始日期，每次往后取base_count天数据，计算；
        # 计算一次以后，起始日期往后移动一天
        #例如：20190508~20190830，第一次回测数据是：20190508~20190802
        for day in list_trade_day:
            #不在指定区间的日期，不处理
            if day <= start_day or day >= end_day:
                print('start_day=', start_day, '  lost day=', day)
                continue

            #保证每次进行计算的kdata数量，等于base_count天
            if temp > 0:
                temp -= 1
                continue

            #区间范围取值
            for r in range(10, 30):
                my_selector = wbottom.CWBotton()
                my_selector.Init(r, start_day, day)
                print("process.... range=", r, ' startday=', start_day, ' endday=', day)
                self.log.getLogger().info("process.... range=" + str(r) + ' startday=' + start_day + ' endday=' + day)
                my_selector.Process()
                my_selector.UnInit()

def main():
    starttime = datetime.datetime.now()
    backtest = CBackTestBydate()
    start_day = '20190515'
    end_day = '20190830'
    #使用多进程
    if backtest.use_mul_process:
        process_pool = Pool(backtest.process_cnt)
        '''
        #python中的除法运算
        average = (end_idx - start_idx) // dataservice.process_cnt
        #给每个线程，分配N个股票任务
        start_pos = -1
        end_pos = -1

        for i in range(1, dataservice.process_cnt+1):
            start_pos = end_pos + 1
            end_pos = start_idx + average*i

            if i is dataservice.process_cnt:
                end_pos = end_idx

            #process(start_pos, end_pos)
            process_pool.apply_async(dataservice.process, (start_pos, end_pos, ), callback=dataservice.process_callback)

        process_pool.close()
        process_pool.join()'''
    else:
        #不使用多进程
        backtest.process(start_day, end_day)

    endtime = datetime.datetime.now()
    print('回测用时(秒)：', (endtime - starttime).seconds)
    backtest.log.getLogger().info('回测用时(秒)：'+ str((endtime - starttime).seconds))

def shutdown(sec):
    # N秒后关机
    cmd = 'shutdown -s -t ' + str(sec)
    os.system(cmd)

if __name__ == '__main__':
    main()
    #shutdown(10)

