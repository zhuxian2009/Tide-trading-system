# coding=utf-8
'''
任务调度管理
控制整个系统的任务调度
提供简单的接口，供flask调用
'''

#from apscheduler.schedulers.background import BackgroundScheduler as myScheduler
from flask_apscheduler import APScheduler as myScheduler
import src.realtime.rt_hotspot as rt_hotspot
import src.datamgr.dataservice_mysql as dataservice
import src.common.filelock as filelock
import src.common.tools as tools
#实时出价
import src.realtime.rt_quotes as rt_quotes
#筹码集中
import src.realtime.rt_chipconcent as rt_chipconcent

import datetime
import os
import sys
from multiprocessing import Array

#共享内存 for 热门概念
g_share_hotspot = Array('i', 100)
#共享内存 for 数据库更新Kdata
g_share_db_update = Array('i', 100)
#共享内存 for 数据库更新Kdata
g_share_hotspotdb_keepalive = Array('i', 100)
g_share_updatedb_keepalive = Array('i', 100)

class CSchedulerMgr:
    def __init__(self, str_conf_path):
        self.scheduler = myScheduler()
        self.rt_hotspot = rt_hotspot.CRT_Hotspot(str_conf_path)
        self.rt_quotes = rt_quotes.CRT_Quotes(str_conf_path)
        self.dataservice = dataservice.CDataServiceMysql(str_conf_path)
        self.rt_chipconcent = rt_chipconcent.CRT_ChipConcent(str_conf_path)

    # 启动任务调度
    def start(self):
        self.add_job()
        self.start_scheduler()

    def get_hotspot_status(self):
        print('get_hotspot_status g_share_hotspot=', g_share_hotspot.value)
        return g_share_hotspot.value

    def get_db_update_status(self):
        print('get_db_update_status g_share_db_update=', g_share_db_update.value)
        return g_share_db_update.value

    def get_db_keepalive_status(self):
        return g_share_hotspotdb_keepalive.value

    def get_updatedb_keepalive_status(self):
        return g_share_updatedb_keepalive.value

    ############################# 任务调度 #############################

    ######################## 热门行业 热门概念################ 任务调度,DB保活
    def aps_keep_hotspotdb_alive(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_keep_hotspotdb_alive')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_keep_db_alive  pid=", os.getpid(), "  ppid=", os.getppid())

        self.rt_hotspot.aps_keep_db_alive(g_share_hotspotdb_keepalive)

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_keep_hotspotdb_alive')

    # 任务调度
    def aps_hotspot(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_hotspot')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_hotspot  pid=", os.getpid(), "  ppid=", os.getppid())

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_hotspot, lock failed')
            return
        
        self.rt_hotspot.aps_hotspot(g_share_hotspot)

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_hotspot')

    ######################## 实时更新出价 ################
    def aps_reatime_quotes(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_reatime_quotes')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_reatime_quotes  pid=", os.getpid(), "  ppid=", os.getppid())

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_reatime_quotes, lock failed')
            return

        self.rt_quotes.aps_reatime_quotes()

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_reatime_quotes')

        # 任务调度,DB保活

    def aps_quotes_keepdbalive(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_quotes_keepdbalive')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_quotes_keepdbalive  pid=", os.getpid(), "  ppid=", os.getppid())

        self.rt_quotes.aps_keep_db_alive()

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_quotes_keepdbalive')

    ######################### 定时更新每天K线数据 ################ 任务调度,DB保活
    def aps_keep_updatedb_alive(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_keep_updatedb_alive')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_keep_updatedb_alive  pid=", os.getpid(), "  ppid=", os.getppid())

        self.dataservice.aps_keep_db_alive(g_share_updatedb_keepalive)

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_keep_updatedb_alive')

    # 任务调度,定时更新kdata
    def aps_dataservice_update(self):
        print(tools.get_cur_time(), ' in aps_dataservice_update')

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_dataservice_update, lock failed')
            return

        self.dataservice.aps_dataservice_update(g_share_db_update)

        print(tools.get_cur_time(), ' out aps_dataservice_update')

    ######################## 实时统计筹码集中的个股 ################
    def aps_rt_chipconcent(self):
        print(tools.get_cur_time(), ' in aps_rt_chipconcent')

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_rt_chipconcent, lock failed')
            return

        self.rt_chipconcent.aps_chip_c()

        print(tools.get_cur_time(), ' out aps_rt_chipconcent')


    def aps_chipconcent_keep_db_alive(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_chipconcent_keep_db_alive')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_chipconcent_keep_db_alive  pid=", os.getpid(), "  ppid=", os.getppid())

        self.rt_chipconcent.aps_keep_db_alive()

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_chipconcent_keep_db_alive')

    ############################################  添加任务调度的具体任务
    def add_job(self):
        g_share_hotspot.value = 'hotspot'
        g_share_hotspotdb_keepalive.value = 'aps_keep_hotspotdb_alive'
        g_share_db_update.value = 'dataservice_update'
        try:
            #db保活,每小时连一次mysql，否则超过8小时会断开
            #self.scheduler.add_job(func=self.aps_keep_hotspotdb_alive, trigger='cron', hour='0-23',second='*/5', day_of_week='*',  id='id_scd_hotspot_keepdbalive')

            #self.scheduler.add_job(func=self.aps_hotspot, trigger='cron', hour='0-23', second='*/10', day_of_week='*', id='id_scd_hotspot_pm')
            #self.scheduler.add_job(func=self.aps_reatime_quotes, trigger='cron', hour='0-23', second='*/10', day_of_week='*', id='id_scd_quotes')
            #self.scheduler.add_job(func=self.aps_rt_chipconcent, trigger='cron', hour='0-23', second='*/10', day_of_week='*', id='id_scd_chipconcent')
            pass
            #self.scheduler.add_job(func=self.aps_quotes_keepdbalive, trigger='cron', hour='0-23', second='*/10',day_of_week='*', id='id_scd_quotes_keepdbalive')
            # 更新最新k线的任务
            #self.scheduler.add_job(func=self.aps_dataservice_update, trigger='cron', second='*/10', day_of_week='mon-fri', id='id_dataservice_update')
            #self.scheduler.add_job(func=self.aps_keep_updatedb_alive, trigger='cron',hour='0-23', second='*/5', day_of_week='*', id='id_scd_update_keepdbalive')
        except Exception as e:
            print('add_hotspot_job error! ... ' + e)

    def remove_hotspot_job(self):
        self.scheduler.remove_job('id_scd_hotspot_am')
        self.scheduler.remove_job('id_scd_hotspot_pm')
        self.scheduler.remove_job('id_dataservice_update')
        self.scheduler.remove_job('id_scd_hotspot_keepdbalive')
        self.scheduler.remove_job('id_scd_update_keepdbalive')

    def start_scheduler(self):
        self.scheduler.start()

    def stop_scheduler(self):
        self.scheduler.shutdown()

    ############################# 任务调度 end #############################