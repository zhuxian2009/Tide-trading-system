import configparser

class CConf_APSDeployment:
    def __init__(self):
        self.trigger = 'cron'
        self.day_of_week = '*'
        self.hour = '0-23'
        self.minutes = '*'
        self.second='*/10'


class CConf:
    #conf/conf.ini
    def __init__(self, conf_filename):
        self.conf_filename = conf_filename
        # 加载现有配置文件
        self.conf = configparser.ConfigParser()
        #双底回测的配置项
        self.session_backtest_w = 'backtest_w'

        self.s_bt_key_startday = 'startday'
        self.s_bt_key_endday = 'endday'
        self.s_bt_key_min_range = 'minrange'
        self.s_bt_key_max_range = 'maxrange'

        self.s_bt_startday = '20171201'
        self.s_bt_endday = '20190701'
        self.s_bt_min_range = 10
        self.s_bt_max_range = 30

        #数据库
        self.session_db = 'db'

        self.db_key_username = 'username'
        self.db_key_pwd = 'pwd'
        self.db_key_host = 'host'

        self.db_username = 'root'
        self.db_pwd = '123'
        self.db_host = 'localhost'

        #任务开关
        self.session_aps_switch = 'aps_switch'
        #key
        self.sw_key_hotspot = 'aps_hotspot'
        self.sw_key_reatime_quotes = 'aps_reatime_quotes'
        self.sw_key_rt_chipconcent = 'aps_rt_chipconcent'
        self.sw_key_dataservice_update = 'aps_dataservice_update'
        self.sw_key_rt_wbottom = 'aps_rt_wbottom'
        #value
        self.sw_hotspot = 0
        self.sw_reatime_quotes = 0
        self.sw_rt_chipconcent = 0
        self.sw_dataservice_update = 0
        self.sw_rt_wbottom = 0
        #计划部署
        self.deploy_hotspot = CConf_APSDeployment()
        self.deploy_reatime_quotes = CConf_APSDeployment()
        self.deploy_rt_chipconcent = CConf_APSDeployment()
        self.deploy_dataservice_update = CConf_APSDeployment()
        self.deploy_rt_wbottom = CConf_APSDeployment()


        self.ReadConf()

    def ReadConf(self):
        #读配置文件
        filename = self.conf.read(self.conf_filename)
        print(filename)

        # 读取双底回测的配置项
        self.s_bt_startday = self.conf.get(self.session_backtest_w, self.s_bt_key_startday)
        self.s_bt_endday = self.conf.get(self.session_backtest_w, self.s_bt_key_endday)
        self.s_bt_min_range = self.conf.getint(self.session_backtest_w, self.s_bt_key_min_range)
        self.s_bt_max_range = self.conf.getint(self.session_backtest_w, self.s_bt_key_max_range)
        #print(self.s_bt_key_startday, ':', self.s_bt_startday)
        #print(self.s_bt_key_endday, ':', self.s_bt_endday)
        #print(self.s_bt_key_min_range, ':', self.s_bt_min_range)
        #print(self.s_bt_key_max_range, ':', self.s_bt_max_range)

        #数据库
        self.db_username = self.conf.get(self.session_db, self.db_key_username)
        self.db_pwd = self.conf.get(self.session_db, self.db_key_pwd)
        self.db_host = self.conf.get(self.session_db, self.db_key_host)
        #print(self.db_key_username, ':', self.db_username)
        #print(self.db_key_pwd, ':', self.db_pwd)
        #print(self.db_key_host, ':', self.db_host)

        #任务开关
        self.sw_hotspot = self.conf.getint(self.session_aps_switch, self.sw_key_hotspot)
        self.sw_reatime_quotes = self.conf.getint(self.session_aps_switch, self.sw_key_reatime_quotes)
        self.sw_rt_chipconcent = self.conf.getint(self.session_aps_switch, self.sw_key_rt_chipconcent)
        self.sw_dataservice_update = self.conf.getint(self.session_aps_switch, self.sw_key_dataservice_update)
        self.sw_rt_wbottom = self.conf.getint(self.session_aps_switch, self.sw_key_rt_wbottom)

        #任务计划
        self.deploy_hotspot = self.GetAPSDeployment(self.sw_key_hotspot)
        self.deploy_reatime_quotes = self.GetAPSDeployment(self.sw_key_reatime_quotes)
        self.deploy_rt_chipconcent = self.GetAPSDeployment(self.sw_key_rt_chipconcent)
        self.deploy_dataservice_update = self.GetAPSDeployment(self.sw_key_dataservice_update)
        self.deploy_rt_wbottom = self.GetAPSDeployment(self.sw_key_rt_wbottom)

    #获取任务的计划部署
    def GetAPSDeployment(self, aps_name):
        deployment = CConf_APSDeployment()
        deployment.trigger = self.conf.get(aps_name, 'trigger')
        deployment.day_of_week = self.conf.get(aps_name, 'day_of_week')
        deployment.hour = self.conf.get(aps_name, 'hour')
        deployment.second = self.conf.get(aps_name, 'second')
        deployment.minutes = self.conf.get(aps_name, 'minutes')
        return deployment

    def SaveAPSDeployment(self, str_session, deployment):
        self.conf.set(str_session, 'trigger', deployment.trigger)
        self.conf.set(str_session, 'day_of_week', deployment.day_of_week)
        self.conf.set(str_session, 'hour', deployment.hour)
        self.conf.set(str_session, 'second', deployment.second)
        self.conf.set(str_session, 'minutes', deployment.minutes)

    def SaveConf(self):
        self.conf.set(self.session_backtest_w, self.s_bt_key_startday, self.s_bt_startday)
        self.conf.set(self.session_backtest_w, self.s_bt_key_endday, self.s_bt_endday)
        self.conf.set(self.session_backtest_w, self.s_bt_key_min_range, str(self.s_bt_min_range))
        self.conf.set(self.session_backtest_w, self.s_bt_key_max_range, str(self.s_bt_max_range))

        self.conf.set(self.session_db, self.db_key_username, self.db_username)
        self.conf.set(self.session_db, self.db_key_pwd, self.db_pwd)
        self.conf.set(self.session_db, self.db_key_host, self.db_host)

        #任务开关
        self.conf.set(self.session_aps_switch, self.sw_key_hotspot, str(self.sw_hotspot))
        self.conf.set(self.session_aps_switch, self.sw_key_reatime_quotes, str(self.sw_reatime_quotes))
        self.conf.set(self.session_aps_switch, self.sw_key_rt_chipconcent, str(self.sw_rt_chipconcent))
        self.conf.set(self.session_aps_switch, self.sw_key_dataservice_update, str(self.sw_dataservice_update))
        self.conf.set(self.session_aps_switch, self.sw_key_rt_wbottom, str(self.sw_rt_wbottom))

        # 任务计划
        self.SaveAPSDeployment(self.sw_key_hotspot, self.deploy_hotspot)
        self.SaveAPSDeployment(self.sw_key_reatime_quotes, self.deploy_reatime_quotes)
        self.SaveAPSDeployment(self.sw_key_rt_chipconcent, self.deploy_rt_chipconcent)
        self.SaveAPSDeployment(self.sw_key_dataservice_update, self.deploy_dataservice_update)
        self.SaveAPSDeployment(self.sw_key_rt_wbottom, self.deploy_rt_wbottom)

        # 写入文件
        with open(self.conf_filename, 'w') as fw:
            self.conf.write(fw)
