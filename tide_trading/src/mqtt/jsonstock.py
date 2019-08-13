# coding=GBK
import json
import numpy as np
#股票信息的json
class CJsonStock:

    def __init__(self):
        self.listStock = dict()

    def AddStock(self,code,name,date,success_rate,strategy,type):
        dict = {}
        dict['code'] = code
        dict['name'] = name
        dict['date'] = date
        dict['success_rate'] = success_rate
        dict['strategy'] = strategy
        dict['type'] = type
        self.listStock.append(dict)

    def ToJson(self):
        stock = {}
        stock['type'] = 'stock_push'
        stock['stock'] = ['']*len(self.listStock)

        for i in range(len(self.listStock)):
            stock['stock'][i]=self.listStock[i]

        #print(stock)

        strJson = json.dumps(stock, ensure_ascii=False)
        print(strJson)
        return strJson
