# coding=utf-8
import strategybase as stt_base

from status import State

''' 吃鱼策略：不吃鱼头，不吃鱼尾，只吃鱼身 '''

class CStrategy01(stt_base.CStrategyBase):

    #投入一份新的数据
    def FeedOneData(self, close, open, low=0, high=0, vol=0):
        #最后加入到基础数据中
        self.AppendOneData(close, open, low, high, vol)
        self.idx = self.idx + 1

        #ma5,ma10,连续5日上行
        up5 = self.Condition1(3, 5)
        up10 = 1  # self.Condition1(5, 10)
        up20 = self.Condition1(3, 20)
        up30 = self.Condition1(3, 30)
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
        cur_ma10 = self.ma10[self.idx]
        cur_ma20 = self.ma20[self.idx]
        cur_ma30 = self.ma30[self.idx]
        cur_ma60 = self.ma60[self.idx]
        cur_volma5 = self.volma5[self.idx]
        cur_volma10 = self.volma10[self.idx]
        #min_vol = self.MinVol(30)

        #状态归0
        if self.Status.getState() is State.out_view or self.Status.getState() is State.sell:
            self.Status.toNone()

        self.Status.Buy2Hold()

        # 5日>10日>20日>60日均线连续上行
        upupup = False
        if cur_ma5>cur_ma10 and cur_ma10>cur_ma20 and up5 and up10 and up20 and up60:
            upupup = True

        # 乖离率
        BIAS5 = 1#(open - cur_ma5) / cur_ma5 * 100

        #买入条件，如果昨日vol>volma5*2 and 2%以上上影线，不买；如果vol>volma5*2.5，直接不买
        # 上影线的形态
        gain1 = self.mytool.calc_gain(high, open)
        gain2 = self.mytool.calc_gain(close, open)
        self.bLongLine = 0
        if gain1 - gain2 > 2:
            self.bLongLine = 1

        if (vol > cur_volma10*2 and self.bLongLine is 1) or vol > cur_volma10*2.5:
            upupup = False


        # 连续两日涨停
        if upupup and pct_chg_beforyesterday > 9 and pct_chg_yesterday > 5 and BIAS5 < 10\
                and self.Status.getState() is not State.buy and self.Status.getState() is not State.hold:
            #判断买入点
            self.Status.View()
            self.Status.Buy2Hold()
            self.Status.setState(State.buy)
            self.buy_price = open
        else:
           # self.Status.Buy2Hold()

            if self.Status.getState() is not State.none:
                #卖点，止盈
                if self.Status.getState() is State.hold:
                    #止盈价格,下穿5日线
                    # 止损价格
                    if close < cur_ma5:
                        self.Status.setState(State.sell)
                        self.sell_price = close
            else:
                self.Status.setState(State.none)

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

