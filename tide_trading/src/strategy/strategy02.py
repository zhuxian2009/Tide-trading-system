# coding=utf-8
import strategybase as stt_base
from strategybase import State


''' 突破平台策略 '''


class CStrategy02(stt_base.CStrategyBase):

    #投入一份新的数据
    def FeedOneData(self, close, open, low=0, high=0, vol=0):
        #self.idx = self.idx + 1

        #ma5,ma10,连续5日上行
        up5 = self.Condition1(5, 5)
        up10 = 1  # self.Condition1(5, 10)
        up20 = self.Condition1(5, 20)
        up60 = self.Condition1(3, 60)
        pct_chg = self.pct_chg[self.idx]

        cur_ma5 = self.ma5[self.idx]
        cur_ma20 = self.ma20[self.idx]
        #状态归0
        if self.enState is State.out_view or self.enState is State.sell:
            self.enState = State.none

        max_high = self.MaxHigh(30)

        #if open > cur_ma5 and close < cur_ma5 and up5 and up10:
        # 5日均线连续上行
        # 当日最高价高于前几日的最高价
        if up5 and up20 and up60 and close > cur_ma5:
            #判断买入点
            print('max high = ', max_high)
            if self.enState is State.view:
                self.enState = State.viewing
            elif self.enState is State.none:
                self.enState = State.view

            if self.enState is State.buy:
                self.enState = State.hold

            #乖离率
            BIAS = (close - cur_ma20)/cur_ma20*100

            #涨幅大于7个点
            #if self.mytool.calc_gain(close, open) > 3 and (self.enState != State.hold) and pct_chg < 9 and BIAS < 10 \
            if self.mytool.calc_gain(close, open) > 3 and (self.enState != State.hold) and pct_chg < 9 and BIAS < 10 \
                    and close > max_high:
                self.enState = State.buy
        else:
            if self.enState is not State.none:
                #下穿5日线，止损
                if self.enState is State.hold:
                    if close >= cur_ma5:
                        return self.enState
                    else:
                        self.enState = self.enState.sell
                else:
                    self.enState = State.out_view

            else:
                self.enState = State.none

        #最后加入到基础数据中
        self.AppendOneData(close, open, low, high)
        self.idx = self.idx + 1
        #self.UpdateMaX()

        return self.enState

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

