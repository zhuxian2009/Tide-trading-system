#coding=utf-8
import src.datamgr.dbmgr as dbmgr
import src.common.conf as conf
import pandas as pd

import sys
import os
import datetime
'''从mysql查询出来的数据，转换成应用可识别的形态，如dataframe'''

class CDBAdapter:
    def __init__(self, str_conf_path, log):
        self.log = log
        self.db = None
        self.myconf = conf.CConf(str_conf_path)
        self.myconf.ReadConf()
        try:
            self.db = dbmgr.CDBMgr(self.myconf.db_host, self.myconf.db_username, self.myconf.db_pwd, 'kdata')
            self.db.connect_db()
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h+str(e))

    def GetDB(self):
        return self.db

        # 根据sql语句的select内容，进行转换
    def QueryAllStockBasic(self):
        result = self.db.query_allstockbasic()

        df = None
        try:
            df = pd.DataFrame(list(result), columns=["ts_code", "symbol", "name", "area", "market", "list_status"])
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h + str(e))
        return df

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

    #查询所有的策略回测结果,id=1表示双底回测id
    def QueryBTStrategy(self, id):
        result = self.db.query_bt_strategy(id)
        # 执行2毫秒
        df = pd.DataFrame(list(result), columns=["ts_code", "buydate", "buyprice", "selldate", "sellprice", "duration", "strategyid"])

        # print(df)
        return df

    def GetToday(self):
        now_time = datetime.datetime.now()
        day = now_time.strftime('%Y%m%d')
        return day