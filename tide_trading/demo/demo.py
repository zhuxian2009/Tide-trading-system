#coding=utf-8
import h5py  #导入工具包
import numpy as np
import tushare as ts
import time
import datetime
import talib
import os
import pandas as pd
import requests
import json

#初始化
def Init():
    ts.set_token('75f181a930dc581d82c0cafd633c09d582d8ac0554c74854f73a9582')

def GetToday():
    now_time = datetime.datetime.now()
    day = now_time.strftime('%Y%m%d')
    print('end time is ', day)
    return day

#函数：获取所有股票列表
def GetStockList():
    pro = ts.pro_api()
    # 查询当前所有正常上市交易的股票列表
    #data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
    print('股票总个数：', len(data))
    return data.head(10)

def GetStockData(szType, szNumber):
    req = urllib2.Request(url)
    #print req
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    s = res.decode('gbk')
    print(s)
    return s

def main():
    # 更新的起始时间
    str_start_day = '20171201'
    str_end_day = GetToday()

    print('***********  main **************')
    #Init()
    #df = ts.pro_bar(ts_code='000001.SZ', adj='qfq', start_date=str_start_day, end_date=str_end_day)
    #print(df)

    url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000001,day,2017-12-01,,640,qfq'
    r = requests.get(url)  # 向指定网址请求，下载股票数据
    print(r.text)
    print('=================================================')
    my_json = json.loads(r.text)
    print(my_json)
    #交易日，开盘价，收盘价，最高价，最低价,总手
    my_day = my_json['data']['sh000001']['day']

    #ts_code trade_day open high low close 涨跌幅 总手 成交额（千元）
    new_list = list()
    for i in range(0, len(my_day)):
        list_row = list()
        list_row.append('sh000001')
        #trade_day
        list_row.append(my_day[i][0])
        # open
        list_row.append(my_day[i][1])
        # high
        list_row.append(my_day[i][3])
        # low
        list_row.append(my_day[i][4])
        # close
        list_row.append(my_day[i][2])
        # 涨跌幅
        list_row.append(0)
        # 总手
        list_row.append(my_day[i][5])
        # 成交额（千元）
        list_row.append(0)

        new_list.append(list_row)

    print(new_list)

if __name__ == '__main__':
    main()
