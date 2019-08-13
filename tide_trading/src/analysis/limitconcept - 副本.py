# coding=utf-8
import src.common.tools as tools
import src.common.statistics as st
import os
import datetime
import tushare as ts

''' 涨停股概念统计模块（子进程）：获取实时数据，统计当前所有涨停股中，概念出现的多少，进行排序 '''

log_name = '../../log/limitconcept'

def main():
    start_idx = 0
    end_idx = 3000
    #不使用多进程
    Init()
    list_code = process(start_idx, end_idx)
    print(list_code)

#初始化
def Init():
    ts.set_token('75f181a930dc581d82c0cafd633c09d582d8ac0554c74854f73a9582')

def process(start_idx, end_idx):
    print("start=", start_idx, " end=", end_idx)

    my_log_filename = log_name + ".txt"

    if os.path.exists(my_log_filename):
        os.remove(my_log_filename)

    log = tools.CLogger('backtest', my_log_filename, 1)

    strMsg = 'start'
    log.getLogger().info(strMsg)
    list_code = GetStockList()

    step = 100
    all_count = len(list_code)
    times = all_count//step
    last_idx = 0


    dataframe1 = ts.get_realtime_quotes(list_code['symbol'][0:500])
    dataframe2 = ts.get_realtime_quotes(list_code['symbol'][501:1000])
    dataframe3 = ts.get_realtime_quotes(list_code['symbol'][1001:1500])
    dataframe4 = ts.get_realtime_quotes(list_code['symbol'][1501:2000])
    dataframe5 = ts.get_realtime_quotes(list_code['symbol'][2001:2500])
    dataframe6 = ts.get_realtime_quotes(list_code['symbol'][2501:3000])
    dataframe7 = ts.get_realtime_quotes(list_code['symbol'][3001:all_count])

    #print('code=',dataframe7['code'])
    #print('name=', dataframe7['name'])
    #print('pre_close=', dataframe7['pre_close'])#昨日收盘价
    #print('price=',dataframe7['price'])#当前价格

    mytool = st.CStatistics()

    list_ok = list()
    limit = 9.5 #界限值
    for idx in range(0,len(dataframe1)):
        code = dataframe1['code'][idx]
        pre_close = dataframe1['pre_close'][idx]
        nowprice = dataframe1['price'][idx]
        gain = mytool.calc_gain(float(nowprice), float(pre_close))#计算涨幅
        if gain > limit:
            list_ok.append(code)

    for idx in range(0, len(dataframe2)):
        code = dataframe2['code'][idx]
        pre_close = dataframe2['pre_close'][idx]
        nowprice = dataframe2['price'][idx]
        gain = mytool.calc_gain(float(nowprice), float(pre_close))  # 计算涨幅
        if gain > limit:
            list_ok.append(code)

    for idx in range(0, len(dataframe3)):
        code = dataframe3['code'][idx]
        pre_close = dataframe3['pre_close'][idx]
        nowprice = dataframe3['price'][idx]
        gain = mytool.calc_gain(float(nowprice), float(pre_close))  # 计算涨幅
        if gain > limit:
            list_ok.append(code)

    for idx in range(0, len(dataframe4)):
        code = dataframe4['code'][idx]
        pre_close = dataframe4['pre_close'][idx]
        nowprice = dataframe4['price'][idx]
        gain = mytool.calc_gain(float(nowprice), float(pre_close))  # 计算涨幅
        if gain > limit:
            list_ok.append(code)

    for idx in range(0, len(dataframe5)):
        code = dataframe5['code'][idx]
        pre_close = dataframe5['pre_close'][idx]
        nowprice = dataframe5['price'][idx]
        gain = mytool.calc_gain(float(nowprice), float(pre_close))  # 计算涨幅
        if gain > limit:
            list_ok.append(code)

    for idx in range(0, len(dataframe6)):
        code = dataframe6['code'][idx]
        pre_close = dataframe6['pre_close'][idx]
        nowprice = dataframe6['price'][idx]
        gain = mytool.calc_gain(float(nowprice), float(pre_close))  # 计算涨幅
        if gain > limit:
            list_ok.append(code)

    for idx in range(0, len(dataframe7)):
        code = dataframe7['code'][idx]
        pre_close = dataframe7['pre_close'][idx]
        nowprice = dataframe7['price'][idx]
        gain = mytool.calc_gain(float(nowprice), float(pre_close))  # 计算涨幅
        if gain > limit:
            list_ok.append(code)
        #print('code=',code,'  gain=',gain1)

    return list_ok

#函数：获取所有股票列表
def GetStockList():
    pro = ts.pro_api()
    # 查询当前所有正常上市交易的股票列表
    #data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
    print('股票总个数：', len(data))
    return data

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    main()
    endtime = datetime.datetime.now()
    print('处理用时 (秒)：', (endtime - starttime).seconds)

