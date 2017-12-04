#!/usr/bin/env python
# -*- coding: utf-8 -*-

from perfect_order_agent import *
from learning import *
if __name__ == "__main__":

    best_score = 0
    best_benefit = 0
    best_losscut = 0
    best_candlesticks = 0

    for benefit in range(2, 11, 1):
        benefit *= 0.001
        for losscut in range(2, 11, 1):
            losscut *= 0.001
            for candlesticks in range(4, 8, 1):
                learning = Learning(benefit, losscut, candlesticks)
                score = learning.getScore()

                print score

                if score >= best_score:
                    best_score = score
                    best_benefit = benefit
                    best_losscut = losscut
                    best_candlesticks = candlesticks

    print "best_score = " + str(best_score)
    print "best_benefit = " + str(best_benefit)
    print "best_losscut = " + str(best_losscut)
    print "best_candlesticks = " + str(best_candlesticks)
