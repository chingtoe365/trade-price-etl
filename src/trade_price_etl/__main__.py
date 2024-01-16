import asyncio
import logging
import sys
from multiprocessing import Pool, Manager

from trade_price_etl.calculators.sig_doube_peg import DoublePegSignal
from trade_price_etl.calculators.sig_volatile import VolatileSignal
from trade_price_etl.extractors.web_scrapers.trading_economics_multi_table import TradingEconomicsMultiTableScraper
from trade_price_etl.extractors.web_scrapers.trading_economics_single_table import TradingEconomicsSingleTableScraper
from trade_price_etl.settings.base_settings import settings
from trade_price_etl.storage.real_time_price import RTS

logger = logging.getLogger(__name__)
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
    crypto_extractor = TradingEconomicsSingleTableScraper('crypto', 0, 'Crypto')
    commodity_extractor = TradingEconomicsMultiTableScraper(
        'commodities', 4, ['Energy', 'Metals', 'Agricultural', 'Industrial']
    )
    stock_extractor = TradingEconomicsMultiTableScraper(
        'stocks', 5, ['United States', 'Europe', 'America', 'Asia', 'Australia']
    )
    forex_extractor = TradingEconomicsSingleTableScraper('currencies', 0, 'Major')

    if settings.DEBUG_WEEKEND:
        asyncio.gather(
            crypto_extractor.extract()
        )
    else:
        asyncio.gather(
            commodity_extractor.extract(),
            forex_extractor.extract(),
            stock_extractor.extract()
        )


async def streamline_calculators():
    logger.debug(f">> Live calculator is on")
    with Pool(processes=settings.MP_CALCULATOR_WORKERS) as p, Manager() as manager:
        last_emissions = manager.dict()
        while True:
            await asyncio.sleep(settings.SIGNAL.COMPUTE_FREQUENCY)
            all_price_dfs = RTS.get_data()
            # logger.debug(f">> All price dataframes: {all_price_dfs}")
            if all_price_dfs:
                # logger.debug(f"Some data has been stored")
                for metric, klass in METRICS.items():
                    # logger.debug(f"Metric to assign tasks: {metric}")
                    p.starmap(
                        klass.compute,
                        [
                            (price, all_price_dfs[price], last_emissions) for price in all_price_dfs
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
