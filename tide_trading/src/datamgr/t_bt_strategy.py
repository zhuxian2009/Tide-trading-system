#coding=utf-8
import logging

class CT_BT_Strategy:
    def __init__(self, connect):
        self.connect = connect

    #增加w底回测数据
    def add_bt_strategy(self, ts_code, buydate, buyprice, selldate, sellprice, duration, strategyid):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "insert into t_bt_strategy (ts_code, buydate, buyprice, selldate, sellprice, duration, strategyid) VALUE (%s,%s,%s,%s,%s,%s,%s);"
        #print(code+">>>"+sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (ts_code, buydate, str(buyprice), selldate, str(sellprice), str(duration), str(strategyid)))
            #cursor.execute(sql)
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()

    #根据策略id，查询策略回测的结果
    def query_bt_strategy(self, id):
        if self.connect is None:
            return None

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句,DESC降序，ASC升序
        sql = "select ts_code, buydate, buyprice, selldate, sellprice, duration, strategyid " \
              "from t_bt_strategy where strategyid = %s order by selldate ASC;"

        try:
            # 执行SQL语句
            cursor.execute(sql, (str(id),))
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
    def truncate_bt_strategy(self):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "truncate table t_bt_strategy;"
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

    def delete_bt_strategy(self, id):
        if self.connect is None:
            return -1

        # 得到一个可以执行SQL语句的光标对象
        cursor = self.connect.cursor()

        # sql语句
        sql = "delete from t_bt_strategy where strategyid=%s;"
        print(sql)

        try:
            # 执行SQL语句
            cursor.execute(sql, (id,))
            # 把修改的数据提交到数据库
            self.connect.commit()
        except Exception as e:
            # 捕捉到错误就回滚
            self.connect.rollback()
            print(e)

        # 关闭光标对象
        cursor.close()
