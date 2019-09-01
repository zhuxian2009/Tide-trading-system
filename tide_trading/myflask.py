# coding=gbk

from flask import Flask, url_for, redirect, render_template, request
import src.common.conf as conf
import src.datamgr.dbmgr as dbmgr
from src.common.pager import Pagination
import datetime
#import src.realtime.rt_hotspot as rt_hotspot
#import src.datamgr.baseinfo as baseinfo
import src.common.schedulermgr as schedulermgr
import matplotlib.pyplot as plt
#导入中文字体，避免显示乱码
import pylab as mpl
import numpy as np
import base64
from io import BytesIO
import pandas as pd
import src.datamgr.baseinfo as baseinfo
import src.common.tools as tools
import os

#任务调度，阻塞
#from flask_apscheduler import APScheduler as myScheduler
#from apscheduler.schedulers.background import BackgroundScheduler as myScheduler

app = Flask(__name__)
#配置文件路径
cur_path = os.getcwd()
print(cur_path)
str_conf_path = cur_path + '/conf/conf.ini'

#日志唯一
g_conf = conf.CConf(str_conf_path)
filename_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
log_filename = cur_path+'/'+g_conf.log_dir+'/tide_system_'+filename_time+'.log'
g_log = tools.CLogger(g_conf.app_name, log_filename, 1).getLogger()

#任务调度
schedulermgr = schedulermgr.CSchedulerMgr(str_conf_path, g_log)
schedulermgr.start()

def GetToday():
    now_time = datetime.datetime.now()
    day = now_time.strftime('%Y%m%d')
    print('end time is ', day)
    return day

#1.修改配置
@app.route('/config')
def config():
    print('in config')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()

    #起始日期
    start_year = myconf.s_bt_startday[0:4]
    start_mouth = myconf.s_bt_startday[4:6]
    start_day = myconf.s_bt_startday[6:8]
    start = start_year+'-'+start_mouth+'-'+start_day
    print('start:'+start)
    #终止日期
    end_year = myconf.s_bt_endday[0:4]
    end_mouth = myconf.s_bt_endday[4:6]
    end_day = myconf.s_bt_endday[6:8]
    end = end_year+'-'+end_mouth+'-'+end_day
    print('end:' + end)

    return render_template('conf.html')


#查询任务状态
@app.route('/server_status')
def server_status():
    print('in server_status')

    #str_hotspot = schedulermgr.get_scheduler_status()
    str_hotspot = schedulermgr.get_hotspot_status()
    str_db_update_status = schedulermgr.get_db_update_status()
    str_rt_wbottom_status = schedulermgr.get_rt_wbottom_status()
    str_reatime_quotes_status = schedulermgr.get_reatime_quotes_status()
    str_rt_chipconcent_status = schedulermgr.get_rt_chipconcent_status()
    msg = '<p>实时热点任务:  '+str_hotspot+'</p><p> 数据库更新任务:  '+str_db_update_status+'</p><p>尾盘双底任务:  '+str_rt_wbottom_status\
          +'</p><p>实时出价任务:  '+str_reatime_quotes_status+'</p><p>探测筹码集中任务:'+str_rt_chipconcent_status+'</p>'
    #print('query_rt_hotconspt ************ pip *************  ',str_hotspot)
    return render_template('conf_status.html', hottime=msg)

#2.查询信息
@app.route('/query')
def query():
    print('in query')
    abc = 'query abc'
    return render_template('query.html', vvv=abc)

