#coding=utf-8
import sys
#print(os.getcwd())
sys.path.append('E:\\workspace\\stock\\hdf5test')

import numpy as np
import tushare as ts
import time
import datetime
import talib
import pandas as pd
import src.datamgr.dbmgr as dbmgr
import src.common.conf as conf
import logging
import os

class CDataServiceMysql:
    def __init__(self, str_conf_path, log):
        self.log = log
        # 只处理数据,否则更新实时数据到数据库
        self.just_process = False
        #更新一部分最新的k线数据;否则全部更新
        self.b_updata_part = True

        # 测试获取多少只股票
        self.stockCnt = 3651
        # 从第几支股票开始
        self.stockStart = 0
        self.conf = conf.CConf(str_conf_path)
        self.work_path = os.getcwd()
        # 每次取200只，休眠x秒
        #self.waitTime = 65
        self.db = dbmgr.CDBMgr(self.conf.db_host, self.conf.db_username, self.conf.db_pwd, 'kdata')
        self.init()
#定义全局变量
#股票列表文件
#file_codelist = 'stocklist.h5'

#file_daily = h5py.File(str_dailyFile, 'a')
#a	Read/write if exists, create otherwise (default)
#r+	Read/write, file must exist
#w- or x	Create file, fail if exists
#r	Readonly, file must exist
#w	Create file, truncate if exists

#

