import src.common.statistics as st
import src.datamgr.baseinfo as bi
#为了实现虚函数
from abc import ABC, abstractmethod
import src.common.status as status
import src.datamgr.dbmgr as dbmgr
import pandas as pd
import datetime
''' 
选股器的基类：
1.获取数据库中每个股票的所有数据
2.提供公共函数给子类使用
'''

class CMySelectorBase(ABC):
    def __init__(self):
        self.Status = status.CStatus()
        #股票交易日期
        self.code_trade_day = 0
        #统计工具
        self.mytool = st.CStatistics()
        self.stock_base_info = bi.CBaseinfo()

        self.db = dbmgr.CDBMgr('localhost', 'root', '123', 'kdata')

    #初始化
    def Init(self):
        #读取每个股票的概念、行业基本信息；
        pass

    # 将需要处理的数据，从mysql数据库读出来，转换成DataFrame进行处理
    # 根据sql语句的select内容，进行转换
    def QueryAllKData(self, code):
        result = self.db.query_allkdata(code)

        df = pd.DataFrame(list(result), columns=["code","trade_day","open","close","high","low",\
              "amount","vol","ma5vol","ma10vol","ma20vol","ma30vol",\
              "ma5","ma10","ma20","ma30","ma60","pct_chg","macd","dea","dif"])
        # print(df)
        return df

    #查询一个时间段内的k线数据
    def QueryRangeKData(self, code, start_day, end_day):

        #执行8毫秒
        result = self.db.query_rangekdata(code, start_day, end_day)

        #执行2毫秒
        df = pd.DataFrame(list(result), columns=["code","trade_day","open","close","high","low",\
              "amount","vol","ma5vol","ma10vol","ma20vol","ma30vol",\
              "ma5","ma10","ma20","ma30","ma60","pct_chg","macd","dea","dif"])

        # print(df)
        return df

    #加载一段时间内的数据
    def LoadData(self, code, start_day, end_day):
        df = self.QueryRangeKData(code, start_day, end_day)
        #all_vol = df['vol']
        return df

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

    #获取股票基本信息
    def GetStockBasic(self):
        # ts_code, symbol, name, area, market, list_status
        data = self.QueryAllStockBasic()
        return data

    def UnInit(self):
        self.db.disconnect_db()

    #处理数据
    @abstractmethod
    def Process(self):
        pass

    #功能：计算百分比
    # 参数：分子，分母
    def percentage(self,Numerator,denominator):
        return Numerator/denominator * 100

    #获取今天的日期
    def GetToday(self):
        now_time = datetime.datetime.now()
        day = now_time.strftime('%Y%m%d')
        #print('GetToday...end time is ', day)
        return day