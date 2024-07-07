from contextlib import ContextDecorator
import logging
import random
from typing import List

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        "https://proxylist.geonode.com/api/proxy-list?protocols=http&limit=500&page=1&sort_by=speed&sort_type=asc",
        json={}
    )
    if proxy_list_resp.status_code == 200:
        proxy_list_resp_json = proxy_list_resp.json()
        if "data" in proxy_list_resp_json:
            proxy_list = proxy_list_resp_json["data"]
            if len(proxy_list) > 0:
                # proxy = proxy_list[0]
                available_proxy_list = [
                    "http://%s:%s" % (proxy["ip"], str(proxy["port"]))
                    for proxy in proxy_list
                ]
    return available_proxy_list


AVAILABLE_PROXIES = get_proxy_list()


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
            proxy = random.choice(AVAILABLE_PROXIES)
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


