# coding=utf-8
import src.common.tools as tools
import xlrd
import xlwt
import re

''' 读取股票的基础信息 ， 股票所属概念，所属行业等'''
class CMystock:
    def __init__(self):
        self.code = ""
        self.name = ""
        #概念,list
        self.conseption = []
        #行业,list
        self.trade = []

    def set_code(self,code):
        self.code = code

    def get_code(self):
        return self.code

    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name

    #给code股票加入新的概念
    def add_conseption(self, conseption):
        self.conseption.append(conseption)

    #获取概念
    def get_conseption(self):
        return self.conseption

    #给code股票加入新的所属行业
    def add_trade(self, trade):
        self.trade.append(trade)

    #获取其中一个行业
    def get_trade(self):
        return self.trade

    #获取所属行业
    def get_trade_count(self):
        return len(self.trade)

class CBaseinfo:
    def __init__(self):
        #股票信息
        self.stocks = dict()
        self.stock_info_excel = None
        #写入信息到excel文件
        self.my_excel = None
        self.excel_sheet = None
        self.file_name = ''

    def read_excel(self):
        if self.stock_info_excel is not None:
            return

        self.stock_info_excel = xlrd.open_workbook(r'data/stockinfo.xls')

        # 索引的方式，从0开始
        sheet = self.stock_info_excel.sheet_by_index(0)

        #获取sheet的最大行数和列数
        nrows = sheet.nrows  # 行
        ncols = sheet.ncols  # 列

        #获取某个单元格的值,第0行是标题，没有用
        for row in range(1, nrows):
            stock = CMystock()
            for col in range(0, ncols):
                # 获取row行col列的表格值
                value = sheet.cell(row, col).value
                #print('r=',row,' c=',col,' v=',value)

                #code
                if col==0:
                    #self.stock = CMystock()
                    value = value[0:6]
                    stock.set_code(value)

                #name
                if col==1:
                    stock.set_name(value)

                #概念
                if col==2:
                    conseption = re.split('[;]', value)
                    count = len(conseption)
                    for idx in range(0,count):
                        stock.add_conseption(conseption[idx])

                #行业
                if col==4:
                    trade = re.split('[-]', value)
                    count = len(trade)
                    for idx in range(0, count):
                        stock.add_trade(trade[idx])

            #self.stocks.append(stock)
            self.stocks[stock.get_code()] = stock

    def get_stock_info(self, code):
        #dict是否存在这种key
        if code in self.stocks:
            return self.stocks[code]
        return None

    def open_excel(self, file_name):
        self.my_excel = xlwt.Workbook()
        self.excel_sheet = self.my_excel.add_sheet('sheet')
        self.file_name = file_name

    def write_excel(self, row, col, value):
        self.excel_sheet.write(row, col, value)

    def close_excel(self):
        self.my_excel.save(self.file_name)

