# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 14:40:41 2018

@author: 123
"""

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


TRADE_DATE = '20180925'
EXCEL_NAME = 'tushare_data.xlsx'
TOKEN = '56c554861c29f507bb46a6514e00355d8bda337ece83f416fe728043'


ts.set_token(TOKEN)
pro = ts.pro_api()
df_industry = ts.get_industry_classified()
industry = list(set(df_industry.c_name))
df = pro.daily(trade_date=TRADE_DATE)


df['amount'] = df.amount/10
sunrise_industry = ['酿酒行业', '食品行业', '生物制药', '医疗器械',
                    '电子器件', '电子信息', '化纤行业', '化工行业',
                    '家电行业', '仪器仪表', '汽车制造', '交通运输',
                    '金融行业', '综合行业', '次新股']
core_stocks = ['600276', '600887', '000538', '600519', '600309', '600660',
               '603288', '002507', '002008', '002415', '002236', '000963',
               '002294', '000858', '002304', '300003', '600486', '600009',
               '601888', '600585']

first_core = ['300003', '002372', '300015', '600763', '300747', '300571',
              '601877', '000895', '600104', '600346', '600487', '601318',
              '601933', '000651', '000333', '002475', '300176', '601100']

second_core = ['300122', '002456', '600036', '600570', '600703', '600867',
               '000338', '600298', '002044', '600872', '601233', '600801',
               '300124', '002714', '600201', '300308', '300347', '600066',
               '300316', '300373', '300188', '300595', '300357', '000661',
               '300595', '603939', '603039']

active_stocks = ['002153', '002368', '002405', '300036', '300253', '300168',
                 '300170', '300188', '300348', '300365', '300377', '002371',
                 '002049', '002268', '603019', '002281', '603986', '300077',
                 '002916', '600460', '600584', '300666', '002129', '300474',
                 '603160', '300496', '300134', '300684', '600522', '603559',
                 '300312']


def trans_code(symbol):
    return symbol[:6]


df['code'] = list(map(trans_code, df.ts_code))
df = df.merge(df_industry)
df.drop(['ts_code', 'change'], axis=1, inplace=True)
cols = list(df)
cols.insert(0, cols.pop(cols.index('c_name')))
cols.insert(1, cols.pop(cols.index('name')))
cols.insert(2, cols.pop(cols.index('code')))
df = df.loc[:, cols]
df.rename(columns={'c_name': '行业',
                   'code': '代码',
                   'name': '公司',
                   'trade_date': '日期',
                   'open': '开盘价',
                   'high': '最高价',
                   'low': '最低价',
                   'close': '收盘价',
                   'pre_close': '昨收盘价',
                   'pct_change': '涨跌幅：%',
                   'vol': '成交量',
                   'amount': '成交额:万元'},
          inplace=True)
writer = pd.ExcelWriter(TRADE_DATE + EXCEL_NAME)
df[df.代码.isin(core_stocks)].to_excel(writer, sheet_name='核心标的')
df[df.代码.isin(first_core)].to_excel(writer, sheet_name='一级标的')
df[df.代码.isin(second_core)].to_excel(writer, sheet_name='二级标的')
df[df.代码.isin(active_stocks)].to_excel(writer, sheet_name='活跃标的')
for i in sunrise_industry:
    df_i = df[df.行业 == i]
    df_i.to_excel(writer, sheet_name=i)
writer.save()
