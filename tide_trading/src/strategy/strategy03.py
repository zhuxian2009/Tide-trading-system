# coding=utf-8
import strategybase as stt_base

from status import State


''' 地量策略：上升过程中，出现地量回调，是买入时机 '''


class CStrategy03(stt_base.CStrategyBase):

    #投入一份新的数据
    def FeedOneData(self, close, open, low=0, high=0, vol=0):
        #self.idx = self.idx + 1

        #ma5,ma10,连续5日上行
        up5 = self.Condition1(3, 5)
        up10 = 1  # self.Condition1(5, 10)
        up20 = self.Condition1(3, 20)
        up60 = self.Condition1(3, 60)
        pct_chg = self.pct_chg[self.idx]

        cur_ma5 = self.ma5[self.idx]
        cur_ma20 = self.ma20[self.idx]
        min_vol = self.MinVol(30)

        #状态归0
        if self.Status.getState() is State.out_view or self.Status.getState() is State.sell:
            self.Status.toNone()

        # 5日均线连续上行
        # 当日最高价高于前几日的最高价
        if up5 and up10 and up20 and up60:
            #判断买入点
            self.Status.View()

            self.Status.Buy2Hold()

            #乖离率
            BIAS = (close - cur_ma20)/cur_ma20*100

            #涨幅大于7个点
            #if self.mytool.calc_gain(close, open) > 3 and (self.enState != State.hold) and pct_chg < 9 and BIAS < 10
            if (self.Status.getState() != State.hold) and vol < min_vol and BIAS>3:
                self.Status.setState(State.buy)
        else:
            if self.Status.getState() is not State.none:
                #下穿5日线，止损
                if self.Status.getState() is State.hold:
                    if pct_chg >= 2:
                        return self.Status.getState()
                    else:
                        self.Status.setState(State.sell)
                else:
                    self.Status.setState(State.out_view)

            else:
                self.Status.setState(State.none)

        #最后加入到基础数据中
        self.AppendOneData(close, open, low, high, vol)
        self.idx = self.idx + 1
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

