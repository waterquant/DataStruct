# encoding: UTF-8

from __future__ import division

import multiprocessing
from collections import OrderedDict
from itertools import product
import copy

from data import *
import math
import json

current_path = os.path.split(os.path.realpath(__file__))[0]


class BacktestEngine(object):
    mode = 'bar'

    def __init__(self, data, rate=0.0002, slip=0, log_path=current_path):
        self.slippage = slip
        self.rate = rate
        self.log_path = log_path

        # 回测相关
        self.strategy = None        # 回测策略

        self.tradeCount = 0             # 成交编号
        self.tradeDict = OrderedDict()  # 成交字典
        
        self.logList = []               # 日志记录
        
        # 当前最新数据，用于模拟成交用
        self.md = data
        self.datetime = data[0].Datetime
        self.param_id = 0

    def play(self):
        md_idx = 0
        md_len = len(self.md)

        while md_idx < md_len:
            if md_idx < md_len:
                md = self.md[md_idx]
                self.datetime = md.Datetime
                md_idx += 1
                if self.mode == 'tick':
                    self.strategy.on_tick(md)
                else:
                    self.strategy.on_bar(md)

    def runBacktesting(self):
        """运行回测"""
        self.clearBacktestingResult()
        self.output(u'开始回测')
        
        self.strategy.inited = True
        self.strategy.on_init()
        self.output(u'策略初始化完成, 开始回放数据')
        self.play()
        self.output(u'数据回放结束')

        if True:
            logFile = "{}/log/{}-{}.log".format(self.log_path, self.param_id, datetime.now().strftime("%Y%m%d-%H%M%S"))
            if not os.path.exists(self.log_path + "/log"):
                os.mkdir(self.log_path + "/log")
            with open(logFile, 'w') as f:
                f.write("\n".join(self.logList))
                pass

    def initStrategy(self, strategyClass, setting=None):
        if setting is not None and "param_id" in setting:
            self.param_id = setting["param_id"]
        self.strategy = strategyClass()
        self.strategy.set_params(self, setting)

    def sendOrder(self, symbol, orderType, price, volume):
        self.tradeCount += 1            # 成交编号自增1
        tradeID = str(self.tradeCount)
        trade = TradeData()
        trade.symbol = symbol
        trade.tradeID = tradeID
        trade.direction = DIRECTION_LONG if orderType == 'buy' else DIRECTION_SHORT
        trade.price = price

        trade.volume = volume
        trade.tradeTime = self.datetime

        self.tradeDict[tradeID] = trade

        return tradeID

    def writeLog(self, content):
        """记录日志"""
        log = ' '.join([str(self.datetime), content])
        self.logList.append(log)
        
    def output(self, content):
        """输出内容"""
        print("{}\t参数组：{} {}".format(datetime.now(), self.param_id, content))

    def clearBacktestingResult(self):
        """清空之前回测的结果"""
        self.tradeCount = 0
        self.tradeDict.clear()

    def calculateBacktestingResult(self):
        """
        计算回测结果
        """
        trdList = [v for v in self.tradeDict.values()]
        self.output(u'计算回测结果')
        return CalculateTradeList1(trdList, self.rate, self.slippage)

    def showBacktestingResult(self):
        """显示回测结果"""
        d = self.calculateBacktestingResult()
        if not d:
            return
        ShowBacktestingResult(d)

    def printTradeList(self, d):
        for trade in d['tradeList']:
            print(trade.symbol, trade.tradeTime, trade.direction, trade.price, trade.volume)

    def roundToPriceTick(self, symbol, price):
        newPrice = round(price, 2)
        return newPrice


