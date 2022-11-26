import logging
import time

import pandas as pd
from urllib.parse import urljoin

from trade_price_etl.extractors.bases.web_scrapers.driver import SeleniumDriver


logger = logging.getLogger(__name__)


def get_price_from_df(df: pd.DataFrame, col_name: str, item: str,):
    return df[df[col_name] == item]['Price'][0]


class TradingEconomicsScraperBase:
    _url_base = 'https://tradingeconomics.com'
    _poll_frequency = 0.5

    def __init__(self, url_dir: str, price_name: str, target_table_index: str):
        self._url_dir = url_dir
        self._price_name = price_name
        self._target_table_idx = target_table_index

    def extract(self):
        full_url = urljoin(self._url_base, self._url_dir)
        with SeleniumDriver(service_args=['--ignore-ssl-errors=true']) as driver:
            driver.get(full_url)
            full_html = driver.page_source
            dfs = pd.read_html(full_html)
            df_old = dfs[self._target_table_idx]
            while True:
                full_html = driver.page_source
                dfs = pd.read_html(full_html)
                df = dfs[self._target_table_idx]
                # if df == df_old:
                #     time.sleep(self._poll_frequency)
                #     continue
                # else:
                old_price = get_price_from_df(df_old, 'Crypto', self._price_name)
                new_price = get_price_from_df(df, 'Crypto', self._price_name)
                if not old_price == new_price:
                    logger.warning('%s Price: $%s', self._price_name, new_price)
                df_old = df
                time.sleep(self._poll_frequency)


