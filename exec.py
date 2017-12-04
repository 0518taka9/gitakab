#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import keyboard
from trader import Trader
from lib import Const
from bollinger import *
from perfect_order_agent import *

PLAYING = 1
PAUSING = 0


def pause():
    global mode
    mode = 1 - mode


if __name__ == '__main__':
    # agent = BollingerAgent(
    #     20,  # 長平均線の長さ
    #     0.9,  # 利確の際の判断係数
    #     1.0,  # 時間係数
    #     0.0002,  # 平均線間のマージン(これより大きいとアクションを行う)
    #     20,  # 価格の平均の幅 (*3s)
    #     20,  # アクション判断の間隔 (*3s)
    #     0.001  # ロスカット
    # )

    agent = PerfectOrderAgent(34, 20)
    """
    :param L: 価格を保持する日数
    :param I: decide()呼び出しの間隔(traderのself.wait * I 秒)
    """

    trader = Trader(agent)
    # keyboard.add_hotkey('esc', pause)

    global mode
    mode = PLAYING
    while not trader.isFinish():
        if mode == PLAYING:
            trader.tick()