class Optimization:
    def __init__(self, data, rate=0.0002, slip=0, log_path=current_path):
        self.slippage = slip
        self.rate = rate
        self.data = data
        self.log_path = log_path

    def output(self, content):
        """输出内容"""
        print(str(datetime.now()) + "\t" + content)

    def runOptimization(self, strategyClass, optimizationSetting, num_core=1):
        """并行优化参数"""
        # 获取优化设置
        settingList = optimizationSetting.generateSetting()
        targetName = optimizationSetting.optimizeTarget

        # 检查参数设置问题
        if not settingList or not targetName:
            self.output(u'优化设置有问题，请检查')
            return

        # 多进程优化，启动一个对应CPU核心数量的进程池
        pool = multiprocessing.Pool(min([multiprocessing.cpu_count(), num_core]))
        l = []

        for setting in settingList:
            l.append(pool.apply_async(optimize, (strategyClass, setting,
                                                 targetName, self.data,
                                                 self.slippage, self.rate,
                                                 self.log_path)))
        pool.close()
        pool.join()

        # 显示结果
        resultList = [res.get() for res in l]
        resultList.sort(reverse=True, key=lambda result:result[1])
        self.output('-' * 30)
        self.output(u'优化结果：')
        for result in resultList:
            self.output(u'%s: %s' %(result[0], result[1]))

        logFile = "{}/result/{}.res".format(self.log_path, datetime.now().strftime("%Y%m%d-%H%M%S"))
        if not os.path.exists(self.log_path+ "/result"):
            os.mkdir(self.log_path + "/result")
        with open(logFile, 'w') as f:
            f.write(json.dumps(resultList, cls=UserEncoder, indent=2))
        return resultList

    def runRollStepParallelOptimization(self, strategyClass, optimizationSetting):
        allSteps = optimizationSetting.getSteps()
        keep = optimizationSetting.keep
        lastStep = None

        stepResult = OrderedDict()
        for s in allSteps:
            # 获取优化设置
            self.output("".join(('-' * 10, "step=", str(s), "-" * 10)))
            settingList = optimizationSetting.generateSettingOneStep(s, lastStep)
            if len(settingList) <= 0:
                stepResult[s] = stepResult[lastStep]
                lastStep = s
                continue
            targetName = optimizationSetting.optimizeTarget

            # 多进程优化，启动一个对应CPU核心数量的进程池
            numProcess = min(multiprocessing.cpu_count(), len(settingList))
            # pool = multiprocessing.Pool(multiprocessing.cpu_count())
            pool = multiprocessing.Pool(numProcess)
            l = []

            for setting in settingList:
                l.append(pool.apply_async(optimize, (strategyClass, setting,
                                                     targetName, self.data,
                                                     self.slippage, self.rate,
                                                     self.log_path)))
            pool.close()
            pool.join()

            # 显示结果
            resultList = [res.get() for res in l] + optimizationSetting.getStepOptResult(lastStep)
            resultList.sort(reverse=True, key=lambda result: result[1])
            self.output(u'%s: %s' % (resultList[0][0], resultList[0][1]))

            if keep < 1:
                keepN = math.ceil(len(resultList) * keep)
            else:
                keepN = keep

            optimizationSetting.setStepOptResult(s, resultList[0:keepN])
            stepResult[s] = resultList[0:keepN]
            lastStep = s
        logFile = "{}/result/{}.res".format(self.log_path, datetime.now().strftime("%Y%m%d-%H%M%S"))
        if not os.path.exists(self.log_path + "/result"):
            os.mkdir(self.log_path + "/result")
        with open(logFile, 'w') as f:
            f.write(json.dumps(stepResult, cls=UserEncoder, indent=2))
        return stepResult


