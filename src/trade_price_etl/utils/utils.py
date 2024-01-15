""" Program wide utilities"""
import datetime
import logging

import pandas as pd

from trade_price_etl.settings.base_settings import settings

logger = logging.getLogger(__name__)


def build_mqtt_topic(trade_item: str, signal: str):
    """ Build MQTT topic name with trade item and signal

    @param price:
    @param signal:
    @return:
    """
    return f'{trade_item.replace(" ", "-").replace("/", "-").lower()}/{signal}'


def is_latest_price_up_to_date(df: pd.DataFrame):
    """ Check if latest price in dataframe is up-to-date
    within the last poll frequency range

    @param df:
    @return:
    """
    time_current = datetime.datetime.fromtimestamp(
        df.at[df.index[-1], 'timestamp']
    )
    elapsed = datetime.datetime.now() - time_current
    # logger.debug(elapsed.seconds)
    return int(elapsed.seconds) <= min(
            settings.EXTRACTOR.POLL_FREQUENCY_MULTIPLE_TABLES,
            settings.EXTRACTOR.POLL_FREQUENCY_SINGLE_TABLE
    )
