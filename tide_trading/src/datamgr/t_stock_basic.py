#coding=utf-8
import pymysql
import numpy as np
import logging

class CT_StockBasic:
    def __init__(self, connect):
        self.connect = connect

    #增加k线数据
    def add_stockbasic(self, ts_code, symbol, name, area, market, list_status):
        if self.connect is None:
            return -1

        ret = self.exist_stockbasic(ts_code)
        if ret > 0:
            return 0

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_stock_basic (ts_code, symbol, name, area, market, list_status) VALUE (%s,%s,%s,%s,%s,%s);"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (ts_code, symbol, name, area, market, list_status))
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
    def del_stockbasic(self, code):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "delete from t_stock_basic where code=%s;"
        print(code+">>>"+sql)

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

    def update_stockbasic(self, ts_code, symbol, name, area, market, list_status):
        if self.connect is None:
            return -1

        logging.debug("update .. "+ ts_code + "  "+name)
        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句 ts_code, symbol, name, area, market, list_status
        sql = "update t_stock_basic set symbol=%s,name=%s,area=%s,market=%s,list_status=%s where ts_code=%s;"
        #print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql,(symbol, name, area, market, list_status, ts_code))
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    #判断某个股票代码是否存在
    def exist_stockbasic(self, code):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "select 1 from t_stock_basic where ts_code = '"+code+"' limit 1;"
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

    #查询股票的基本信息，返回一条记录或者空值
    def query_stockbasic(self, code):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select ts_code, symbol, name, area, market, list_status from t_stock_basic where ts_code = %s;"
        print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code,))
            # 把修改的数据提交到数据库
            self.connect.commit()

            result = cursor.fetchone()

            # 关闭光标对象
            cursor.close()
            return result
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        return None

    # 查询所有股票的基本信息，返回记录集合或者空
    def query_allstockbasic(self):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select ts_code, symbol, name, area, market, list_status from t_stock_basic order by ts_code;"
        print(">>>" + sql)

        try:
            # 执行SQL语句
            cursor.execute(sql)
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