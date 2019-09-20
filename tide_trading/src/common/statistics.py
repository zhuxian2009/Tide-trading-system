# coding=utf-8
import src.common.tools as tools


class CStatistics:
    def __init__(self):
        self.buy_price = 0
        self.buy_date = "000"
        self.sell_price = 0
        self.sell_date = "000"
        self.log = tools.CLogger('backtest', '../../log/backtest_log.txt', 1)

    def set_buy_info(self, price, date):
        self.buy_price = price
        self.buy_date = date

    def set_sell_info(self, price, date):
        self.sell_price = price
        self.sell_date = date

    def statistics(self, code):
        #print('统计差率, buy price=', self.buy_price, 'sell price=', self.sell_price)
        if self.sell_price > self.buy_price:
            rang = self.sell_price - self.buy_price
            percent = rang / self.buy_price
            #print('统计利润  盈利:{:.2f}%'.format(percent * 100))
            strLog = '统计利润  盈利:{:.2f}%'.format(percent * 100)
            strLog = strLog + '  buy date=' + self.buy_date + ', sell date=' + self.sell_date+" code="+code
            self.log.getLogger().info(strLog)
        else:
            rang = self.buy_price - self.sell_price
            percent = rang / self.buy_price
            #print('统计利润  亏损::{:.2f}%'.format(percent * 100))
            strLog = '统计利润  亏损:{:.2f}%'.format(percent * 100)
            strLog = strLog + '  buy date=' + self.buy_date + ', sell date=' + self.sell_date+" code="+code
            self.log.getLogger().info(strLog)

    #计算涨幅
    def calc_gain(self, close, open):
        if close==0 or open==0:
            return 0

        rang = close - open
        gain = (rang / open)*100
        gain = '%.2f' % gain
        return gain

    #计算涨停价格
    def calc_limit_price(self, pre_close):
        if pre_close == 0:
            return 0

        limit = pre_close + pre_close*0.1
        limit = '%.2f'%limit
        return limit
