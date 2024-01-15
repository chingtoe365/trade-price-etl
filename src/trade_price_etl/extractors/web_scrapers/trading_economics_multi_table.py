import asyncio
import datetime
import logging
import re
import sys
from typing import List

import pandas as pd
from urllib.parse import urljoin

from trade_price_etl.extractors.web_scrapers.driver import SeleniumDriver
from trade_price_etl.settings.base_settings import settings
from trade_price_etl.storage.real_time_price import RTS


logger = logging.getLogger(__name__)


def get_price_from_df(df: pd.DataFrame, col_name: str, item: str,):
    return df[df[col_name] == item]['Price'][0]


class TradingEconomicsMultiTableScraper:
    _url_base = 'https://tradingeconomics.com'
    _poll_frequency = settings.EXTRACTOR.POLL_FREQUENCY_MULTIPLE_TABLES
    _wait_for_blockade_unfrozen = settings.EXTRACTOR.BLOCKADE_STOPPAGE_WAIT

    def __init__(self, url_dir: str, target_table_num: int, name_columns: List[str]):
        self._url_dir = url_dir
        self._target_table_num = target_table_num
        self._name_cols = name_columns

    async def extract(self):
        tables_not_found_error = True
        full_url = urljoin(self._url_base, self._url_dir)
        # logger.info(settings.model_dump())
        # print("ok")
        logger.debug(">> Extracting price")
        with SeleniumDriver(service_args=['--ignore-ssl-errors=true']) as driver:
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
                        await asyncio.sleep(self._wait_for_blockade_unfrozen)
                        continue
                    logger.debug(
                        ">> First attempt successful. Category: %s, Table number: %s",
                        self._url_dir, str(self._target_table_num)
                    )
                except ValueError as ve:
                    if ve.args[0].lower() == 'no tables found':
                        logger.warning(
                            "Exception found in first attempt. Page: %s. Will try again in %d secs",
                            self._url_dir,
                            self._wait_for_blockade_unfrozen
                        )
                        await asyncio.sleep(self._wait_for_blockade_unfrozen)
                        continue
                    else:
                        sys.exit(f"Error getting table: {ve.args[0]}")
            # logger.debug(">> Getting into the loop")
            # driver.get(full_url)
            while True:
                driver.get(full_url)
                full_html = driver.page_source
                try:
                    dfs = pd.read_html(full_html)
                    # logger.debug(">> Read html into table")
                except ValueError as ve:
                    # catch exception when sometimes no tables are found then skip and continue
                    if ve.args[0].lower() == 'no tables found':
                        logger.warning(
                            "No tables found. Page: %s. Will try again in %d secs",
                            self._url_dir,
                            self._wait_for_blockade_unfrozen
                        )
                        await asyncio.sleep(self._wait_for_blockade_unfrozen)
                        continue

                if len(dfs) < self._target_table_num:
                    logger.warning(
                        f">> Not enough tables found. {self._target_table_num} required but found {len(dfs)}"
                    )
                    await asyncio.sleep(self._wait_for_blockade_unfrozen)
                    continue
                for table_idx in range(self._target_table_num):
                    df = dfs[table_idx]
                    # if isinstance(df_old, pd.DataFrame) and len(df_old) > 0:
                    df_old = dfs_old[table_idx]
                    for i in df.index:
                        price_name = df[self._name_cols[table_idx]][i]
                        new_price = df['Price'][i]
                        old_price = df_old['Price'][i]
                        if new_price != old_price:
                            # logger.debug(f'>> {price_name} \n old: {old_price} \n new: {new_price}')
                            # store in storage
                            RTS.insert(price_name, datetime.datetime.now().timestamp(), new_price)
                            # msg = '%s Price: $%s' % (price_name, new_price)
                            # logger.warning('publish new message to topic: ' + price_name + '; message: ' + msg)
                dfs_old = dfs

                await asyncio.sleep(self._poll_frequency)