#查询回测数据  w底
@app.route('/query_bt_w', methods=['GET', 'POST'])
def query_bt_w():
    print('in query_bt_w')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    list_ret = db.query_rangebacktest_wbottom('20190101', GetToday())
    db.disconnect_db()
    ################## 分页 ######################
    req_page = request.args.get("page", 1)
    print('query_bt_w ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #根据分页的参数，截取部分数据显示
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_backtest_wbotton.html', wb_value=args_ret, html=str_html)

#查看指定热点的动态图
@app.route('/query_rt_hotconspt_one/<conspt>', methods=['GET', 'POST'])
def query_rt_hotconspt_one(conspt):
    print('query_rt_hotconspt_one...', conspt)
    #数据
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    trade_day = db.query_last_tradeday(10)
    #trade_day = pd.DataFrame(list(result), columns=['trade_day'])

    # 加载股票概念
    pBaseInfo = baseinfo.CBaseinfo()
    pBaseInfo.read_excel()

    #conspt_df = pd.DataFrame(columns=['date', 'count'])
    list_date = list()
    list_count = list()
    for day in trade_day:
        codes = db.query_limit(day[0])
        print('limit num=', len(codes))

        count = 0
        #遍历所有code
        for code in codes:
            #去除.SZ .SH的后缀
            str_code = code[0][0:6]
            my_stock_info = pBaseInfo.get_stock_info(str_code)
            if my_stock_info is None:
                print(code, ' is not exist!aps_hotspot')
                continue

            consepts = my_stock_info.get_conseption()
            #查询的概念是否在list中
            if conspt in consepts:
                count = count + 1

        list_date.append(day[0])
        list_count.append(count)
        print(day[0])

    '''
    list_date = ['20190813', '20190814', '20190815', '20190816', '20190819']
    list_count = [8, 8, 6, 11, 19]

    d = {'date': list_date,
         'count': list_count}
    conspt_df = pd.DataFrame(d)
    print(conspt_df)'''

    db.disconnect_db()
    #############################################绘图
    #中文乱码问题
    #myfont = FontProperties(fname=r'/smb/share/hdf5test/venv/lib/python3.7/site-packages/matplotlib/mpl-data/fonts/ttf/simhei.ttf')
    #mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['font.sans-serif'] = ['simhei']
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['axes.unicode_minus'] = False

    # 生成figure对象,相当于准备一个画板
    fig = plt.figure(figsize=(8, 3))

    # 生成axis对象，相当于在画板上准备一张白纸，111，11表示只有一个表格，第3个1，表示在第1个表格上画图
    ax = fig.add_subplot(111)
    plt.title(conspt)
    plt.xlabel(u'交易日')
    plt.ylabel(u'涨停数量')

    #将字符串的日期，转换成日期对象
    xs = [datetime.datetime.strptime(d, '%Y%m%d').date() for d in list_date]

    #日期对象作为参数设置到横坐标,并且使用list_date中的字符串日志作为对象的标签（别名）
    #x坐标的刻度值
    ar_xticks = np.arange(1, len(list_date)+1, step=1)
    plt.xticks(ar_xticks, list_date, rotation=45, fontsize=10)
    plt.yticks(np.arange(0, 30, step=2), fontsize=10)
    ax.plot(ar_xticks, list_count, color='r')

    #下方图片显示不完整的问题
    plt.tight_layout()

    #在点阵上方标明数值
    for x, y in zip(ar_xticks, list_count):
        plt.text(x, y + 0.3, str(y), ha='center', va='bottom', fontsize=10)

    #fmt = mdates.DateFormatter('%Y%m%D')
    #xs = [datetime.datetime.strptime(d, '%Y%m%d').date() for d in conspt_df['date']]
    #plt.plot(xs, conspt_df['count'], 'o-')

    #plt.savefig('ttt.png')
    # figure 保存为二进制文件
    buffer = BytesIO()
    plt.savefig(buffer)
    plot_data = buffer.getvalue()
    # 将matplotlib图片转换为HTML
    imb = base64.b64encode(plot_data)  # 对plot_data进行编码
    ims = imb.decode()
    imd = "data:image/png;base64," + ims
    return render_template('query_realtime_hotconspt_one.html', img=imd)

#查询实时数据  热点概念
@app.route('/query_rt_hotconspt', methods=['GET', 'POST'])
def query_rt_hotconspt():
    print('in query_rt_hotconspt')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    list_ret = db.query_allhotconsept()
    db.disconnect_db()
    if list_ret is None:
        list_ret=('概念', '0', '000')


    ################## 分页 ######################
    req_page = request.args.get("page", 1)
    print('query_rt_hotconspt ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #根据分页的参数，截取部分数据显示
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    #return render_template('query_realtime_hotconspt.html', rt_value=args_ret, html=str_html, img=img_path)
    return render_template('query_realtime_hotconspt.html', rt_value=args_ret, html=str_html)

#查询实时数据  热点行业
@app.route('/query_rt_hottrade', methods=['GET', 'POST'])
def query_rt_hottrade():
    print('in query_rt_hottrade')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    list_ret = db.query_allhottrade()
    db.disconnect_db()
    if list_ret is None:
        list_ret=('行业','0','000')

    ################## 分页 ######################
    req_page = request.args.get("page", 1)
    print('query_rt_hottrade ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #根据分页的参数，截取部分数据显示
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_realtime_hottrade.html', rt_value=args_ret, html=str_html)

#筹码已经集中
@app.route('/query_chipconcent', methods=['GET', 'POST'])
def query_chipconcent():
    print('in query_chipconcent')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    #当天日期
    now_time = datetime.datetime.now()
    today = now_time.strftime('%Y-%m-%d')
    #today = '2019-08-16'

    list_ret = db.query_chipconcent(today)
    db.disconnect_db()
    if list_ret is None:
        list_ret=('代码','名称','间隔','time','day','num')

    ################## 分页 ######################
    req_page = request.args.get("page", 1)
    print('query_chipconcent ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #根据分页的参数，截取部分数据显示
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_chipconcent.html', rt_value=args_ret, html=str_html)

## 实时双底
@app.route('/query_rt_wbottom', methods=['GET', 'POST'])
def query_rt_wbottom():
    print('in query_rt_wbottom')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()

    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    today = GetToday()

    list_ret = db.query_today_rt_strategy(today)

    db.disconnect_db()

    if list_ret is None:
        list_ret=('代码','探测时间')

    ################## 分页 ######################
    req_page = request.args.get("page", 1)
    print('query_chipconcent ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #根据分页的参数，截取部分数据显示
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_realtime_wbottom.html', rt_value=args_ret, html=str_html)

#2.登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        user = request.form["username"]
        password = request.form["password"]
        print(user)
        print(password)
        if user == 'admin' and password == '123':
            return redirect(url_for('query'))
        elif user == 'root' and password == 'root':
            return redirect(url_for('config'))

        #flash('邮箱或者密码错误，请检查后再试.')
    return render_template('login.html')

#登录后的导航界面
@app.route('/index')
def index():
    print('index')
    #重新定向
    return render_template('index.html')

#首页
@app.route('/')
def home():
    print('my home')
    #重新定向
    return redirect(url_for('login'))


if __name__ == "__main__":
    print('this is main!')
    #use_reloader=False  防止执行两遍
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
