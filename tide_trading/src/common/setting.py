# coding=utf-8
import os
#import src.analysis.limitconcept as limitconcept
import src.realtime.rt_limitconcept as limitconcept
import src.datamgr.baseinfo as baseinfo
import datetime
import src.datamgr.dbmgr as dbmgr
import src.common.conf as conf

'''
设置参数
'''

class CSetting:
    def __init__(self, str_conf_path):
        #self.name = self.__class__.__name__
        myconf = conf.CConf(str_conf_path)
        myconf.ReadConf()
        self.db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
        print('CRT_Hotspot ... ', self.db)


    # 设置
    def set_config(self):
        self.db.set_global_config()

