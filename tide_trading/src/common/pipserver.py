#coding=utf-8
import os
'''
命名管道服务端，只写
服务器先启动，创建好管道文件，client再启动，否则读不到文件
'''

class CPipServer:
    def __init__(self,pipname):
        self.pipname = pipname
        self.pip_path = '/tmp/' + pipname
        if os.path.exists(self.pip_path):
            os.remove(self.pip_path)

        os.mkfifo(self.pip_path)
        self.wf = os.open(self.pip_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)

    def writepip(self, msg):
        #str.encode: str to bytes
        os.write(self.wf, str.encode(msg))

    def __del__(self):
        print('CPipServer::__del__')
        os.close(self.wf)
