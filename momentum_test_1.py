# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 09:38:11 2018

@author: 123
"""

import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt


START_DATE = '2018-03-01'
END_DATE = '2018-07-18'
NUM = 5
'''
core_stocks = ['600276','600887','000538','600519','600309','600660','603288','002507',
               '002008','002415','002236','000963','002294','000858','002304','300003',
               '600486','600009','601888','600585']

df_core = pd.DataFrame()
for s in core_stocks:
    df = ts.get_k_data(s,START_DATE,END_DATE)
    df['change'] = df.close.pct_change()
    df_core = df_core.append(df,ignore_index = True)
    
grouped = df_core.groupby('code')['change'].agg({'return':lambda x:(x+1).prod()-1})
grouped.sort_values(by='return',inplace=True)

monentum_list = list(grouped.index[-NUM:])
'''

# 计算最大连续上涨天数和连续下跌天数


def max_successive_up(date_line, return_line):
    """
    :param date_line: 日期序列
    :param return_line: 账户日收益率序列
    :return: 输出最大连续上涨天数和最大连续下跌天数
    """
    df = pd.DataFrame({'date': date_line, 'rtn': return_line})
    # 新建一个全为空值的一列
    df['up'] = [np.nan] * len(df)

    # 当收益率大于0时，up取1，小于0时，up取0，等于0时采用前向差值
    df.iloc[df['rtn'] > 0, 'up'] = 1
    df.iloc[df['rtn'] < 0, 'up'] = 0
    df['up'].fillna(method='ffill', inplace=True)

    # 根据up这一列计算到某天为止连续上涨下跌的天数
    rtn_list = list(df['up'])
    successive_up_list = []
    num = 1
    for i in range(len(rtn_list)):
        if i == 0:
            successive_up_list.append(num)
        else:
            if (rtn_list[i] == rtn_list[i - 1] == 1) or\
                    (rtn_list[i] == rtn_list[i-1] == 0):
                num += 1
            else:
                num = 1
            successive_up_list.append(num)
    # 将计算结果赋给新的一列'successive_up'
    df['successive_up'] = successive_up_list
    # 分别在上涨和下跌的两个dataframe里按照'successive_up'的值排序并取最大值
    max_successive_up = df[df['up'] == 1].sort_values(
            by='successive_up', ascending=False)['successive_up'].iloc[0]
    max_successive_down = df[df['up'] == 0].sort_values(
            by='successive_up', ascending=False)['successive_up'].iloc[0]
    print('最大连续上涨天数为：%d  最大连续下跌天数为：%d' % (
            max_successive_up, max_successive_down))
    return max_successive_up, max_successive_down

# 计算上涨和下跌天数


def cal_up_down_days(s, START_DATE, END_DATE):
    df = ts.get_k_data(s, START_DATE, END_DATE)
    df['change'] = df.close/df.close.shift(1)-1
    df_up = df[df.change > 0]
    df_down = df[df.change < 0]
    print('上涨的天数为：{},下跌的天数为：{}'.format(len(df_up), len(df_down)))
    return len(df_up), len(df_down)

# stock_basics = ts.get_stock_basics()
# ts.get_profit_data(2018,1)


def draw_most(capital_date, capital_list):
    df = pd.DataFrame({'date': capital_date, 'capital': capital_list})
    df['d2max'] = df.capital.expanding().max()
    df['d2here'] = 1 - df['capital']/df['d2max']
    temp = df.sort_values(by=['d2here'], ascending=False)
    draw_max = temp.iloc[0].d2here
    end_date = temp.iloc[0].date
    temp_here = df[df.date < end_date]
    start_date = temp_here.sort_values(by=['capital'],
                                       ascending=False).iloc[0].date
    print('最大回撤：{},开始日期：{},结束日期：{}'.format(draw_max,
          start_date, end_date))


core_stocks = ['600276', '600887', '000538', '600519', '600309', '600660',
               '603288', '002507', '002008', '002415', '002236', '000963',
               '002294', '000858', '002304', '300003', '600486', '600009',
               '601888', '600585']


def momentum_and_contrarian(all_stock, start_date=START_DATE,
                            end_date=END_DATE):
    num = int(len(all_stock)/4)
    df = pd.DataFrame()
    for s in all_stock:
        df_temp = ts.get_k_data(s, start_date, end_date)
        df_temp['change'] = df_temp.close.pct_change()
        if len(df_temp) > 20:
            df = df.append(df_temp, ignore_index=True)
    df_return = df.groupby('code')['change'].agg({
                'return': lambda x: (x+1).prod()-1})
    df_return.sort_values(by='return', inplace=True)
    momentum_list = list(df_return.index)[-num:]
    contrarian_list = list(df_return.index)[:num]
    return momentum_list, contrarian_list

# a,b = momentum_and_contrarian(core_stocks)


def haigui(s, start_date=START_DATE, end_date=END_DATE):
    N1 = 20
    N2 = 10
    df = ts.get_k_data(s, start_date, end_date)
    if len(df) < 2*N1:
        print('the mount of date is too short')
    df['change'] = df.close.pct_change()
    df['近N1日最高点'] = df.close.rolling(N1).max()
    df.近N1日最高点.fillna(value=df.close.expanding().max(), inplace=True)
    df['近N2日最低点'] = df.close.rolling(N2).min()
    df.近N2日最低点.fillna(value=df.close.expanding().min(), inplace=True)
    buy_index = df[df.close > df.近N1日最高点.shift(1)].index
    df.loc[buy_index, '收盘发出的信号'] = 1
    sell_index = df[df.close < df.近N2日最低点.shift(1)].index
    df.loc[sell_index, '收盘发出的信号'] = 0
    df['当天仓位'] = df.收盘发出的信号.shift(1)
    df.当天仓位.fillna(method='ffill', inplace=True)
    df['资金指数'] = (df.change*df.当天仓位 + 1).cumprod()
    '''
    df['close_normalize'] = (df.close-df.close.mean())/df.close.std()
    df.close_normalize.plot(style='b-',figsize=(10,6))
    '''
    df.资金指数.plot(style='g-')
    plt.legend(loc='best')
    plt.title('Cumulative Return')
    plt.show()

