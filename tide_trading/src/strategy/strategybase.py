import h5py  #导入工具包
import talib
import math
import numpy as np
import src.common.statistics as st
import src.datamgr.baseinfo as bi
#为了实现虚函数
from abc import ABC, abstractmethod
import src.common.status as status

#input 股票详情
#str_dailyFile = 'stockdaily.h5'
#file_daily = h5py.File(str_dailyFile, 'r')

class CStrategyBase(ABC):
    def __init__(self, file_daily):
        self.file_daily = file_daily
        self.allClose = 0
        self.allOpen = 0
        self.allHigh = 0
        self.allVol = 0
        self.allTradeDay = 0#所有交易日
        self.ma5 = 0
        self.ma10 = 0
        self.ma20 = 0
        self.ma30 = 0
        self.ma60 = 0
        self.volma5 = 0
        self.volma10 = 0
        self.volma20 = 0
        self.volma30 = 0
        #涨幅
        self.pct_chg = 0
        self.Status = status.CStatus()
        #股票交易日期
        self.code_trade_day = 0
        #当前回测所在的位置
        self.idx = 0
        #统计工具
        self.mytool = st.CStatistics()
        self.stock_base_info = bi.CBaseinfo()
        #买卖状态时，价格等信息
        self.buy_price = 0
        self.buy_open = 0
        self.buy_close = 0
        self.sell_price = 0
        self.sell_open = 0
        self.sell_close = 0

    #初始化
    def Init(self):
        #读取每个股票的概念、行业基本信息；
        self.stock_base_info.read_excel()

    #加载前N天的数据，N=0时，表示全部加载
    def LoadData(self, code, n=0):

        if code == 'trade_day' or code == '/trade_day':
            self.allTradeDay = self.file_daily['/trade_day/trade_date'][:]
            return

        #idx 索引从0开始
        self.idx = n-1
        key = '/' + code

        if n == 0:
            # 所有的收盘价
            self.allClose = self.file_daily[key + '/close'][:]
            # 所有的开盘价
            self.allOpen = self.file_daily[key + '/open'][:]
            self.allHigh = self.file_daily[key + '/high'][:]
            self.allVol = self.file_daily[key + '/vol'][:]
        else:
            # 所有的收盘价
            self.allClose = self.file_daily[key + '/close'][:n]
            # 所有的开盘价
            self.allOpen = self.file_daily[key + '/open'][:n]
            self.allHigh = self.file_daily[key + '/high'][:n]
            self.allVol = self.file_daily[key + '/vol'][:n]

        self.ma5 = self.file_daily[key + '/ma5'][:]
        self.ma10 = self.file_daily[key + '/ma10'][:]
        self.ma20 = self.file_daily[key + '/ma20'][:]
        self.ma30 = self.file_daily[key + '/ma30'][:]
        self.ma60 = self.file_daily[key + '/ma60'][:]
        self.volma5 = self.file_daily[key + '/ma5vol'][:]
        self.volma10 = self.file_daily[key + '/ma10vol'][:]
        self.volma20 = self.file_daily[key + '/ma20vol'][:]
        self.volma30 = self.file_daily[key + '/ma30vol'][:]
        self.pct_chg = self.file_daily[key + '/pct_chg'][:]
        self.code_trade_day = self.file_daily[key + '/trade_date'][:]

    #更新算术平均值
    def UpdateMaX(self):
        self.ma5 = talib.SMA(self.allClose, timeperiod=5)
        self.ma10 = talib.SMA(self.allClose, timeperiod=10)

    def UnInit(self):
        self.file_daily.close()

    '''条件之一：判断某股票的平均值maX，是否连续N日上行,Period表示算术平均值'''
    def Condition1(self, N, Period):
        #计算maX
        if(Period == 5):
            self.maX = self.ma5
        elif(Period == 10):
            self.maX = self.ma10
        elif (Period == 20):
            self.maX = self.ma20
        elif (Period == 30):
            self.maX = self.ma30
        elif (Period == 60):
            self.maX = self.ma60
        #else:
        #    self.maX = talib.SMA(self.allClose, timeperiod=Period)
        #print('*************** code = ',file_daily[key].name,' ma5 ****************len=',len(maX),' 计算多日算术平均值:',Period)

        #数组中，有效值的开始位置
        validIdx = 0
        #是否上行
        isUp = True

        #比较N个maX的值
        for i in range(N):
            #回退到N个交易日前，开始统计
            curIdx = i + (self.idx - N + 1)

            #判断空值,容错
            if math.isnan(self.maX[curIdx]):
                continue
            else:
                #最近N日，ma5连续向上
                if curIdx >= self.idx:
                    print('......  ma', Period, ' 数据不够，无法处理')
                    isUp = False
                    break

                #h5文件中，索引越大，日期越大
                for j in range(curIdx, N+curIdx-1):
                    yestoday = self.maX[j]
                    today = self.maX[j+1]
                    if(today < yestoday):
                        isUp=False
                        break

                return isUp
        return False

    #条件之一:前N日，出现涨停板;涨停之后，连续3日运行于涨停之上
    def Condition2(self, N):
        totalCnt = len(self.allClose)
        if totalCnt - N - 2 <= 0:
            return False

        # N日前收盘价,开盘价
        #CloseN=self.file_daily[code + '/close'][N]
        #OpenN=self.file_daily[code + '/open'][N]

        CloseN = self.allClose[N]
        OpenN = self.allOpen[N]

        #N+1前日收盘价
        CloseN1 = self.allClose[N + 1]
        OpenN1 = self.allOpen[N + 1]

        # N-1日前收盘价,开盘价
        CloseN_1=self.allClose[N-1]
        OpenN_1=self.allOpen[N-1]

        # N-2日前收盘价,开盘价
        CloseN_2=self.allClose[N-2]
        OpenN_2=self.allOpen[N-2]

        # N-3日前收盘价,开盘价
        CloseN_3=self.allClose[N-3]
        OpenN_3=self.allOpen[N-3]

        #涨幅超过9%
        if CloseN1*1.09<CloseN:
            if CloseN_1>CloseN and CloseN_2>CloseN and CloseN_3>CloseN:
                return True
        return False

    #投入一份新的数据 ，虚函数
    @abstractmethod
    def FeedOneData(self, close, open, low=0, high=0):
        pass

    def AppendOneData(self, close, open, low=0, high=0, vol=0):
        # 最后加入到基础数据中
        self.allClose = np.append(self.allClose, close)
        self.allOpen = np.append(self.allOpen, open)
        self.allHigh = np.append(self.allHigh, high)
        self.allVol = np.append(self.allVol, vol)

    #遍历H5文件中，遍历所有股票，获取某一天的信息
    def PrintH5(self):
        print('>>>>>>>>>>>>> loop h5 file keys  <<<<<<<<<<<<<<<<<<<<')

        for key in self.file_daily.keys():

            #计算ma5
            ma5 = talib.SMA(self.allClose,timeperiod=5)
            print('*************** code = ',self.file_daily[key].name,' ma5 ****************len=',len(ma5))
            #print(ma5)

            print('.......................')
            #数组中，有效值的开始位置
            validIdx = 0
            isUp = True

            for i in range(len(ma5)):
                #print(ma5[i])
                #判断空值
                if math.isnan(ma5[i]):
                    #print('i=',i,'  is none')
                    validIdx = i+1
                else:
                    #最近N日，ma5连续向上
                    N=3
                    if validIdx+N+1 >= len(ma5):
                        print('......  ma5 数据不够，无法处理')
                        isUp = False
                        break

                    for j in range(validIdx,N+validIdx):
                        if(ma5[j]<ma5[j+1]):
                            isUp=False
                            break

                    if isUp is True:
                        print('......  ma5 连续上行')
                        break
                    #if isUp is True:
                     #   print('......  ma5 连续上行')
                    continue

            #总条目数
            totalCnt = len(self.allClose)


