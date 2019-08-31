#coding=utf-8
import logging
import sys
import datetime


def singleton(cls):
    """
    单例模式的装饰器函数
    :param cls: 实体类
    :return: 返回实体类对象
    """
    instances = {}

    def getInstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getInstance


@singleton
class CLogger(object):
    def __init__(self, appName, logFileName, out=0):
        """
        获取日志处理对象
        :param appName: 应用程序名
        :param logFileName: 日志文件名
        :param out: 设置输出端：0：默认控制台，1：输入文件，其他：控制台和文件都输出
        :return: 返回日志对象
        """
        self.appName = appName
        self.logFileName = logFileName
        self.out = out

    def getLogger(self):
        # 获取logging实例
        logger = logging.getLogger(self.appName)
        # 指定输出的格式
        formatter = logging.Formatter('%(name)s  %(asctime)s  %(levelname)-8s:%(message)s')

        # 文件日志
        if not logger.handlers:
            file_handler = logging.FileHandler(self.logFileName, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logging.basicConfig(filename=self.logFileName, filemode="w",
                                format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S",
                                level=logging.DEBUG)

            # 控制台日志
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)

            # # 指定日志的最低输出级别
            logger.setLevel(logging.INFO)  # 20

            # 为logger添加具体的日志处理器输出端
            if self.out == 1:
                logger.addHandler(file_handler)
            elif self.out == 0:
                logger.addHandler(console_handler)
            else:
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)
        return logger


#废弃
'''
import sys
def get_cur_info():
    # 当前文件名，可以通过__file__获得
    print(sys._getframe().f_code.co_filename, end=' ')
    # 当前函数名
    print(sys._getframe().f_code.co_name, end=' ')
    # 当前行号
    print(sys._getframe().f_lineno, end=' ')'''

#获取当前时间
def get_cur_time():
    str_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return str_time

