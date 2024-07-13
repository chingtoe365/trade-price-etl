import asyncio
import datetime
import logging
import re
import sys
from typing import List

import pandas as pd
from urllib.parse import urljoin

from trade_price_etl.extractors.web_scrapers.driver import BadProxyException, SeleniumDriver, on_table_not_found
from trade_price_etl.notifications.redis import async_write_price
from trade_price_etl.settings.base_settings import settings
from trade_price_etl.storage.real_time_price import RTS


logger = logging.getLogger(__name__)


def get_price_from_df(df: pd.DataFrame, col_name: str, item: str,):
    return df[df[col_name] == item]['Price'][0]


class TradingEconomicsMultiTableScraper:
    _url_base = 'https://tradingeconomics.com'
    _poll_frequency = settings.EXTRACTOR.POLL_FREQUENCY_MULTIPLE_TABLES
    _frozen_duration = settings.EXTRACTOR.FROZEN_FOR_RETRY

    def __init__(self, url_dir: str, target_table_num: int, name_columns: List[str]):
        self._url_dir = url_dir
        self._target_table_num = target_table_num
        self._name_cols = name_columns

    @on_table_not_found
    async def extract(self, driver: SeleniumDriver):
        tables_not_found_error = True
        full_url = urljoin(self._url_base, self._url_dir)
        # logger.info(settings.model_dump())
        # print("ok")
        logger.debug(">> Extracting price from %s", full_url)
        driver.get(full_url)
        full_html = driver.page_source
        # df_old = pd.DataFrame()
        # dfs = pd.DataFrame()
        while tables_not_found_error:
            try:
                dfs_old = pd.read_html(full_html)
                if len(dfs_old) >= self._target_table_num and all(isinstance(df, pd.DataFrame) for df in dfs_old):
                    tables_not_found_error = False
                else:
                    logger.warning(
                        "First attempt found %d/%d tables. Will try again in %d secs",
                        len(dfs_old), self._target_table_num, self._wait_for_blockade_unfrozen
                    )
                    await asyncio.sleep(self._frozen_duration)
                    continue
                logger.debug(
                    ">> First attempt successful. Category: %s, Table number: %s",
                    self._url_dir, str(self._target_table_num)
                )
            except ValueError as ve:
                if ve.args[0].lower() == 'no tables found':
                    logger.warning(
                        "Exception found in first attempt. Page: %s. Will rotate proxy now.",
                        self._url_dir
                    )
                    raise BadProxyException("Bad proxy. Rotate immediately")
                else:
                    sys.exit(f"Error getting table: {ve.args[0]}")
        # logger.debug(">> Getting into the loop")
        # driver.get(full_url)
        while True:
            driver.execute_script("return document.body.innerHTML")
            full_html = driver.page_source
            try:
                dfs = pd.read_html(full_html)
                # logger.debug(">> Read html into table")
            except ValueError as ve:
                # catch exception when sometimes no tables are found then skip and continue
                if ve.args[0].lower() == 'no tables found':
                    logger.warning(
                        "No tables found. Page: %s. Will rotate proxy now.",
                        self._url_dir
                    )
                    raise BadProxyException("Bad proxy. Rotate immediately")

            if len(dfs) < self._target_table_num:
                logger.warning(
                    f">> Not enough tables found. {self._target_table_num} required but found {len(dfs)}",
                    f"Will retry in {self._frozen_duration} seconds"
                )
                await asyncio.sleep(self._frozen_duration)
                continue
            for table_idx in range(self._target_table_num):
                df = dfs[table_idx]
                # if isinstance(df_old, pd.DataFrame) and len(df_old) > 0:
                df_old = dfs_old[table_idx]
                for i in df.index:
                    price_name = df[self._name_cols[table_idx]][i]
                    new_price = df['Price'][i]
                    old_price = df_old['Price'][i]
                    # cache in redis timeseries kv 
                    await async_write_price(price_name, new_price)
                    # REDIS_TS.add(price_name, datetime.datetime.now().timestamp(), float(new_price))
                    if new_price != old_price:
                        # logger.debug(f'>> {price_name} \n old: {old_price} \n new: {new_price}')
                        # store in storage
                        RTS.insert(price_name, datetime.datetime.now().timestamp(), new_price)
                        # msg = '%s Price: $%s' % (price_name, new_price)
                        # logger.warning('publish new message to topic: ' + price_name + '; message: ' + msg)
            dfs_old = dfs

            await asyncio.sleep(self._poll_frequency)
