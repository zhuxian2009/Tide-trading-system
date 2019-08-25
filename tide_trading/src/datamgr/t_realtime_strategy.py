#coding=utf-8
import pymysql
import numpy as np
import logging

'''实时策略选股的结果'''
class CT_Realtime_Strategy:
    def __init__(self, connect):
        self.connect = connect

    #增加数据
    def add_rt_strategy(self, code, strategy_id, strategy_name, update_day, update_time):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_rt_strategy (code, strategy_id,strategy_name,update_date,update_time) VALUE (%s,%s,%s,%s,%s);"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (code, str(strategy_id), strategy_name, update_day, update_time))
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
    def truncate_rt_strategy(self):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "truncate table t_rt_strategy;"
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

    def query_today_rt_strategy(self, day):
        if self.connect is None:
            return None

            # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select code, update_time,update_date, strategy_id, strategy_name from t_rt_strategy where update_date=%s order by update_time DESC;"
        print(">>>" + sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (day,))
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

    # 查询所有信息，返回记录集合或者空
    def query_all_rt_strategy(self):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select code, strategy_id, strategy_name, update_time from t_rt_strategy order by update_time DESC;"
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