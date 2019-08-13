# coding=utf-8
import src.realtime.rt_hotspot as rt_hotspot
import src.datamgr.dbmgr as dbmgr
import datetime

def GetToday():
    now_time = datetime.datetime.now()
    day = now_time.strftime('%Y%m%d')
    print('end time is ', day)
    return day

if __name__ == '__main__':
    hotspot = rt_hotspot.CRT_Hotspot()
    hotspot.start()

    db = dbmgr.CDBMgr('localhost', 'root', '123', 'kdata')
    list_ret = db.query_allhotconsept()
    db.disconnect_db()
