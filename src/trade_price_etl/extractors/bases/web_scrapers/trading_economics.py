import asyncio
import datetime
import logging
import sys
import time

import pandas as pd
from urllib.parse import urljoin

from trade_price_etl.extractors.bases.web_scrapers.driver import SeleniumDriver
from trade_price_etl.settings.base_settings import settings
from trade_price_etl.storage.real_time_price import RTS
from trade_price_etl.notifications.publisher import publich_message, connect_mqtt, publish

logger = logging.getLogger(__name__)


def get_price_from_df(df: pd.DataFrame, col_name: str, item: str,):
    return df[df[col_name] == item]['Price'][0]


class TradingEconomicsScraperBase:
    _url_base = 'https://tradingeconomics.com'
    _poll_frequency = 1
    _wait_for_blockade_unfrozen = 3

    def __init__(self, url_dir: str, target_table_index: str, name_column: str):
        self._url_dir = url_dir
        self._target_table_idx = target_table_index
        self._name_col = name_column

    async def extract(self):
        table_not_found_error = True
        full_url = urljoin(self._url_base, self._url_dir)
        # logger.info(settings.model_dump())
        # print("ok")
        logger.debug(">> Extracting price")
        with SeleniumDriver(service_args=['--ignore-ssl-errors=true']) as driver:
            driver.get(full_url)
            full_html = driver.page_source
            # df_old = pd.DataFrame()
            # dfs = pd.DataFrame()
            while table_not_found_error:
                try:
                    dfs_old = pd.read_html(full_html)
                    if len(dfs_old) > 0:
                        df_old = dfs_old[self._target_table_idx]
                        table_not_found_error = False
                    logger.debug(">> First attempt successful")
                except ValueError as ve:
                    logger.warning(">> Exception found in first attempt")
                    if ve.args[0].lower() == 'no tables found':
                        await asyncio.sleep(self._wait_for_blockade_unfrozen)
                        continue
                    else:
                        sys.exit(f"Error getting table: {ve.args[0]}")
            logger.debug(">> Getting into the loop")
            # driver.get(full_url)
            while True:
                driver.get(full_url)
                full_html = driver.page_source
                try:
                    dfs = pd.read_html(full_html)
                    logger.debug(">> Read html into table")
                except ValueError as ve:
                    # catch exception when sometimes no tables are found then skip and continue
                    if ve.args[0].lower() == 'no tables found':
                        logger.warning(">> No tables found")
                        await asyncio.sleep(self._wait_for_blockade_unfrozen)
                        continue
                df = dfs[self._target_table_idx]
                if isinstance(df_old, pd.DataFrame) and len(df_old) > 0:
                    for i in df.index:
                        price_name = df[self._name_col][i]
                        new_price = df['Price'][i]
                        old_price = df_old['Price'][i]
                        if new_price != old_price:
                            logger.debug(f'>> {price_name} \n old: {old_price} \n new: {new_price}')
                            # store in storage
                            RTS.insert(price_name, datetime.datetime.now().timestamp(), new_price)
                            # msg = '%s Price: $%s' % (price_name, new_price)
                            # logger.warning('publish new message to topic: ' + price_name + '; message: ' + msg)

                    df_old = df.copy()
                await asyncio.sleep(self._poll_frequency)
