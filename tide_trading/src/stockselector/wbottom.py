# coding=utf-8
import talib
import math
import numpy as np
import src.stockselector.myselectorbase as myselectorbase
import operator
import src.common.tools as tools
import datetime

''' 找出双重底的个股(w底) '''
class CWBotton(myselectorbase.CMySelectorBase):
    def Init(self, min_interval, start_day, end_day):
        #将大区间分为N个小区间
        self.min_interval=min_interval
        # 大区间
        self.max_interval=2 * self.min_interval
        # 颈线位到左底涨幅
        self.neck = 10

        self.start_day = start_day
        self.end_day = end_day
        #self.start_day = '20190101'
        #self.end_day = self.GetToday()
        self.log = tools.CLogger('backtest', 'wbottom', 1)


    def ProcessEx(self, all_stock_kdata):
        if all_stock_kdata.empty:
            return

        starttime = datetime.datetime.now()

        # 需要的原始数据
        #交易日期
        trade_day = all_stock_kdata['trade_day']
        #收盘价 最高价 最低价
        low_price = all_stock_kdata['low']
        high_price = all_stock_kdata['high']
        close_price = all_stock_kdata['close']
        # 成交额
        amount = all_stock_kdata['amount']
        #macd指标
        macd = all_stock_kdata['macd']
        dif = all_stock_kdata['dif']
        dea = all_stock_kdata['dea']
        #当前被处理的股票代码
        code = all_stock_kdata['code'].iloc[0]
        cur_close = close_price.iloc[-1]
        cur_low = low_price.iloc[-1]
        cur_trade_day = trade_day.iloc[-1]

        # 每个小区间内的最低价
        len_low = len(low_price)

        #左底最低价格
        bottom1 = 0
        #左底在原始数据中的位置
        bottom1_idx = 0

        #右底最低价格
        bottom2 = 0
        # 右底在原始数据中的位置
        bottom2_idx = 0

        if len_low < self.max_interval:
            return
        #取最近一段固定时间作为小区间，找双底；
        # 算法描述：
        # 1. 找左区域的极小值
        # 2. 找右区域的极小值
        # 3. 找左底与右底之间区域的极大值
        # 4. 比较左底与右底的涨幅，是否相差<3%
        # 5. 比较左底与右底的macd值，是否形成底背离
        # 6. 终点日期收盘价，是否突破颈线位;并且最低点在颈线位下方
        # 以下条件可选
        # 7. 比较左底与右底的成交额，是否左底成交额>右底成交额
        # 8. 比较左底与极大值之间涨跌幅，是否>N%(判断颈线位幅度)
        # 9. 比较左底与右底之间，是否出现过涨停(判断股性活跃程度)
        # 10. 其他
        for i in range(len_low - self.max_interval, len_low, self.min_interval):
            #当前计算区间范围，左索引，右索引
            '''
            |---------------------------------|
            |             大区间              |
            |----------------|----------------|
            |     小区间1    |     小区间2    |
            |----------------|----------------|
            左索引        右索引
            '''
            idx_left = i
            idx_right = i + self.min_interval

            # 从原始数据中，提取需要计算的大区间
            interval_arrary = low_price[idx_left:idx_right]
            # 获取大区间数组中的极小值，以及对应的索引号
            min_index, min_number = min(enumerate(interval_arrary), key=operator.itemgetter(1))
            # print('[' , idx_left , ', ' , idx_right, ')','len = ',len(interval_arrary))

            # 小区间索引，映射到原始数据的索引号
            index = min_index + idx_left
            # this_day = trade_day[index]

            #小区间1的极小值，成为底1
            if bottom1 is 0:
                bottom1 = min_number
                bottom1_idx = index
            else:
                # 小区间2的极小值，成为底2
                bottom2 = min_number
                bottom2_idx = index

            #底1和底2都找到
            if bottom1 is not 0 and bottom2 is not 0:
                #计算两个底之间的百分比差值
                per = self.percentage(bottom2 - bottom1, bottom2)
                # 保留2位小数点
                per = round(per, 2)

                # 差距小于3个点，认为是双底
                if abs(per) < 3:
                    # 条件1 W底MACD值
                    bottom1_macd = macd[bottom1_idx]
                    bottom1_amount = amount[bottom1_idx]
                    #bottom1_dea = dea[bottom1_idx]
                    #bottom1_diff = dif[bottom1_idx]
                    bottom2_macd = macd[bottom2_idx]
                    bottom2_amount = amount[bottom2_idx]
                    #bottom2_dea = dea[bottom2_idx]
                    #bottom2_diff = dif[bottom2_idx]

                    #条件2 macd底背离
                    b_macd_depart = False
                    if bottom1_macd < bottom2_macd:
                        b_macd_depart = True
                    else:
                        continue

                    #条件3 底2缩量
                    b_bottom2_lessamount = False
                    if bottom1_amount > bottom2_amount:
                        b_bottom2_lessamount = True
                    else:
                        continue

                    #条件4 极大值与极小值之间，颈线位涨幅达到N%
                    b_neck = False
                    # 双底之间的区间极大值
                    w_interval = high_price[bottom1_idx:bottom2_idx]
                    max_index, max_number = max(enumerate(w_interval), key=operator.itemgetter(1))

                    # W底小区间索引映射成原始数据的索引
                    highest_idx = bottom1_idx + max_index
                    #print('W底区间极大值：', max_number, '  trade day=', trade_day[highest_idx])

                    per_gain = self.percentage(max_number - bottom1, bottom1)
                    # 保留2位小数点
                    per_gain = round(per_gain, 2)
                    #涨幅达到N%
                    if per_gain > self.neck:
                        #print('关注标的 ...  code=', code, ' per_gain=', per_gain)
                        b_neck = True
                    else:
                        continue

                    #条件5 双底之间，出现过涨停,统计涨停次数
                    '''b_has_limitup = False
                    # limitup_times = 0
                    for idx in range(bottom1_idx, bottom2_idx, 1):
                        close_today = close_price[idx]
                        close_yesterday = close_price[idx - 1]
                        # 日内涨幅
                        day_gain = (close_today - close_yesterday) / close_yesterday
                        # 保留2位小数点
                        day_gain = round(day_gain, 2)

                        if (day_gain > 0.09):
                            #print('涨幅=', day_gain, ' code=', code)
                            # limitup_times += 1
                            b_has_limitup = True
                    '''
                    #条件6 今天收盘价突破颈线位
                    b_standup_neck = False
                    if cur_close > max_number and cur_low < max_number:
                        b_standup_neck = True

                    #打印满足条件的标的
                    if b_macd_depart and b_bottom2_lessamount and b_neck and b_standup_neck:#b_has_limitup:
                        print('******** ', code, ' *********')
                        print('小间距：', self.min_interval,
                              '起始时间:', trade_day[len_low - self.max_interval], '~', trade_day[len_low - 1])
                        print('价格间距 = ', per, '%')
                        print('底1：index=', bottom1_idx, '  price=', bottom1, ' trade day=', trade_day[bottom1_idx])
                        print('底2：index=', bottom2_idx, '  price=', bottom2, ' trade day=', trade_day[bottom2_idx])
                        self.log.getLogger().info('******** ' + code + ' *********')
                        self.log.getLogger().info('底1：price=' + str(bottom1) + ' trade day=' + trade_day[bottom1_idx])
                        self.log.getLogger().info('底2：price=' + str(bottom2) + ' trade day=' + trade_day[bottom2_idx])
                        self.db.add_backtest_wbottom(code, bottom1, bottom2,
                                                     trade_day[bottom1_idx], trade_day[bottom2_idx], cur_trade_day,
                                                     self.min_interval)

                        #结果写数据库 code 名称 底的价格 双底相差幅度 区间大小 底的日期 突破日期；
                        # 唯一key：双底日期组合


    def Process(self):
        #self.Init()
        starttime = datetime.datetime.now()
        stock_basic = self.GetStockBasic()
        for code in stock_basic['ts_code']:

            all_stock_kdata = self.LoadData(code, self.start_day, self.end_day)

            #执行需要1毫秒
            #starttime2 = datetime.datetime.now()
            self.ProcessEx(all_stock_kdata)

            #endtime2 = datetime.datetime.now()
            #times2 = (endtime2 - starttime2).microseconds
            #if times2>0:
            #    print('wbottom LoadData 用时(微秒)：', times2)

        endtime = datetime.datetime.now()
        times = (endtime - starttime).seconds
        print('wbottom Process for code 用时(秒)：', times)
        #self.UnInit()


