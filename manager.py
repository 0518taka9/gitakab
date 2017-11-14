#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import Const
import sys
from bitflyer import *


class Manager:
    MARGIN = 0.0001

    def __init__(self):
        self.count = 0
        self.load()
#        self.api = BitflyerAPI("", "")
#        self.product = Product.BTC_FX

    def load(self):
        self.data = []

        f = open('log/log.txt', 'r')
        for line in f:
            data = eval(line)
            self.data.append(data)
        f.close()

    def tick(self):
        """
        価格、数量、ロスカットを設定する。
        Traderのtickで呼び出される。
        ロスカット未実装
        :return: 平均値、取引量、ロスカットするかどうか
        """

        last = self.data[self.count][0]     # 終値
        average = self.data[self.count][1]  # 平均値
        amount = self.data[self.count][2]   # 取引量

        losscut = False

        self.count += 1
        if self.count == len(self.data):
            sys.exit()

#        average = float(self.api.get_ticker(self.product)['ltp'])
#        amount = 0.1

        return (last, average, amount, losscut)

    def sendOrder(self, action, amount):
        """
        シミュレーション用
        アクションと数量を渡し, 成行注文で注文を発行する。
        指値は未実装。
        
        Traderのtickで呼び出される。
        :param action: 
        :param amount: 
        :return: 
        """
        price = self.data[self.count][1]

        if action == Const.ACT_ASK:
            price *= 1 + self.MARGIN
            return price

        if action == Const.ACT_BID:
            price *= 1 - self.MARGIN
            return price

        sys.exit()

        # return float(self.api.get_ticker(self.product)['ltp'])
