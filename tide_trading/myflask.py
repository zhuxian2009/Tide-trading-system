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
#�����������壬������ʾ����
import pylab as mpl
import numpy as np
import base64
from io import BytesIO
import pandas as pd
import src.datamgr.baseinfo as baseinfo
import src.common.tools as tools
import os

#������ȣ�����
#from flask_apscheduler import APScheduler as myScheduler
#from apscheduler.schedulers.background import BackgroundScheduler as myScheduler

app = Flask(__name__)
#�����ļ�·��
cur_path = os.getcwd()
print(cur_path)
str_conf_path = cur_path + '/conf/conf.ini'

#��־Ψһ
g_conf = conf.CConf(str_conf_path)
filename_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
log_filename = cur_path+'/'+g_conf.log_dir+'/tide_system_'+filename_time+'.log'
g_log = tools.CLogger(g_conf.app_name, log_filename, 1).getLogger()

#�������
schedulermgr = schedulermgr.CSchedulerMgr(str_conf_path, g_log)
schedulermgr.start()

def GetToday():
    now_time = datetime.datetime.now()
    day = now_time.strftime('%Y%m%d')
    print('end time is ', day)
    return day

#1.�޸�����
@app.route('/config')
def config():
    print('in config')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()

    #��ʼ����
    start_year = myconf.s_bt_startday[0:4]
    start_mouth = myconf.s_bt_startday[4:6]
    start_day = myconf.s_bt_startday[6:8]
    start = start_year+'-'+start_mouth+'-'+start_day
    print('start:'+start)
    #��ֹ����
    end_year = myconf.s_bt_endday[0:4]
    end_mouth = myconf.s_bt_endday[4:6]
    end_day = myconf.s_bt_endday[6:8]
    end = end_year+'-'+end_mouth+'-'+end_day
    print('end:' + end)

    return render_template('conf.html')


#��ѯ����״̬
@app.route('/server_status')
def server_status():
    print('in server_status')

    #str_hotspot = schedulermgr.get_scheduler_status()
    str_hotspot = schedulermgr.get_hotspot_status()
    str_db_update_status = schedulermgr.get_db_update_status()
    str_rt_wbottom_status = schedulermgr.get_rt_wbottom_status()
    str_reatime_quotes_status = schedulermgr.get_reatime_quotes_status()
    str_rt_chipconcent_status = schedulermgr.get_rt_chipconcent_status()
    msg = '<p>ʵʱ�ȵ�����:  '+str_hotspot+'</p><p> ���ݿ��������:  '+str_db_update_status+'</p><p>β��˫������:  '+str_rt_wbottom_status\
          +'</p><p>ʵʱ��������:  '+str_reatime_quotes_status+'</p><p>̽����뼯������:'+str_rt_chipconcent_status+'</p>'
    #print('query_rt_hotconspt ************ pip *************  ',str_hotspot)
    return render_template('conf_status.html', hottime=msg)

#2.��ѯ��Ϣ
@app.route('/query')
def query():
    print('in query')
    abc = 'query abc'
    return render_template('query.html', vvv=abc)

