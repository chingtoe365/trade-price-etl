from collections import deque

from typing import Dict


queue_max_size = 100000


class RealTimePriceStorage:

    def __init__(self):
        self._full_dict: Dict[str, Dict[str, deque(maxlen=queue_max_size)]] = {}

    def _get_timestamp(self, price_name: str) -> deque:
        return self._full_dict.get(price_name).get('timestamp')

    def _get_price(self, price_name: str) -> deque:
        return self._full_dict.get(price_name).get('price')

    def insert(self, price_name: str, ts: float, price: float):
        if price_name in self._full_dict:
            self._get_timestamp(price_name).append(ts)
            self._get_price(price_name).append(price)
        else:
            self._full_dict[price_name] = {}
            self._full_dict[price_name]['timestamp'] = deque([ts], maxlen=queue_max_size)
            self._full_dict[price_name]['price'] = deque([price], maxlen=queue_max_size)


RTS = RealTimePriceStorage()