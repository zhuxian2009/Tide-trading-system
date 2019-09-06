# coding=utf-8
#import src.analysis.limitconcept as limitconcept
import src.realtime.rt_limitconcept as limitconcept
import src.datamgr.baseinfo as baseinfo
import datetime
import src.datamgr.dbmgr as dbmgr
import src.common.conf as conf
import pandas as pd
import src.stockselector.wbottom as wbottom
import redis
import sys
import os

'''
实时监控模块，负责监控尾盘出现的双底突破
'''

class CRT_WBottom(wbottom.CWBotton):
    def __init__(self, str_conf_path, log):
        self.log = log
        #self.name = self.__class__.__name__
        #获取排行榜中多少条热点概念
        myconf = conf.CConf(str_conf_path)
        myconf.ReadConf()
        #redis key值
        self.key_start_day = 'key_w_start_day'
        self.key_end_day = 'key_w_end_day'
        self.key_stock_basic = 'key_stock_basic'
        self.key_today = 'key_today'
        self.cur_open = 0
        self.cur_close = 0
        self.cur_high = 0
        self.cur_low = 0
        self.db = None
        self.re = None

        try:
            self.db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
            self.re = redis.Redis(host='127.0.0.1', port=6379, db=0)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h+e)

        self.wbottom = wbottom.CWBotton(self.db, self.log)

    def GetToday(self):
        now_time = datetime.datetime.now()
        day = now_time.strftime('%Y%m%d')
        print('end time is ', day)
        return day

    # 任务调度
    #share 共享内存
    def aps_wbottom(self):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, 'in aps_wbottom')

        try:
            self.db.connect_db()
            #redis 保存任务状态
            self.re.set('key_rt_wbottom_aps_wbottom', cur_time)
            #print(self.re.get('key_rt_wbottom_aps_wbottom'))
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h + e)


        start_day = ''
        end_day = ''

        starttime = datetime.datetime.now()

        #如果redis记录的日期与当前日期不匹配，则需要更新数据
        redis_day = self.re.get(self.key_today)

        b_not_update = False

        if redis_day is not None:
            str_redis_day = str(redis_day, 'UTF-8')
            b_not_update = str_redis_day == self.GetToday()

        #需要更新数据
        if b_not_update is False:
            self.re.delete(self.key_start_day)
            self.re.delete(self.key_end_day)
            self.re.delete(self.key_stock_basic)

        #redis已经存在开始时间、结束时间，直接获取
        if self.re.exists(self.key_start_day) and self.re.exists(self.key_end_day):
            start_day = self.re.get(self.key_start_day)
            end_day = self.re.get(self.key_end_day)
            start_day = self.to_string(start_day)
            end_day = self.to_string(end_day)
        else:
            # 获取交易日期列表
            list_trade_day = self.GetOfflineTradeDays()
            # 最近的60个交易日
            start_day = list_trade_day[-60]
            end_day = list_trade_day[-1]
            self.re.set(self.key_start_day, start_day)
            self.re.set(self.key_end_day, end_day)

        #获取所有的股票基本信息from mysql
        if self.re.exists(self.key_stock_basic):
            list_code = self.re.lrange(self.key_stock_basic, 0, -1)
        else:
            stock_basic = self.GetStockBasic()
            list_code = list(stock_basic['ts_code'])
            for code in list_code:
                #从右侧插入一个值，省去排序
                self.re.rpush(self.key_stock_basic, code)

        #从mysql获取当前所有的分时数据
        rt_quotes = self.db.query_realtime_quotes()#tuple

        for code in list_code:
            code = self.to_string(code)
            key_code = 'key_code_last60_'+self.to_string(code)

            cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(cur_time, '...... ', key_code)


            #查找指定股票的分时数据
            stock_name = code[0:6]
            b_got_new_price = False
            for quote in rt_quotes:

                if quote[-1] == stock_name:
                    self.cur_open = quote[1]
                    self.cur_close = quote[3]
                    self.cur_high = quote[4]
                    self.cur_low = quote[5]
                    print(' cur_open=', self.cur_open, ' cur_close=', self.cur_close, ' cur_high=', self.cur_high,
                          ' cur_low=', self.cur_low)
                    b_got_new_price = True
                    break

            #没有获取到当天数据，不操作
            if b_got_new_price is False:
                print('b_got_new_price=', b_got_new_price, '  stock_name=', stock_name)
                continue

            #test
            #self.re.delete(key_code)

            if b_not_update is False:
                self.re.delete(key_code)

            #读写dataframe
            if self.re.exists(key_code):
                print('from redis')
                df_bytes = self.re.get(key_code)
                all_stock_kdata = pd.read_msgpack(df_bytes)
            else:
                print('from mysql')
                all_stock_kdata = self.LoadData(code, start_day, end_day)
                try:

                    all_stock_kdata[['open', 'close', 'high', 'low', 'amount', 'vol', 'ma5vol',
                                     'ma10vol','ma20vol','ma30vol','ma5','ma10','ma20','ma30',
                                     'ma60','pct_chg','macd','dea','dif']] = \
                        all_stock_kdata[['open', 'close', 'high', 'low', 'amount', 'vol', 'ma5vol',
                                     'ma10vol','ma20vol','ma30vol','ma5','ma10','ma20','ma30',
                                     'ma60','pct_chg','macd','dea','dif']].astype('float')

                    df_bytes = all_stock_kdata.to_msgpack(compress='zlib')
                    self.re.set(key_code, df_bytes)
                except Exception as e:
                    print(e)
                    log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
                    self.log.error(log_h + e)

            if all_stock_kdata.empty:
                print(code, 'is empty! --- wbottom.py Process')
                continue

            #第一个交易日不是需要的起始时间(本来是获取前60日，如果不一致，说明上市时间小于60个交易日)，不处理
            first_trade_day = all_stock_kdata['trade_day'][0]
            str_start_day = self.to_string(start_day)
            if (first_trade_day == str_start_day) is False:
                print(code, 'start trade day is lost! --- wbottom.py Process, first_trade_day=',
                      first_trade_day, ' str_start_day=', str_start_day)
                continue

            #运行选股策略
            #设置双底区间范围
            #设置数据源的起止时间
            #设置结果回调函数
            #需要加入今天的KData
            #开始处理
            for cur_range in range(10, 20, 2):
                self.log.info(code+'  '+str(cur_range))
                self.wbottom.Init(cur_range, start_day, end_day, self.savetodb_callback)
                try:
                    self.wbottom.SetTodayKData(self.cur_close, self.cur_low)
                    self.wbottom.ProcessEx(all_stock_kdata)
                except Exception as e:
                    print(e)
                    log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
                    self.log.error(log_h + e)

        if b_not_update is False:
            self.re.set(self.key_today, self.GetToday())

        self.db.disconnect_db()

        print(cur_time, 'out aps_wbottom')
        endtime = datetime.datetime.now()
        print('取值用时(秒)：', (endtime - starttime).seconds)


    #保存到数据库的回调函数
    def savetodb_callback(self,code, bottom1, bottom2, trade_day_b1, trade_day_b2, cur_trade_day, min_interval):
        print(code)
        cur_day = datetime.datetime.now().strftime('%Y%m%d')
        cur_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.db.add_rt_strategy(code, 1, '双底尾盘策略', cur_day, cur_time)

        #转成string，存入redis；
        # 结果存redis出现问题：如果第一次检测出现code1，第二次检测清空了，就无法显示第一次；
        #如果不清空，就会不断累积，出现重复
        #strRetWBottom = str(code)+','+cur_time
        #self.re.lpush(self.key_result_wbottom, strRetWBottom)

    # 获取所有离线的交易日期，mysql
    def GetOfflineTradeDays(self):
        trade_days = []
        # 离线数据
        data = self.QueryAllTradeDays()
        for i in data['trade_day']:
            trade_days.append(i)

        return trade_days

        # 根据sql语句的select内容，进行转换

    def QueryAllTradeDays(self):
        result = self.db.query_tradeday()

        df = pd.DataFrame(list(result), columns=['trade_day'])
        # print(df)
        return df

    # 根据sql语句的select内容，进行转换
    def QueryAllStockBasic(self):
        result = self.db.query_allstockbasic()

        try:
            df = pd.DataFrame(list(result), columns=["ts_code", "symbol", "name", "area", "market", "list_status"])
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h + e)
        # df = pd.DataFrame(list(result))
        # print(df)
        return df

    # 获取股票基本信息
    def GetStockBasic(self):
        # ts_code, symbol, name, area, market, list_status
        data = self.QueryAllStockBasic()
        return data

    # 查询一个时间段内的k线数据
    def QueryRangeKData(self, code, start_day, end_day):
        # 执行8毫秒
        result = self.db.query_rangekdata(code, start_day, end_day)

        # 执行2毫秒
        df = pd.DataFrame(list(result), columns=["code", "trade_day", "open", "close", "high", "low", \
                                                 "amount", "vol", "ma5vol", "ma10vol", "ma20vol", "ma30vol", \
                                                 "ma5", "ma10", "ma20", "ma30", "ma60", "pct_chg", "macd", "dea",
                                                 "dif"])

        # print(df)
        return df

    # 加载一段时间内的数据
    def LoadData(self, code, start_day, end_day):
        df = self.QueryRangeKData(code, start_day, end_day)
        # all_vol = df['vol']
        return df

    def GetToday(self):
        now_time = datetime.datetime.now()
        day = now_time.strftime('%Y%m%d')
        print('end time is ', day)
        return day

    #bytes to string
    def to_string(self, data):
        if (isinstance(data, str)):
            return data
        else:
            return str(data, 'UTF-8')

    def consept_to_db(self, list_consept):
        #先清空，在写新数据
        self.db.truncate_hotconsept()
        cur_time = datetime.datetime.now()
        str_time = datetime.datetime.strftime(cur_time, '%Y-%m-%d %H:%M:%S')
        for value in list_consept:
            #value[0],value[1],写数据库
            self.db.add_hotconsept(value[0], value[1], str_time)