#��ѯ�ز�����  w��
@app.route('/query_bt_w', methods=['GET', 'POST'])
def query_bt_w():
    print('in query_bt_w')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    list_ret = db.query_rangebacktest_wbottom('20190101', GetToday())
    db.disconnect_db()
    ################## ��ҳ ######################
    req_page = request.args.get("page", 1)
    print('query_bt_w ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #���ݷ�ҳ�Ĳ�������ȡ����������ʾ
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_backtest_wbotton.html', wb_value=args_ret, html=str_html)

#�鿴ָ���ȵ�Ķ�̬ͼ
@app.route('/query_rt_hotconspt_one/<conspt>', methods=['GET', 'POST'])
def query_rt_hotconspt_one(conspt):
    print('query_rt_hotconspt_one...', conspt)
    #����
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    trade_day = db.query_last_tradeday(10)
    #trade_day = pd.DataFrame(list(result), columns=['trade_day'])

    # ���ع�Ʊ����
    pBaseInfo = baseinfo.CBaseinfo()
    pBaseInfo.read_excel()

    #conspt_df = pd.DataFrame(columns=['date', 'count'])
    list_date = list()
    list_count = list()
    for day in trade_day:
        codes = db.query_limit(day[0])
        print('limit num=', len(codes))

        count = 0
        #��������code
        for code in codes:
            #ȥ��.SZ .SH�ĺ�׺
            str_code = code[0][0:6]
            my_stock_info = pBaseInfo.get_stock_info(str_code)
            if my_stock_info is None:
                print(code, ' is not exist!aps_hotspot')
                continue

            consepts = my_stock_info.get_conseption()
            #��ѯ�ĸ����Ƿ���list��
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
    #############################################��ͼ
    #������������
    #myfont = FontProperties(fname=r'/smb/share/hdf5test/venv/lib/python3.7/site-packages/matplotlib/mpl-data/fonts/ttf/simhei.ttf')
    #mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['font.sans-serif'] = ['simhei']
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['axes.unicode_minus'] = False

    # ����figure����,�൱��׼��һ������
    fig = plt.figure(figsize=(8, 3))

    # ����axis�����൱���ڻ�����׼��һ�Ű�ֽ��111��11��ʾֻ��һ����񣬵�3��1����ʾ�ڵ�1������ϻ�ͼ
    ax = fig.add_subplot(111)
    plt.title(conspt)
    plt.xlabel(u'������')
    plt.ylabel(u'��ͣ����')

    #���ַ��������ڣ�ת�������ڶ���
    xs = [datetime.datetime.strptime(d, '%Y%m%d').date() for d in list_date]

    #���ڶ�����Ϊ�������õ�������,����ʹ��list_date�е��ַ�����־��Ϊ����ı�ǩ��������
    #x����Ŀ̶�ֵ
    ar_xticks = np.arange(1, len(list_date)+1, step=1)
    plt.xticks(ar_xticks, list_date, rotation=45, fontsize=10)
    plt.yticks(np.arange(0, 30, step=2), fontsize=10)
    ax.plot(ar_xticks, list_count, color='r')

    #�·�ͼƬ��ʾ������������
    plt.tight_layout()

    #�ڵ����Ϸ�������ֵ
    for x, y in zip(ar_xticks, list_count):
        plt.text(x, y + 0.3, str(y), ha='center', va='bottom', fontsize=10)

    #fmt = mdates.DateFormatter('%Y%m%D')
    #xs = [datetime.datetime.strptime(d, '%Y%m%d').date() for d in conspt_df['date']]
    #plt.plot(xs, conspt_df['count'], 'o-')

    #plt.savefig('ttt.png')
    # figure ����Ϊ�������ļ�
    buffer = BytesIO()
    plt.savefig(buffer)
    plot_data = buffer.getvalue()
    # ��matplotlibͼƬת��ΪHTML
    imb = base64.b64encode(plot_data)  # ��plot_data���б���
    ims = imb.decode()
    imd = "data:image/png;base64," + ims
    return render_template('query_realtime_hotconspt_one.html', img=imd)

#��ѯʵʱ����  �ȵ����
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
        list_ret=('����', '0', '000')


    ################## ��ҳ ######################
    req_page = request.args.get("page", 1)
    print('query_rt_hotconspt ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #���ݷ�ҳ�Ĳ�������ȡ����������ʾ
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    #return render_template('query_realtime_hotconspt.html', rt_value=args_ret, html=str_html, img=img_path)
    return render_template('query_realtime_hotconspt.html', rt_value=args_ret, html=str_html)

#��ѯʵʱ����  �ȵ���ҵ
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
        list_ret=('��ҵ','0','000')

    ################## ��ҳ ######################
    req_page = request.args.get("page", 1)
    print('query_rt_hottrade ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #���ݷ�ҳ�Ĳ�������ȡ����������ʾ
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_realtime_hottrade.html', rt_value=args_ret, html=str_html)

#�����Ѿ�����
@app.route('/query_chipconcent', methods=['GET', 'POST'])
def query_chipconcent():
    print('in query_chipconcent')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')
    db.connect_db()

    #��������
    now_time = datetime.datetime.now()
    today = now_time.strftime('%Y-%m-%d')
    #today = '2019-08-16'

    list_ret = db.query_chipconcent(today)
    db.disconnect_db()
    if list_ret is None:
        list_ret=('����','����','���','time','day','num')

    ################## ��ҳ ######################
    req_page = request.args.get("page", 1)
    print('query_chipconcent ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #���ݷ�ҳ�Ĳ�������ȡ����������ʾ
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_chipconcent.html', rt_value=args_ret, html=str_html)

## ʵʱ˫��
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
        list_ret=('����','̽��ʱ��')

    ################## ��ҳ ######################
    req_page = request.args.get("page", 1)
    print('query_chipconcent ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #���ݷ�ҳ�Ĳ�������ȡ����������ʾ
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_realtime_wbottom.html', rt_value=args_ret, html=str_html)

#2.��¼
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

        #flash('�����������������������.')
    return render_template('login.html')

#��¼��ĵ�������
@app.route('/index')
def index():
    print('index')
    #���¶���
    return render_template('index.html')

#��ҳ
@app.route('/')
def home():
    print('my home')
    #���¶���
    return redirect(url_for('login'))


if __name__ == "__main__":
    print('this is main!')
    #use_reloader=False  ��ִֹ������
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
