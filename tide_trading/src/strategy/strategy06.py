# coding=utf-8
import src.strategy.strategybase as stt_base

from src.common.status import State

''' 相对前面的量能，很少的量拉涨停； vol<vol_ma20*2; ma30乖离率调参 '''

class CStrategy06(stt_base.CStrategyBase):

    #投入一份新的数据
    def FeedOneData(self, close, open, low=0, high=0, vol=0):
        #self.idx = self.idx + 1
        #最后加入到基础数据中
        self.AppendOneData(close, open, low, high, vol)
        self.idx = self.idx + 1

        #ma5,ma10,连续5日上行
        #up5 = self.Condition1(3, 5)
        #up10 = 1  # self.Condition1(5, 10)
        #up20 = self.Condition1(3, 20)
        #up60 = self.Condition1(3, 60)
        #今天
        #涨幅，应该根据close open 计算，这里简单处理
        pct_chg_idx = self.idx
        pct_chg_today = self.pct_chg[pct_chg_idx]
        vol_today = self.allVol[pct_chg_idx]
        close_today = self.allClose[pct_chg_idx]
        # 昨天
        pct_chg_yesterday = self.pct_chg[pct_chg_idx-1]
        vol_yesterday = self.allVol[pct_chg_idx-1]
        close_yesterday = self.allClose[pct_chg_idx-1]
        # 前天
        pct_chg_beforyesterday = self.pct_chg[pct_chg_idx-2]
        vol_beforyesterday = self.allVol[pct_chg_idx-2]
        close__beforyesterday = self.allClose[pct_chg_idx-2]

        cur_ma5 = self.ma5[self.idx]
        cur_ma20 = self.ma20[self.idx]
        cur_ma30 = self.ma30[self.idx]
        cur_ma60 = self.ma60[self.idx]
        cur_volma10 = self.volma10[self.idx]
        cur_volma20 = self.volma20[self.idx]
        min_vol = self.MinVol(30)

        #过滤第一天出现长上影线的形态
        #gain1 = self.mytool.calc_gain(high, open)
        #gain2 = self.mytool.calc_gain(close, open)
        #self.bLongLine = 0
        #if gain1-gain2 > 2:
        #    self.bLongLine = 1

        #状态归0
        if self.Status.getState() is State.out_view or self.Status.getState() is State.sell:
            self.Status.toNone()

        # 条件1：昨天涨停的情况
        bCanBuy = False
        if pct_chg_yesterday > 9 and vol_yesterday<cur_volma20*2:
            bCanBuy = True

        #条件2：前5日，波动价格不能大于15%，表示启动的初级阶段
        max_price = self.MaxHigh(5)
        min_price = self.MinPrice(5)
        rang_price = self.mytool.calc_gain(max_price, min_price)

        # 条件3：涨停之日，close突破所有均线
        if bCanBuy:
            if close_yesterday<cur_ma60 or close_yesterday<cur_ma5:
                bCanBuy = False

        # 当日最高价高于前几日的最高价
        if (bCanBuy and rang_price < 15):
            #判断买入点
            self.Status.View()
            self.Status.Buy2Hold()
            self.Status.setState(State.buy)
            self.buy_price = open
        else:
            self.Status.Buy2Hold()

            if self.Status.getState() is not State.none:
                #卖点，止盈
                if self.Status.getState() is State.hold:
                    #止盈价格
                    sellprice = self.mytool.calc_gain(high, self.buy_price)
                    # 止损价格;如果买入当日出现阴线，且量远大于涨停量，第二日马上跑路
                    sellprice2 = self.mytool.calc_gain(close, self.buy_price)
                    #赚2个点卖掉
                    if sellprice >= 5:
                        self.Status.setState(State.sell)
                        self.sell_price = high
                    # 卖点，止损
                    elif sellprice2 < -3:
                        self.Status.setState(State.sell)
                        self.sell_price = close
            else:
                self.Status.setState(State.none)

        #最后加入到基础数据中
        #self.AppendOneData(close, open, low, high, vol)
        #self.idx = self.idx + 1
        #self.UpdateMaX()

        return self.Status.getState()

    #N天内最高价
    def MaxHigh(self, days):
        self.max = 0
        for day in range(days):
            self.now = self.allHigh[self.idx-day-1]
            if self.max <= self.now:
                self.max = self.now
            else:
                continue
        return self.max

    # N天内最低价(简单处理，开盘价)
    def MinPrice(self, days):
        self.min = 1000
        for day in range(days):
            self.now = self.allOpen[self.idx - day - 1]
            if self.min >= self.now:
                self.min = self.now
            else:
                continue
        return self.min

    #N天内最高成交量（手）
    def MaxVol(self, days):
        self.max = 0
        for day in range(days):
            self.now = self.allVol[self.idx-day-1]
            if self.max <= self.now:
                self.max = self.now
            else:
                continue
        return self.max

    #N天内最低成交量（手）
    def MinVol(self, days):
        self.min = self.allVol[self.idx-1]
        for day in range(days):
            self.now = self.allVol[self.idx-day-1]
            if self.min >= self.now:
                self.min = self.now
            else:
                continue
        return self.min

