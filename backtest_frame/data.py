# encoding: UTF-8
import os
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# 默认空值
EMPTY_STRING = ''
EMPTY_UNICODE = u''
EMPTY_INT = 0
EMPTY_FLOAT = 0.0

# 方向常量
DIRECTION_NONE = u'none'
DIRECTION_LONG = u'long'
DIRECTION_SHORT = u'short'


class TickData(object):
    """Tick行情数据类"""

    def __init__(self):
        # 代码相关
        self.InstrumentID = EMPTY_STRING  # 合约代码

        # 成交数据
        self.LastPrice = EMPTY_FLOAT  # 最新成交价
        self.LastVolume = EMPTY_INT  # 最新成交量
        self.Volume = EMPTY_INT  # 今天总成交量
        self.OpenInterest = EMPTY_INT  # 持仓量
        self.Time = EMPTY_STRING  # 时间 11:20:56
        self.Milliseconds = EMPTY_STRING  # 时间 11:20:56
        self.TradingDay = EMPTY_STRING  # 日期 20151009
        self.Datetime = None  # python的datetime时间对象

        # 常规行情
        self.OpenPrice = EMPTY_FLOAT  # 今日开盘价
        self.HighestPrice = EMPTY_FLOAT  # 今日最高价
        self.LowestPrice = EMPTY_FLOAT  # 今日最低价
        self.PreClosePrice = EMPTY_FLOAT

        self.Turnover = EMPTY_FLOAT
        self.PreOpenInterest = EMPTY_INT
        self.PreSettlementPrice = EMPTY_FLOAT
        self.ClosePrice = EMPTY_FLOAT
        self.SettlementPrice = EMPTY_FLOAT
        self.PreDelta = EMPTY_FLOAT
        self.CurrDelta = EMPTY_FLOAT
        self.PreIOPV = EMPTY_FLOAT
        self.IOPV = EMPTY_FLOAT
        self.State = EMPTY_INT
        self.RecordDate = EMPTY_STRING
        self.RecordTime = EMPTY_STRING

        self.UpperLimitPrice = EMPTY_FLOAT  # 涨停价
        self.LowerLimitPrice = EMPTY_FLOAT  # 跌停价

        # 五档行情
        self.BidPrice1 = EMPTY_FLOAT
        self.BidPrice2 = EMPTY_FLOAT
        self.BidPrice3 = EMPTY_FLOAT
        self.BidPrice4 = EMPTY_FLOAT
        self.BidPrice5 = EMPTY_FLOAT
        self.BidPrice6 = EMPTY_FLOAT
        self.BidPrice7 = EMPTY_FLOAT
        self.BidPrice8 = EMPTY_FLOAT
        self.BidPrice9 = EMPTY_FLOAT
        self.BidPrice10 = EMPTY_FLOAT

        self.AskPrice1 = EMPTY_FLOAT
        self.AskPrice2 = EMPTY_FLOAT
        self.AskPrice3 = EMPTY_FLOAT
        self.AskPrice4 = EMPTY_FLOAT
        self.AskPrice5 = EMPTY_FLOAT
        self.AskPrice6 = EMPTY_FLOAT
        self.AskPrice7 = EMPTY_FLOAT
        self.AskPrice8 = EMPTY_FLOAT
        self.AskPrice9 = EMPTY_FLOAT
        self.AskPrice10 = EMPTY_FLOAT

        self.BidVolume1 = EMPTY_INT
        self.BidVolume2 = EMPTY_INT
        self.BidVolume3 = EMPTY_INT
        self.BidVolume4 = EMPTY_INT
        self.BidVolume5 = EMPTY_INT
        self.BidVolume6 = EMPTY_INT
        self.BidVolume7 = EMPTY_INT
        self.BidVolume8 = EMPTY_INT
        self.BidVolume9 = EMPTY_INT
        self.BidVolume10 = EMPTY_INT

        self.AskVolume1 = EMPTY_INT
        self.AskVolume2 = EMPTY_INT
        self.AskVolume3 = EMPTY_INT
        self.AskVolume4 = EMPTY_INT
        self.AskVolume5 = EMPTY_INT
        self.AskVolume6 = EMPTY_INT
        self.AskVolume7 = EMPTY_INT
        self.AskVolume8 = EMPTY_INT
        self.AskVolume9 = EMPTY_INT
        self.AskVolume10 = EMPTY_INT

        self.ProdId = EMPTY_STRING
        self.ExchId = EMPTY_STRING
        self.LineNumber = EMPTY_INT

    def from_taoli(self, dic):
        self.InstrumentID = dic["contractCode"]
        self.TradingDay = str(dic["date"])
        tm = str(dic["time"])
        if len(tm) == 8:
            tm = "0" + tm
        self.Time = tm[:2] + ":" + tm[2:4] + ":" + tm[4:6]
        self.Datetime = datetime.strptime(str(dic["date"] * 1000000000 + dic["time"]), "%Y%m%d%H%M%S%f")
        self.Milliseconds = dic["time"] % 1000
        self.PreClosePrice = float(dic["preClosePrice"])
        self.OpenPrice = float(dic["openPrice"])
        self.LastPrice = float(dic["lastPrice"])
        self.Volume = dic["totalVolume"]
        self.Turnover = float(dic["totalTurnover"])
        self.UpperLimitPrice = float(dic["upperLimitPrice"])
        self.LowerLimitPrice = float(dic["lowerLimitPrice"])
        self.AskPrice1 = float(dic["askPrice1"])
        self.BidPrice1 = float(dic["bidPrice1"])
        self.AskVolume1 = dic["askVolume1"]
        self.BidVolume1 = dic["bidVolume1"]
        self.AskPrice2 = float(dic["askPrice2"])
        self.BidPrice2 = float(dic["bidPrice2"])
        self.AskVolume2 = dic["askVolume2"]
        self.BidVolume2 = dic["bidVolume2"]
        self.AskPrice3 = float(dic["askPrice3"])
        self.BidPrice3 = float(dic["bidPrice3"])
        self.AskVolume3 = dic["askVolume3"]
        self.BidVolume3 = dic["bidVolume3"]
        self.AskPrice4 = float(dic["askPrice4"])
        self.BidPrice4 = float(dic["bidPrice4"])
        self.AskVolume4 = dic["askVolume4"]
        self.BidVolume4 = dic["bidVolume4"]
        self.AskPrice5 = float(dic["askPrice5"])
        self.BidPrice5 = float(dic["bidPrice5"])
        self.AskVolume5 = dic["askVolume5"]
        self.BidVolume5 = dic["bidVolume5"]
        return self

    @property
    def Instrument(self):
        return self.InstrumentID

    @property
    def PreClose(self):
        return self.PreClosePrice

    @property
    def BeijingDay(self):
        return self.RecordDate

    @property
    def BidPrice(self):
        # if 'BidPrice6' in dir(self):
        try:
            return [
                self.BidPrice1,
                self.BidPrice2,
                self.BidPrice3,
                self.BidPrice4,
                self.BidPrice5,
                self.BidPrice6,
                self.BidPrice7,
                self.BidPrice8,
                self.BidPrice9,
                self.BidPrice10,
            ]
        # else:
        except:
            return [
                self.BidPrice1,
                self.BidPrice2,
                self.BidPrice3,
                self.BidPrice4,
                self.BidPrice5,
            ]

    @property
    def AskPrice(self):
        # if 'AskPrice6' in dir(self):
        try:
            return [
                self.AskPrice1,
                self.AskPrice2,
                self.AskPrice3,
                self.AskPrice4,
                self.AskPrice5,
                self.AskPrice6,
                self.AskPrice7,
                self.AskPrice8,
                self.AskPrice9,
                self.AskPrice10,
            ]
        # else:
        except:
            return [
                self.AskPrice1,
                self.AskPrice2,
                self.AskPrice3,
                self.AskPrice4,
                self.AskPrice5,
            ]

    @property
    def BidVolume(self):
        try:
            # if 'BidVolume6' in dir(self):
            return [
                self.BidVolume1,
                self.BidVolume2,
                self.BidVolume3,
                self.BidVolume4,
                self.BidVolume5,
                self.BidVolume6,
                self.BidVolume7,
                self.BidVolume8,
                self.BidVolume9,
                self.BidVolume10,
            ]
        # else:
        except:
            return [
                self.BidVolume1,
                self.BidVolume2,
                self.BidVolume3,
                self.BidVolume4,
                self.BidVolume5,
            ]

    @property
    def AskVolume(self):
        try:
            # if 'AskVolume6' in dir(self):
            return [
                self.AskVolume1,
                self.AskVolume2,
                self.AskVolume3,
                self.AskVolume4,
                self.AskVolume5,
                self.AskVolume6,
                self.AskVolume7,
                self.AskVolume8,
                self.AskVolume9,
                self.AskVolume10,
            ]
        # else:
        except:
            return [
                self.AskVolume1,
                self.AskVolume2,
                self.AskVolume3,
                self.AskVolume4,
                self.AskVolume5,
            ]

    @property
    def UpdateTime(self):
        return '.'.join([self.Time, str(self.Milliseconds)])

    @property
    def TurnOver(self):
        return self.Turnover


