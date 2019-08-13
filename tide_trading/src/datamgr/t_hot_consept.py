#coding=utf-8
import pymysql
import numpy as np
import logging

'''热点概念'''
class CT_HotConsept:
    def __init__(self, connect):
        self.connect = connect

    #增加数据
    def add_hotconsept(self, consept, times, update_time):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_hot_consept (consept, times, update_time) VALUE (%s,%s,%s);"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (consept, times, update_time))
            #cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    # 清空表
    def truncate_hotconsept(self):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "truncate table t_hot_consept;"
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
    def query_allhotconsept(self):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select consept, times, update_time from t_hot_consept order by times DESC;"
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