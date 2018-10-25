# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 09:50:09 2018

@author: 123
"""
import math
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import optimize
import matplotlib.pyplot as plt
START_DATE = '2011-09-01'
END_DATE = '2018-07-18'
s = '300253'
# zxb = ts.get_sme_classified()
EPSINON = 1e-6
MAX = 100
N1 = 20
N2 = 10
START_DATE = '2018-03-01'
END_DATE = '2018-07-01'
core_stocks = ['600276', '600887', '000538', '600519', '600309', '600660',
               '603288', '002507', '002008', '002415', '002236', '000963',
               '002294', '000858', '002304', '300003', '600486', '600009',
               '601888', '600585']


def judge_pivot_up(lst, N1=200, N2=45, N3=0.8, N4=0.5):
    temp_lst = []
    for s in lst:
        df = ts.get_k_data(s, START_DATE, END_DATE)
        if len(df) < N1:
            continue
        bottom = df.tail(N1).low.min()
        up = df.tail(N1).low.max()
        if df.tail(N2).low.min() > bottom+(up-bottom)*N4 and \
                df.tail(N2).low.max() > bottom+(up-bottom)*N3:
            temp_lst.append(s)
    return temp_lst

# zxb_pivot_up = judge_pivot_up(list(zxb.code))
# 精确四舍五入


def roundUp(value, decDigits=2):
    result = str(value).strip()
    if result != '':
        zeroCount = decDigits
        indexDec = result.find('.')
        if indexDec > 0:
            zeroCount = len(result[indexDec + 1:])
            if zeroCount > decDigits:
                if int(result[indexDec + decDigits + 1]) > 4:
                    result = str(value + pow(10, decDigits * -1))

                # 存在进位的可能，小数点会移位
                indexDec = result.find('.')

                result = result[:indexDec + decDigits + 1]
                zeroCount = 0
            else:
                zeroCount = decDigits - zeroCount
        else:
            result += '.'
        for i in range(zeroCount):
            result += '0'
    return result


def judge_limit_up(s, DATE='2018-07-20'):
    if not ts.is_holiday(DATE):
        last_day = datetime.strptime(DATE, '%Y-%m-%d') - timedelta(1)
        last_day = datetime.strftime(last_day, '%Y-%m-%d')
        df_last_day = ts.get_k_data(s, last_day, last_day)
        while df_last_day.empty:
            last_day = datetime.strptime(DATE, '%Y-%m-%d') - timedelta(1)
            last_day = datetime.strftime(last_day, '%Y-%m-%d')
        df = ts.get_k_data(s, last_day, DATE)
        if abs(float(df[0:1].close)*1.1 - float(df[1:].close)) <= EPSINON:
            return True
        else:
            return False
    else:
        print('please input correct date!')
        return -1

# temp_lst = ['300487']


def fun_line(x, a, b):
    return a*x + b


'''
zxb_pivot_up = judge_pivot_up(list(zxb.code),N1=200,N2=45,N3=0.7,N4=0.4)


ratio_s = []
for s in zxb_pivot_up:
    df = ts.get_k_data(s,START_DATE,END_DATE)
    temp = df[df.high==df.high.max()].date
    df_after_max = ts.get_k_data(s,str(temp).split()[1],END_DATE)
    if len(df_after_max)<10:
        ratio_s.append(MAX)
        continue
    db = df_after_max.reset_index(drop=True)
    x_index = list(db.index)
    y_close = list(db.close)

    ratio,x = optimize.curve_fit(fun_line,x_index,y_close)[0]
    ratio_s.append(abs(ratio))

zxb_ratio = dict(zip(list(zxb_pivot_up),ratio_s))

zxb_ratio = sorted(zxb_ratio.items(),key=lambda x:x[1])
'''


def cal_ratio(s, start_date='2018-01-01', end_date='2018-07-01'):
    df = ts.get_k_data(s, start_date, end_date)
    if len(df) < 10:
        return MAX
    x_index = list(df.index)
    y_close = list(df.close)
    ratio, x = optimize.curve_fit(fun_line, x_index, y_close)[0]
    return math.atan(ratio)*180/math.pi


# print(cal_ratio('002153','2018-01-01','2018-07-15'))

# print(cal_ratio('600271','2018-04-12','2018-07-20'))

# print(cal_ratio('300586','2018-02-06','2018-07-20'))


def cal_core_ratio():
    core_stock_ratio = []
    for s in core_stocks:
        core_stock_ratio.append(cal_ratio(s))
    return dict(zip(core_stocks, core_stock_ratio))


'''
#core_stock_ratio = cal_core_ratio()

hryy = ts.get_k_data(s,START_DATE,END_DATE)
#hryy.reset_index(inplace=True)
hryy = hryy.set_index('date')
hryy['change'] = hryy.close.pct_change()
hryy = hryy.drop(START_DATE)
#计算N1日最高价的最高价，并以最高价填充缺省值
#expanding()函数，计算最大回测，回测起止时间时很有用
hryy['最近N1日高点'] = hryy.high.rolling(N1).max()
hryy['最近N1日高点'].fillna(value=hryy.high.expanding().max(),inplace=True)

hryy['最近N2日低点'] = hryy.low.rolling(N2).min()
hryy['最近N2日低点'].fillna(value=hryy.low.expanding().min(),inplace=True)

# 当当天的【close】> 昨天的【最近N1个交易日的最高点】时，将【收盘发出的信号】设定为1

buy_index = hryy[hryy.close>hryy.最近N1日高点.shift(1)].index
hryy.loc[buy_index,'收盘发出的信号'] = 1

sell_index = hryy[hryy.close<hryy.最近N2日低点.shift(1)].index
hryy.loc[sell_index,'收盘发出的信号'] = 0


# 取1992年之后的数据，排出较早的数据
#index_data = index_data[index_data['date'] >= pd.to_datetime('19930101')]

# 当仓位为1时，买入上证指数，当仓位为0时，空仓。计算从19920101至今的资金指数

# 计算每天的仓位，当天持有上证指数时，仓位为1，当天不持有上证指数时，仓位为0

hryy['当天的仓位'] = hryy.收盘发出的信号.shift(1)
hryy['当天的仓位'].fillna(method='ffill',inplace=True)

hryy['资金指数'] = (hryy.change * hryy.当天的仓位+1).cumprod()
initial_idx = hryy.iloc[0]['close']/(1+hryy.iloc[0]['change'])
#hryy['资金指数'] *= initial_idx

plt.plot(hryy.资金指数)

hryy['每日涨跌幅'] = hryy.change*hryy.当天的仓位
hryy['new_index'] = pd.to_datetime(hryy.index)
hryy['old_index'] = hryy.index
hryy = hryy.set_index('new_index')

#year_rtn = hryy[['change','海龟每日涨跌幅']].resample('A',how=lambda x:((x+1.).prod()-1)*100)
#year_rtn = hryy[['change','每日涨跌幅']].resample('A').apply(lambda x:((x+1.).prod()-1)*100)
'''

'''
def hma(df,n):
    return wma((2*wma(df,int(n/2))-wma(df,n)),int(math.sqrt(n)))


N = 10
hr = ts.get_k_data('600585','2016-01-01','2018-07-01')
hr = hr.reset_index(drop=True)

#hr['close_index']=hr['close']*hr['index']
hr['idx'] = hr.index + 1
hr['wma_N'] = (hr.close*hr.idx).rolling(N).sum()/((hr.idx.rolling(N).sum()))
hr['wma_N/2'] = (hr.close*hr.idx).rolling(int(N/2)).sum()/((hr.idx.rolling(int(N/2)).sum()))
hr['temp'] = 2*hr['wma_N/2']-hr['wma_N']
hr['hma'] = (hr.temp*hr.idx).rolling(int(math.sqrt(N))).sum()/((hr.idx.rolling(int(math.sqrt(N))).sum()))
hr['ma'] = hr.close.rolling(int(N)).mean()

hr = hr.drop(['date','open','high','low','volume'],axis=1)
hr.close.plot(style='b-', figsize=(14, 7))
hr.ma.plot(style='r-')
hr.hma.plot(style='g-')
plt.legend(loc='best')
plt.title('hma')
plt.show()
'''


def draw_most(date_line, capital_line):
    df = pd.DataFrame({'date': date_line, 'capital': capital_line})
    df['d2here'] = df.capital.expanding().max()
    df['dd2here'] = df.capital/df.d2here - 1
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

# draw_most(list(hryy.old_index),list(hryy.close))


def haigui(s, start_date=START_DATE, end_date=END_DATE):
    N1 = 20
    N2 = 10
    df = ts.get_k_data(s, start_date, end_date)
    df['change'] = df.close.pct_change()
    df['近N1日最高点'] = df.close.rolling(N1).max()
    df.fillna(value=df.close.expanding().max(), inplace=True)
    df['近N2日最低点'] = df.close.rolling(N2).min()
    df.fillna(value=df.close.expanding().min(), inplace=True)
    buy_index = df[df.close > df.近N1日最高点.shift(1)].index
    df.loc[buy_index, '收盘信号'] = 1
    sell_index = df[df.close < df.近N2日最低点.shift(1)].index
    df.loc[sell_index, '收盘信号'] = 0
    df['当日仓位'] = df.收盘信号.shift(1)
    df.fillna(method='ffill', inplace=True)
    df['资金指数'] = (df.change*df.当日仓位+1).cumprod()
    df.资金指数.plot(style='r-', figsize=(10, 5))
