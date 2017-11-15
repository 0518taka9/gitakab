#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import Const, Sequence


class PerfectOrderAgent:
    N_CURVE = 5  # 曲線の数
    WIDTH = 300  # 表示するデータ数

    STATE_STAY = 0
    STATE_ASK = 1
    STATE_BID = 2

    def __init__(self, L, I, LOSSCUT):
        """
        :param L: 価格を保持する日数
        :param I: decide()呼び出しの間隔(traderのself.wait * I 秒)
        :param double LOSSCUT: 
        """
        self.priceSeq = Sequence(L)
        self.shortEMA = Sequence(L)     # 10EMA
        self.middleEMA1 = Sequence(L)   # 30EMA
        self.middleEMA2 = Sequence(L)   # 60EMA
        self.longEMA = Sequence(L)      # 120EMA

        self.isActive = False  # 価格情報が取得できているか
        self.state = self.STATE_STAY

        self.tick_count = 0  # tick()呼び出し回数のカウント

        self.L = L
        self.I = I
        self.LOSSCUT = LOSSCUT

        self.first_day = True
        self.up_trend = 0
        self.down_trend = 0
        self.hold_price = 0

    def drawerInfo(self):
        """
        グラフ描画用クラスDrawerに情報を渡す
        :return: 曲線数、幅
        """
        return (self.N_CURVE, self.WIDTH)

    def reset(self):
        """
       注文がリジェクトされた時などに呼び出される
       """
        self.state = self.STATE_STAY

    def tick(self, last, average, amount, active):
        """
        価格を元に何らかの指標を計算する。
        (I)回に一回(tick()の呼び出しはデフォルトで3秒ごと、10回ごとにすれば30秒に一回)
        decide()を呼び出し、Traderにアクションを返す。
        
        :param price: manager.tick()で設定した価格
        :param amount: manager.tick()で設定した取引量
        :param active: 前回の注文が成功したか
        :return: decide()
        """
        self.last = last
        self.average = average
        self.tick_count += 1

        # (I)回に1回decide()を呼び出す
        if self.tick_count == self.I:
            self.tick_count = 0
            return self.decide(active)

        else:
            return (Const.ACT_STAY, None)

    # def getPrice(self):
    #     return self.price

    def decide(self, active):
        """
        1分に1回呼び出し
        調整する箇所：
        EMAの日数、PO崩壊条件、利確の幅
        エントリー条件(PO条件がローソク何本分続くか、価格と短期移動平均線の差)
        
        :param active: 前回の注文が成功したか
        :return: アクション、グラフ描画用データ(N_CURVE数)
        """

        # 価格を取得し保持
        last = self.last
        average = self.average
        self.priceSeq.append(average)

        self.isActive = (self.priceSeq.get(0) > 0)

        # 1日目は移動平均に終値を用いる
        if self.first_day:
            short = average
            middle1 = average
            middle2 = average
            long = average

            self.shortEMA.append(short)
            self.middleEMA1.append(middle1)
            self.middleEMA2.append(middle2)
            self.longEMA.append(long)

            self.first_day = False
        else:
            # 2日目以降
            # EMA(n) = EMA(n－1) + α ×｛当日価格 - EMA(n-1)｝
            # α（平滑化定数）＝2 / (n＋1）
            short = self.shortEMA.get(-1) + (2.0 / 11.0) * (average - self.shortEMA.get(-1))
            middle1 = self.middleEMA1.get(-1) + (2.0 / 31.0) * (average - self.middleEMA1.get(-1))
            middle2 = self.middleEMA2.get(-1) + (2.0 / 61.0) * (average - self.middleEMA2.get(-1))
            long = self.longEMA.get(-1) + (2.0 / 121.0) * (average - self.longEMA.get(-1))

            self.shortEMA.append(short)
            self.middleEMA1.append(middle1)
            self.middleEMA2.append(middle2)
            self.longEMA.append(long)

        # パーフェクトオーダー条件(上昇トレンド)
        if short > middle1 and middle1 > middle2 and middle2 > long and self.shortEMA.df(-1) > 0 and self.middleEMA1.df(-1) > 0 and self.middleEMA2.df(-1) > 0 and self.longEMA.df(-1) > 0:
            self.up_trend += 1
            self.down_trend = 0
        # 10EMAと30EMAが下降しだしたら崩壊
        elif self.shortEMA.df(-1) < 0 and self.middleEMA1.df(-1) < 0:
            self.up_trend = 0

        # パーフェクトオーダー条件(下降トレンド)
        if short < middle1 and middle1 < middle2 and middle2 < long and self.shortEMA.df(-1) < 0 and self.middleEMA1.df(-1) < 0 and self.middleEMA2.df(-1) < 0 and self.longEMA.df(-1) < 0:
            self.down_trend += 1
            self.up_trend = 0
        # 10EMAと30EMAが上昇しだしたら崩壊
        elif self.shortEMA.df(-1) > 0 and self.middleEMA1.df(-1) > 0:
            self.down_trend = 0
            
        # print "up :" + str(self.up_trend)
        # print "down :" + str(self.down_trend)
        # print "------------------"

        # 行動決定
        act = Const.ACT_STAY
        if self.isActive and active:
            state = self.state

            # 買い状態
            if state == self.STATE_ASK:
                # PO条件が崩壊 or 損切り or 利益が保持価格の0.002倍以上
                if self.up_trend == 0 or average < self.cut or average - self.hold_price > self.hold_price * 0.002:
                    self.up_trend = 0
                    self.state = self.STATE_STAY
                    act = Const.ACT_BID

            # 売り状態
            if state == self.STATE_BID:
                # PO条件が崩壊 or 損切り or 利益が保持価格の0.002倍以上
                if self.down_trend == 0 or average > self.cut or self.hold_price - average > self.hold_price * 0.002:
                    self.down_trend = 0
                    self.state = self.STATE_STAY
                    act = Const.ACT_ASK

            # 行動待機
            if state == self.STATE_STAY:
                # 5本のローソク足が経過してもPO条件(上昇)維持 and 価格と短期移動平均線に近づく
                if self.up_trend >= 5 and self.shortEMA.get(-1) - average > self.hold_price * 0.001:
                    self.state = self.STATE_ASK
                    act = Const.ACT_ASK
                    self.cut = average * (1 - self.LOSSCUT)
                    self.hold_price = average

                # 5本のローソク足が経過してもPO条件(下降)維持 and 価格と短期移動平均線に近づく
                if self.down_trend >= 5 and average - self.shortEMA.get(-1) > self.hold_price * 0.001:
                    self.state = self.STATE_BID
                    act = Const.ACT_BID
                    self.cut = average * (1 + self.LOSSCUT)
                    self.hold_price = average

        return (act, (average, short, middle1, middle2, long))
