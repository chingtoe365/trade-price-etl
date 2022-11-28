import logging

from trade_price_etl.extractors.bases.web_scrapers.markets_insiders import MarketsInsiderScraperBase
from trade_price_etl.extractors.bases.web_scrapers.trading_economics import TradingEconomicsScraperBase

logger = logging.getLogger(__name__)


def streamline_extractors():
    crypto_extractor = TradingEconomicsScraperBase('crypto', 0, 'Crypto')
    crypto_extractor.extract()


def main():
    streamline_extractors()


main()