class TradingResult(object):
    """每笔交易的结果"""

    def __init__(self, entryPrice, entryDt, exitPrice,
                 exitDt, volume, rate, slippage):
        """Constructor"""
        self.entryPrice = entryPrice    # 开仓价格
        self.exitPrice = exitPrice      # 平仓价格
        
        self.entryDt = entryDt          # 开仓时间datetime    
        self.exitDt = exitDt            # 平仓时间
        
        self.volume = volume    # 交易数量（+/-代表方向）
        
        self.turnover = (self.entryPrice+self.exitPrice)*abs(volume)   # 成交金额
        self.commission = self.turnover*rate                                # 手续费成本
        self.slippage = 0.01*slippage*2*abs(volume)                         # 滑点成本
        self.pnl = ((self.exitPrice - self.entryPrice) * volume
                    - self.commission - self.slippage)                      # 净盈亏

    def __str__(self):
        return "entryPrice:{0},exitPrice:{1},entryDT:{2},exitDT:{3},vol:{4},turnover:{5:.3f},commission:{6:.3f},slip:{7:.3f},pnl:{8:.3f}".format(
            self.entryPrice, self.exitPrice, self.entryDt,
            self.exitDt, self.volume, self.turnover, self.commission,
            self.slippage, self.pnl
        )

    def __repr__(self):
        return "entryPrice:{0},exitPrice:{1},entryDT:{2},exitDT:{3},vol:{4},turnover:{5:.3f},commission:{6:.3f},slip:{7:.3f},pnl:{8:.3f}".format(
            self.entryPrice, self.exitPrice, self.entryDt,
            self.exitDt, self.volume, self.turnover, self.commission,
            self.slippage, self.pnl
        )


class OptimizationSetting(object):
    """优化设置"""

    def __init__(self):
        """Constructor"""
        self.paramDict = OrderedDict()
        self.optimizeDict = OrderedDict()
        self.paramDefaultDict = OrderedDict()
        self.paramOptStepDict = OrderedDict()
        self.stepList = []
        self.paramStepOptResultDict = OrderedDict()
        self.keep = 5
        self.hadRunSetting = []

        self.optimizeTarget = ''        # 优化目标字段

    def addOptimizeDic(self, paraOrderedDict):
        self.optimizeDict = paraOrderedDict

    def getOptimizeParaList(self):
        return self.optimizeDict.keys()

    def setOptimizedParam(self, paraName, value):
        self.optimizeDict[paraName] = value

    def getParamValueLen(self, para):
        return len(self.paramDict[para])

    def addParameterList(self, name, valueList):
        """增加优化参数"""
        if not isinstance(valueList, list):
            self.paramDict[name] = [valueList]

        if len(valueList) <= 0:
            print(u'参数列表为空')
            return

        self.paramDict[name] = valueList

    def addParameter(self, name, start, end=None, step=None):
        """增加优化参数"""
        if end is None and step is None:
            self.paramDict[name] = [start]
            return 
        
        if end < start:
            print(u'参数起始点必须不大于终止点')
            return
        
        if step <= 0:
            print(u'参数布进必须大于0')
            return
        
        l = []
        param = start
        
        while param <= end:
            l.append(param)
            param += step
        
        self.paramDict[name] = l
        
    def generateSetting(self):
        """生成优化参数组合"""
        # 参数名的列表
        nameList = self.paramDict.keys()
        paramList = self.paramDict.values()
        
        # 使用迭代工具生产参数对组合
        productList = list(product(*paramList))
        
        # 把参数对组合打包到一个个字典组成的列表中
        settingList = []
        id = 0
        for p in productList:
            d = dict(zip(nameList, p))
            d["param_id"]=id
            id += 1
            settingList.append(d)
    
        return settingList

    def generateSettingOneParam(self, param):
        """生成优化参数组合"""
        # 把参数对组合打包到一个个字典组成的列表中
        settingList = []
        id = 0
        for v in self.paramDict[param]:
            self.optimizeDict[param] = v
            self.optimizeDict["param_id"]=id
            id += 1
            settingList.append(self.optimizeDict)

        return settingList

    def setOptimizeTarget(self, target):
        """设置优化目标字段"""
        self.optimizeTarget = target

    def addParam(self, name, default, opt_step=0, valueList=None):
        """增加优化参数"""
        if valueList is None:
            self.paramDict[name] = [default]
        elif not isinstance(valueList, list):
            self.paramDict[name] = [valueList]
        else:
            self.paramDict[name] = valueList

        self.paramDefaultDict[name] = default
        self.stepList.append(opt_step)
        self.stepList = list(set(self.stepList))
        self.stepList.sort()
        if opt_step in self.paramOptStepDict.keys():
            self.paramOptStepDict[opt_step].append(name)
        else:
            self.paramOptStepDict[opt_step] = list()
            self.paramOptStepDict[opt_step].append(name)

    def setDefaultKeep(self, k):
        self.keep = k

    def setStepOptResult(self, step, optResult):
        """生成优化参数组合"""
        self.paramStepOptResultDict[step] = optResult

    def getStepOptResult(self, step):
        """生成优化参数组合"""
        if step is None:
            return []
        return self.paramStepOptResultDict[step]

    def clearStepOptResult(self):
        """生成优化参数组合"""
        self.paramStepOptResultDict.clear()
        self.hadRunSetting.clear()

    def getSteps(self):
        """生成优化参数组合"""
        return self.stepList

    def generateSettingOneStep(self, step, lastStep):
        """生成优化参数组合"""
        settingList = []
        id = 0
        for pn in self.paramOptStepDict[step]:
            for p in self.paramDict[pn]:
                if lastStep in self.paramStepOptResultDict.keys():
                    for s in self.paramStepOptResultDict[lastStep]:
                        sc = copy.deepcopy(eval(s[0]))
                        sc[pn] = p
                        key = "".join([str(v) for v in sc.values()])
                        if key not in self.hadRunSetting:
                            self.hadRunSetting.append(key)
                            sc["param_id"]=id
                            id += 1
                            settingList.append(sc)
                else:
                    sc = copy.deepcopy(self.paramDefaultDict)
                    sc[pn] = p
                    key = "".join([str(v) for v in sc.values()])
                    if key not in self.hadRunSetting:
                        self.hadRunSetting.append(key)
                        sc["param_id"]=id
                        id += 1
                        settingList.append(sc)

        return settingList