class TradeData(object):
    """成交数据类"""

    def __init__(self):
        """Constructor"""
        # 代码编号相关
        self.symbol = EMPTY_STRING              # 合约代码
        self.tradeID = EMPTY_STRING             # 成交编号

        # 成交相关
        self.direction = EMPTY_UNICODE          # 成交方向
        self.price = EMPTY_FLOAT                # 成交价格
        self.volume = EMPTY_INT                 # 成交数量
        self.tradeTime = EMPTY_STRING           # 成交时间

    def __str__(self):
        return "time:{},symbol:{},direction:{},price:{},vol:{}".format(
            self.tradeTime, self.symbol, self.direction, self.price, self.volume
        )

    def __repr__(self):
        return "time:{},symbol:{},direction:{},price:{},vol:{}".format(
            self.tradeTime, self.symbol, self.direction, self.price, self.volume
        )


class BarData(object):
    """K线数据"""

    def __init__(self):
        """Constructor"""
        self.open = EMPTY_FLOAT             # OHLC
        self.high = EMPTY_FLOAT
        self.low = EMPTY_FLOAT
        self.close = EMPTY_FLOAT

        self.date = EMPTY_STRING            # bar开始的时间，日期
        self.time = EMPTY_STRING            # 时间
        self.Datetime = None                # python的datetime时间对象
        self.dt = EMPTY_FLOAT               # oadata

        self.volume = EMPTY_INT             # 成交量
        self.openInterest = EMPTY_INT       # 持仓量
        self.instrument = EMPTY_STRING
        self.amount = EMPTY_FLOAT

        self.is_finished = False
        self.is_started = False
        self.is_history = False

    @property
    def TradingDay(self):
        return self.Datetime.strftime("%Y%m%d")

    @property
    def Instrument(self):
        return self.instrument

    @property
    def DateTime(self):
        return self.dt

    @property
    def Open(self):
        return self.open

    @property
    def High(self):
        return self.high

    @property
    def Low(self):
        return self.low

    @property
    def Close(self):
        return self.close

    @property
    def Volume(self):
        return self.volume

    @property
    def Amount(self):
        return self.amount

    @property
    def OpenInterest(self):
        return self.openInterest

    @property
    def isFinished(self):
        if 'is_finished' in dir(self):
            return self.is_finished
        return True

    @property
    def isStarted(self):
        if 'is_started' in dir(self):
            return self.is_started
        return True

    @property
    def isHistory(self):
        if 'is_history' in dir(self):
            return self.is_history
        return True


