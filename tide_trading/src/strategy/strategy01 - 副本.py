import h5py  #导入工具包
import talib
import math


#input 股票详情
str_dailyFile = 'stockdaily.h5'
file_daily = h5py.File(str_dailyFile, 'r')

def UnInit():
    file_daily.close()

#遍历H5文件中，遍历所有股票，获取某一天的信息
def PrintH5():
    print('>>>>>>>>>>>>> loop h5 file keys  <<<<<<<<<<<<<<<<<<<<')

    for key in file_daily.keys():

        #计算ma5
        ma5 = talib.SMA(file_daily[key + '/close'][:],timeperiod=5)
        print('*************** code = ',file_daily[key].name,' ma5 ****************len=',len(ma5))
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
                if validIdx+N+1>=len(ma5):
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

        #ma20 = talib.SMA(file_daily[key + '/close'][:], timeperiod=20)
        #print('*************** code = ', file_daily[key].name, ' ma20 ****************len=',len(ma20))
        #print(ma20)

        #ma30 = talib.SMA(file_daily[key + '/close'][:], timeperiod=30)
        #print('*************** code = ', file_daily[key].name, ' ma30 ****************len=',len(ma30))
        #print(ma30)



        #总条目数
        totalCnt = len(file_daily[key + '/open'])

'''
        for i in range(totalCnt):
            print('key=', key, end='')
            #倒序显示
            print(' open=',file_daily[key + '/open'][totalCnt-i-1],end='')
            print(' close=',file_daily[key + '/close'][totalCnt-i-1],end='')
            print(' high=',file_daily[key + '/high'][totalCnt-i-1],end='')
            print(' low=',file_daily[key + '/low'][totalCnt-i-1],end='')
            print(' pct_chg=',file_daily[key + '/pct_chg'][totalCnt-i-1])
#        print(file_daily[key + '/open'][:])
#        print(file_daily[key+'/close'][:])
#        print(file_daily[key+'/pct_chg'][:])
'''

def main():
    print('***********  main **************')
    PrintH5()
    UnInit()

if __name__ == '__main__':
    main()