def optimize(strategyClass, setting, targetName, data,
             slippage=0, rate=0.0002, log_path=current_path):
    """多进程优化时跑在每个进程中运行的函数"""
    engine = BacktestEngine(data, rate, slippage, log_path)

    engine.initStrategy(strategyClass, setting)
    engine.runBacktesting()
    d = engine.calculateBacktestingResult()
    try:
        targetValue = d[targetName]
    except KeyError:
        targetValue = 0            
    return (str(setting), targetValue, d)


def CalculateTradeList1(tradeList, rate, slippage):
    """
    计算回测结果
    """
    # 首先基于回测后的成交记录，计算每笔交易的盈亏
    resultList = []             # 交易结果列表

    longTrade = {}              # 未平仓的多头交易
    shortTrade = {}             # 未平仓的空头交易

    tradeTimeList = []          # 每笔成交时间戳
    posList = [0]               # 每笔成交后的持仓情况
    tdList = copy.deepcopy(tradeList)

    for trade in tdList:
        # 多头交易
        if trade.direction == DIRECTION_LONG:
            # 如果尚无空头交易
            if not shortTrade or trade.symbol not in shortTrade.keys() or len(shortTrade[trade.symbol]) <= 0:
                if trade.symbol not in longTrade.keys():
                    longTrade[trade.symbol] = []
                    longTrade[trade.symbol].append(trade)
                else:
                    longTrade[trade.symbol].append(trade)
            # 当前多头交易为平空
            else:
                while True:
                    entryTrade = shortTrade[trade.symbol][0]
                    exitTrade = trade

                    # 清算开平仓交易
                    closedVolume = min(exitTrade.volume, entryTrade.volume)
                    result = TradingResult(entryTrade.price, entryTrade.tradeTime,
                                           exitTrade.price, exitTrade.tradeTime,
                                           -closedVolume, rate, slippage)
                    resultList.append(result)

                    posList.extend([-1, 0])
                    tradeTimeList.extend([result.entryDt, result.exitDt])

                    # 计算未清算部分
                    entryTrade.volume -= closedVolume
                    exitTrade.volume -= closedVolume

                    # 如果开仓交易已经全部清算，则从列表中移除
                    if not entryTrade.volume:
                        shortTrade[trade.symbol].pop(0)

                    # 如果平仓交易已经全部清算，则退出循环
                    if not exitTrade.volume:
                        break

                    # 如果平仓交易未全部清算，
                    if exitTrade.volume:
                        # 且开仓交易已经全部清算完，则平仓交易剩余的部分
                        # 等于新的反向开仓交易，添加到队列中
                        if not shortTrade:
                            longTrade[trade.symbol].append(exitTrade)
                            break
                        # 如果开仓交易还有剩余，则进入下一轮循环
                        else:
                            pass

        # 空头交易
        else:
            # 如果尚无多头交易
            if not longTrade or trade.symbol not in longTrade.keys() or len(longTrade[trade.symbol]) <= 0:
                if trade.symbol not in shortTrade.keys():
                    shortTrade[trade.symbol] = []
                    shortTrade[trade.symbol].append(trade)
                else:
                    shortTrade[trade.symbol].append(trade)
            # 当前空头交易为平多
            else:
                while True:
                    entryTrade = longTrade[trade.symbol][0]
                    exitTrade = trade

                    # 清算开平仓交易
                    closedVolume = min(exitTrade.volume, entryTrade.volume)
                    result = TradingResult(entryTrade.price, entryTrade.tradeTime,
                                           exitTrade.price, exitTrade.tradeTime,
                                           closedVolume, rate, slippage)
                    resultList.append(result)

                    posList.extend([1, 0])
                    tradeTimeList.extend([result.entryDt, result.exitDt])

                    # 计算未清算部分
                    entryTrade.volume -= closedVolume
                    exitTrade.volume -= closedVolume

                    # 如果开仓交易已经全部清算，则从列表中移除
                    if not entryTrade.volume:
                        longTrade[trade.symbol].pop(0)
                        if len(longTrade[trade.symbol]) <= 0:
                            break

                    # 如果平仓交易已经全部清算，则退出循环
                    if not exitTrade.volume:
                        break

                    # 如果平仓交易未全部清算，
                    if exitTrade.volume:
                        # 且开仓交易已经全部清算完，则平仓交易剩余的部分
                        # 等于新的反向开仓交易，添加到队列中
                        if not longTrade:
                            shortTrade[trade.symbol].append(exitTrade)
                            break
                        # 如果开仓交易还有剩余，则进入下一轮循环
                        else:
                            pass

                            # 检查是否有交易
    if not resultList:
        print(u'无交易结果')
        return {}

    # 然后基于每笔交易的结果，我们可以计算具体的盈亏曲线和最大回撤等
    capital = 0             # 资金
    maxCapital = 0          # 资金最高净值
    drawdown = 0            # 回撤

    totalResult = 0         # 总成交数量
    totalTurnover = 0       # 总成交金额（合约面值）
    totalCommission = 0     # 总手续费
    totalSlippage = 0       # 总滑点

    timeList = []           # 时间序列
    pnlList = []            # 每笔盈亏序列
    capitalList = []        # 盈亏汇总的时间序列
    drawdownList = []       # 回撤的时间序列

    winningResult = 0       # 盈利次数
    losingResult = 0        # 亏损次数
    totalWinning = 0        # 总盈利金额
    totalLosing = 0         # 总亏损金额

    for result in resultList:
        capital += result.pnl
        maxCapital = max(capital, maxCapital)
        drawdown = capital - maxCapital

        pnlList.append(result.pnl)
        timeList.append(result.exitDt)      # 交易的时间戳使用平仓时间
        capitalList.append(capital)
        drawdownList.append(drawdown)

        totalResult += 1
        totalTurnover += result.turnover
        totalCommission += result.commission
        totalSlippage += result.slippage

        if result.pnl >= 0:
            winningResult += 1
            totalWinning += result.pnl
        else:
            losingResult += 1
            totalLosing += result.pnl

    # 计算盈亏相关数据
    winningRate = winningResult/totalResult*100         # 胜率

    averageWinning = 0                                  # 这里把数据都初始化为0
    averageLosing = 0
    profitLossRatio = 0

    if winningResult:
        averageWinning = totalWinning/winningResult     # 平均每笔盈利
    if losingResult:
        averageLosing = totalLosing/losingResult        # 平均每笔亏损
    if averageLosing:
        profitLossRatio = -averageWinning/averageLosing # 盈亏比

    # 返回回测结果
    d = {}
    d['capital'] = capital
    d['maxCapital'] = maxCapital
    d['drawdown'] = drawdown
    d['totalResult'] = totalResult
    d['totalTurnover'] = totalTurnover
    d['totalCommission'] = totalCommission
    d['totalSlippage'] = totalSlippage
    d['timeList'] = timeList
    d['pnlList'] = pnlList
    d['capitalList'] = capitalList
    d['drawdownList'] = drawdownList
    d['winningRate'] = winningRate
    d['averageWinning'] = averageWinning
    d['averageLosing'] = averageLosing
    d['profitLossRatio'] = profitLossRatio
    d['posList'] = posList
    d['tradeTimeList'] = tradeTimeList
    d['tradeList'] = list(tradeList)
    d['tradeResultList'] = list(resultList)

    return d


