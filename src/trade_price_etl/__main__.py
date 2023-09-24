import asyncio
import logging
from multiprocessing import Pool

from trade_price_etl.calculators.sig_doube_peg import DoublePegSignal
from trade_price_etl.extractors.bases.web_scrapers.trading_economics import TradingEconomicsScraperBase
from trade_price_etl.notifications.publisher import connect_mqtt
from trade_price_etl.storage.real_time_metric import RTMS
from trade_price_etl.storage.real_time_price import RTS

logger = logging.getLogger(__name__)
COMPUTE_FREQUENCY = 0.5
METRICS = {
    'double_peg': DoublePegSignal
}


async def streamline_extractors():
    crypto_extractor = TradingEconomicsScraperBase('crypto', 0, 'Crypto')
    await crypto_extractor.extract()


async def streamline_calculators():
    client = connect_mqtt()
    client.loop_start()
    with Pool(processes=16) as p:
        while True:
            await asyncio.sleep(COMPUTE_FREQUENCY)
            all_price_dfs = RTS.get_data()
            for _, klass in METRICS.items():
                p.map(klass.compute, ((price, all_price_dfs[price]) for price in all_price_dfs))


async def run_pipelines():
    await streamline_extractors()
    await streamline_calculators()
    while True:
        await asyncio.sleep(0.5)
        RTMS.flag()


def main():
    asyncio.run(run_pipelines())


main()