#初始化
    def init(self):
        cur_time = datetime.datetime.now()
        log_filename = datetime.datetime.strftime(cur_time, '/log/dataservice_mysql_%Y%m%d_%H%M%S')
        #log_filename = self.work_path + log_filename
        #logging.basicConfig(filename=log_filename+".log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
        #                    datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
        ts.set_token('75f181a930dc581d82c0cafd633c09d582d8ac0554c74854f73a9582')
        print(ts.__version__)
        logging.debug('init... ts.set_token OK!')

    #mydbmgr = dbmgr.CDBMgr('localhost', 'root', '123', 'kdata')
    #mydbmgr.connect_db()
    #mydbmgr.create_table()
    #mydbmgr.add_kdata('000001',11.38,11.36,11.55,11.28,754246)

    def GetToday(self):
        now_time = datetime.datetime.now()
        day = now_time.strftime('%Y%m%d')
        print('end time is ', day)
        return day

    def UnInit(self):
        pass

    # 根据sql语句的select内容，进行转换
    def QueryAllStockBasic(self):
        result = self.db.query_allstockbasic()

        try:
            df = pd.DataFrame(list(result), columns=["ts_code", "symbol", "name", "area", "market", "list_status"])
        except Exception as e:
            print(e)
        #df = pd.DataFrame(list(result))
        # print(df)
        return df

    #函数：获取所有股票名称列表
    def GetStockList(self):
        if self.just_process is False:
            pro = ts.pro_api()
            # 查询当前所有正常上市交易的股票列表
            #data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,market,list_status')

            # 使用values可以查看DataFrame里的数据值，返回的是一个数组
            arrayAllInfo = data.values

            # 遍历
            for arrayOne in reversed(arrayAllInfo):
                # 列： ts_code,symbol,name,area,market,list_status
                # 索引：    0    1      2    3    4       5
                self.db.add_stockbasic(arrayOne[0], arrayOne[1], arrayOne[2], arrayOne[3], arrayOne[4], arrayOne[5])
        else:
            #ts_code, symbol, name, area, market, list_status
            data = self.QueryAllStockBasic()

        print('股票总个数：', len(data))
        logging.debug('股票总个数：' + str(len(data)))
        return data.head(self.stockCnt)

    # 根据sql语句的select内容，进行转换
    def QueryAllTradeDays(self):
        result = self.db.query_tradeday()

        df = pd.DataFrame(list(result), columns=['trade_day'])
        # print(df)
        return df

    #获取所有在线的交易日期，tushare
    def GetOnlineTradeDays(self, str_start_day, str_end_day):
        trade_days = []
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的时间
        # data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        data = pro.trade_cal(exchange='', start_date=str_start_day, end_date=str_end_day)
        idx = 0
        gotCnt = 0

        for cal_date in data['cal_date']:
            gotCnt += 1

            is_open = data['is_open'][idx]

            if is_open == 1:
                trade_days.append(cal_date)
            idx += 1
        print('tushare 在线数据，股票从 ', str_start_day, '--- ', str_end_day, ' 一共交易天数：', len(data))
        logging.debug('股票从 ' + str_start_day + '--- ' + str_end_day + ' 一共交易天数：' + str(len(data)))
        return trade_days

    # 获取所有离线的交易日期，mysql
    def GetAllOfflineTradeDays(self):
        trade_days = []
        # 离线数据
        data = self.QueryAllTradeDays()
        for i in data['trade_day']:
            trade_days.append(i)

        print('mysql离线数据  一共交易天数：', len(data))
        logging.debug('股票从   一共交易天数：' + str(len(data)))
        return trade_days

    #函数：获取所有交易日期
    def GetTradeDays(self, str_start_day, str_end_day):

        trade_days = []

        if self.just_process is False:
            pro = ts.pro_api()

            # 查询当前所有正常上市交易的时间
            #data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            data = pro.trade_cal(exchange='', start_date=str_start_day, end_date=str_end_day)
            idx = 0
            gotCnt = 0

            for cal_date in data['cal_date']:
                gotCnt += 1

                is_open = data['is_open'][idx]

                if is_open == 1:
                    trade_days.append(cal_date)
                idx += 1
        else:
            #离线数据
            #data = self.QueryAllTradeDays()
            #for i in data.iterrows():
            #    trade_days.append(i)
            trade_days = self.GetAllOfflineTradeDays()

        print('股票从 ', str_start_day, '--- ', str_end_day, ' 一共交易天数：', len(trade_days))
        logging.debug('股票从 ' + str_start_day + '--- ' + str_end_day + ' 一共交易天数：' + str(len(trade_days)))
        return trade_days

    #tushare获取日线行情
    #更新时间：交易日每天15点～16点之间
    #函数：获取多只股票code的日线行情,写入数据库
    #日期都填YYYYMMDD格式，比如20181010
    def GetOnlineKData(self, codes, startDay, endDay):
        #已经获取的个数，受tushare限制，每分钟只能调用200次
        gotCnt = 0

        #上一次调用接口时间
        last_calltime = datetime.datetime.now()
        #一定时间内，调用接口次数
        call_times = 0

        # 清空“下载数据表”
        self.db.truncate_kdata_down()

        #股票列表正在处理第几只
        idx = 0
        pro = ts.pro_api()
        for code in codes['ts_code']:
            gotCnt += 1

            name = codes['name'][idx]
            symbol = codes['symbol'][idx]
            idx += 1
            #code= 000006.SZ   name= 深振业A   symbol= 000006
            print('code=', code, '  name=', name, '  symbol=', symbol)
            #logging.debug('code='+ code+ '  name='+ name+ '  symbol='+ symbol)

            #从第N支股票开始获取，用于连接中断时，续传
            if gotCnt <= self.stockStart:
                continue
            '''
            try:
                ret = self.db.exist_kdata(code)
                if ret > 0:
                    print('已经存在 ', code)
                    continue
            except Exception as e:
                print('code=', code, 'not exist')
                '''
            print("GetOnlineKData..."+code)
            logging.debug("GetOnlineKData..."+code)
			
            df=None
            try:
                #返回dataframe结构：ts_code/trade_date/open/high/low/close/pre_close/change/pct_chg/vol/amount
                #df = pro.daily(ts_code=code, start_date=startDay, end_date=endDay)

                #qfq,前复权； hfq,后复权
                #返回dataframe结构：ts_code/trade_date/open/high/low/close/pre_close/change/pct_chg/vol/amount
                #老版本1.2.18写法
                #df = ts.pro_bar(ts_code=code, pro_api=pro, adj='qfq', start_date=startDay,end_date=endDay,retry_count=10)
                # 新版本1.2.39写法
                df = ts.pro_bar(ts_code=code, adj='qfq', start_date=startDay, end_date=endDay,
                                retry_count=10)

                call_times += 1
                if call_times == 195:
                    endtime = datetime.datetime.now()
                    used_sec = (endtime - last_calltime).seconds
                    #一分钟最多调200次
                    while(used_sec<60):
                        time.sleep(1)
                        print('GetOnlineKData >>>  used_sec=',used_sec)
                        endtime = datetime.datetime.now()
                        used_sec = (endtime - last_calltime).seconds

                    call_times = 0
                    last_calltime = datetime.datetime.now()

                #print(df)
                if df is None or len(df) == 0:
                    print(code + ' pro_bar error!!!!!!!!!!!!!!!\n')
                    logging.error(code+' pro_bar error!!!!!!!!!!!!!!!\n')
                    continue
            except Exception as e:
                print('tushare pro_bar error. daily. code=',code,e)
                logging.error(code + 'tushare pro_bar error. daily. code=')
                continue


            #查看dataframe类型
            #print(df.dtypes)

            #使用values可以查看DataFrame里的数据值，返回的是一个数组
            # 列： ts_code trade_day open high low close 昨收价 涨跌额 涨跌幅 总手 成交额（千元）
            # 索引：    0    1         2    3    4    5    6      7      8      9    10
            arrayAllInfo = df.values

            #删除多维数组中的第6.7列
            # 列： ts_code trade_day open high low close 涨跌幅 总手 成交额（千元）
            # 索引：    0    1         2    3    4    5    6      7      8
            arrayAllInfo = np.delete(arrayAllInfo, [6, 7], axis=1)
            self.db.add_kdata_down_many(arrayAllInfo)
            #倒序遍历，写mysql数据库
            #for arrayOne in reversed(arrayAllInfo):
                # 列： ts_code trade_day open high low close 昨收价 涨跌额 涨跌幅 总手 成交额（千元）
                # 索引：    0    1         2    3    4    5    6      7      8      9    10
                #print(arrayOne[0],"--",arrayOne[1],"--", arrayOne[2],"--",arrayOne[5],"--",arrayOne[7],"--",arrayOne[8])
                #前复权
                #self.db.add_kdata_down(arrayOne[0],arrayOne[1], arrayOne[2], arrayOne[5], arrayOne[3], arrayOne[4], arrayOne[9], arrayOne[8], arrayOne[10])

    # tushare获取最新部分的日线行情，并保持到mysql
    # 函数：获取多只股票code的日线行情,写入数据库
    # 日期都填YYYYMMDD格式，比如20181010
    def GetPartKDataAndSave(self, codes, startDay, endDay, retry=5):
        print('GetPartKDataAndSave retry=', retry)
        if retry < 0:
            return

        # 已经获取的个数，受tushare限制，每分钟只能调用200次
        gotCnt = 0
        # 上一次调用接口时间
        last_calltime = datetime.datetime.now()
        # 一定时间内，调用接口次数
        call_times = 0

        # 股票列表正在处理第几只
        idx = 0
        pro = ts.pro_api()

        list_error_code = list()

        for code in codes['ts_code']:
            gotCnt += 1

            name = codes['name'][idx]
            symbol = codes['symbol'][idx]
            idx += 1
            # code= 000006.SZ   name= 深振业A   symbol= 000006
            print('code=', code, '  name=', name, '  symbol=', symbol)
            # logging.debug('code='+ code+ '  name='+ name+ '  symbol='+ symbol)

            # 从第N支股票开始获取，用于连接中断时，续传
            #if gotCnt <= self.stockStart:
            #    continue

            print("GetOnlineKData..." + code)
            logging.debug("GetOnlineKData..." + code)

            try:
                # 返回dataframe结构：ts_code/trade_date/open/high/low/close/pre_close/change/pct_chg/vol/amount
                # df = pro.daily(ts_code=code, start_date=startDay, end_date=endDay)

                # qfq,前复权； hfq,后复权
                # 返回dataframe结构：ts_code/trade_date/open/high/low/close/pre_close/change/pct_chg/vol/amount
                df = ts.pro_bar(ts_code=code, api=None, start_date=startDay, end_date=endDay, retry_count=3)

                call_times += 1
                if call_times == 195:
                    endtime = datetime.datetime.now()
                    used_sec = (endtime - last_calltime).seconds
                    # 一分钟最多调200次
                    while (used_sec < 60):
                        time.sleep(1)
                        print('GetOnlineKData >>>  used_sec=', used_sec)
                        endtime = datetime.datetime.now()
                        used_sec = (endtime - last_calltime).seconds

                    call_times = 0
                    last_calltime = datetime.datetime.now()


                # print(df)
                if df is None or len(df) == 0:
                    print(code + ' pro_bar error!!!!!!!!!!!!!!!\n')
                    logging.error(code + ' pro_bar error!!!!!!!!!!!!!!!\n')
                    list_error_code.append(code)
                    continue
            except Exception as e:
                print('tushare pro_bar error. daily. code=', code)
                logging.error(code + 'tushare pro_bar error. daily. code=')
                list_error_code.append(code)

            # 查看dataframe类型
            # print(df.dtypes)

            # 使用values可以查看DataFrame里的数据值，返回的是一个数组
            # 列： ts_code trade_day open high low close 昨收价 涨跌额 涨跌幅 总手 成交额（千元）
            # 索引：    0    1         2    3    4    5    6      7      8      9    10
            arrayAllInfo = df.values

            # 删除多维数组中的第6.7列
            # 列： ts_code trade_day open high low close 涨跌幅 总手 成交额（千元）
            # 索引：    0    1         2    3    4    5    6      7      8
            arrayAllInfo = np.delete(arrayAllInfo, [6, 7], axis=1)
            self.db.add_kdata_many(arrayAllInfo)
            # 倒序遍历，写mysql数据库
            # for arrayOne in reversed(arrayAllInfo):
            # 列： ts_code trade_day open high low close 昨收价 涨跌额 涨跌幅 总手 成交额（千元）
            # 索引：    0    1         2    3    4    5    6      7      8      9    10
            # print(arrayOne[0],"--",arrayOne[1],"--", arrayOne[2],"--",arrayOne[5],"--",arrayOne[7],"--",arrayOne[8])
            # 前复权
            # self.db.add_kdata_down(arrayOne[0],arrayOne[1], arrayOne[2], arrayOne[5], arrayOne[3], arrayOne[4], arrayOne[9], arrayOne[8], arrayOne[10])

        # list转dataframe
        if len(list_error_code) is 0:
            return

        mydict = {
            'ts_code': list_error_code,
            'name': list_error_code,
            'symbol': list_error_code
        }

        df_tmp = pd.DataFrame(mydict)

        self.GetPartKDataAndSave(df_tmp, startDay, endDay, retry - 1)

    #保存所有的交易日期
    def SaveTradeDay(self, strade_days):
        for sd in strade_days:
            #是否存在
            ret = self.db.exist_trade_day(sd)
            if ret > 0:
                #print('已经存在 ', sd)
                continue
            #写数据库
            self.db.add_trade_day(sd)

    #将需要处理的数据，从mysql数据库读出来，转换成DataFrame进行处理
    #根据sql语句的select内容，进行转换
    def QueryKData(self, code):
        result = self.db.query_kdata(code)

        df = pd.DataFrame(list(result), columns=["open", "close", "high", "low", "vol", "trade_day"])
        #print(df)
        return df

    def QueryKDataDown(self, code):
        result = self.db.query_kdata_down(code)

        df = pd.DataFrame(list(result), columns=["open", "close", "high", "low", "vol", "trade_day"])
        #print(df)
        return df

    #查询一部分时间的k线数据
    def QueryPartKDataDown(self, code, start_day, end_day, before_days):
        result = self.db.query_kdata_down_by_day(code, start_day, end_day, before_days)

        df = pd.DataFrame(list(result), columns=["open", "close", "high", "low", "vol", "trade_day"])
        #print(df)
        return df

    #查询一部分时间的k线数据
    def QueryPartKData(self, code, start_day, end_day, before_days):
        result = self.db.query_kdata_by_day(code, start_day, end_day, before_days)

        df = pd.DataFrame(list(result), columns=["open", "close", "high", "low", "vol", "trade_day"])
        #print(df)
        return df

    #数据加工
    #生成ma5，ma10，ma20，ma30，ma60
    def DataProcess(self, list_code):
        for code in list_code['ts_code']:
            print("DataProcess.... code=", code)
            logging.debug("DataProcess.... code=" + code)
            #mysql数据转换成dataframe
            df = self.QueryKDataDown(code)
            all_vol = df['vol']
            all_close = df['close']
            all_trade_day = df['trade_day']

            try:
                #计算收盘价、成交量的平均值
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

                #移动平滑异同平均线(Moving Average Convergence Divergence，简称MACD指标)策略
                diff, dea, my_macd = talib.MACD(close_all,
                                             fastperiod=12,
                                             slowperiod=26,
                                             signalperiod=9)
    
                #写入mysql
                len_record = len(all_trade_day)
                for i in range(len_record):
                    self.db.update_kdata_down(code, all_trade_day[i],
                                         ma5[i], ma10[i], ma20[i], ma30[i], ma60[i],
                                         ma5_vol[i], ma10_vol[i], ma20_vol[i], ma30_vol[i],
                                         my_macd[i], diff[i], dea[i])
                    #print(code," trade_day=",all_trade_day[i],"  ma5=",ma5[i])

            except Exception as e:
                print('DataProcess  error,e=', e, 'code=', code)

            print("End ... DataProcess.... code=", code)

    # 部分数据加工,处理一段时间内的数据，并且更新指定范围的加工结果到mysql
    # 生成ma5，ma10，ma20，ma30，ma60
    #before_days:起始时间往前移动60天，因为需要计算60日平均值
    def PartDataProcess(self, list_code, start_day, end_day, before_days=60):
        for code in list_code['ts_code']:
            print("DataProcess.... code=", code)
            logging.debug("DataProcess.... code=" + code)
            # mysql数据转换成dataframe
            #更新数据库，值需要更新start_day~end_day的范围
            df = self.QueryPartKData(code, start_day, end_day, before_days)
            all_vol = df['vol']
            all_close = df['close']
            all_trade_day = df['trade_day']

            try:
                # 计算收盘价、成交量的平均值
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

                # 移动平滑异同平均线(Moving Average Convergence Divergence，简称MACD指标)策略
                diff, dea, my_macd = talib.MACD(close_all,
                                                fastperiod=12,
                                                slowperiod=26,
                                                signalperiod=9)

                # 写入mysql
                len_record = len(all_trade_day)

                real_count = len_record-before_days
                #遍历最新的real_count条记录
                for i in range(len_record-1, before_days-1, -1):
                    self.db.update_kdata(code, all_trade_day[i],
                                              ma5[i], ma10[i], ma20[i], ma30[i], ma60[i],
                                              ma5_vol[i], ma10_vol[i], ma20_vol[i], ma30_vol[i],
                                              my_macd[i], diff[i], dea[i])
                    # print(code," trade_day=",all_trade_day[i],"  ma5=",ma5[i])

            except Exception as e:
                print('DataProcess  error,e=', e, 'code=', code)

            print("End ... DataProcess.... code=", code)
    #将缓存t_kdata_down数据clone到t_kdata中
    def CloneDB(self):
        self.db.clone_kdata_down()

    #比较mysql保存的最新交易日期，与tushare的最新交易日期是否相同，不同则更新
    #返回需要更新多少天的数据
    def NeedUpdateData(self, str_start_day, str_end_day):
        list_online_trade_days = self.GetOnlineTradeDays(str_start_day, str_end_day)
        list_offline_trade_days = self.GetAllOfflineTradeDays()

        #mysql数据库是空表
        if list_offline_trade_days is None or len(list_offline_trade_days) == 0:
            update_days = len(list_online_trade_days)
            print('Need to update_days...', update_days)
            return update_days
            return len(list_online_trade_days)

        newest_online_trade_days = list_online_trade_days[-1]
        print('newest tushare...', newest_online_trade_days)
        newest_offline_trade_days = list_offline_trade_days[-1]
        print('newest mysql...', newest_offline_trade_days)

        #计算mysql最新的记录，与在线的记录，相差多少天
        idx = list_online_trade_days.index(newest_offline_trade_days, 0, len(list_online_trade_days))

        if newest_online_trade_days > newest_offline_trade_days:
            update_days = len(list_online_trade_days) - idx - 1
            print('Need to update_days...', update_days)
            return update_days
        return 0

    #任务调度，db保活
    def aps_keep_db_alive(self, share):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, 'dataservice_mysql  aps_keep_db_alive')
        share.value = cur_time
        return self.db.query_tradeday()

    # 任务调度,更新K线数据
    #share 共享内存
    def aps_dataservice_update(self, share):
        starttime = datetime.datetime.now()
        cur_time = starttime.strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, "dataservice_mysql  aps_dataservice_update  pid=", os.getpid(), "  ppid=", os.getppid())

        self.db.connect_db()

        if share != None:
            share.value = cur_time

        # 更新的起始时间
        str_start_day = '20171201'
        str_end_day = self.GetToday()

        print('***********  aps_dataservice_update **************')

        # list_trade_days = dataservice.GetTradeDays(str_start_day, str_end_day)
        # 比较mysql保存的最新交易日期，与tushare的最新交易日期是否相同，不同则更新
        update_days = self.NeedUpdateData(str_start_day, str_end_day)
        print('update_days = ', update_days)
        if update_days > 0:
            self.just_process = False

        list_code = self.GetStockList()

        # 全部下载，处理
        if self.b_updata_part is False:
            # 下载数据时,顺带处理
            if self.just_process is False:
                list_online_trade_days = self.GetOnlineTradeDays(str_start_day, str_end_day)
                self.SaveTradeDay(list_online_trade_days)
                self.GetOnlineKData(list_code, str_start_day, str_end_day)
                self.DataProcess(list_code)
                self.CloneDB()

                # 处理离线数据
            if self.just_process is True:
                self.DataProcess(list_code)

        # 最新部分下载，处理
        elif update_days > 0 and self.b_updata_part is True:
            # 下载数据时,顺带处理
            if self.just_process is False:
                # 1. 获取最新的交易日期
                list_online_trade_days = self.GetOnlineTradeDays(str_start_day, str_end_day)

                # 2.获取最新一组K线数据
                idx = len(list_online_trade_days) - update_days - 1
                str_start_day = list_online_trade_days[idx + 1]
                str_end_day = list_online_trade_days[-1]
                print('updata_part, real start day=', str_start_day, '  end day=', str_end_day)
                # 获取部分最新k线数据，直接写入kdata表
                self.GetPartKDataAndSave(list_code, str_start_day, str_end_day, 5)

                # 3.这组新K线添加到mysql以后，处理新数据+前60天K线，计算出macd，ma5...ma60等
                self.PartDataProcess(list_code, str_start_day, str_end_day)
                # 4. 最新的交易日期，更新到mysql
                self.SaveTradeDay(list_online_trade_days)

        self.db.disconnect_db()

        endtime = datetime.datetime.now()
        times = (endtime - starttime).seconds
        print('更新数据用时(秒)：', times)
        logging.debug('更新数据用时(秒)：' + str(times))
