import datetime
import logging
import re
from typing import List
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from trade_price_etl.extractors.bases.web_scrapers.driver import SeleniumDriver

logger = logging.getLogger(__name__)


class PresenceOfAnyElements(object):
    """An expectation for checking that an element has a particular css class.

      locator - used to find the element
      returns the WebElement once it has the particular css class
    """

    def __init__(self, locator, css_classes: List[str]):
        self.locator = locator
        self.css_classes = css_classes

    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element
        if any([cls in element.get_attribute("class") for cls in self.css_classes]):
            return element
        else:
            return False


class MarketsInsiderScraperBase:
    _base_url = 'https://markets.businessinsider.com/'
    _target_span_class_name = "price-section__current-value"
    _max_wait_time = 100

    def __int__(self, dir_url, price_name):
        self._dir_url = dir_url
        self._price_name = price_name

    def extract(self):
        with SeleniumDriver(service_args=['--ignore-ssl-errors=true']) as driver:
            wait = WebDriverWait(driver, self._max_wait_time)
            while True:
                obtained_price = self._browse_site(driver)
                logger.info('Time: {}, Price: ${}'.format(
                    datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%M-%d %h:%m:%s'),
                    str(obtained_price)
                ))
                wait.until(
                    PresenceOfAnyElements(
                        (By.CLASS_NAME, self._target_span_class_name),
                        [
                            'price-section__current-value--negative-updated',
                            'price-section__current-value--positive-updated'
                        ]
                    )

                )

    def _browse_site(self, driver: SeleniumDriver) -> float:
        full_url = urljoin(self._base_url, self._dir_url)
        driver.get(full_url)
        price_span = driver.find_elements_by_xpath(
            '//span[contains(@class, {})]'.format(self._target_span_class_name)
        )
        price_content = price_span.get_attribute('innerHTML')
        price_match_result = re.search(r'"(\d+\.\d+)"', price_content)
        if not price_match_result:
            logger.error('Failed to obtain price for ', self._price_name)
        price = float(price_match_result.group(1))
        return price
