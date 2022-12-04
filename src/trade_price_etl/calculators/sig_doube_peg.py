import asyncio
import logging

import numpy as np

from trade_price_etl.calculators.base import CalculatorBase
from trade_price_etl.storage.real_time_metric import RTMS
from trade_price_etl.storage.real_time_price import RTS


logger = logging.getLogger(__name__)


class DoublePegSignal(CalculatorBase):

    metric_name = 'double_peg'

    async def compute(self):
        while True:
            await asyncio.sleep(self._compute_frequency)
            out_metric = {}
            # flag = False
            to_long = 0
            all_price_dfs = RTS.get_data()
            for price_item, df in all_price_dfs.items():
                # only calculate from the last 50 price points
                df = df[-50]
                if len(df['price'].unique()) < 4:
                    try:
                        df['duration'] = np.concatenate(
                            (
                                np.nan,
                                np.array(df['timestamp'][1:]) - np.array(df['timestamp'][:-1])
                            )
                        )
                        duration_agg = df.groupby('price').sum()
                        duration_agg_price_min = duration_agg.iloc[0,]['duration']
                        duration_agg_price_max = duration_agg.iloc[-1,]['duration']
                        if duration_agg_price_max > duration_agg_price_min:
                            to_long = 1
                        elif duration_agg_price_max < duration_agg_price_min:
                            to_long = -1
                        # flag = True
                    except Exception as e:
                        logger.error('Error in computing double peg signal: %s', e.args[0])
                RTMS.update_metric_for_price_item(self.metric_name, price_item, to_long)

