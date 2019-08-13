# coding=utf-8
import strategybase as stt_base

from status import State

''' 价涨量缩策略：连续上升，连续缩量，是买入时机 '''

class CStrategy04(stt_base.CStrategyBase):

    #投入一份新的数据
    def FeedOneData(self, close, open, low=0, high=0, vol=0):
        #self.idx = self.idx + 1
        #最后加入到基础数据中
        self.AppendOneData(close, open, low, high, vol)
        self.idx = self.idx + 1

        #ma5,ma10,连续5日上行
        up5 = self.Condition1(3, 5)
        up10 = 1  # self.Condition1(5, 10)
        up20 = self.Condition1(3, 20)
        up60 = self.Condition1(3, 60)
        #今天
        #涨幅，应该根据close open 计算，这里简单处理
        pct_chg_idx = self.idx
        pct_chg_today = self.pct_chg[pct_chg_idx]
        vol_today = self.allVol[pct_chg_idx]
        # 昨天
        pct_chg_yesterday = self.pct_chg[pct_chg_idx-1]
        vol_yesterday = self.allVol[pct_chg_idx-1]
        # 前天
        pct_chg_beforyesterday = self.pct_chg[pct_chg_idx-2]
        vol_beforyesterday = self.allVol[pct_chg_idx-2]

        cur_ma5 = self.ma5[self.idx]
        cur_ma20 = self.ma20[self.idx]
        cur_ma30 = self.ma30[self.idx]
        cur_ma60 = self.ma60[self.idx]
        min_vol = self.MinVol(30)

        #过滤第一天出现长上影线的形态
        gain1 = self.mytool.calc_gain(high, open)
        gain2 = self.mytool.calc_gain(close, open)
        self.bLongLine = 0
        if gain1-gain2 > 2:
            self.bLongLine = 1

        #状态归0
        if self.Status.getState() is State.out_view or self.Status.getState() is State.sell:
            self.Status.toNone()

        # 5日均线连续上行
        # 当日最高价高于前几日的最高价
        if pct_chg_today > 0 and pct_chg_yesterday > 0 and pct_chg_beforyesterday > 1  and pct_chg_today < 9\
                and (vol_yesterday/vol_today>2 or vol_beforyesterday/vol_today>2) and vol_yesterday < vol_beforyesterday \
                and up20 and not self.bLongLine and cur_ma20>cur_ma30 and cur_ma30>cur_ma60:
            #判断买入点
            self.Status.View()
            self.Status.Buy2Hold()
            self.Status.setState(State.buy)
            self.buy_price = close
        else:
            self.Status.Buy2Hold()

            if self.Status.getState() is not State.none:
                #卖点，止盈
                if self.Status.getState() is State.hold:
                    #止盈价格
                    sellprice = self.mytool.calc_gain(high, self.buy_price);
                    # 止损价格
                    sellprice2 = self.mytool.calc_gain(close, self.buy_price);
                    #赚2个点卖掉
                    if sellprice >= 2:
                        self.Status.setState(State.sell)
                        self.sell_price = high
                    # 卖点，止损
                    elif sellprice2 < -2:
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

