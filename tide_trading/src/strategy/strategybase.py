#coding=utf-8
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
#导入中文字体，避免显示乱码
import pylab as mpl
import numpy as np
import datetime

class CStrategyBase(ABC):

    # 加入日K数据源
    @abstractmethod
    def input_new_data(self, kdata):
        pass

    # 买入
    @abstractmethod
    def buy(self, res):
        pass

    # 统计
    @abstractmethod
    def statistics(self):
        pass

    #绘制统计图形
    def draw(self, list_date, list_y, title):
        mpl.rcParams['font.sans-serif'] = ['simhei']
        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['axes.unicode_minus'] = False

        # 生成figure对象,相当于准备一个画板
        fig = plt.figure(figsize=(8, 3))

        # 生成axis对象，相当于在画板上准备一张白纸，111，11表示只有一个表格，第3个1，表示在第1个表格上画图
        ax = fig.add_subplot(111)
        plt.title(title)
        plt.xlabel(u'交易日')
        plt.ylabel(u'盈亏百分比')

        # 将字符串的日期，转换成日期对象
        xs = [datetime.datetime.strptime(d, '%Y%m%d').date() for d in list_date]

        # 日期对象作为参数设置到横坐标,并且使用list_date中的字符串日志作为对象的标签（别名）
        # x坐标的刻度值
        ar_xticks = np.arange(1, len(list_date) + 1, step=1)
        plt.xticks(ar_xticks, list_date, rotation=90, fontsize=10)
        plt.yticks(np.arange(0, 30, step=2), fontsize=10)
        ax.plot(ar_xticks, list_y, color='r')

        # 下方图片显示不完整的问题
        plt.tight_layout()

        # 在点阵上方标明数值
        for x, y in zip(ar_xticks, list_y):
            plt.text(x, y + 0.3, str(y), ha='center', va='bottom', fontsize=10)

        plt.show()



