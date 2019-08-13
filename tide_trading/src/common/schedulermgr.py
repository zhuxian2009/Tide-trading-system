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
        self.dataservice = dataservice.CDataServiceMysql(str_conf_path)

    # 启动任务调度
    def start(self):
        self.add_hotspot_job()
        self.add_dataservice_update_job()
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

    ############################# 任务调度 * 热门概念  #############################

    # 任务调度,DB保活
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

    # 任务调度,DB保活
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

    # 检测热点的任务
    def add_hotspot_job(self):
        g_share_hotspot.value = 'hotspot'
        g_share_hotspotdb_keepalive.value = 'aps_keep_hotspotdb_alive'

        print('in CSchedulerMgr ... add_hotspot_job')
        print('add_hotspot_job*************** pid=', os.getpid(), '  g_share_hotspot=', g_share_hotspot.value)
        # APScheduler有三种内置的(trigger)触发器
        # date 日期：触发任务运行的具体日期
        # interval 间隔：触发任务运行的时间间隔
        # cron 周期：触发任务运行的周期

        # 参数说明
        # second='*/5',每5秒执行一次
        # minute='*/2',每两分钟执行一次
        # hour='9-15',9点到15点之间执行
        #day_of_week='mon-fri',周一到周五；day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun) -
        # （表示一周中的第几天，既可以用0-6表示也可以用其英语缩写表示）
        try:
            '''self.scheduler.add_job(func=self.aps_hotspot, trigger='cron',
                                   hour='9-11', minute=30, second='*/5', day_of_week='mon-fri', id='id_scd_hotspot_am')
            self.scheduler.add_job(func=self.aps_hotspot, trigger='cron',
                                   hour='13-15', second='*/5', day_of_week='mon-fri', id='id_scd_hotspot_pm')'''
            '''self.scheduler.add_job(func=self.aps_hotspot, trigger='cron',
                                   hour='0-23', second='*/5', day_of_week='mon-fri', id='id_scd_hotspot_am')'''

            #db保活,每小时连一次mysql，否则超过8小时会断开
            self.scheduler.add_job(func=self.aps_keep_hotspotdb_alive, trigger='cron',
                                   hour='0-23',second='*/5', day_of_week='*',  id='id_scd_hotspot_keepdbalive')
            #self.scheduler.add_job(func=self.aps_hotspot, trigger='cron',
            #                       hour='13-15', second='*/5', day_of_week='mon-fri', id='id_scd_hotspot_pm')
        except Exception as e:
            print('add_hotspot_job error! ... ' + e)

    # 更新最新k线的任务
    def add_dataservice_update_job(self):
        g_share_db_update.value = 'dataservice_update'
        print('in CSchedulerMgr ... add_dataservice_update_job')
        print('add_dataservice_update_job*************** pid=', os.getpid(), '  g_share_db_update=', g_share_db_update.value)
        # APScheduler有三种内置的(trigger)触发器
        # date 日期：触发任务运行的具体日期
        # interval 间隔：触发任务运行的时间间隔
        # cron 周期：触发任务运行的周期

        # 参数说明
        # second='*/5',每5秒执行一次
        # minute='*/2',每两分钟执行一次
        # hour='9-15',9点到15点之间执行
        # day_of_week='mon-fri',周一到周五；day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun) -
        # （表示一周中的第几天，既可以用0-6表示也可以用其英语缩写表示）
        try:
            # db保活,每小时连一次mysql，否则超过8小时会断开
            self.scheduler.add_job(func=self.aps_keep_updatedb_alive, trigger='cron',
                                   hour='0-23', second='*/5', day_of_week='*', id='id_scd_update_keepdbalive')
            self.scheduler.add_job(func=self.aps_dataservice_update, trigger='cron',
                                   hour=18, minute=10, day_of_week='mon-fri', id='id_dataservice_update')
            # self.scheduler.add_job(func=self.aps_hotspot, trigger='cron',
            #                       hour='13-15', second='*/5', day_of_week='mon-fri', id='id_scd_hotspot_pm')
        except Exception as e:
            print('add_dataservice_update_job error! ... ' , e)

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