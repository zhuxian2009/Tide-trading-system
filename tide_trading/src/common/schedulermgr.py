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
#设置，调用一次
import src.common.setting as setting
#实时双底
import src.realtime.rt_wbottom as rt_wbottom
#配置文件
import src.common.conf as conf

import redis
import os
import sys

class CSchedulerMgr:
    def __init__(self, str_conf_path, log):
        #配置文件
        self.myconf = conf.CConf(str_conf_path)
        self.myconf.ReadConf()

        self.log = log

        self.scheduler = myScheduler()
        self.rt_hotspot = rt_hotspot.CRT_Hotspot(str_conf_path, log)
        self.rt_quotes = rt_quotes.CRT_Quotes(str_conf_path, log)
        self.dataservice = dataservice.CDataServiceMysql(str_conf_path, log)
        self.rt_chipconcent = rt_chipconcent.CRT_ChipConcent(str_conf_path, log)
        self.setting = setting.CSetting(str_conf_path, log)
        self.rt_wbottom = rt_wbottom.CRT_WBottom(str_conf_path, log)
        self.re = None

        try:
            self.re = redis.Redis(host='127.0.0.1', port=6379, db=0)
        except Exception as e:
            print(e)
            log_h = os.path.basename(__file__) + ":" + __name__ + ":" + str(sys._getframe().f_lineno) + ":  "
            self.log.error(log_h+e)

        #设置系统参数
        self.setting.set_config()

    # 启动任务调度
    def start(self):
        self.add_job()
        self.start_scheduler()

    ############################# 获取任务参数 #############################
    def get_hotspot_status(self):
        ret = self.re.get('key_rt_hotspot_aps_hotspot')
        return str(ret, 'utf-8')
    def get_rt_wbottom_status(self):
        ret = self.re.get('key_rt_wbottom_aps_wbottom')
        return str(ret, 'utf-8')
    def get_reatime_quotes_status(self):
        ret = self.re.get('key_rt_quotes_aps_reatime_quotes')
        return str(ret, 'utf-8')
    def get_db_update_status(self):
        ret = self.re.get('key_dataservice_mysql_aps_dataservice_update')
        return str(ret, 'utf-8')
    def get_rt_chipconcent_status(self):
        ret = self.re.get('key_rt_chipconcent_aps_chip_c')
        return str(ret, 'utf-8')
    ############################# 任务调度 #############################

    ######################## 热门行业 热门概念################ 任务调度

    # 任务调度
    def aps_hotspot(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_hotspot')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_hotspot  pid=", os.getpid(), "  ppid=", os.getppid())

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_hotspot, lock failed')
            return
        
        self.rt_hotspot.aps_hotspot()

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_hotspot')
        my_lock.unlock()

    ######################## 热门行业 热门概念################ 任务调度

    # 任务调度
    def aps_rt_wbottom(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_rt_wbottom')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_rt_wbottom  pid=", os.getpid(), "  ppid=", os.getppid())

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_rt_wbottom, lock failed')
            return

        self.rt_wbottom.aps_wbottom()

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_rt_wbottom')
        my_lock.unlock()

    ######################## 实时更新出价 ################
    def aps_reatime_quotes(self):
        print(tools.get_cur_time(), ' in CSchedulerMgr ... aps_reatime_quotes')
        # os.getpid()获取当前进程id     os.getppid()获取父进程id
        print("aps_reatime_quotes  pid=", os.getpid(), "  ppid=", os.getppid())

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_reatime_quotes, lock failed')
            return

        self.setting.set_config()
        self.rt_quotes.aps_reatime_quotes()

        print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_reatime_quotes')
        my_lock.unlock()

    ######################### 定时更新每天K线数据 ################ 任务调度

    # 任务调度,定时更新kdata
    def aps_dataservice_update(self):
        print(tools.get_cur_time(), ' in aps_dataservice_update')

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_dataservice_update, lock failed')
            return

        self.dataservice.aps_dataservice_update()

        print(tools.get_cur_time(), ' out aps_dataservice_update')
        my_lock.unlock()

    ######################## 实时统计筹码集中的个股 ################
    def aps_rt_chipconcent(self):
        print(tools.get_cur_time(), ' in aps_rt_chipconcent')

        my_lock = filelock.CFileLock(sys._getframe().f_code.co_name)
        if my_lock.lock() is False:
            print(tools.get_cur_time(), ' out CSchedulerMgr ... aps_rt_chipconcent, lock failed')
            return

        self.rt_chipconcent.aps_chip_c()

        print(tools.get_cur_time(), ' out aps_rt_chipconcent')
        my_lock.unlock()

    ############################################  添加任务调度的具体任务
    def add_job(self):
        try:
            if self.myconf.sw_hotspot is 1:
                self.scheduler.add_job(func=self.aps_hotspot, trigger=self.myconf.deploy_hotspot.trigger,
                                       hour=self.myconf.deploy_hotspot.hour, second=self.myconf.deploy_hotspot.second,
                                       day_of_week=self.myconf.deploy_hotspot.day_of_week, id='id_scd_hotspot_pm')

            if self.myconf.sw_dataservice_update is 1:
                self.scheduler.add_job(func=self.aps_dataservice_update, trigger=self.myconf.deploy_dataservice_update.trigger,
                                       hour=self.myconf.deploy_dataservice_update.hour,
                                       minute=self.myconf.deploy_dataservice_update.minute,
                                       second=self.myconf.deploy_dataservice_update.second,
                                       day_of_week=self.myconf.deploy_dataservice_update.day_of_week, id='id_dataservice_update')

            if self.myconf.sw_reatime_quotes is 1:
                self.scheduler.add_job(func=self.aps_reatime_quotes, trigger=self.myconf.deploy_reatime_quotes.trigger,
                                       hour=self.myconf.deploy_reatime_quotes.hour, second=self.myconf.deploy_reatime_quotes.second,
                                       day_of_week=self.myconf.deploy_reatime_quotes.day_of_week, id='id_scd_quotes')

            if self.myconf.sw_rt_chipconcent is 1:
                self.scheduler.add_job(func=self.aps_rt_chipconcent, trigger=self.myconf.deploy_rt_chipconcent.trigger,
                                       hour=self.myconf.deploy_rt_chipconcent.hour,
                                       second=self.myconf.deploy_rt_chipconcent.second,
                                       day_of_week=self.myconf.deploy_rt_chipconcent.day_of_week, id='id_scd_chipconcent')


            if self.myconf.sw_rt_wbottom is 1:
                self.scheduler.add_job(func=self.aps_rt_wbottom, trigger=self.myconf.deploy_rt_wbottom.trigger,
                                       hour=self.myconf.deploy_rt_wbottom.hour,
                                       minute=self.myconf.deploy_rt_wbottom.minute,
                                       second=self.myconf.deploy_rt_wbottom.second,
                                       day_of_week=self.myconf.deploy_rt_wbottom.day_of_week, id='id_rt_wbottom')
        except Exception as e:
            print('add_job error! ... ' + e)

    def remove_hotspot_job(self):
        self.scheduler.remove_job('id_scd_hotspot_am')
        self.scheduler.remove_job('id_scd_hotspot_pm')
        
        self.scheduler.remove_job('id_scd_quotes_am')
        self.scheduler.remove_job('id_scd_quotes_pm')
        
        self.scheduler.remove_job('id_scd_chipconcent_am')
        self.scheduler.remove_job('id_scd_chipconcent_pm')
        
        self.scheduler.remove_job('id_dataservice_update')

    def start_scheduler(self):
        self.scheduler.start()

    def stop_scheduler(self):
        self.scheduler.shutdown()

    ############################# 任务调度 end #############################