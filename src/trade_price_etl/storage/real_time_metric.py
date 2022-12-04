from collections import deque

from typing import Dict

import numpy as np
import pandas as pd

from trade_price_etl.constants.constants import Metrics

queue_max_size = 100000


class RealTimeMetricStorage:
    _metric_map = {
      'double_peg' : 0,
    }
    _price_map = {
        'natural gas': 0,
        'oil': 1
    }
    _metric_map_r = dict(zip(_metric_map.values(), _metric_map.keys()))
    _price_map_r = dict(zip(_price_map.values(), _price_map.keys()))

    def __init__(self):
        self._metric: np.array = np.zeros((len(self._price_map), len(self._metric_map)))

    def update_metric_for_price_item(self, metric: Metrics, price_item: str, value: float):
        self._metric[self._price_map[price_item]][self._metric_map[metric]] = value

    def flag(self):
        hits = np.where(self._metric != 0)
        for i in range(len(hits[0])):
            hit_price_idx = hits[0][i]
            hit_metric_idx = hits[1][i]
            price_item = self._price_map_r[hit_price_idx]
            metric_item = self._metric_map_r[hit_metric_idx]
            signal = self._metric[hit_price_idx][hit_metric_idx]
            print("Trade Item: {}, Metric: {}, Signal: {}".format(
                price_item, metric_item, signal
            ))


RTMS = RealTimeMetricStorage()
