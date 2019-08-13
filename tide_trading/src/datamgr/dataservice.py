#coding=utf-8
import h5py  #导入工具包
import numpy as np
import tushare as ts
import time
import datetime
import talib
import os
import pandas as pd

#定义全局变量
#股票列表文件
#file_codelist = 'stocklist.h5'

#股票详情
str_dailyFile = '../../data/stockdaily.h5'
#file_daily = h5py.File(str_dailyFile, 'a')
#a	Read/write if exists, create otherwise (default)
#r+	Read/write, file must exist
#w- or x	Create file, fail if exists
#r	Readonly, file must exist
#w	Create file, truncate if exists
#只处理数据
just_process = False

if just_process is False:
    if os.path.exists(str_dailyFile):
        os.remove(str_dailyFile)

file_daily = h5py.File(str_dailyFile, 'a')

#测试获取多少只股票
stockCnt = 3500
#从第几支股票开始
stockStart = 0
#每次取200只，休眠x秒
waitTime = 65
#

#初始化
def Init():
    ts.set_token('75f181a930dc581d82c0cafd633c09d582d8ac0554c74854f73a9582')

def GetToday():
    now_time = datetime.datetime.now()
    day = now_time.strftime('%Y%m%d')
    print('end time is ', day)
    return day

def UnInit():
    file_daily.close()

#函数：获取所有股票列表
def GetStockList():
    pro = ts.pro_api()
    # 查询当前所有正常上市交易的股票列表
    #data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
    print('股票总个数：', len(data))
    return data.head(stockCnt)

#函数：获取所有交易日期
def GetTradeDays(str_start_day, str_end_day):
    pro = ts.pro_api()
    # 查询当前所有正常上市交易的时间
    #data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data = pro.trade_cal(exchange='', start_date=str_start_day, end_date=str_end_day)

    idx = 0
    gotCnt = 0
    trade_days=[]
    for cal_date in data['cal_date']:
        gotCnt += 1

        is_open = data['is_open'][idx]

        if is_open==1:
            trade_days.append(cal_date)
        idx += 1

    print('股票从 ', str_start_day, '--- ', str_end_day, ' 一共交易天数：', len(data))
    return trade_days

#日线行情
#更新时间：交易日每天15点～16点之间
#函数：获取多只股票code的日线行情,写入h5文件
#日期都填YYYYMMDD格式，比如20181010
def GetDaily(codes, startDay, endDay):
    #已经获取的个数，受tushare限制，每分钟只能调用200次
    gotCnt = 0

    #股票列表正在处理第几只
    idx = 0
    pro = ts.pro_api()
    for code in codes['ts_code']:
        gotCnt += 1

        name = codes['name'][idx]
        symbol = codes['symbol'][idx]
        idx+=1
        #code= 000006.SZ   name= 深振业A   symbol= 000006
        print('code=', code, '  name=', name, '  symbol=', symbol)

        #从第N支股票开始获取，用于连接中断时，续传
        if gotCnt <= stockStart:
            continue

        try:
            if len(file_daily[code]) > 0:
                print('已经存在 ', code)
                continue
        except Exception as e:
            print('code=', code, 'not exist')

        #每取一次，休眠半秒
        time.sleep(0.1)

        #每次取150支股票，休眠90秒
        if gotCnt % 150 == 0:
            print('zzzzzzzzzzzzzzzzz need sleep  gotCnt=', gotCnt)
            time.sleep(waitTime)

        print(code)

        try:
            df = pro.daily(ts_code=code, start_date=startDay, end_date=endDay)
        except Exception as e:
            print('tushare error. daily. code=',code)

        if len(df)==0:
            print('error!!!!!!!!!!!!!!!\n')
            continue

        #print(dir(df))
        #print(type(df))
        #Write2HDF5(code,df.open)

        try:
            gStock = file_daily.create_group(code)

            # 交易日期,保存到h5文件
            dt = h5py.special_dtype(vlen=str)
            ds = gStock.create_dataset('trade_date', df.trade_date.shape, dtype=dt)
            ds[:] = df.trade_date[::-1]

            #gStock['date'] = list1
            # 开盘价  [::-1]表示倒序，日期越大，索引越大
            gStock['open'] = df.open[::-1]
            # 最高价
            gStock['high'] = df.high[::-1]
            # 最低价
            gStock['low'] = df.low[::-1]
            # 收盘价
            gStock['close'] = df.close[::-1]
            # 涨跌额
            gStock['change'] = df.change[::-1]
            # 涨跌幅
            gStock['pct_chg'] = df.pct_chg[::-1]
            # 成交量 （手）
            gStock['vol'] = df.vol[::-1]
            # 成交额 （千元）
            gStock['amount'] = df.amount[::-1]
            # 股票名称
            gStock['name'] = name
            # 股票代号
            gStock['symbol'] = symbol
        except Exception as e:
            print('e=', e)
        #print(">>>>>>>>>>>>>>>>>",gStock['name'].value)
    return df

