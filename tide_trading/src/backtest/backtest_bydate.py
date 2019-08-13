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
from src.common.status import State
import datetime
from multiprocessing import Pool #导入进程池

''' 回测模块：回测一天中，所有股票在该日期中的表现; 横向回测，不支持多进程 '''

log_name = '../../log/backtest_log'

def main():
    start_idx = 0
    end_idx = 3000
    #不使用多进程
    process(start_idx, end_idx)


def process(start_idx, end_idx):
    print("start=", start_idx, " end=", end_idx)

    my_log_filename = log_name + str(start_idx) + ".txt"

    if os.path.exists(my_log_filename):
        os.remove(my_log_filename)

    # input 股票详情
    str_filename = '../../data/stockdaily.h5'

    file_daily = h5py.File(str_filename, 'r')
    log = tools.CLogger('backtest', my_log_filename, 1)

    strMsg = 'open success, for start_idx='+str(start_idx)+'  end_idx='+str(end_idx)
    log.getLogger().info(strMsg)

    # 策略
    #strategy = strategy01.CStrategy01(file_daily)
    # 策略
    strategy = strategy06.CStrategy06(file_daily)

    #遍历所有交易日期
    strategy.Init()
    strategy.LoadData('trade_day')
    dates = strategy.allTradeDay

    # 回测最近N天数据
    N = 30
    idx_cnt = 0
    day_cnt = len(dates)

    strategy.stock_base_info.open_excel('每日涨停概念统计.xls')
    strategy.stock_base_info.write_excel(0, 0, '日期')
    strategy.stock_base_info.write_excel(0, 1, '概念')
    strategy.stock_base_info.write_excel(0, 2, '次数')
    #try:
    #    strategy.stock_base_info.write_excel(0, 0, 'aaa')
    #except Exception as e:
    #   print('')

    row = 1
    col = 0
    for date in dates:
        if idx_cnt < day_cnt - N:
            idx_cnt += 1
            continue

        consept_count = process_oneday(strategy, file_daily, date)

        idx_cnt += 1

        #遍历所有的概念
        for cc in consept_count.keys():
            print('date = ', date, ' conseption  = ', cc, ' count=', consept_count[cc])
            strategy.stock_base_info.write_excel(row, col, date)
            col += 1
            strategy.stock_base_info.write_excel(row, col, cc)
            col += 1
            strategy.stock_base_info.write_excel(row, col, consept_count[cc])
            row += 1
            col = 0
            # else:
            #   print('have no my data')

    strategy.stock_base_info.close_excel()

def process_oneday(strategy, file_daily, date):
    cur_code_idx = 0
    ##记录每只股票在当天的涨幅
    #字典《//code.SZ,0.9》
    gains = dict()
    #print('加载股票数据')
    for key in file_daily.keys():
        if key is 'trade_day':
            continue

        cur_code_idx += 1

        code = file_daily[key].name

        #hdf5数据有点问题
        #if cur_code_idx > 2900 or cur_code_idx < 2800:
        #    continue

        #加载该股票所有的数据
        strategy.LoadData(code)

        cur_idx = 0
        #print('筛选 ',code,' 数据之：',date)
        for one_day in strategy.code_trade_day:
            if date == one_day:
                gain = strategy.pct_chg[cur_idx]
                #记录每只股票在当天的涨幅
                #gains.update({code, gain})
                gains[code] = gain
            cur_idx += 1

    #统计根据概念出现的次数
    consept_count = dict()

    for code in gains:
        #打印涨幅>9%的个股
        if(gains[code] > 9):
            stock_code = code[1:]
            my_stock = strategy.stock_base_info.get_stock_info(stock_code)
            conseptions = my_stock.get_conseption()
            print('date=', date, '  code=', stock_code, '  gain=', gains[code])
            #遍历股票的所属概念
            for consept in my_stock.get_conseption():
                print(consept)
                if consept in consept_count:
                    count = consept_count[consept]
                    consept_count[consept] = count + 1
                else:
                    consept_count[consept] = 1

    return consept_count


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    main()
    endtime = datetime.datetime.now()
    print('回测用时(秒)：', (endtime - starttime).seconds)

