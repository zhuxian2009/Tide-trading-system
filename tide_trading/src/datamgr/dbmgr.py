#coding=utf-8
import pymysql
import src.datamgr.t_trade_day as t_trade_day
import src.datamgr.t_kdata as t_kdata
import src.datamgr.t_kdata_down as t_kdata_down
import src.datamgr.t_stock_basic as t_stock_basic
import src.datamgr.t_backtest_wbottom as t_backtest_wbottom
import src.datamgr.t_hot_consept as t_hot_consept
import src.datamgr.t_hot_trade as t_hot_trade
import src.datamgr.t_realtime_quotes as t_realtime_quotes
import src.datamgr.t_chipconcent as t_chipconcent
import src.datamgr.t_realtime_strategy as t_realtime_strategy
import src.datamgr.t_bt_strategy as t_bt_strategy

class CDBMgr:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connect = None
        self.trade_day = None
        self.kdata = None
        self.stockbasic = None
        self.bt_wbottom = None
        self.hotconsept = None
        self.hottrade = None
        self.realtime_quotes = None
        self.chipconcent = None
        self.realtime_strategy = None
        self.bt_strategy = None
        #self.connect_db()

    #connect database
    def connect_db(self):
        self.connect = pymysql.connect(self.host, self.user, self.password, self.database, charset="utf8")
        self.trade_day = t_trade_day.CT_Tradeday(self.connect)
        self.kdata = t_kdata.CT_Kdata(self.connect)
        self.kdata_down = t_kdata_down.CT_KdataDown(self.connect)
        self.stockbasic = t_stock_basic.CT_StockBasic(self.connect)
        self.bt_wbottom = t_backtest_wbottom.CT_BT_WBottom(self.connect)
        self.hotconsept = t_hot_consept.CT_HotConsept(self.connect)
        self.hottrade = t_hot_trade.CT_HotTrade(self.connect)
        self.realtime_quotes = t_realtime_quotes.CT_Realtime_Quotes(self.connect)
        self.chipconcent = t_chipconcent.CT_Chip_Concent(self.connect)
        self.realtime_strategy = t_realtime_strategy.CT_Realtime_Strategy(self.connect)
        self.bt_strategy = t_bt_strategy.CT_BT_Strategy(self.connect)

    def disconnect_db(self):
        self.connect.close()

    ############################################################################### t_kdata
    #增加k线数据
    def add_kdata(self, code, trade_day, open, close, high, low, vol,pct_chg,amount):
        if self.connect is None:
            return -1

        self.kdata.add_kdata(code,trade_day, open, close, high, low, vol,pct_chg,amount)

    # 批量增加k线数据
    def add_kdata_many(self, datas):
        if self.connect is None:
            return -1

        self.kdata.add_kdata_many(datas)

    #根据股票代码，删除表中的数据
    def del_kdata(self,code):
        if self.connect is None:
            return -1

        self.kdata.del_kdata(code)

    def update_kdata(self, code, trade_day, ma5, ma10, ma20, ma30, ma60,
                     ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                     macd, dif, dea):
        if self.connect is None:
            return -1

        self.kdata.update_kdata(code, trade_day, ma5, ma10, ma20, ma30, ma60,
                                ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                                macd, dif, dea)


    #判断某个股票代码是否存在
    def exist_kdata(self, code):
        if self.connect is None:
            return -1

        return self.kdata.exist_kdata(code)

    def query_kdata(self, code):
        if self.connect is None:
            return -1

        return self.kdata.query_kdata(code)

    def query_allkdata(self, code):
        if self.connect is None:
            return -1

        return self.kdata.query_allkdata(code)

    def query_rangekdata(self, code, start_day, end_day):
        if self.connect is None:
            return -1

        return self.kdata.query_rangekdata(code, start_day, end_day)

    # 根据日期范围查询
    def query_kdata_by_day(self, code, start_day, end_day, before_days):
        if self.connect is None:
            return -1

        return self.kdata.query_kdata_by_day(code, start_day, end_day, before_days)

    #查询某日的涨停个股
    def query_limit(self, day):
        if self.connect is None:
            return -1

        return self.kdata.query_limit(day)

    #把kdata_down的数据clone过来
    def clone_kdata_down(self):
        if self.connect is None:
            return -1

        return self.kdata.clone_kdata_down()

    ########################################################################t_kdata_down
    # 增加k线数据
    def add_kdata_down(self, code, trade_day, open, close, high, low, vol, pct_chg, amount):
        if self.connect is None:
            return -1

        self.kdata_down.add_kdata_down(code, trade_day, open, close, high, low, vol, pct_chg, amount)

    # 批量增加k线数据
    def add_kdata_down_many(self, datas):
        if self.connect is None:
            return -1

        self.kdata_down.add_kdata_down_many(datas)

        # 根据股票代码，删除表中的数据

    def del_kdata_down(self, code):
        if self.connect is None:
            return -1

        self.kdata_down.del_kdata_down(code)

    def update_kdata_down(self, code, trade_day, ma5, ma10, ma20, ma30, ma60,
                     ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                     macd, dif, dea):
        if self.connect is None:
            return -1

        self.kdata_down.update_kdata_down(code, trade_day, ma5, ma10, ma20, ma30, ma60,
                                ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                                macd, dif, dea)

        # 判断某个股票代码是否存在

    def exist_kdata_down(self, code):
        if self.connect is None:
            return -1

        return self.kdata_down.exist_kdata_down(code)

    def query_kdata_down(self, code):
        if self.connect is None:
            return -1

        return self.kdata_down.query_kdata_down(code)

    #根据日期范围查询
    def query_kdata_down_by_day(self, code, start_day, end_day, before_days):
        if self.connect is None:
            return -1

        return self.kdata_down.query_kdata_down_by_day( code, start_day, end_day, before_days)

    def query_rangekdata_down(self, code, start_day, end_day):
        if self.connect is None:
            return -1

        return self.kdata_down.query_rangekdata_down(code, start_day, end_day)

    def truncate_kdata_down(self):
        if self.connect is None:
            return -1

        return self.kdata_down.truncate_kdata_down()

    def set_global_config(self):
        if self.connect is None:
            return -1

        return self.kdata_down.set_global_config()

    ######################################################################## t_trade_day
    # 判断某个交易日期是否存在
    def exist_trade_day(self, trade_day):
        if self.connect is None:
            return -1

        return self.trade_day.exist_trade_day(trade_day)

    def add_trade_day(self, trade_day):
        if self.connect is None:
            return -1

        return self.trade_day.add_tradeday(trade_day)

    def query_tradeday(self):
        if self.connect is None:
            return -1

        return self.trade_day.query_tradeday()

    #最近的N个交易日
    def query_last_tradeday(self, N):
        if self.connect is None:
            return -1

        return self.trade_day.query_last_tradeday(N)

    ####################################################################### t_stock_basic
    #增加k线数据
    def add_stockbasic(self, ts_code, symbol, name, area, market, list_status):
        if self.connect is None:
            return -1

        self.stockbasic.add_stockbasic(ts_code, symbol, name, area, market, list_status)

    #根据股票代码，删除表中的数据
    def del_stockbasic(self, code):
        if self.connect is None:
            return -1

        self.stockbasic.del_stockbasic(code)

    def update_stockbasic(self, ts_code, symbol, name, area, market, list_status):
        if self.connect is None:
            return -1

        self.stockbasic.update_stockbasic(ts_code, symbol, name, area, market, list_status)


    #判断某个股票代码是否存在
    def exist_stockbasic(self, code):
        if self.connect is None:
            return -1

        return self.stockbasic.exist_kdata(code)

    def query_stockbasic(self, code):
        if self.connect is None:
            return -1

        return self.stockbasic.query_stockbasic(code)

    def query_allstockbasic(self):
        if self.connect is None:
            return -1

        return self.stockbasic.query_allstockbasic()

    ############################################################################### t_backtest_wbottom
    # 增加回测结果数据
    def add_backtest_wbottom(self, ts_code, bottom1, bottom2, trade_day1, trade_day2, trade_day, minrange):
        if self.connect is None:
            return -1

        self.bt_wbottom.add_backtest_wbottom(ts_code, bottom1, bottom2, trade_day1, trade_day2, trade_day, minrange)

    # 根据股票代码，删除表中的数据
    def del_backtest_wbottom(self, code):
        if self.connect is None:
            return -1

        self.bt_wbottom.del_backtest_wbottom(code)

    def update_backtest_wbottom(self, code, trade_day, ma5, ma10, ma20, ma30, ma60,
                          ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                          macd, dif, dea):
        if self.connect is None:
            return -1

        self.bt_wbottom.update_backtest_wbottom(code, trade_day, ma5, ma10, ma20, ma30, ma60,
                                          ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                                          macd, dif, dea)

        # 判断某个股票代码+底1+底2，是否存在
    def exist_backtest_wbottom_day(self, code, trade_day1, trade_day2):
        if self.connect is None:
            return -1

        return self.bt_wbottom.exist_backtest_wbottom_day(code, trade_day1, trade_day2)

    def query_backtest_wbottom(self, code):
        if self.connect is None:
            return -1

        return self.bt_wbottom.query_backtest_wbottom(code)

    def query_rangebacktest_wbottom(self, start_day, end_day):
        if self.connect is None:
            return -1

        return self.bt_wbottom.query_rangebacktest_wbottom(start_day, end_day)

    def truncate_backtest_wbottom(self):
        if self.connect is None:
            return -1

        return self.bt_wbottom.truncate_backtest_wbottom()

    ############################################################################### t_hot_consept
    # 增加热点概念结果数据
    def add_hotconsept(self, consept, times, update_time):
        if self.connect is None:
            return -1

        self.hotconsept.add_hotconsept(consept, times, update_time)

    # 根据股票代码，删除表中的数据
    def query_allhotconsept(self):
        if self.connect is None:
            return -1

        return self.hotconsept.query_allhotconsept()


    def truncate_hotconsept(self):
        if self.connect is None:
            return -1

        return self.hotconsept.truncate_hotconsept()

    ############################################################################### t_hot_consept
    # 增加回测结果数据
    def add_hottrade(self, consept, times, update_time):
        if self.connect is None:
            return -1

        self.hottrade.add_hottrade(consept, times, update_time)

        # 根据股票代码，删除表中的数据

    def query_allhottrade(self):
        if self.connect is None:
            return -1

        return self.hottrade.query_allhottrade()

    def truncate_hottrade(self):
        if self.connect is None:
            return -1

        return self.hottrade.truncate_hottrade()

    #######################实时出价 t_quotes_many
        # 批量增加实时出价数据
    def add_realtime_quotes_many(self, datas):
        if self.connect is None:
            return -1

        self.realtime_quotes.add_realtime_quotes_many(datas)

    def query_realtime_quotes(self):
        if self.connect is None:
            return -1

        return self.realtime_quotes.query_realtime_quotes()

    def truncate_realtime_quotes(self):
        if self.connect is None:
            return -1

        return self.realtime_quotes.truncate_realtime_quotes()

    #######################实时出价 t_chipconcent
    # 批量增加实时出价数据
    def add_chipconcent_many(self, datas):
        if self.connect is None:
            return -1

        self.chipconcent.add_chip_concent_many(datas)

    def query_chipconcent(self, date):
        if self.connect is None:
            return -1

        return self.chipconcent.query_chip_concent(date)

    def truncate_chipconcent(self):
        if self.connect is None:
            return -1

        return self.chipconcent.truncate_chip_concent()

