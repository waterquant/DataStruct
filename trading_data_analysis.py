# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:00:50 2018

@author: 123
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


trade_list = pd.read_excel('D:\\BaiduNetdiskDownload/交易数据14.7—15.7/15.1.xlsx')

trade_list_net_1 = trade_list[~pd.isna(trade_list.成交时间)]

trade_list_net_2 = trade_list[trade_list['成交数量'] != 0]

trade_list = trade_list_net_1
'''
trade_list_net_2 - trade_list_net_1
#  两个dataframe相减，先append再drop_duplicates，思想不错
trade_net = trade_list_net_2.append(trade_list_net_1).drop_duplicates(keep=False)
'''
# trade_list = trade_list.dropna(axis='index')

s_date = set(trade_list['成交日期'])

s_symbol = set(trade_list['证券名称'])
result = pd.DataFrame(np.full((len(s_date), len(s_symbol)), np.nan),
                      index=list(s_date), columns=list(s_symbol))


for s in s_date:
    s_symbol = set(trade_list[trade_list.成交日期 == s]['证券名称'])
    for symbol in s_symbol:
        '''
        a = trade_list[trade_list.成交日期==s]
        b = a[a.证券名称==symbol]
        c = b[b.操作=='买']
        d = b[b.备注=='融券卖出']
        '''
        c = trade_list[(trade_list.成交日期 == s) & (trade_list.证券名称 ==
                       symbol) & (trade_list.操作 == '买')]
        d = trade_list[(trade_list.成交日期 == s) & (trade_list.证券名称 ==
                       symbol) & (trade_list.操作 == '卖')]
        if abs(c['成交数量'].sum() - d['成交数量'].sum()) < 100:
            result.loc[s][symbol] = d['成交金额'].sum() * (1 - 0.0013) -\
                                    c['成交金额'].sum()*(1+0.0003)
result.sort_index(axis=0, ascending=False)
rslt = result.dropna(axis='columns', how='all').T
rslt['汇总'] = rslt.T.sum()
rslt = rslt[rslt['汇总'] != 0]
r = rslt.T
r['总计'] = rslt.sum()
rslt = r.T
plt.plot(r['总计'][0:len(rslt.columns)-1].cumsum())
print('月度总盈利：', rslt['汇总']['总计'])
result = rslt.T.drop('汇总')


def draw_most(date_line, capital_line):
    df = pd.DataFrame({'date': date_line, 'capital': capital_line})
    df['d2here'] = df.capital.expanding().max()
    df['dd2here'] = df.capital / df.d2here - 1
    temp = df.sort_values(by='dd2here').iloc[0][['date', 'dd2here']]
    max_dd = temp['dd2here']
    # end_date = temp['date'].strftime('%Y-%m-%d')
    end_date = temp['date']
    # 取出最大回撤之前的数据
    df = df[df['date'] <= end_date]
    # 再在其中寻找capital最大的对应的日期即是回撤起始时间
    # start_date = df.sort_values(by='capital', ascending=False).iloc[0]['date'].strftime('%Y-%m-%d')
    start_date = df.sort_values(by='capital', ascending=False).iloc[0]['date']
    print('最大回撤为：%f, 开始日期：%s, 结束日期：%s' % (max_dd, start_date, end_date))
    return max_dd


most = draw_most(list(result.index), list(result.总计.cumsum()))