#保存所有的交易日期
def save_trade_day(strade_day_name, strade_days):
    try:
        if len(file_daily[strade_day_name]) > 0:
            print('已经存在 ', strade_day_name)
            return
    except Exception as e:
        print('code=', strade_day_name, 'error')

    try:
        gTradeDay = file_daily.create_group(strade_day_name)

        ids_encode = list()
        for sd in strade_days:
            ids_encode.append(sd.encode())
        ids_encode = pd.Series(ids_encode)

        # 交易日期,保存到h5文件
        dt = h5py.special_dtype(vlen=str)
        ds = gTradeDay.create_dataset('trade_date', (len(ids_encode),), dtype=dt)
        ds[:] = ids_encode[:]
    except Exception as e:
        print('code=', strade_day_name, 'error')

#写入hdf5文件
def Write2HDF5(key, value):
    # 创建一个h5文件，文件指针是f
    print('key='+key)
    print(value)
    gStock = file_daily.create_group(key)
    gStock['open'] = value.open


#数据加工
#生成ma5，ma10，ma20，ma30，ma60
def DataProcess(list_code):
    for code in list_code['ts_code']:
        key = '/' + code
        try:
            all_close = file_daily[key + '/close'][:]
            all_vol = file_daily[key + '/vol'][:]

            #倒序
            close_all = all_close
            ma5 = talib.SMA(close_all, timeperiod=5)
            ma10 = talib.SMA(close_all, timeperiod=10)
            ma20 = talib.SMA(close_all, timeperiod=20)
            ma30 = talib.SMA(close_all, timeperiod=30)
            ma60 = talib.SMA(close_all, timeperiod=60)

            vol_all = all_vol
            ma5_vol = talib.SMA(vol_all, timeperiod=5)
            ma10_vol = talib.SMA(vol_all, timeperiod=10)
            ma20_vol = talib.SMA(vol_all, timeperiod=20)
            ma30_vol = talib.SMA(vol_all, timeperiod=30)

            #写入h5文件

            if file_daily.get(key + '/ma5') is None:
                file_daily[key + '/ma5'] = ma5

            if file_daily.get(key + '/ma10') is None:
                file_daily[key + '/ma10'] = ma10

            if file_daily.get(key + '/ma20') is None:
                file_daily[key + '/ma20'] = ma20

            if file_daily.get(key + '/ma30') is None:
                file_daily[key + '/ma30'] = ma30

            if file_daily.get(key + '/ma60') is None:
                file_daily[key + '/ma60'] = ma60

            if file_daily.get(key + '/ma5vol') is None:
                file_daily[key + '/ma5vol'] = ma5_vol

            if file_daily.get(key + '/ma10vol') is None:
                file_daily[key + '/ma10vol'] = ma10_vol

            if file_daily.get(key + '/ma20vol') is None:
                file_daily[key + '/ma20vol'] = ma20_vol

            if file_daily.get(key + '/ma30vol') is None:
                file_daily[key + '/ma30vol'] = ma30_vol

        except Exception as e:
            print('DataProcess  error,e=', e, 'code=', code)

'''        Write2HDF5('ma5', ma5)
        Write2HDF5('ma10', ma10)
        Write2HDF5('ma20', ma20)
        Write2HDF5('ma30', ma30)
        Write2HDF5('ma60', ma60)'''

#遍历H5文件中，所有股票的其中一个类型
def PrintH5():
    print('>>>>>>>>>>>>> loop h5 file keys  <<<<<<<<<<<<<<<<<<<<')
    for key in file_daily.keys():
        print(key)
        print(file_daily[key + '/open'][:])
        print(file_daily[key+'/close'][:])
        print(file_daily[key+'/pct_chg'][:])

def main():
    # 更新的起始时间
    str_start_day = '20171201'
    str_end_day = GetToday()

    print('***********  main **************')
    Init()
    list_trade_days = GetTradeDays(str_start_day, str_end_day)
    list_code = GetStockList()

    if not just_process:
        save_trade_day('trade_day', list_trade_days)
        GetDaily(list_code, str_start_day, str_end_day)

    DataProcess(list_code)
    UnInit()


if __name__ == '__main__':
    main()
