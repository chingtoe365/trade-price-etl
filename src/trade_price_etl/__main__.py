import logging

from trade_price_etl.extractors.bases.web_scrapers.markets_insiders import MarketsInsiderScraperBase
from trade_price_etl.extractors.bases.web_scrapers.trading_economics import TradingEconomicsScraperBase

logger = logging.getLogger(__name__)


def main():
    # btc_extractor = MarketsInsiderScraperBase(
    #     'currencies/btc-usd',
    #     'bitcoin'
    # )
    # btc_extractor.extract()
    btc_extractor = TradingEconomicsScraperBase('crypto', 0, 'Crypto')
    btc_extractor.extract()

main()

