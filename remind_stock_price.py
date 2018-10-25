# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 09:29:08 2018

@author: 123
"""
import time
import queue
from smtplib import *
from datetime import datetime
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import threading
import itchat
# mytoken = '56c554861c29f507bb46a6514e00355d8bda337ece83f416fe728043'


class Stock():
    '''
    获取股票实时信息
    '''
    def __init__(self, q, stock_num='600276'):
        self.q = q
        self.stock_num = stock_num
        self._terminal = True

    def query_stock_real_price(self):
        df = ts.get_realtime_quotes(self.stock_num)
        df = df[['price', 'time']]
        price = df['price'].values[0]
        time = df['time'].values[0]
        return price, time

    def get_kline_real_price(self):
        today = datetime.now().strftime('%Y-%m-%d')
        df = ts.get_hist_data(self.stock_num, start='2018-08-08', end=today)
        return df[['ktype']]

    def start_run(self):
        while self._terminal:
            p, t = self.query_stock_real_price()
            print(f'>>{t}:stock price {p}')
            self.q.put(float(p))
            time.sleep(3)

    def stop_run(self):
        self._terminal = False


itchat.login()
itchat.send(u'恒瑞医药', 'filehelper')
q = queue.Queue(maxsize=50)
stock = Stock(q)
start_dt = datetime(datetime.today().year, datetime.today().month,
                    datetime.today().day, hour=9, minute=30, second=0)
stop_dt = datetime(datetime.today().year, datetime.today().month,
                   datetime.today().day, hour=15, minute=0, second=0)


def query():
    while True:
        now_dt = datetime.now()
        if now_dt < start_dt or now_dt > stop_dt:
            print('stock market closed')
            stock.stop_run()
            itchat.send('stock market closed', 'filehelper')
            break
        if not q.empty():
            cur_price = q.get()
            high_price = 66.68
            low_price = 66.65
            if cur_price > high_price or cur_price < low_price:
                title = f'股票{stock.stock_num}:价格{cur_price},\
                max:{high_price},min:{low_price}'
                print(title)
                itchat.send(f'恒瑞医药当前股价：{cur_price} 元', 'filehelper')
                time.sleep(8)
# watching stock real price every min


t1 = threading.Thread(target=stock.start_run, args=())
t2 = threading.Thread(target=query, args=())
t1.start()
t2.start()
t1.join()
t2.join()



'''
class Server():
    def __init__(self,server_name=SMTP_SERVER,passwd=PASSWORD,from_addr=FROM_ADDR,debug=False):
        self.smtp_server = SMTP_SSL(SMTP_SERVER)
        self.passwd = passwd
        self.from_addr = from_addr
        self.smtp_server.set_debuglevel(debug)
    
    def connet(self):
        try:
            self.smtp_server.ehlo(SMTP_SERVER)
            self.smtp_server.login(self.from_addr,self.passwd)
            return True
        except SMTPException:
            print('login failed')
            return False
    
    def close(self):
        self.smtp_server.quit()

class Mail():
    def __init__(self,server=None,to_addr=None):
        self._server = server
        self._to_addr = to_addr
        self._title = 'Empty title'
        self._contect = 'Hi,this is mail contect'
    
    @property
    def mail_title(self):
        return self._title
    
    @mail_title.setter
    def mail_title(self,title):
        self._title = title
    
    @property
    def mail_contect(self):
        return self._contect
    
    @mail_contect.setter
    def mail_contect(self,contect):
        self._contect = contect
    
    def send_mail(self):
        cur_time = time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime())
        try:
            msg = MIMEText(self.mail_contect,'plain','utf-8')
            msg['From'] = self._server.from_addr
            msg['To'] = ';'.join(self._to_addr)
            msg['Subject'] = cur_time+'  '+self._title
            self._server.smtp_server.sendmail(self._server.from_addr,self._to_addr)
            print(f'{cur_time}:From {self._server.from_addr} to {self._to_addr} send successfully')
        except SMTPException as e:
            print(e)
            print(f'{cur_time}:From {self._server.from_addr} to {self._to_addr} send failed')



#watching stock real price every min
t = threading.Thread(target=stock.start_run,args=())
t.start()
start_dt = datetime(datetime.today().year,datetime.today().month,datetime.today().day,
                    hour=9,minute=30,second=0)
stop_dt = datetime(datetime.today().year,datetime.today().month,\
                   datetime.today().day, hour=15,minute=00,second=0)

while True:
    now_dt = datetime.now()
    if now_dt<start_dt or now_dt>stop_dt:
        print(f'Cur Time {now_dt} > {stop_dt},we will stop!')
        stock.stop_run()
        break
    if not q.empty():
        cur_price = q.get()
        setting = read_setting()
        high_price = float(setting.get('high_price'))
        low_price = float(setting.get('low_price'))
        if setting and cur_price>high_price or cur_price<low_price:
            title = f'股票{stock_name}:价格{cur_price},\
            max:{high_price},min:{low_price}'
            print(title)
            send_mail(title)
            time.sleep(60)
t.join()
'''