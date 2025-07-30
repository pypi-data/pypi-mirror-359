# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/8 14:29
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""
import time

import polars as pl
from quda.data.zoo import base
import ylog
import ygo
# from quda.factor.core import FactorContext
#
# if __name__ == '__main__':
#     date = "2025-05-06"
#     start_t = time.time()
#     # res = base.fac_kline_minute.get_values(date, beg_time="09:31:00", end_time="09:40:00", freq="1min")
#     res = base.fac_cap.get_history(date, time="09:31:00", period="-20d", )
#     # res = base.fac_cap.get_values(date, beg_time="09:31:00", end_time="09:40:00", freq="1min")
#     # res = base.fac_cap.get_history_depends(date, period="-2d", time="09:31:00")
#     # res = base.fac_kline_minute.get_values(date, time="09:35:00", beg_time="09:31:00", end_time="09:40:00", freq="1min")
#     # res = base.fac_kline_minute.get_history(date, period="-2d", time="09:35:00")
#     # res = base.fac_kline_day.get_history(date, period="-100d", )
#     # res = base.fac_kline_day.get_value(date, time="15:00:00")
#     ylog.info(res.filter(pl.col("asset") == "000001"))
#     ylog.info(f"cost {(time.time() - start_t):.3f} s")
if __name__ == '__main__':
    # print(FactorContext.__dataclass_fields__.keys())
    print(ygo.fn_info(ygo.delay(base.fac_prev_close.fn)(env="rt")))