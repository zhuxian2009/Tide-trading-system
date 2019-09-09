# coding=utf-8
import src.common.tools as tools
import xlrd
import xlwt
import re
#导入copy模块,修改excel
from xlutils.copy import copy

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
        self.file_name = r'data/stockinfo.xls'

    def read_excel(self):
        if self.stock_info_excel is not None:
            return

        self.stock_info_excel = xlrd.open_workbook(self.file_name)

        # 索引的方式，从0开始
        sheet = self.stock_info_excel.sheet_by_index(0)

        #创建黑名单
        if self.get_blacklist_flag(sheet) is True:
            self.load_excel_data(sheet, None)
            self.make_blacklist()

        list_back = self.get_blacklist(sheet)
        self.load_excel_data(sheet, list_back)

    #加载excel数据
    def load_excel_data(self, sheet, list_back):
        # 获取sheet的最大行数和列数
        nrows = sheet.nrows  # 行
        ncols = sheet.ncols  # 列

        # 获取某个单元格的值,第0行是标题，没有用
        for row in range(1, nrows):
            stock = CMystock()
            for col in range(0, ncols):
                # 获取row行col列的表格值
                value = sheet.cell(row, col).value
                # print('r=',row,' c=',col,' v=',value)

                # code
                if col == 0:
                    # self.stock = CMystock()
                    value = value[0:6]
                    stock.set_code(value)

                # name
                if col == 1:
                    stock.set_name(value)

                # 概念
                if col == 2:
                    conseption = re.split('[;]', value)
                    count = len(conseption)
                    for idx in range(0, count):
                        cur_consept = conseption[idx]

                        #判断是否包含在黑名单
                        
                        if list_back is not None and cur_consept in list_back:
                            continue

                        stock.add_conseption(cur_consept)

                # 行业
                if col == 4:
                    trade = re.split('[-]', value)
                    count = len(trade)
                    for idx in range(0, count):
                        stock.add_trade(trade[idx])

            # self.stocks.append(stock)
            self.stocks[stock.get_code()] = stock

    #判断是否需要新建黑名单
    def get_blacklist_flag(self, sheet):
        # 获取黑名单的数目
        try:
            str_blacklist = sheet.cell(1, 5).value
            if str_blacklist == '':
                return True
        except Exception as e:
            print(e)
            return True
        return False

    #获取黑名单列表
    def get_blacklist(self, sheet):
        blacklist_count = sheet.cell(1, 5).value
        max_row_num = int(blacklist_count)

        #获取黑名单概念
        list_black = list()
        for i in range(2, max_row_num, 1):
            str_blackconsept = sheet.cell(i, 5).value
            print(str_blackconsept)
            list_black.append(str_blackconsept)

        return list_black

    # 生成概念黑名单
    def make_blacklist(self):
        # 利用xlutils.copy下的copy函数复制
        wb = copy(self.stock_info_excel)
        # 获取表单0
        ws = wb.get_sheet(0)
        # 改变（0,0）的值
        ws.write(0, 5, '黑名单')

        #统计概念，成分股超过500只，加入黑名单
        dict_consept_count = dict()
        for cs in self.stocks.values():
            list_conseption = cs.get_conseption()
            #print(cs.get_conseption())
            #生成字典[consept:count]
            for one_consept in list_conseption:
                if one_consept in dict_consept_count.keys():
                    dict_consept_count[one_consept] = dict_consept_count[one_consept] + 1
                else:
                    dict_consept_count[one_consept] = 1

        i_row = 2
        for key in dict_consept_count.keys():
            #概念数量
            consept_count = dict_consept_count[key]
            if consept_count >= 500:
                ws.write(i_row, 5, key)
                i_row = i_row + 1

        ws.write(1, 5, i_row)
        print('blacklist count ', i_row-3)
        # 增加（8,0）的值
        #ws.write(8, 0, label='好的')
        # 保存文件
        wb.save(self.file_name)



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

