# coding=utf-8
import os
import datetime
import src.datamgr.dbmgr as dbmgr
import src.common.conf as conf
import pandas as pd
import src.common.statistics as st

'''
实时监控模块，chip concentration
通过买一与卖一之间挂单，计算筹码集中程度；挂单相差越大，表示流通筹码越少，控盘能力越强
写数据库
'''

class CRT_ChipConcent:
    def __init__(self, str_conf_path, log):
        self.log = log
        #获取排行榜中多少条热点概念
        self.top_ChipC_num = 20
        myconf = conf.CConf(str_conf_path)
        myconf.ReadConf()
        self.db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')


    # 取出次数最多的20个概念，行业
    def top_dict(self, my_dict, N):
        # 先排序，降序
        sort_dict = sorted(my_dict.items(), key=lambda d: d[1], reverse=True)
        # print(sort_dict)
        if len(sort_dict) > N:
            return sort_dict[0:N]
        else:
            return sort_dict

    def aps_keep_db_alive(self):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, 'aps_keep_db_alive')
        
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_keep_db_alive  pid=", os.getpid(), "  ppid=", os.getppid())
        self.db.query_allhotconsept()

    # 任务调度,筹码集中
    #share 共享内存
    def aps_chip_c(self):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, 'aps_chip_c')
        
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_chip_c  pid=", os.getpid(), "  ppid=", os.getppid())

        self.db.connect_db()
        #
        list_result = self.get_quotes_gap()
        # print(list_code)

        self.db.add_chipconcent_many(list_result)

        self.db.disconnect_db()
        # 统计
        #for list_row in list_result:
        #    print(list_row[0], list_row[1])

        '''
        #概念排序，取最顶部的N个概念，写数据库
        list_top_consept = self.top_dict(consept_count, self.top_consept_num)
        self.consept_to_db(list_top_consept)
        list_top_trade = self.top_dict(trade_count, self.top_trade_num)
        self.trade_to_db(list_top_trade)'''


    #获取出价间隔
    def get_quotes_gap(self):
        result = self.db.query_realtime_quotes()
        df = pd.DataFrame(list(result), columns=
            ["name", "open", "pre_close", "price", "high", "low", "bid", "ask", "amount", "volume",
             "b1_v", "b1_p", "b2_v", "b2_p", "b3_v", "b3_p", "b4_v", "b4_p", "b5_v", "b5_p",
             "a1_v", "a1_p", "a2_v", "a2_p", "a3_v", "a3_p", "a4_v", "a4_p", "a5_v", "a5_p",
             "date", "time", "code"])

        mytool = st.CStatistics()

        # 卖一与买一之间的间隔幅度
        list_ok = list()
        for idx in range(0, len(df)):
            code = df['code'][idx]
            #pre_close = df['pre_close'][idx]
            now_price = df['price'][idx]
            now_b1_p = df['b1_p'][idx]
            now_a1_p = df['a1_p'][idx]
            now_time = df['time'][idx]
            now_date = df['date'][idx]
            name = df['name'][idx]

            #过滤条件
            #1.价格大于3元
            #2.简称中，不包含ST
            if name.find('ST') >= 0 or now_price < 3:
                continue

            # 计算间隔涨幅
            gain = mytool.calc_gain(float(now_a1_p), float(now_b1_p))
            if gain >= 0.5:
                list_row = list()
                #列名：code name gain date_time
                list_row.append(code)
                list_row.append(name)
                list_row.append(round(gain, 2))
                list_row.append(now_date)
                list_row.append(now_time)

                list_ok.append(list_row)

        return list_ok

