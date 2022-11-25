import logging

from trade_price_etl.extractors.bases.web_scrapers.markets_insiders import MarketsInsiderScraperBase

logger = logging.getLogger(__name__)


def main():
    btc_extractor = MarketsInsiderScraperBase(
        'currencies/btc-usd',
        'bitcoin'
    )
    btc_extractor.extract()

main()

