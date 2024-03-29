# coding=utf-8

'''
文件锁，全局有效

'''

import platform

#动态载入模块
fcntl = None
msvcrt = None
bLinux = True
if platform.system() != 'Windows':
    fcntl = __import__("fcntl")
    bLinux = True
else:
    msvcrt = __import__('msvcrt')
    bLinux = False


#文件锁
class CFileLock:
    def __init__(self, filename):
        self.filename = filename + '.lock'
        self.file = None

    #文件锁
    def lock(self):
        if bLinux is True:
            self.file = open(self.filename, 'wb')
            try:
                fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                print(self.filename, ' file_lock success ********')
            except:
                print(self.filename, ' file_lock error')
                return False
        else:
            self.file = open(self.filename, 'wb')
            try:
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
                print(self.filename, ' file_lock success ********')
            except:
                print(self.filename, ' file_lock error')
                return False

            return True

    def unlock(self):
        try:
            if bLinux is True:
                fcntl.flock(self.file, fcntl.LOCK_UN)
                self.file.close()
            else:
                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            print(self.filename, ' file_unlock success')
        except:
            print('file_unlock error')

    #def __del__(self):
        #print('CFileLock.__del__  unlock')
        #self.unlock()