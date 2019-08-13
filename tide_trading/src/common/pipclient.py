#coding=utf-8
'''
命名管道客户端，只读
服务器先启动，创建好管道文件，client再启动，否则读不到文件
'''

import os

class CPipClient:
    def __init__(self, pipname):
        self.pipname = pipname
        self.pip_path = '/tmp/' + pipname
        self.rf = None

    def readpip(self):
        if self.rf is None:
            self.rf = os.open(self.pip_path, os.O_RDONLY)

        msg = os.read(self.rf, 1024)
        #bytes to str
        msg = bytes.decode(msg)
        print('CPipClient::readpip ', msg)
        return  msg

    def __del__(self):
        print('CPipClient::__del__')
        os.close(self.rf)