def formatNumber(n):
    """格式化数字到字符串"""
    rn = round(n, 2)        # 保留两位小数
    return format(rn, ',')  # 加上千分符


def ShowBacktestingResult(d):
    """显示回测结果"""
    if not isinstance(d, dict) or d == {}:
        return

    # 输出
    print('-' * 30)
    print(u'第一笔交易：\t%s' % d['timeList'][0])
    print(u'最后一笔交易：\t%s' % d['timeList'][-1])

    print(u'总交易次数：\t%s' % formatNumber(d['totalResult']))
    print(u'总盈亏：\t%s' % formatNumber(d['capital']))
    print(u'最大回撤: \t%s' % formatNumber(min(d['drawdownList'])))

    print(u'平均每笔盈利：\t%s' %formatNumber(d['capital']/d['totalResult']))
    print(u'平均每笔滑点：\t%s' %formatNumber(d['totalSlippage']/d['totalResult']))
    print(u'平均每笔佣金：\t%s' %formatNumber(d['totalCommission']/d['totalResult']))

    print(u'胜率\t\t%s%%' %formatNumber(d['winningRate']))
    print(u'盈利交易平均值\t%s' %formatNumber(d['averageWinning']))
    print(u'亏损交易平均值\t%s' %formatNumber(d['averageLosing']))
    print(u'盈亏比：\t%s' %formatNumber(d['profitLossRatio']))

    # 绘图
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        import seaborn as sns       # 如果安装了seaborn则设置为白色风格
        sns.set_style('whitegrid')
    except ImportError:
        pass

    pCapital = plt.subplot(4, 1, 1)
    pCapital.set_ylabel("capital")
    pCapital.plot(d['capitalList'], color='r', lw=0.8)

    pDD = plt.subplot(4, 1, 2)
    pDD.set_ylabel("DD")
    pDD.bar(range(len(d['drawdownList'])), d['drawdownList'], color='g')

    pPnl = plt.subplot(4, 1, 3)
    pPnl.set_ylabel("pnl")
    pPnl.hist(d['pnlList'], bins=50, color='c')

    pPos = plt.subplot(4, 1, 4)
    pPos.set_ylabel("Position")
    if d['posList'][-1] == 0:
        del d['posList'][-1]
    tradeTimeIndex = [item.strftime("%m/%d %H:%M:%S") for item in d['tradeTimeList']]
    xindex = np.arange(0, len(tradeTimeIndex), np.int(len(tradeTimeIndex) / 10) or 1)
    tradeTimeIndex = list(map(lambda i: tradeTimeIndex[i], xindex))
    pPos.plot(d['posList'], color='k', drawstyle='steps-pre')
    pPos.set_ylim(-1.2, 1.2)
    plt.sca(pPos)
    plt.tight_layout()
    plt.xticks(xindex, tradeTimeIndex, rotation=30)  # 旋转15

    plt.show()


class UserEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TradeData):
            # return obj.__str__()
            return obj.__dict__
        elif isinstance(obj, TradingResult):
            # return obj.__str__()
            return obj.__dict__
        elif isinstance(obj, datetime):
            return obj.__str__()

        return json.JSONEncoder.default(self, obj)

