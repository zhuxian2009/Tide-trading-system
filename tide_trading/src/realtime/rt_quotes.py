# coding=utf-8
import datetime
import tushare as ts
import sys
import src.common.conf as conf
import src.datamgr.dbmgr as dbmgr
import redis
import sys
import os

''' 实时获取出价信息，写数据库 '''
class CRT_Quotes:
    def __init__(self, str_conf_path, log):
        #cur_time = datetime.datetime.now()
        #log_filename = datetime.datetime.strftime(cur_time, '%Y%m%d_%H%M%S')
        #self.log_name = 'log/limitconcept'+log_filename
        self.conf = conf.CConf(str_conf_path)
        self.log = log
        self.db = None
        self.re = None

        try:
            self.db = dbmgr.CDBMgr(self.conf.db_host, self.conf.db_username, self.conf.db_pwd, 'kdata')
            self.re = redis.Redis(host='127.0.0.1', port=6379, db=0)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h+e)

        self.__Init()

    #初始化
    def __Init(self):
        ts.set_token('75f181a930dc581d82c0cafd633c09d582d8ac0554c74854f73a9582')

    def process(self):
        #可以优化成从数据库读取股票列表
        list_code = self.GetStockList()

        try:
            #先清空，再写入（以后改成update）
            self.db.truncate_realtime_quotes()

            all_count = len(list_code)
            dataframe1 = ts.get_realtime_quotes(list_code['symbol'][0:500])
            #空值替换成0
            dataframe1 = dataframe1.replace('', 0)
            self.db.add_realtime_quotes_many(dataframe1.values)

            dataframe2 = ts.get_realtime_quotes(list_code['symbol'][501:1000])
            dataframe2 = dataframe2.replace('', 0)
            self.db.add_realtime_quotes_many(dataframe2.values)

            dataframe3 = ts.get_realtime_quotes(list_code['symbol'][1001:1500])
            dataframe3 = dataframe3.replace('', 0)
            self.db.add_realtime_quotes_many(dataframe3.values)

            dataframe4 = ts.get_realtime_quotes(list_code['symbol'][1501:2000])
            dataframe4 = dataframe4.replace('', 0)
            self.db.add_realtime_quotes_many(dataframe4.values)

            dataframe5 = ts.get_realtime_quotes(list_code['symbol'][2001:2500])
            dataframe5 = dataframe5.replace('', 0)
            self.db.add_realtime_quotes_many(dataframe5.values)

            dataframe6 = ts.get_realtime_quotes(list_code['symbol'][2501:3000])
            dataframe6 = dataframe6.replace('', 0)
            self.db.add_realtime_quotes_many(dataframe6.values)

            dataframe7 = ts.get_realtime_quotes(list_code['symbol'][3001:all_count])
            dataframe7 = dataframe7.replace('', 0)
            self.db.add_realtime_quotes_many(dataframe7.values)

        except Exception as e:
            print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, e)

        return True

    #函数：在线获取所有股票列表
    def GetStockList(self):
        pro = ts.pro_api()
        # 查询当前所有正常上市交易的股票列表
        #data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
        print('股票总个数：', len(data))
        return data

    def aps_reatime_quotes(self):
        try:
            cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(cur_time, 'in aps_hotspot')

            self.db.connect_db()

            #redis 保存任务状态
            self.re.set('key_rt_quotes_aps_reatime_quotes', cur_time)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h + e)

        self.process()

        self.db.disconnect_db()
