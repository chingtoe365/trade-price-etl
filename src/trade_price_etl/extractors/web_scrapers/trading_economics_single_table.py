import asyncio
import datetime
import logging
import re
import sys

import pandas as pd
from urllib.parse import urljoin

from trade_price_etl.extractors.web_scrapers.driver import BadProxyException, SeleniumDriver, on_table_not_found
from trade_price_etl.notifications.redis import async_write_price, write_price
from trade_price_etl.settings.base_settings import settings
from trade_price_etl.storage.real_time_price import RTS


logger = logging.getLogger(__name__)


def get_price_from_df(df: pd.DataFrame, col_name: str, item: str,):
    return df[df[col_name] == item]['Price'][0]


class TradingEconomicsSingleTableScraper:
    _url_base = 'https://tradingeconomics.com'
    _poll_frequency = settings.EXTRACTOR.POLL_FREQUENCY_SINGLE_TABLE

    def __init__(self, url_dir: str, target_table_index: int, name_column: str):
        self._url_dir = url_dir
        self._target_table_idx = target_table_index
        self._name_col = name_column

    @on_table_not_found
    async def extract(self, driver: SeleniumDriver):
        table_not_found_error = True
        full_url = urljoin(self._url_base, self._url_dir)
        logger.debug(">> Extracting price from %s", full_url)
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
                logger.debug(
                    ">> First attempt successful. Category: %s, Idx: %s",
                    self._url_dir, str(self._target_table_idx)
                )
            except ValueError as ve:
                logger.warning(
                    f">> Exception found in first attempt. Table: {self._name_col}"
                )
                logger.warning(ve)
                logger.warning(re.search("<table", full_html))
                if ve.args[0].lower() == 'no tables found':
                    raise BadProxyException("Bad proxy. Rotate immediately")
                else:
                    sys.exit(f"Unknown error when getting table: {ve.args[0]}")
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
                    logger.warning(f">> No table: {self._name_col} found.")
                    raise BadProxyException("Bad proxy. Rotate immediately")
            df = dfs[self._target_table_idx]
            if isinstance(df_old, pd.DataFrame) and len(df_old) > 0:
                for i in df.index:
                    price_name = df[self._name_col][i]
                    new_price = df['Price'][i]
                    old_price = df_old['Price'][i]
                    # cache in redis timeseries kv 
                    # await async_write_price(price_name, new_price)
                    write_price(price_name, new_price)
                    if new_price != old_price:
                        # logger.debug(f'>> {price_name} \n old: {old_price} \n new: {new_price}')
                        # store in storage
                        RTS.insert(price_name, datetime.datetime.now().timestamp(), new_price)
                        # msg = '%s Price: $%s' % (price_name, new_price)
                        # logger.warning('publish new message to topic: ' + price_name + '; message: ' + msg)

                df_old = df.copy()
            await asyncio.sleep(self._poll_frequency)
