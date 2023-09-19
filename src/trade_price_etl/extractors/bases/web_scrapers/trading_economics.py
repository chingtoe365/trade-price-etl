import asyncio
import datetime
import logging
import time

import pandas as pd
from urllib.parse import urljoin

from trade_price_etl.extractors.bases.web_scrapers.driver import SeleniumDriver
from trade_price_etl.storage.real_time_price import RTS
from trade_price_etl.notifications.publisher import publich_message, connect_mqtt, publish

logger = logging.getLogger(__name__)


def get_price_from_df(df: pd.DataFrame, col_name: str, item: str,):
    return df[df[col_name] == item]['Price'][0]


class TradingEconomicsScraperBase:
    _url_base = 'https://tradingeconomics.com'
    _poll_frequency = 0.5

    def __init__(self, url_dir: str, target_table_index: str, name_column: str):
        self._url_dir = url_dir
        self._target_table_idx = target_table_index
        self._name_col = name_column

    async def extract(self):
        full_url = urljoin(self._url_base, self._url_dir)
        client = connect_mqtt()
        client.loop_start()
        with SeleniumDriver(service_args=['--ignore-ssl-errors=true']) as driver:
            driver.get(full_url)
            full_html = driver.page_source
            dfs = pd.read_html(full_html)
            df_old = dfs[self._target_table_idx]
            while True:
                full_html = driver.page_source
                dfs = pd.read_html(full_html)
                df = dfs[self._target_table_idx]
                for i in df.index:
                    price_name = df[self._name_col][i]
                    new_price = df['Price'][i]
                    old_price = df_old['Price'][i]
                    if new_price != old_price:
                        # store in storage
                        RTS.insert(price_name, datetime.datetime.now().timestamp(), new_price)
                        msg = '%s Price: $%s' % (price_name, new_price)
                        logger.warning('publish new message to topic: ' + price_name + '; message: ' + msg)
                        # publish this message to mosquitto
                        publish(client, price_name, msg)


                df_old = df
                await asyncio.sleep(self._poll_frequency)
