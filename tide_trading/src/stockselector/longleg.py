# coding=utf-8
import src.common.tools as tools
import src.common.statistics as st
import os
import datetime
import tushare as ts
import src.stockselector.selectorbase as selectorbase

''' 涨停股概念统计模块（子进程）：获取实时数据，统计当前所有涨停股中，概念出现的多少，进行排序 '''
class CLongLeg(selectorbase.CSelectorBase):
    def __init__(self):
        self.log_name = 'log/limitconcept'
        self.MyInit()

    def process(self):
        list_code = self.GetStockList()

        all_count = len(list_code)
        dataframe1 = ts.get_realtime_quotes(list_code['symbol'][0:500])
        dataframe2 = ts.get_realtime_quotes(list_code['symbol'][501:1000])
        dataframe3 = ts.get_realtime_quotes(list_code['symbol'][1001:1500])
        dataframe4 = ts.get_realtime_quotes(list_code['symbol'][1501:2000])
        dataframe5 = ts.get_realtime_quotes(list_code['symbol'][2001:2500])
        dataframe6 = ts.get_realtime_quotes(list_code['symbol'][2501:3000])
        dataframe7 = ts.get_realtime_quotes(list_code['symbol'][3001:all_count])

        mytool = st.CStatistics()

        list_ok = list()
        limit = 9.5 #界限值
        for idx in range(0, len(dataframe1)):
            code = dataframe1['code'][idx]
            pre_close = dataframe1['pre_close'][idx]
            nowprice = dataframe1['price'][idx]
            low = dataframe1['low'][idx]
            gain = mytool.calc_gain(float(nowprice), float(pre_close))#计算涨幅
            low_gain = mytool.calc_gain(float(nowprice), float(low))  # 计算涨幅
            aaa = abs(low_gain/gain)
            if abs(low_gain/gain) > 3:
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

