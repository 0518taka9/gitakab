#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, sys
from lib import *
from manager import Manager


class Trader:
    AVAILABLE = 0.8     #
    CHALLENGE = 10      #

    def __init__(self, agent):
        self.agent = agent
        self.manager = Manager()
        self.drawer = Drawer(self.agent.drawerInfo())
        self.trade = 0
        self.wait = 0
        self.benefit = 0
        self.last_action = time.time()

    def reset(self):
        if self.trade > 0:
            print(self.benefit)
        self.trade = 0
        self.agent.reset()

    def tick(self):
        if time.time() - self.last_action >= self.wait:
            self.last_action = time.time()

            (last, average, amount, losscut) = self.manager.tick()

            if losscut:
                self.reset()

            (act, data) = self.agent.tick(last, average, amount, True)

            if data is None:
                return

            trade = 0

            if act == Const.ACT_ASK:
                if self.trade > 0:
                    # 買い戻し
                    trade = self.trade
                else:
                    # 買い入れ
                    trade = 1

            if act == Const.ACT_BID:
                if self.trade > 0:
                    # 売り戻し
                    trade = self.trade
                else:
                    # 売り入れ
                    trade = 1

            if trade > 0:
                ac_price = self.manager.sendOrder(act, trade)
                print("[Action: " + str(act) + " at Price: " + str(ac_price) + "]")
                if self.trade > 0:
                    if act == Const.ACT_ASK:
                        self.benefit += self.start_price - ac_price
                        self.reset()

                    if act == Const.ACT_BID:
                        self.benefit += ac_price - self.start_price
                        self.reset()
                else:
                    self.trade = trade
                    self.start_price = ac_price

            self.drawer.update(data)

            # print("ACT: " + str(act))
            # print("Trade: " + str(self.trade))
            # print("Price: " + str(price))
            # print("Amount: " + str(amount))
            # print("Time: " + str(time.time()))
            # print("-----")

        self.drawer.sleep(0.001)
