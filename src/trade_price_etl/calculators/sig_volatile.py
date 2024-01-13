import datetime
import json
import logging
from typing import Dict

import pandas as pd
import numpy as np

from trade_price_etl.calculators.base import CalculatorBase
from trade_price_etl.constants.constants import Metrics, MetricsShortDescription
from trade_price_etl.notifications.publisher import publish
from trade_price_etl.utils.utils import build_mqtt_topic

logger = logging.getLogger(__name__)


def get_price_n_minutes_ago(n: int, df: pd.DataFrame) -> float:
    """ Get the price of item n minutes ago

    @param n: Time to roll back (in the unit of minute)
    @param df: Price dataframe
    @return: Price at that time
    """
    # logger.debug(f">> get timestamp")
    time_current = datetime.datetime.fromtimestamp(
        df.at[df.index[-1], 'timestamp']
    )
    # logger.debug(f">> Current time object {time_current}")
    time_n_minute_minus = time_current - datetime.timedelta(minutes=n)
    df['next_timestamp'] = df['timestamp'].shift(-1)
    # logger.debug(df)
    df['is_price_n_min_ago'] = df.apply(
        lambda x: (x['timestamp'] <= time_n_minute_minus.timestamp()) and
                  (x['next_timestamp'] > time_n_minute_minus.timestamp()),
        axis=1
    )
    df_n_min_ago = df[df['is_price_n_min_ago']]
    # logger.debug(f">> Price {n} minutes ago: {df_n_min_ago}")
    return np.nan if df_n_min_ago.empty else float(df_n_min_ago['price'])


class VolatileSignal(CalculatorBase):

    metric_name = 'volatile'
    small_threshold = 0.01  # 0.0008
    one_min_emit_frozen_duration = 180
    five_min_emit_frozen_duration = 1500

    @classmethod
    def compute(cls, price_item: str, df: pd.DataFrame, last_emissions: Dict):
        """ Compute signal

        @param price_item:
        @param df:
        @param last_emissions:
        @return:
        """
        # logger.debug(f">> Computing metric: {cls.metric_name} item: {price_item}")
        # logger.debug(">> another message")
        # logger.debug(f">> check DF : {df[-1]['price']}")
        price_current = float(df.at[df.index[-1], 'price'])
        # logger.debug(price_current)
        price_one_minute_ago = get_price_n_minutes_ago(1, df)
        # logger.debug(price_one_minute_ago)
        pch_one_minute_ago = (price_current - price_one_minute_ago) / price_one_minute_ago
        # logger.debug(f" Percentage change ONE min ago: {pch_one_minute_ago}")
        if not np.isnan(pch_one_minute_ago) and pch_one_minute_ago > cls.small_threshold:
            topic = build_mqtt_topic(price_item, str(Metrics.VOLATILE_UP_1_1))
            # If price go up more than 1% in the last minute
            # and the signal emission frozen period has past
            # raise signal
            # logger.warning(
            #     f">> {price_item} price go up > {cls.small_threshold * 100}% in last 1 minutes"
            # )
            publish(
                last_emissions,
                topic,
                f"{MetricsShortDescription.VOLATILE_UP_1_1}",
                cls.one_min_emit_frozen_duration
            )
        if not np.isnan(pch_one_minute_ago) and pch_one_minute_ago < -cls.small_threshold:
            topic = build_mqtt_topic(price_item, str(Metrics.VOLATILE_DOWN_1_1))
            # If price go down more than 1% in the last minute
            # and the signal emission frozen period has past
            # raise signal
            # logger.warning(
            #     f">> {price_item} price go down > {cls.small_threshold * 100}% in last 1 minutes"
            # )
            publish(
                last_emissions,
                topic,
                f"{MetricsShortDescription.VOLATILE_DOWN_1_1}",
                cls.one_min_emit_frozen_duration
            )

        price_five_minute_ago = get_price_n_minutes_ago(5, df)
        pch_five_minute_ago = (price_current - price_five_minute_ago) / price_one_minute_ago
        # logger.debug(f" Percentage change FIVE min ago: {pch_five_minute_ago}")
        if not np.isnan(pch_five_minute_ago) and pch_five_minute_ago > cls.small_threshold:
            topic = build_mqtt_topic(price_item, str(Metrics.VOLATILE_UP_1_5))
            # If price go up more than 1% in the last 5 minutes
            # and the signal emission frozen period has past
            # raise signal
            # logger.warning(
            #     f">> {price_item} price go up > {cls.small_threshold * 100}% in last 5 minutes"
            # )
            publish(
                last_emissions,
                topic,
                f"{MetricsShortDescription.VOLATILE_UP_1_5}",
                cls.five_min_emit_frozen_duration
            )
        if not np.isnan(pch_five_minute_ago) and pch_five_minute_ago < -cls.small_threshold:
            topic = build_mqtt_topic(price_item, str(Metrics.VOLATILE_DOWN_1_5))
            # If price go down more than 1% in the last 5 minutes
            # and the signal emission frozen period has past
            # raise signal
            # logger.warning(
            #     f">> {price_item} price go down > {cls.small_threshold * 100}% in last 5 minutes"
            # )
            publish(
                last_emissions,
                topic,
                f"{MetricsShortDescription.VOLATILE_DOWN_1_5}",
                cls.five_min_emit_frozen_duration
            )
