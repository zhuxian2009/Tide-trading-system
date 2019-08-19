#coding=utf-8
import pymysql
import numpy as np
import logging

'''筹码已经集中'''
class CT_Chip_Concent:
    def __init__(self, connect):
        self.connect = connect

    #增加数据
    def add_chip_concent_many(self, list_values):
        if self.connect is None:
            return -1

        #list_values = []
        #for i in range(0, len(datas)):
        #   list_values.append(list(datas[i]))
        #list_values = list(datas)
        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_chip_concent (code,name,ab_gain,date,time) VALUE (%s,%s,%s,%s,%s);"
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
            print('add_chip_concent_many...', e)

        # 关闭光标对象
        cursor.close()

    # 清空表
    def truncate_chip_concent(self):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "truncate table t_chip_concent;"
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

    # 查询某日的所有信息，返回记录集合或者空
    def query_chip_concent(self, date):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        #sql = "select code,name,ab_gain,date,time from t_chip_concent where date=%s order by ab_gain DESC;"
        sql="select code,name,ab_gain,date,time,count(code) as num from t_chip_concent where date=%s group by code order by ab_gain DESC;"
        print(">>>" + sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (date,))
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
