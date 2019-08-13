# coding=utf-8
import os
import src.analysis.limitconcept as limitconcept
import src.datamgr.baseinfo as baseinfo
import datetime
import src.datamgr.dbmgr as dbmgr
import src.common.conf as conf

'''
实时监控模块，负责监控、统计实盘中涨停股的概念，写数据库
'''

class CRT_Hotspot:
    def __init__(self, str_conf_path):
        #self.name = self.__class__.__name__
        #获取排行榜中多少条热点概念
        self.top_consept_num = 20
        myconf = conf.CConf(str_conf_path)
        myconf.ReadConf()
        self.db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
        print('CRT_Hotspot ... ', self.db)


    # 取出次数最多的20个概念，推送
    def top_consept(self,consept_count, N):
        # 先排序，降序
        sort_dict = sorted(consept_count.items(), key=lambda d: d[1], reverse=True)
        # print(sort_dict)
        if len(sort_dict) > N:
            return sort_dict[0:N]
        else:
            return sort_dict

    def aps_keep_db_alive(self, share):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, 'aps_keep_db_alive')
        
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_keep_db_alive  pid=", os.getpid(), "  ppid=", os.getppid())
        
        share.value = cur_time
        return self.db.query_allhotconsept()

    # 任务调度
    #share 共享内存
    def aps_hotspot(self, share):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(cur_time, 'aps_hotspot')
        share.value = cur_time
        
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_hotspot  pid=", os.getpid(), "  ppid=", os.getppid())

        # 加载股票概念
        pBaseInfo = baseinfo.CBaseinfo()
        pBaseInfo.read_excel()

        # 获取当前所有涨停的个股
        pLimit = limitconcept.CLimitConcept()

        #while True:
        # 统计概念出现的次数
        consept_count = dict()
        list_code = pLimit.processEx()
        # print(list_code)

        # 统计所有涨停个股的概念
        for code in list_code:
            my_stock_info = pBaseInfo.get_stock_info(code)
            if my_stock_info is None:
                print(code, ' is not exist!aps_hotspot')
                continue
            # 遍历每一个概念，进行统计，排序
            for consept in my_stock_info.get_conseption():
                if consept in consept_count:
                    count = consept_count[consept]
                    consept_count[consept] = count + 1
                else:
                    consept_count[consept] = 1

        list_top = self.top_consept(consept_count, self.top_consept_num)
        #print(dict_top20)
        self.consept_to_db(list_top)

    def consept_to_db(self, list_consept):
        #先清空，在写新数据
        self.db.truncate_hotconsept()
        cur_time = datetime.datetime.now()
        str_time = datetime.datetime.strftime(cur_time, '%Y%m%d_%H%M%S')
        for value in list_consept:
            #value[0],value[1],写数据库
            self.db.add_hotconsept(value[0], value[1], str_time)


