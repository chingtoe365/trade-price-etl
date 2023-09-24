import logging

from trade_price_etl.calculators.base import CalculatorBase
from trade_price_etl.notifications.publisher import publish

logger = logging.getLogger(__name__)


class DoublePegSignal(CalculatorBase):

    metric_name = 'double_peg'

    def compute(cls, price_item, df, mqtt_client):
        # only calculate from the last 50 price points
        df = df[-50:]
        if len(df['price'].unique()) < 4:
            logger.warning(f">> Double Peg appears in {price_item}")
            # TODO: get all topics (with user specification) created from core and push to all of them
            publish(mqtt_client, f"{price_item}_{cls.metric_name}", 1)
