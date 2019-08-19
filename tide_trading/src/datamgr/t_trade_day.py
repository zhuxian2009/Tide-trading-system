#coding=utf-8
import pymysql

class CT_Tradeday:
    def __init__(self, connect):
        self.connect = connect

    #增加交易时间
    def add_tradeday(self, trade_day):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_trade_day (trade_day) VALUE (%s);"
        print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (trade_day,))
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    #判断某个股票代码是否存在
    def exist_trade_day(self, trade_day):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()


        # sql语句
        sql = "select 1 from t_trade_day where trade_day = '"+trade_day+"' limit 1;"
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

    #查询所有的交易日期,返回查询出来的结果
    def query_tradeday(self):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "select trade_day from t_trade_day order by trade_day ASC;"
        #print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()

            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()
        return None

    def query_last_tradeday(self, N):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = " select trade_day from (select * from t_trade_day order by trade_day DESC limit %s) as tmp order by trade_day ASC;"
        #print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (N,))
            # 把修改的数据提交到数据库
            self.connect.commit()

            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()
        return None