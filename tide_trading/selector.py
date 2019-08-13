# coding=utf-8
import multiprocessing
import time
import src.analysis.limitconcept as limitconcept
import src.stockselector.wbottom as wbottom
import src.datamgr.baseinfo as baseinfo
import src.mqtt.jsonconcept as jsonconcept
#import src.mqtt.wxmgr as wxmgr
import sys
import datetime

'''选股器'''
def main():

    que = multiprocessing.Queue()
    print('***********  main **************')
    #选股
    p_limit = multiprocessing.Process(target=proc_selector, args=(que,))
    #发布
    #p_public = multiprocessing.Process(target=proc_public, args=(que,))
    p_limit.start()
    #p_public.start()
    p_limit.join()
    #p_public.join()

def proc_public(que):
    pass
    #登录微信
    #bot = wxmgr.CMyWX()
    #gooke_group = bot.get_group('谷壳')
    #bot.send_msg(gooke_group, 'test')
    #fri = bot.get_friend('文件传输助手')
    #bot.send_msg(fri, 'test')
    #bot.sendto_filehelper('test')
'''
    while True:
        jconcept = jsonconcept.CJsonConcept()
        sys.stdout.write('before que.get()...............\n')
        sys.stdout.flush()

        #阻塞的，get到数据才往下走
        concepts = que.get()

        sys.stdout.write('proc_public... 1\n')
        sys.stdout.flush()

        for concept in concepts:
            jconcept.AddConcept(concept[0], concept[1])

        sys.stdout.write('proc_public... 2\n')
        sys.stdout.flush()

        #myConceptJson = jconcept.ToJson()
        myConceptStr = jconcept.ToDictString()
        sys.stdout.write('proc_public ...............3\n')
        sys.stdout.flush()
        # 发布
        #mymqtt.PublishMQTT('/test', myConceptJson)
        #推送
        #bot.send_msg(gooke_group, myConceptStr)
        bot.sendto_filehelper(myConceptStr)
        sys.stdout.write('proc_public ...............4\n')
        sys.stdout.flush()
'''
#子进程，选股
def proc_selector(que):

    #数据源_数据库
    my_selector = wbottom.CWBotton()
    my_selector.Process()


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    main()
    endtime = datetime.datetime.now()
    print('选股用时(秒)：', (endtime - starttime).seconds)
