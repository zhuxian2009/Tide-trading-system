import configparser

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


    def SaveConf(self):
        self.conf.set(self.session_backtest_w, self.s_bt_key_startday, self.s_bt_startday)
        self.conf.set(self.session_backtest_w, self.s_bt_key_endday, self.s_bt_endday)
        self.conf.set(self.session_backtest_w, self.s_bt_key_min_range, str(self.s_bt_min_range))
        self.conf.set(self.session_backtest_w, self.s_bt_key_max_range, str(self.s_bt_max_range))

        self.conf.set(self.session_db, self.db_key_username, self.db_username)
        self.conf.set(self.session_db, self.db_key_pwd, self.db_pwd)
        self.conf.set(self.session_db, self.db_key_host, self.db_host)

        # 写入文件
        with open(self.conf_filename, 'w') as fw:
            self.conf.write(fw)
