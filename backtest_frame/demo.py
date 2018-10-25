# -*- coding: utf-8 -*-
from strategy import BaseStrategy


class DemoStrategy(BaseStrategy):

    def __init__(self):
        super(DemoStrategy, self).__init__()

        self.dt = None
        self.tick_cnt = 0
        self.input = 50
        self.out = 550
        pass

    def his_init(self,  parameters):
        self.input = int(parameters['testParam1'])
        self.out = int(parameters['testParam2'])
        self.logout("hist_init")
        pass

    def on_tick(self, tick):
        self.dt = tick.Datetime
        if tick.LastPrice < 0.00001:
            return
        self.tick_cnt += 1
        # print("{} {} tick".format(self.tick_cnt, self.dt))
        if self.tick_cnt == self.input:
            self.buy(tick.Instrument, tick.LastPrice, 100)
        if self.tick_cnt == self.out:
            self.sell(tick.Instrument, tick.LastPrice, 100)
        pass

    def on_bar(self, bar):
        self.dt = bar.Datetime
        if bar.open < 0.00001:
            return
        self.tick_cnt += 1
        # print("{} {} tick".format(self.tick_cnt, self.dt))
        if self.tick_cnt == self.input:
            self.buy(bar.Instrument, bar.open, 100)
        if self.tick_cnt == self.out:
            self.sell(bar.Instrument, bar.open, 100)


if __name__ == '__main__':
    # 创建回测引擎
    from data import load_history_data
    from backtest import BacktestEngine, Optimization, OptimizationSetting
    import numpy as np
    ticks = load_history_data("SH600000", '20180212', '20180712', data_path="E:\\hdata", cycle='60')
    # BacktestEngine.mode = 'tick'  # or 'bar'
    BacktestEngine.mode = 'bar'  # or 'bar'

    # 进行单次回测
    if True:
        engine = BacktestEngine(ticks, slip=1, rate=0.0007)

        # 在引擎中创建策略对象
        d = {"testParam1": 50,
             "testParam2": 1450}

        engine.initStrategy(DemoStrategy, d)

        # 开始跑回测
        engine.runBacktesting()

        # 打印日志
        # fp = "test.log"
        # f = open(fp, "w")
        # for log in engine.logList:
        #     f.write(log+'\n')
        # f.close()

        # # 显示回测结果
        engine.showBacktestingResult()

        d = engine.calculateBacktestingResult()
        if d:
            engine.printTradeList(d)
    else:
        opt = Optimization(ticks, slip=0, rate=0.0007)
        setting = OptimizationSetting()  # 新建一个优化任务设置对象
        setting.setOptimizeTarget('capital')  # 设置优化排序的目标是策略净盈利
        setting.addParam('testParam1', 50)
        setting.addParam('testParam2', 450, 1, np.arange(100, 800, 100).tolist())
        setting.setDefaultKeep(3)

        opt.runOptimization(DemoStrategy, setting, 2)

        # 参数优化
        pass