def to_class(cl, r):
    c = cl()
    c.__dict__ = r
    return c


def load_history_data(symbol, start_date, end_date=None, data_path=None, cycle='tick'):
    md = []
    if cycle == 'tick':
        if str(symbol).startswith("0") or str(symbol).startswith("2") or \
                str(symbol).startswith("0") or str(symbol).startswith("3"):
            prod = "SZA"
            exch = "SZE"
        else:
            prod = "SHA"
            exch = "SSE"
        dt = datetime.strptime(start_date, '%Y%m%d')
        if end_date is None:
            endDt = dt
        else:
            endDt = datetime.strptime(end_date, '%Y%m%d')
        print("开始加载博睿数据")
        while dt <= endDt:
            if ts.is_holiday(dt.strftime("%Y-%m-%d")):
                dt = dt + timedelta(days=1)
                continue
            mdfile = "{}/{}/{}/{}/tick/{}.csv".format(data_path, exch, prod, dt.strftime("%Y%m%d"), symbol)
            if not os.path.exists(mdfile):
                print("{} 文件不存在".format(mdfile))
                continue
            md = pd.read_csv(
                mdfile,
                dtype={
                    'InstrumentID': object},
                skipinitialspace=True)
            md["Datetime"] = md.apply(
                lambda r: datetime.strptime(
                    "{} {}.{:03d}".format(
                        r['TradingDay'],
                        r['Time'],
                        r['Milliseconds']),
                    '%Y%m%d %H:%M:%S.%f'),
                axis=1)
            md.extend(md.apply(lambda r: to_class(TickData, r.to_dict()), axis=1).values)
            dt = dt + timedelta(days=1)
        print("加载结束")
    else:
        import scipy.io as scio
        if cycle == 'day':
            data = scio.loadmat("{}/{}/{}.mat".format(data_path, cycle, symbol))
            data = data['data']
            for i in range(len(data)):
                if data[i, 0] < int(start_date) or data[i, 0] > int(end_date):
                    continue
                bar = BarData()
                bar.instrument = symbol
                bar.date = str(int(data[i, 0]))
                bar.time = "09:00:00"
                day = int(data[i, 0])
                bar.Datetime = datetime(day // 10000, day % 10000 // 100, day % 100)
                bar.open = data[i, 1]
                bar.high = data[i, 2]
                bar.low = data[i, 3]
                bar.close = data[i, 4]
                bar.volume = data[i, 5]
                bar.amount = data[i, 6]
                md.append(bar)
        else:
            data = scio.loadmat("{}/{}/{}.mat".format(data_path, "60", symbol))
            data = data['data']
            for i in range(len(data)):
                if data[i, 0] < int(start_date) or data[i, 0] > int(end_date):
                    continue
                bar = BarData()
                bar.instrument = symbol
                bar.date = str(data[i, 0])
                if data[i, 1] < 960:
                    bar.time = "0" + str(data[i, 1] // 100) + ":" + str(data[i, 1]) + ":00"
                else:
                    bar.time = str(data[i, 1] // 100) + ":" + str(data[i, 1]) + ":00"
                day = int(data[i, 0])
                tm = int(data[i, 1])
                bar.Datetime = datetime(day // 10000, day % 10000 // 100, day % 100, tm // 100, tm % 100)
                bar.open = data[i, 2]
                bar.high = data[i, 3]
                bar.low = data[i, 4]
                bar.close = data[i, 5]
                bar.volume = data[i, 6]
                bar.amount = data[i, 7]
                md.append(bar)
    return md


def convert_to_double_datetime(dt):
    dlt = dt - datetime(1899, 12, 30)
    return dlt.total_seconds() / 86400.0


def generate_kline(tick, k):
    from datetime import time
    freq = str(k) + "S"
    tick1 = tick[["InstrumentID", 'Datetime', 'LastPrice', 'Volume']]
    tick1 = tick1.set_index('Datetime')
    # tick0 = tick1['LastPrice'].resample(freq).ohlc().ffill()
    # tick0['volume'] = tick1['Volume'].resample(freq).sum().ffill()
    tick0 = tick1['LastPrice'].resample(freq).ohlc()
    tick0['volume'] = tick1['Volume'].resample(freq).sum()
    tick0['instrument'] = tick["InstrumentID"][0]
    tick0['Datetime'] = tick0.index
    tick0['datetime'] = tick0.apply(
        lambda r: convert_to_double_datetime(
            r['Datetime']), axis=1)
    tick0['time'] = tick0.apply(lambda r: r.Datetime.time(), axis=1)
    tick0 = tick0.dropna()
    tick0 = tick0[(0.000001 < tick0["high"]) & (0.000001 < tick0["open"])]
    tick0 = tick0[(time(9,30) <= tick0["time"])]
    # tick0 = tick0[((time(21) <= tick0["time"]) & (tick0["time"] <= time(23))) |
    #               ((time(9) <= tick0["time"]) & (tick0["time"] <= time(10, 15))) |
    #               ((time(10, 30) <= tick0["time"]) & (tick0["time"] <= time(11, 30))) |
    #               ((time(13, 30) <= tick0["time"]) & (tick0["time"] <= time(15)))]
    return tick0
