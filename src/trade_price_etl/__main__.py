import asyncio
import logging
import sys
from multiprocessing import Pool

from trade_price_etl.calculators.sig_doube_peg import DoublePegSignal
from trade_price_etl.calculators.sig_volatile import VolatileSignal
from trade_price_etl.extractors.bases.web_scrapers.trading_economics import TradingEconomicsScraperBase
from trade_price_etl.storage.real_time_metric import RTMS
from trade_price_etl.storage.real_time_price import RTS

logger = logging.getLogger(__name__)
COMPUTE_FREQUENCY = 3
METRICS = {
    'double_peg': DoublePegSignal,
    'volatile': VolatileSignal
}


# def mp_debug(a, b, *args, **kwargs):
def mp_debug(a, b):
    logger.debug(f">> Calling this function in multiple processors")
    logger.debug(f">> A: {a}")
    logger.debug(f">> B: {b}")
    # logger.debug(f">> Args: {args}")


async def streamline_extractors():
    # crypto_extractor = TradingEconomicsScraperBase('crypto', 0, 'Crypto')
    energy_extractor = TradingEconomicsScraperBase('commodities', 0, 'Energy')
    metal_extractor = TradingEconomicsScraperBase('commodities', 1, 'Metals')
    agriculture_extractor = TradingEconomicsScraperBase('commodities', 2, 'Agricultural')
    industrial_extractor = TradingEconomicsScraperBase('commodities', 3, 'Industrial')
    forex_extractor = TradingEconomicsScraperBase('currencies', 0, 'Major')
    # await crypto_extractor.extract()
    asyncio.gather(
        # crypto_extractor.extract(),
        energy_extractor.extract(),
        metal_extractor.extract(),
        agriculture_extractor.extract(),
        industrial_extractor.extract(),
        forex_extractor.extract()
    )
    # await crypto_extractor.extract()


async def streamline_calculators():
    logger.debug(f">> Live calculator is on")
    with Pool(processes=2) as p:
        while True:
            await asyncio.sleep(COMPUTE_FREQUENCY)
            all_price_dfs = RTS.get_data()
            # logger.debug(f">> All price dataframes: {all_price_dfs}")
            if all_price_dfs:
                # logger.debug(f"Some data has been stored")
                for metric, klass in METRICS.items():
                    # logger.debug(f"Metric to assign tasks: {metric}")
                    p.starmap(
                        klass.compute,
                        [
                            (price, all_price_dfs[price]) for price in all_price_dfs
                        ]
                    )
                    # logger.debug(f"Multiprocessing jobs assignment completed")


async def run_pipelines():
    extract_task = asyncio.create_task(streamline_extractors())
    calculate_task = asyncio.create_task(streamline_calculators())
    await extract_task
    await calculate_task
    # while True:
    #     await asyncio.sleep(0.5)
    #     RTMS.flag()


def main():
    asyncio.run(run_pipelines())


sys.exit(main())
