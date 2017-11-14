#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt
from lib import Const, Sequence
import time


#################################
#  バンドが拡大した際に買い、    ####
#  一度上回った線(0.9σ, 1.8σ) ####
#	を下回ったら売る             ####
#################################

class BollingerAgent:
    N_CURVE = 8
    WIDTH = 100

    STATE_STAY = 0
    STATE_ASK = 1
    STATE_BID = 2

    NAN_ACHIEVED = -10

    def __init__(self, L, B, K, M, P, I, LOSSCUT):
        self.priceSeq = Sequence(L)
        self.averageCurve = Sequence(L)
        self.bandWidth = Sequence(L)

        self.isActive = False
        self.state = self.STATE_STAY
        self.achieved = self.NAN_ACHIEVED

        self.inter_count = 0

        self.price = 0

        self.L = L
        self.B = B
        self.K = K
        self.M = M
        self.amountSeq = Sequence(P)
        self.I = I
        self.LOSSCUT = LOSSCUT

    def drawerInfo(self):
        return (self.N_CURVE, self.WIDTH)

    def reset(self):
        self.state = self.STATE_STAY

    def tick(self, price, amount, active):
        # 価格指標の計算
        pre_amount = self.amountSeq.summarize(lambda x: x)

        if pre_amount + amount != 0:
            k = self.K * amount / (pre_amount + amount)
            self.price = self.price * (1 - k) + price * k

        self.amountSeq.append(amount)

        self.inter_count += 1

        if self.inter_count == self.I:
            self.inter_count = 0
            return self.decide(active)
        else:
            return (Const.ACT_STAY, None)

    def getPrice(self):
        return self.price

    def decide(self, active):
        price = self.getPrice()
        self.priceSeq.append(price)

        self.isActive = (self.priceSeq.get(0) > 0)

        ################################
        #  各統計変数の計算      ########
        ################################

        s = self.priceSeq.summarize(lambda x: x)
        ss = self.priceSeq.summarize(lambda x: x * x)
        sd = sqrt((self.L * ss - s * s) / (self.L * (self.L - 1)))

        average = s / self.L
        b = self.B * sd

        self.averageCurve.append(average)
        self.bandWidth.append(sd)

        ################################
        #  以下、行動の選択部分   ########
        ################################

        act = Const.ACT_STAY

        if self.isActive and active:
            state = self.state

            # 買い状態
            if state == self.STATE_ASK:
                if (self.achieved != self.NAN_ACHIEVED and price < average + self.achieved * b) or price < self.cut:
                    self.state = self.STATE_STAY
                    act = Const.ACT_BID

            # 売り状態
            if state == self.STATE_BID:
                if (self.achieved != self.NAN_ACHIEVED and price > average - self.achieved * b) or price > self.cut:
                    self.state = self.STATE_STAY
                    act = Const.ACT_ASK

            # 行動待機
            if state == self.STATE_STAY:
                if self.bandWidth.df(-2) < 0 and self.bandWidth.df(-1) > 0:
                    if self.averageCurve.df(-1) > 0:
                        self.state = self.STATE_ASK
                        act = Const.ACT_ASK
                        self.achieved = self.NAN_ACHIEVED
                        self.cut = price * (1 - self.LOSSCUT)

                    if self.averageCurve.df(-1) < 0:
                        self.state = self.STATE_BID
                        act = Const.ACT_BID
                        self.achieved = self.NAN_ACHIEVED
                        self.cut = price * (1 + self.LOSSCUT)

        # 価格更新
        if self.state == self.STATE_ASK:
            for i in range(4):
                if price > average + b * (i - 1):
                    self.achieved = max(self.achieved, i - 1)

        if self.state == self.STATE_BID:
            for i in range(4):
                if price < average - b * (i - 1):
                    self.achieved = max(self.achieved, i - 1)

        return (act, (
        price, average, average + b, average - b, average + b * 2, average - b * 2, average + b * 3, average - b * 3))
