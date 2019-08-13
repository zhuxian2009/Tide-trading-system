# coding=utf-8
#import strategy01
#import strategybase as sttbase
#import strategy02
#import strategy04
#import strategy05
import src.strategy.strategy06 as strategy06
import src.common.statistics as st
import h5py  #导入工具包
import src.common.tools as tools
import sys
import os
from src.common.status import State
import datetime
from multiprocessing import Pool #导入进程池

''' 回测模块，每次回测一支股票的所有日期，k线数据 '''
log_name = '../../log/backtest_log'
use_mul_process = 0
#进程池里进程个数
process_cnt = 3

#进程结束以后，进入回调函数
def process_callback(x):
    pass


def main():
    start_idx = 0
    end_idx = 3000
    #使用多进程
    if use_mul_process:
        process_pool = Pool(process_cnt)

        #python中的除法运算
        average = (end_idx - start_idx) // process_cnt
        #给每个线程，分配N个股票任务
        start_pos = -1
        end_pos = -1

        for i in range(1, process_cnt+1):
            start_pos = end_pos + 1
            end_pos = start_idx + average*i

            if i is process_cnt:
                end_pos = end_idx

            #process(start_pos, end_pos)
            process_pool.apply_async(process, (start_pos, end_pos, ), callback=process_callback)

        process_pool.close()
        process_pool.join()
    else:
        #不使用多进程
        process(start_idx, end_idx)


def process(start_idx, end_idx):
    print("start=", start_idx, " end=", end_idx)

    my_log_filename = log_name + str(start_idx) + ".txt"

    if os.path.exists(my_log_filename):
        os.remove(my_log_filename)

    #首次投入基础数据的数量
    base_count = 70

    # input 股票详情
    str_filename = '../../data/stockdaily.h5'

    file_daily = h5py.File(str_filename, 'r')
    log = tools.CLogger('backtest', my_log_filename, 1)

    strMsg = 'open success, for start_idx='+str(start_idx)+'  end_idx='+str(end_idx)
    log.getLogger().info(strMsg)

    # 策略1
    #strategy = strategy01.CStrategy01(file_daily)
    # 策略2
    strategy = strategy06.CStrategy06(file_daily)

    cur_code_idx = 0

    for key in file_daily.keys():
        cur_code_idx += 1
        #不属于自己的股票，不处理
        if cur_code_idx not in range(start_idx, end_idx+1):
            continue

        code = file_daily[key].name
        strategy.Init()
        strategy.LoadData(code, base_count)

        print('process ... ', cur_code_idx, ' code=', code)

        myStati = st.CStatistics()

        # 股票符号，如000001
        stockSymbol = file_daily[code + '/symbol'].value

        # 股票名
        stockName = file_daily[code + '/name'].value

        #取后续一天一天的数据，模拟新数据
        key = '/' + code
        totalCnt = len(file_daily[key + '/close'][:])
        for i in range(totalCnt-base_count):
            newIdx = i+base_count
            close_price = file_daily[key + '/close'][newIdx]
            open_price = file_daily[key + '/open'][newIdx]
            low_price = file_daily[key + '/low'][newIdx]
            high_price = file_daily[key + '/high'][newIdx]
            vol = file_daily[key + '/vol'][newIdx]

            trade_date = file_daily[key + '/trade_date'][newIdx]
            #输入一天数据
            state = strategy.FeedOneData(close_price, open_price, low_price, high_price, vol)
            if state is State.view:
                print(sys._getframe().f_code.co_name, sys._getframe().f_lineno,':',
                       code, '开始观察, state=', state, ' date=', trade_date)
            elif state is State.out_view:
                print(sys._getframe().f_code.co_name, sys._getframe().f_lineno, ':',
                       code, ' , 退出观察 state=', state, ' date=', trade_date, end='\n\n')
            elif state is State.buy:
                #买入的价格
                #myStati.set_buy_info((high_price + low_price)/2)
                myStati.set_buy_info(strategy.buy_price, trade_date)

                strLog = "%s%d,code=%s,买入 state=%s  date=%s open=%.2f,close=%.2f"%(
                    sys._getframe().f_code.co_name, sys._getframe().f_lineno, code, state, trade_date, open_price,
                    close_price)

                # 给日志加锁
                log.getLogger().info(strLog)

            elif state is State.sell:
                #卖出的价格
                #myStati.set_sell_info((high_price + low_price) / 2)
                myStati.set_sell_info(strategy.sell_price, trade_date)

                strLog = "%s%d,code=%s,卖出 state=%s  date=%s open=%.2f,close=%.2f" % (
                sys._getframe().f_code.co_name, sys._getframe().f_lineno, code, state, trade_date, open_price,
                close_price)

                #写多个日志文件  不需要加锁
                log.getLogger().info(strLog)
                #统计卖出后的盈亏
                myStati.statistics(code)


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    main()
    endtime = datetime.datetime.now()
    print('回测用时(秒)：', (endtime - starttime).seconds)

