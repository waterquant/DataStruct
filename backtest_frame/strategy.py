# -*- coding: utf-8 -*-


class BaseStrategy(object):

    # 策略的基本变量，由引擎管理
    inited = False                 # 是否进行了初始化
    engine = None
    dicParams = {}

    def __init__(self):
        pass

    def set_params(self, engine, setting=None):
        self.engine = engine
        self.dicParams = setting
        pass

    def on_init(self):
        self.his_init(self.dicParams)

    def his_init(self,  parameters):
        pass

    def on_tick(self, tick):
        pass

    def on_bar(self, tick):
        pass

    def logout(self, str):
        self.engine.writeLog(str)
        pass

    def buy(self, instrument, price, volume):
        return self.engine.sendOrder(instrument, 'buy', price, volume)

    def sell(self, instrument, price, volume):
        return self.engine.sendOrder(instrument, 'sell', price, volume)
