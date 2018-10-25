# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 14:35:40 2018

@author: 123
"""

import numpy as np
import pandas as pd
import tushare as ts
from datetime import datetime,timedelta
import matplotlib.pyplot as plt

NEW_STOCK_START = 20180301   #新股上市日期不得晚于此日
NEW_STOCK_END = 20150601    #新股上市日期不得早于此日
BASE_VOLUME = 80000000     #八千万成交金额阈值
BASE_PERIOD = 151           #所取成交数据的周期跨度，包含非交易日
TEST_DATE = '2018-07-10'  #测试数据截止日期
MA_PERIOD = 20            #均线周期  
STD_MULTI = 2.25          #标准差倍数,值为2.25时，名臣健康刚好被选出
DAY_AMPLITUDE = 6.5         #日内振幅阈值
DOWM_AMPLITUDE = -0.       #下降幅度
N1 = 100                   #中枢上移标的选取时的总k线数
N2 = 30                    #中枢上移标的选取时的上移K线数
N3 = 0.8                   #中枢上移标的选取时最高价比例系数
N4 = 0.5                   #中枢上移标的选取时最低价比例系数
N5 = 0.65                  #中枢上移标的选取时收盘价比例系数
START_DATE = '2017-12-01'  #中枢上移标的选取时的起始时间
END_DATE = '2018-07-15'    #中枢上移标的选取时的截止时间


all_stock_basics = ts.get_stock_basics()
new_stock = all_stock_basics[all_stock_basics.timeToMarket>NEW_STOCK_END]
new_stock_code = new_stock[new_stock.timeToMarket<NEW_STOCK_START].index

filename = 'D:\\anaconda_project/stock_chosen_system/new_stock_code'
with open(filename,'w+') as f:
    for i in list(new_stock_code):
        f.write(i)
        f.write('\n')

#filename = 'D:\\anaconda_project/stock_chosen_system/new_stock_code'
new_stock_lst = []
with open(filename,'r+') as f:
    for line in f.readlines():
        new_stock_lst.append(line.strip())
         
#第一步：成交量删选，成交金额
new_stock_volume_ok = []
for s in new_stock_lst:
    df = ts.get_k_data(s,(datetime.strptime(TEST_DATE,'%Y-%m-%d')-
                                     timedelta(BASE_PERIOD)).strftime('%Y-%m-%d'),TEST_DATE)
    
    df['turn_volume'] = df['close']*df['volume']

    #防止有些是刚复牌股票，交易日较短影响判断
    if df['turn_volume'].mean()*100>BASE_VOLUME and len(df)>BASE_PERIOD*0.5:
        new_stock_volume_ok.append(s)

#第二部：振幅删选。
#先从比较强势的标的删选，在中枢内震荡的个股
'''
new_stock_volume_amplitude_ok = []
for s in new_stock_volume_ok:
    df = ts.get_k_data(s,(datetime.strptime(TEST_DATE,'%Y-%m-%d')-
                                     timedelta(BASE_PERIOD)).strftime('%Y-%m-%d'),TEST_DATE)
    df['ma'] = df['close'].rolling(MA_PERIOD).mean()
    df['std'] = df['close'].rolling(MA_PERIOD).std()
    new_df = df.loc[:,['close','ma','std']].iloc[MA_PERIOD:len(df),:]
    if (new_df['close']>=new_df['ma']-new_df['std']*STD_MULTI).all() and \
    (new_df['ma']+STD_MULTI*new_df['std']>=new_df['close']).all():
        new_stock_volume_amplitude_ok.append(s)
'''
#超跌后，两中枢背驰股票池
'''
new_stock_volume_downmost = []
s_return = []
for s in new_stock_volume_ok:
    df = ts.get_k_data(s,(datetime.strptime(TEST_DATE,'%Y-%m-%d')-
                                     timedelta(BASE_PERIOD)).strftime('%Y-%m-%d'),TEST_DATE)
    df['pct_change'] = df['close'].pct_change()
    df['returns'] = (df['pct_change']+1).cumprod()
    df = df.set_index('date')
    s_return.append(float(df['returns'][TEST_DATE]))
    
s_returns = dict(zip(new_stock_volume_ok,s_return))
s_returns = sorted(s_returns.items(),key = lambda x:x[1],reverse=True)
'''
 
#选出波动率较高个股
'''
new_stock_volume_day_amplitude = []
for s in new_stock_volume_ok:
    df = ts.get_k_data(s,(datetime.strptime(TEST_DATE,'%Y-%m-%d')-
                                     timedelta(BASE_PERIOD)).strftime('%Y-%m-%d'),TEST_DATE)
    df['amplitude'] = 100 * (df['high'] - df['low'])/df['close']
    if df['amplitude'].mean()>DAY_AMPLITUDE:
        new_stock_volume_day_amplitude.append(s)

'''       
        
#全市场删选，选出流动性好，跌幅较大个股
#全市场删选，速度较慢，费时
'''
all_stock_volume_downmost = []
START_DATE = (datetime.strptime(TEST_DATE,'%Y-%m-%d')-timedelta(BASE_PERIOD)).strftime('%Y-%m-%d')
for s in all_stock_basics.index:
    df = ts.get_k_data(s,START_DATE,TEST_DATE)
    if df.empty or len(df) < 0.5*BASE_PERIOD:
        continue
    
    df['turn_volume'] = df['close']*df['volume']
'''
'''
    df = df.set_index('date')
    START = START_DATE
    END = TEST_DATE
    while df.loc[START].empty:
        START = (datetime.strptime(START,'%Y-%m-%d')+timedelta(1)).strftime('%Y-%m-%d')
    while df.loc[END].empty:
        END = (datetime.strptime(END,'%Y-%m-%d')-timedelta(1)).strftime('%Y-%m-%d')
    '''
'''
    #防止有些是刚复牌股票，交易日较短影响判断
    if df['turn_volume'].mean()*100>0.8*BASE_VOLUME  and\
    float(df.iloc[len(df)-1].close/df.iloc[0].close-1)<DOWM_AMPLITUDE:
        all_stock_volume_downmost.append(s)
'''
  
#选出中枢上移个股
stock_pivot_up = []
for s in list(new_stock_volume_ok):
    df = ts.get_k_data(s,START_DATE,END_DATE)
    if len(df)<N1:
        continue
    bottom = df.tail(N1).low.min()
    up = df.tail(N1).high.max()
    
    if df.tail(N2).low.min()>bottom + (up-bottom)*N4 and \
    df.tail(N2).high.max()>bottom +(up-bottom)*N3:
        stock_pivot_up.append(s)

print(stock_pivot_up)
# vwap = (prices * volume).sum()/volume.sum()

    

     

    

    