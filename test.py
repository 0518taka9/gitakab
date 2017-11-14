#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from bitflyer import *

if __name__ == '__main__':
    api = BitflyerAPI("", "")
    while True:
        print(api.get_board(Product.BTC_FX))
        time.sleep(3)