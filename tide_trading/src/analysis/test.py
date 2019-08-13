import requests,re,json,time,os
import heapq
from bs4 import BeautifulSoup

class GPINFO(object):
     """docstring for GPINFO"""
 9     def __init__(self):
10         self.Url = 'http://quote.eastmoney.com/stocklist.html'
11         self.BaseData = []
12         self.Date = time.strftime('%Y%m%d')
13         self.Record = 'basedata'+self.Date
14         if os.path.exists(self.Record):
15             print ('record exist...')
16             self.BaseData = self.get_base_data_from_record()
17         else:
18             print ('fuck-get data again...')
19             self.get_data()
20 
21     def write_record(self,text):
22         with open(self.Record,'ab') as f:
23             f.write((text+'\n').encode('utf-8'))
24 
25     def get_base_data_from_record(self):
26         ll = []
27         with open(self.Record,'rb') as f:
28             json_l = f.readlines()
29             for j in json_l:
30                 ll.append(json.loads(j.decode('utf-8')))
31         return ll
32 
33     def get_data(self):
34         #请求数据
35         orihtml = requests.get(self.Url).content
36         #创建 beautifulsoup 对象
37         soup = BeautifulSoup(orihtml,'lxml')
38         #采集每一个股票的信息
39         count = 0
40         for a in soup.find('div',class_='quotebody').find_all('a',{'target':'_blank'}):
41             record_d = {}
42             #代号
43             num = a.get_text().split('(')[1].strip(')')
44             if not (num.startswith('00') or num.startswith('60')):continue #只需要6*/0*
45             record_d['num']=num
46             #名称
47             name = a.get_text().split('(')[0]
48             record_d['name']=name
49             #详情页
50             detail_url = a['href']
51             record_d['detail_url']=detail_url
52 
53             cwzburl = detail_url
54             #发送请求
55             try:
56                 cwzbhtml = requests.get(cwzburl,timeout=30).content
57             except Exception as e:
58                 print ('perhaps timeout:',e)
59                 continue
60             #创建soup对象
61             cwzbsoup = BeautifulSoup(cwzbhtml,'lxml')
62 
63             #财务指标列表 [浦发银行，总市值    净资产    净利润    市盈率    市净率    毛利率    净利率    ROE] roe:净资产收益率
64             try:
65                 cwzb_list = cwzbsoup.find('div',class_='cwzb').tbody.tr.get_text().split()
66             except Exception as e:
67                 print ('error:',e)
68                 continue
69             #去除退市股票
70             if '-' not in cwzb_list:
71                 record_d['data']=cwzb_list
72                 self.BaseData.append(record_d)
73                 self.write_record(json.dumps(record_d))
74                 count=count+1
75                 print (len(self.BaseData))
76 
77 def main():
78     test = GPINFO()
79     result = test.BaseData
80     #[浦发银行，总市值    净资产    净利润    市盈率    市净率    毛利率    净利率    ROE] roe:净资产收益率]
81     top_10 = heapq.nlargest(10,result,key=lambda r:float(r['data'][7].strip('%')))
82     for i in top_10:
83         print(i['data'])
84 
85 if __name__ == '__main__':
86     main()