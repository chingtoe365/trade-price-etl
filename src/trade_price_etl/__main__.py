import asyncio
import logging
import time
import threading

from trade_price_etl.calculators.sig_doube_peg import DoublePegSignal
from trade_price_etl.extractors.bases.web_scrapers.markets_insiders import MarketsInsiderScraperBase
from trade_price_etl.extractors.bases.web_scrapers.trading_economics import TradingEconomicsScraperBase
from trade_price_etl.storage.real_time_metric import RTMS

logger = logging.getLogger(__name__)


async def streamline_extractors():
    crypto_extractor = TradingEconomicsScraperBase('crypto', 0, 'Crypto')
    await crypto_extractor.extract()


async def streamline_calculators():
    dp_calculator = DoublePegSignal()
    await dp_calculator.compute()


async def run_pipelines():
    await streamline_extractors()
    await streamline_calculators()
    while True:
        await asyncio.sleep(0.5)
        RTMS.flag()


def main():
    asyncio.run(run_pipelines())


main()