############################################################################### t_rt_strategy
    # 增加策略选股结果数据
    def add_rt_strategy(self,  code, strategy_id, strategy_name, update_day, update_time):
        if self.connect is None:
            return -1

        self.realtime_strategy.add_rt_strategy( code, strategy_id, strategy_name, update_day, update_time)

    def query_all_rt_strategy(self):
        if self.connect is None:
            return -1

        return self.realtime_strategy.query_all_rt_strategy()

    #查询当天选股结果
    def query_today_rt_strategy(self, day):
        if self.connect is None:
            return -1

        return self.realtime_strategy.query_today_rt_strategy(day)


    def truncate__rt_strategy(self):
        if self.connect is None:
            return -1

        return self.realtime_strategy.truncate_rt_strategy()

    ############################################################################### t_bt_statistic策略回测统计
    def add_bt_strategy(self, ts_code, buydate, buyprice, selldate, sellprice, duration, strategyid):
        if self.connect is None:
            return -1
        return self.bt_strategy.add_bt_strategy(ts_code, buydate, buyprice, selldate, sellprice, duration, strategyid)

    def query_bt_strategy(self, id):
        if self.connect is None:
            return -1
        return self.bt_strategy.query_bt_strategy(id)

    def truncate_bt_strategy(self):
        if self.connect is None:
            return -1
        return self.bt_strategy.truncate_bt_strategy()

    def delete_bt_strategy(self, id):
        if self.connect is None:
            return -1
        return self.bt_strategy.delete_bt_strategy(id)

