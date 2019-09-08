# coding=utf-8
import os
#import src.analysis.limitconcept as limitconcept
import src.realtime.rt_limitconcept as limitconcept
import src.datamgr.baseinfo as baseinfo
import datetime
import src.datamgr.dbmgr as dbmgr
import src.common.conf as conf
import redis
import sys
import pickle

'''
收盘以后，日K线更新以后，统计最近10个交易日涨停的热点数量
结果保存在redis
key=hottrace_20190905
value={'富时罗素概念股': 13, '深股通': 10, '军工': 5, '融资融券': 7, '转融券标的': 7, '地方国资改革': 5, 
'互联网金融': 14, '区块链': 11, '国产软件': 11, '5G': 10, '文化传媒': 2, '新能源汽车': 3, '大数据': 9, '华为概念': 5,
 '沪股通': 7, '半年报预增': 3, '高送转': 7, '央企国资改革': 2, '互联网+': 7, '云计算': 6}
'''

class CRT_HotTrace:
    def __init__(self, str_conf_path, log):
        #self.name = self.__class__.__name__
        #获取排行榜中多少条热点概念
        self.top_consept_num = 20
        self.top_trade_num = 20
        myconf = conf.CConf(str_conf_path)
        myconf.ReadConf()
        self.log = log
        self.db = None
        self.re = None
        self.pBaseInfo = baseinfo.CBaseinfo()

        try:
            self.pBaseInfo.read_excel()
            self.db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
            self.re = redis.Redis(host='127.0.0.1', port=6379, db=0)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h+str(e))


    # 取出次数最多的20个概念，行业,返回list
    def top_dict(self, my_dict, N):
        # 先排序，降序
        sort_dict = sorted(my_dict.items(), key=lambda d: d[1], reverse=True)
        # print(sort_dict)
        if len(sort_dict) > N:
            return sort_dict[0:N]
        else:
            return sort_dict

    # 任务调度
    def aps_hottrace(self):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, 'in aps_hottrace')

        try:
            self.db.connect_db()
            #redis 保存任务状态
            self.re.set('key_rt_hottrace_aps_hottrace', cur_time)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h + str(e))
        
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_hottrace  pid=", os.getpid(), "  ppid=", os.getppid())

        # 加载股票概念
        #pBaseInfo = baseinfo.CBaseinfo()
        #pBaseInfo.read_excel()

        #1.从t_trade_day找出最近10个交易日的日期
        trade_day = self.db.query_last_tradeday(10)
        # 2.从每个交易日中找出涨停股票
        dict_consept_count = dict()

        for cur_day in trade_day:
            day = cur_day[0]
            today_limit = self.db.query_limit(day)

            # 3.获取每个交易日中，统计涨停股对应概念的个数，形成{consept:count}, {consept:count}形式
            for code in today_limit:
                # 去除.SZ .SH的后缀
                str_code = code[0][0:6]

                #获取股票的基本信息
                my_stock_info = self.pBaseInfo.get_stock_info(str_code)
                if my_stock_info is None:
                    print(code, ' is not exist!aps_hotspot')
                    continue

                #获取股票的概念
                consepts = my_stock_info.get_conseption()

                # 查询的概念是否在dict中
                for conspt in consepts:
                    b_is_new = True
                    for dict_key_consept in dict_consept_count.keys():
                        #找到相同的概念，计数+1
                        if conspt == dict_key_consept:
                            dict_consept_count[dict_key_consept] = dict_consept_count[dict_key_consept] + 1
                            b_is_new = False
                    #add new dict
                    if b_is_new is True:
                        dict_consept_count[conspt] = 1

        # 4.统计10个交易日中，概念累积个数，进行排序
        list_sort = self.top_dict(dict_consept_count, 20)
        print(list_sort)

        #统计信息写入redis
        try:
            #提取数据，不需要概念名称,list写入redis
            self.re.delete('rt_hottrace_key_statistic')
            for i in list_sort:
                self.re.rpush('rt_hottrace_key_statistic', i[1])

            #self.re.set('rt_hottrace_key_statistic', list_sort)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h+str(e))

        # 5.根据排序结果，获取每个最近10个交易日，每个交易日的热点概念分布情况
        self.hotspot_distribution(trade_day, list_sort)

        ##############################################################
        #概念排序，取最顶部的N个概念，写数据库
        #list_top_consept = self.top_dict(consept_count, self.top_consept_num)
        #self.consept_to_db(list_top_consept)
        self.db.disconnect_db()

    #每个交易日的热点概念分布情况
    def hotspot_distribution(self, trade_day, list_sort):
        for day in trade_day:
            str_day = day[0]
            today_limit = self.db.query_limit(str_day)

            dict_consept_count = dict()
            for v in list_sort:
                dict_consept_count[v[0]] = 0

            # 3.获取每个交易日中，统计涨停股对应概念的个数，形成{consept:count}, {consept:count}形式
            for code in today_limit:
                # 去除.SZ .SH的后缀
                str_code = code[0][0:6]

                #获取股票的基本信息
                my_stock_info = self.pBaseInfo.get_stock_info(str_code)
                if my_stock_info is None:
                    print(code, ' is not exist!aps_hotspot')
                    continue

                #获取股票的概念
                consepts = my_stock_info.get_conseption()

                for conspt in consepts:
                    for value in list_sort:
                        #找到相同的概念
                        if conspt == value[0]:
                            dict_consept_count[conspt] = dict_consept_count[conspt] + 1

            print('save to db...... ', str_day)
            #print(dict_consept_count)
            self.hottrace_to_db(str_day, dict_consept_count)

    def hottrace_to_db(self, str_day, dict_consept):
        #先清空，在写新数据
        print(str_day, '  ', dict_consept)
        redis_key = 'hottrace_' + str_day

        try:
            mydict = pickle.dumps(dict_consept)
            self.re.set(redis_key, mydict)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h+str(e))
        #for key in dict_consept.keys():
            #value[0],value[1],写数据库
         #   print(day, '  ', key, '  ', dict_consept[key])


