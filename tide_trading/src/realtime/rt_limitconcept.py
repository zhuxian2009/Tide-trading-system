# coding=utf-8
import src.common.tools as tools
import src.common.statistics as st
import datetime

import pandas as pd

''' 涨停股概念统计模块（子进程）：获取实时数据，统计当前所有涨停股中，概念出现的多少，进行排序 '''
class CRT_LimitConcept:
    def __init__(self, db):
        cur_time = datetime.datetime.now()
        log_filename = datetime.datetime.strftime(cur_time, '%Y%m%d_%H%M%S')
        self.log_name = 'log/limitconcept'+log_filename
        self.db = db
        self.MyInit()

    #初始化
    def MyInit(self):
        my_log_filename = self.log_name + ".txt"

        #if os.path.exists(my_log_filename):
        #    os.remove(my_log_filename)

        log = tools.CLogger('limitconcept', my_log_filename, 1)
        strMsg = 'start'
        log.getLogger().info(strMsg)

    def __process(self):
        #从数据库读取股票列表
        result = self.db.query_realtime_quotes()
        df = pd.DataFrame(list(result), columns=\
        ["name","open","pre_close","price", "high", "low", "bid","ask", "amount","volume",\
        "b1_v","b1_p","b2_v","b2_p","b3_v","b3_p","b4_v","b4_p","b5_v","b5_p", \
        "a1_v","a1_p","a2_v","a2_p","a3_v","a3_p","a4_v","a4_p","a5_v","a5_p",\
        "date","time","code"])

        mytool = st.CStatistics()

        #过滤出来的涨停个股
        list_ok = list()
        for idx in range(0, len(df)):
            code = df['code'][idx]
            pre_close = df['pre_close'][idx]
            nowprice = df['price'][idx]
            # 计算涨停价格
            limit = mytool.calc_limit_price(float(pre_close))
            if float(nowprice) >= float(limit):
                list_ok.append(code)

        return list_ok

    def processEx(self):
        starttime = datetime.datetime.now()
        list_code = self.__process()
        endtime = datetime.datetime.now()
        print('rt_limitconcept processEx 处理用时 (秒)：', (endtime - starttime).seconds)
        return list_code

