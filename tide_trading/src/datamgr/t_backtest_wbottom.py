#coding=utf-8
import pymysql
import numpy as np
import logging

class CT_BT_WBottom:
    def __init__(self, connect):
        self.connect = connect

    #增加w底回测数据
    def add_backtest_wbottom(self, ts_code, bottom1, bottom2, trade_day1, trade_day2, trade_day, minrange):
        if self.connect is None:
            return -1

        ret = self.exist_backtest_wbottom_day(ts_code, trade_day1, trade_day2)
        if ret > 0:
            return 0

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_backtest_wbottom (ts_code,bottom1,bottom2,trade_day1,trade_day2,trade_day,minrange) VALUE (%s,%s,%s,%s,%s,%s,%s);"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (ts_code, str(bottom1), str(bottom2), trade_day1, trade_day2, trade_day, minrange))
            #cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    #根据股票代码，删除表中的数据
    def del_backtest_wbottom(self, code):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "delete from t_backtest_wbottom where ts_code=%s;"
        print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code,))
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    def update_backtest_wbottom(self, code, trade_day, ma5, ma10, ma20, ma30, ma60,
                     ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                     macd, dif, dea):
        if self.connect is None:
            return -1

        logging.debug("update .. "+ code + "  "+trade_day)
        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        macd = macd * 2
        # sql语句
        sql = "update t_kdata set ma5=%s,ma10=%s,ma20=%s,ma30=%s,ma60=%s," \
              "ma5vol=%s,ma10vol=%s,ma20vol=%s,ma30vol=%s," \
              " macd=%s,dif=%s,dea=%s where code=%s and trade_day=%s;"
        #print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql,(str(ma5),str(ma10),str(ma20),str(ma30),str(ma60),
                                str(ma5_vol),str(ma10_vol),str(ma20_vol),str(ma30_vol),
                                str(macd), str(dif), str(dea), code,trade_day))
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    # 判断某个股票代码+底1+底2，是否存在
    def exist_backtest_wbottom_day(self, code, trade_day1, trade_day2):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "select 1 from t_backtest_wbottom where ts_code = '" + code + "'and trade_day1='" + trade_day1 + "'and trade_day2='" + trade_day2 + "' limit 1;"
        #print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()

            result = cursor.fetchone()
            # 关闭光标对象
            cursor.close()

            if result is None:
                return 0

            for i in result:
                #print(i)
                if i == 1:
                    return 1

        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)
        return 0

    def query_backtest_wbottom(self, code):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select ts_code,bottom1,bottom2,trade_day1,trade_day2,trade_day,minrange " \
              "from t_backtest_wbottom where ts_code = %s order by trade_day ASC;"
        print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code,))
            # 把修改的数据提交到数据库
            self.connect.commit()

            result = cursor.fetchall()

            # 关闭光标对象
            cursor.close()
            return result
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        return None

    #查询一个时间范围的记录
    def query_rangebacktest_wbottom(self, start_day, end_day):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select ts_code,bottom1,bottom2,trade_day1,trade_day2,trade_day,minrange " \
              "from t_backtest_wbottom where " \
              " trade_day1>=%s and trade_day<=%s order by trade_day ASC;"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (start_day, end_day))
            # 把修改的数据提交到数据库
            self.connect.commit()

            result = cursor.fetchall()

            # 关闭光标对象
            cursor.close()
            return result
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        return None

    #清空表
    def truncate_backtest_wbottom(self):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "truncate table t_backtest_wbottom;"
        print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()
