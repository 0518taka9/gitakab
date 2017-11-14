#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import Const
import sys
from bitflyer import *

API_KEY = ""
API_SECRET = ""

class Manager:
    MARGIN = 0.000001

    def __init__(self):
        """
        初期設定
        """

        """logのデータでシミュレート"""
        # self.count = 0
        # self.load()

        """実際のチャートでシミュレート"""
        self.api = BitflyerAPI("", "")
        self.product = Product.BTC_FX
        self.act = Const.ACT_STAY
        self.last_id = 0

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

        """logのデータでシミュレート"""
        # last = self.data[self.count][0]     # 終値
        # average = self.data[self.count][1]  # 平均値
        # amount = self.data[self.count][2]   # 取引量
        #
        # self.count += 1
        # if self.count == len(self.data):
        #     sys.exit()

        """実際のチャートでシミュレート"""

        # 約定履歴を取得
        trades = self.api.get_executions(self.product)

        s_price = 0  # 価格 * 取引数量の総和
        s_amount = 0  # 取引数量の総和

        for trade in trades:
            price = float(trade['price'])
            amount = float(trade['size'])
            trade_id = trade['id']

            # trade_idがlast_idならループを抜ける
            if self.last_id == trade_id:
                break

            s_price += price * amount
            s_amount += amount

        # last_idを設定
        if len(trades) > 0:
            self.last_id = trades[0]['id']

        # priceを設定
        if s_amount == 0:
            self.average = self.getLastPrice()
        else:
            self.average = s_price / s_amount

        last = self.getLastPrice()
        average = self.average
        amount = 0

        losscut = False

        return (last, average, amount, losscut)

    def getLastPrice(self):
        """
        現在の終値を返す。
        :return: 現在の終値
        """
        return float(self.api.get_ticker(self.product)['ltp'])

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

        """logのデータでシミュレート"""
        # price = self.data[self.count][1]

        """実際のチャートでシミュレート"""
        price = self.average

        if action == Const.ACT_ASK:
            price *= 1 + self.MARGIN
            return price

        if action == Const.ACT_BID:
            price *= 1 - self.MARGIN
            return price

        sys.exit()
