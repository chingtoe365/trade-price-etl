import logging
import random
import requests

from contextlib import ContextDecorator
from functools import wraps
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

import pandas as pd


logger = logging.getLogger(__name__)


def get_proxy_list() -> List[str]:
    available_proxy_list = [
        "http://77.68.33.138:8080"
        "http://160.86.242.23:8080",
        "http://172.183.241.1:8080",
        "http://47.251.70.179:80",
        "http://20.235.159.154:80"
    ]
    proxy_list_resp = requests.get(
        # "https://proxylist.geonode.com/api/proxy-list?protocols=http&limit=500&page=1&sort_by=speed&sort_type=asc",
        "https://free-proxy-list.net/",
        json={}
    )
    if proxy_list_resp.status_code == 200:
        proxy_tables = pd.read_html(proxy_list_resp.text)
        if len(proxy_tables):
            available_proxy_list = proxy_tables[0].apply(lambda x: f"http://{x['IP Address']}:{x['Port']}", axis=1).tolist()[:10]
    return available_proxy_list


class SeleniumDriver(ContextDecorator):
    driver = None

    def __init__(
        self, first_attempt: bool=True, chrome_options=None, *args, **kwargs
    ):
        '''
        initialize Chrome webdriver
        '''
        self._first_attempt = first_attempt
        self._chrome_options = chrome_options or Options()
        self._args = args
        self._kwargs = kwargs

    def _get_desired_capabilities(self):
        return {}

    def __enter__(self, headless=True) -> webdriver:
        '''
        Opens and returns the driver
        '''
        # if self.set_headless:
        #     self._chrome_options.set_headless()
        if headless:
            self._chrome_options.headless = headless

        self._chrome_options.add_argument('--no-sandbox')
        self._chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self._chrome_options.add_experimental_option('excludeSwitches', ["enable-automation"])
        self._chrome_options.add_experimental_option('useAutomationExtension', False)

        if not self._first_attempt:
            # randomly select a proxy
            proxy_list = get_proxy_list()
            proxy = random.choice(proxy_list)
            self._chrome_options.add_argument("--proxy-server=%s" % proxy)
            logger.info("Proxy %s set for selenium" % proxy)

        self.driver = webdriver.Chrome(
            chrome_options=self._chrome_options,
            **self._kwargs
        )
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            }
        )
        return self.driver

    def _get_kwargs(self):
        return self._kwargs

    def __exit__(self, *exec):
        '''
        close driver
        '''
        self.driver.quit()
        self.driver = None

    def __del__(self):
        """ When the object is deleted tries to call the exit method
        We declare this method because the thread that is running this
        could be timeouted by its parent, this could cause the exit to
        not be called.
        """
        """
            !Remember __del__ and circular references are enemies
        """
        if self.driver:
            self.__exit__()



class BadProxyException(Exception):
    pass


def on_table_not_found(async_extractor_func):
    @wraps(async_extractor_func)
    async def wrapped_func(*args, **kwargs):
        first_attempt = True
        while True:
            try:
                with SeleniumDriver(first_attempt=first_attempt) as driver:
                    await async_extractor_func(driver=driver, *args, **kwargs),
            except BadProxyException as bpe:
                first_attempt = False
                logger.warning("Bad proxy. Rotating proxies...")
            except WebDriverException as wde:
                first_attempt = False
                logger.warning("Table not managed to be exracted. Rotating proxies...")
    return wrapped_func