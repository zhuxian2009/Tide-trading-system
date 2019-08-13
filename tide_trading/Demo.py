import paho.mqtt.client as mqtt
import time

 ####################################### MQTT Client
#HOST = "127.0.0.1"
HOST = "192.168.1.103"
PORT = 1883

def client_loop():
    client_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    client = mqtt.Client(client_id)    # ClientId不能重复，所以使用当前时间
    #client.username_pw_set("admin", "public")  # 必须设置，否则会返回「Connected with result code 4」
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, 60)
    client.loop_forever()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/test")

def on_message(client, userdata, msg):
    print(msg.topic+" "+msg.payload.decode("utf-8"))

if __name__ == '__main__':
    client_loop()
'''
# coding=GBK
import  json

if __name__ == '__main__':
    dict = {}
    dict['code']='000001'
    dict['name'] = '中国平安'

    dict2 = {}
    dict2['code'] = '000002'
    dict2['name'] = '中国平安2'

    stock = {}
    #stock={'stock':dict}
    stock['type'] = 'stock_push'
    stock['stock'] = [dict,dict2]

    print(dict)
    j = json.dumps(stock,ensure_ascii=False)
    print(j)
    '''