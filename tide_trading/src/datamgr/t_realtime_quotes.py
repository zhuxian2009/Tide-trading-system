#coding=utf-8
import pymysql
import numpy as np
import logging

'''实时出价'''
class CT_Realtime_Quotes:
    def __init__(self, connect):
        self.connect = connect

    #增加数据
    def add_realtime_quotes_many(self, datas):
        if self.connect is None:
            return -1

        list_values = []
        for i in range(0, len(datas)):
           list_values.append(list(datas[i]))
        #list_values = list(datas)
        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_realtime_quotes (name,open,pre_close,price, high, low, bid,ask, amount,volume," \
              "b1_v,b1_p,b2_v,b2_p,b3_v,b3_p,b4_v,b4_p,b5_v,b5_p," \
              "a1_v,a1_p,a2_v,a2_p,a3_v,a3_p,a4_v,a4_p,a5_v,a5_p," \
              "date,time,code)" \
              " VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
              "%s,%s,%s);"
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
            print('add_realtime_quotes_many...', e)

        # 关闭光标对象
        cursor.close()

    # 清空表
    def truncate_realtime_quotes(self):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "truncate table t_realtime_quotes;"
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

    # 查询所有信息，返回记录集合或者空
    def query_realtime_quotes(self):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select name,open,pre_close,price, high, low, bid,ask, amount,volume," \
              "b1_v,b1_p,b2_v,b2_p,b3_v,b3_p,b4_v,b4_p,b5_v,b5_p," \
              "a1_v,a1_p,a2_v,a2_p,a3_v,a3_p,a4_v,a4_p,a5_v,a5_p," \
              "date,time,code from t_realtime_quotes order by code DESC;"
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