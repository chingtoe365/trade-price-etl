from contextlib import ContextDecorator

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SeleniumDriver(ContextDecorator):
    driver = None

    def __init__(
        self, chrome_options=None, set_headless=True, *args, **kwargs
    ):
        '''
        initialize Chrome webdriver
        '''
        self._chrome_options = chrome_options or Options()
        self._args = args
        self._kwargs = kwargs
        self.set_headless = set_headless

    def _get_desired_capabilities(self):
        return {}

    def __enter__(self) -> webdriver:
        '''
        Opens and returns the driver
        '''
        if self.set_headless:
            self._chrome_options.set_headless()
        self.driver = webdriver.Chrome(
            chrome_options=self._chrome_options,
            **self._kwargs
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