from contextlib import ContextDecorator
import logging
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PROXIES = [
    "http://160.86.242.23:8080",
    "http://172.183.241.1:8080",
    "http://47.251.70.179:80",
    "http://20.235.159.154:80"
]

logger = logging.getLogger(__name__)


class SeleniumDriver(ContextDecorator):
    driver = None

    def __init__(
        self, chrome_options=None, *args, **kwargs
    ):
        '''
        initialize Chrome webdriver
        '''
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

        # randomly select a proxy
        proxy = random.choice(PROXIES)
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