######################################################################################################################
def main():
    dataservice = CDataServiceMysql()
    dataservice.aps_dataservice_update(None)
    # 更新的起始时间
    '''str_start_day = '20171201'
    str_end_day = dataservice.GetToday()

    print('***********  main **************')

    #list_trade_days = dataservice.GetTradeDays(str_start_day, str_end_day)
    #比较mysql保存的最新交易日期，与tushare的最新交易日期是否相同，不同则更新
    update_days = dataservice.NeedUpdateData(str_start_day, str_end_day)
    print('update_days = ', update_days)
    if update_days > 0:
        dataservice.just_process = False

    list_code = dataservice.GetStockList()

    #全部下载，处理
    if dataservice.b_updata_part is False:
        # 下载数据时,顺带处理
        if dataservice.just_process is False:
            list_online_trade_days = dataservice.GetOnlineTradeDays(str_start_day, str_end_day)
            dataservice.SaveTradeDay(list_online_trade_days)
            dataservice.GetOnlineKData(list_code, str_start_day, str_end_day)
            dataservice.DataProcess(list_code)
            dataservice.CloneDB()

            # 处理离线数据
        if dataservice.just_process is True:
            dataservice.DataProcess(list_code)

    #最新部分下载，处理
    elif update_days > 0 and dataservice.b_updata_part is True:
        # 下载数据时,顺带处理
        if dataservice.just_process is False:
            #1. 获取最新的交易日期
            list_online_trade_days = dataservice.GetOnlineTradeDays(str_start_day, str_end_day)

            #2.获取最新一组K线数据
            idx = len(list_online_trade_days) - update_days - 1
            str_start_day = list_online_trade_days[idx+1]
            str_end_day = list_online_trade_days[-1]
            print('updata_part, real start day=', str_start_day, '  end day=', str_end_day)
            #获取部分最新k线数据，直接写入kdata表
            dataservice.GetPartKDataAndSave(list_code, str_start_day, str_end_day)

            #3.这组新K线添加到mysql以后，处理新数据+前60天K线，计算出macd，ma5...ma60等
            dataservice.PartDataProcess(list_code, str_start_day, str_end_day)
            # 4. 最新的交易日期，更新到mysql
            dataservice.SaveTradeDay(list_online_trade_days)'''


def shutdown(sec):
    # N秒后关机
    cmd = 'shutdown -s -t ' + str(sec)
    os.system(cmd)

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    #starttime=starttime-9583
    main()
    endtime = datetime.datetime.now()
    times = (endtime - starttime).seconds
    print('下载数据用时(秒)：', times)
    logging.debug('下载数据用时(秒)：' + str(times))

    #10s后关机
    if False:
        shutdown(10)
