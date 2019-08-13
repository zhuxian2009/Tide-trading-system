#coding=utf-8
import pymysql
import numpy as np
import logging

'''
下载到t_kdata_down缓存起来
然后同步到t_kdata
'''

class CT_KdataDown:
    def __init__(self, connect):
        self.connect = connect

    #增加k线数据
    def add_kdata_down(self, code, trade_day, open, close, high, low, vol, pct_chg, amount):
        if self.connect is None:
            return -1

        ret = self.exist_kdata_down_day(code, trade_day)
        if ret > 0:
            return 0

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_kdata_down (code,trade_day, open, close, high, low, vol,pct_chg,amount) VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code, trade_day, open, close, high, low, vol,pct_chg,amount))
            #cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    # datas
    # 列： ts_code trade_day open high low close 涨跌幅 总手 成交额（千元）
    # 索引：    0    1         2    3    4    5    6      7      8
    def add_kdata_down_many(self, datas):
        if self.connect is None:
            return -1

        list_values = []
        for i in range(0, len(datas)):
           list_values.append(list(datas[i]))
        #list_values = list(datas)
        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_kdata_down (code,trade_day, open, high, low, close,pct_chg, vol,amount)" \
              " VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.executemany(sql, list_values)
            #cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print('add_kdata_down_many...', e)

        # 关闭光标对象
        cursor.close()

    #根据股票代码，删除表中的数据
    def del_kdata_down(self, code):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "delete from t_kdata_down where code=%s;"
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

    def update_kdata_down(self, code, trade_day, ma5, ma10, ma20, ma30, ma60,
                     ma5_vol, ma10_vol, ma20_vol, ma30_vol,
                     macd, dif, dea):
        if self.connect is None:
            return -1

        logging.debug("update .. "+ code + "  "+trade_day)
        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        if np.isnan(ma5):
            ma5 = 0
        if np.isnan(ma10):
            ma10 = 0
        if np.isnan(ma20):
            ma20 = 0
        if np.isnan(ma30):
            ma30 = 0
        if np.isnan(ma60):
            ma60 = 0
        if np.isnan(ma5_vol):
            ma5_vol = 0
        if np.isnan(ma10_vol):
            ma10_vol = 0
        if np.isnan(ma20_vol):
            ma20_vol = 0
        if np.isnan(ma30_vol):
            ma30_vol = 0
        if np.isnan(macd):
            macd = 0
        if np.isnan(dif):
            dif = 0
        if np.isnan(dea):
            dea = 0

        macd = macd * 2
        # sql语句
        sql = "update t_kdata_down set ma5=%s,ma10=%s,ma20=%s,ma30=%s,ma60=%s," \
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

    #判断某个股票代码是否存在
    def exist_kdata_down(self, code):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "select 1 from t_kdata_down where code = '"+code+"' limit 1;"
        #print(sql)

        #logging.debug(code+">>>"+sql)

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

    # 判断某个股票代码,在具体日期的k线数据是否存在
    def exist_kdata_down_day(self, code, trade_day):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "select 1 from t_kdata_down where code = '" + code + "'and trade_day='" + trade_day + "' limit 1;"
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

    def query_kdata_down(self,code):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select open,close,high,low,vol,trade_day from t_kdata_down where code = %s order by trade_day ASC;"
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

    def query_kdata_down_by_day(self, code, start_day, end_day, before_days):
        if self.connect is None:
            return None

        count = self.query_kdata_down_count(code, start_day, end_day)
        total = before_days + count

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select * from (select open,close,high,low,vol,trade_day from t_kdata_down " \
              "where code = %s and trade_day<=%s order by trade_day DESC limit %s)  " \
              "as tb order by trade_day ASC;"
        print(code+">>>"+sql, '  total=', total)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code,end_day,total))
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

    #查询某段时间内，某只股票的记录数量
    def query_kdata_down_count(self, code, start_day, end_day):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select count(*) from t_kdata_down " \
              "where code = %s and trade_day>=%s and trade_day<=%s;"
        print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code,start_day,end_day))
            # 把修改的数据提交到数据库
            self.connect.commit()

            result = cursor.fetchone()
            count = result[0]

            # 关闭光标对象
            cursor.close()
            return count
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        return 0

    def query_rangekdata_down(self,code, start_day, end_day):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select code,trade_day,open,close,high,low," \
              "amount,vol,ma5vol,ma10vol,ma20vol,ma30vol," \
              "ma5,ma10,ma20,ma30,ma60,pct_chg,macd,dea,dif from t_kdata_down where code = %s and" \
              " trade_day>%s and trade_day<%s order by trade_day ASC;"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code, start_day, end_day))
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

        # 清空表
    def truncate_kdata_down(self):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "truncate table t_kdata_down;"
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