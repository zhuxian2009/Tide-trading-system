# coding=gbk

from flask import Flask, url_for, redirect, render_template, request
import src.common.conf as conf
import src.datamgr.dbmgr as dbmgr
from src.common.pager import Pagination
import datetime
#import src.realtime.rt_hotspot as rt_hotspot
#import src.datamgr.baseinfo as baseinfo
import src.common.schedulermgr as schedulermgr
import os
#������ȣ�����
#from flask_apscheduler import APScheduler as myScheduler
#from apscheduler.schedulers.background import BackgroundScheduler as myScheduler

app = Flask(__name__)
#�����ļ�·��
cur_path = os.getcwd()
print(cur_path)
str_conf_path = cur_path + '/conf/conf.ini'
#�������
schedulermgr = schedulermgr.CSchedulerMgr(str_conf_path)
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
    str_db_keepalive_status = schedulermgr.get_db_keepalive_status()
    msg = 'hotspot:'+str_hotspot+'  update:'+str_db_update_status+' dbkeepalive:'+str_db_keepalive_status
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

#��ѯʵʱ����  �ȵ����
@app.route('/query_rt_hotconspt', methods=['GET', 'POST'])
def query_rt_hotconspt():
    print('in query_rt_hotconspt')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')

    list_ret = db.query_allhotconsept()
    db.disconnect_db()
    if list_ret is None:
        list_ret=('����','0','000')

    ################## ��ҳ ######################
    req_page = request.args.get("page", 1)
    print('query_rt_hotconspt ... req_page=', req_page)
    pager_obj = Pagination(req_page, len(list_ret), request.path, request.args, per_page_count=20)
    print(request.args)
    #���ݷ�ҳ�Ĳ�������ȡ����������ʾ
    args_ret = list_ret[pager_obj.start:pager_obj.end]
    str_html = pager_obj.page_html()
    print(str_html)
    return render_template('query_realtime_hotconspt.html', rt_value=args_ret, html=str_html)

#��ѯʵʱ����  �ȵ���ҵ
@app.route('/query_rt_hottrade', methods=['GET', 'POST'])
def query_rt_hottrade():
    print('in query_rt_hottrade')
    myconf = conf.CConf(str_conf_path)
    myconf.ReadConf()
    db = dbmgr.CDBMgr(myconf.db_host, myconf.db_username, myconf.db_pwd, 'kdata')

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

    #��������
    now_time = datetime.datetime.now()
    #today = now_time.strftime('%Y-%m-%d')
    today = '2019-08-16'

    list_ret = db.query_chipconcent(today)
    db.disconnect_db()
    if list_ret is None:
        list_ret=('����','����','���','time','day')

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
