import logging
from typing import Dict

import pandas as pd

from trade_price_etl.calculators.base import CalculatorBase
from trade_price_etl.constants.constants import Metrics, MetricsShortDescription
from trade_price_etl.notifications.publisher import publish
from trade_price_etl.utils.utils import build_mqtt_topic

logger = logging.getLogger(__name__)


class DoublePegSignal(CalculatorBase):

    metric_name = 'double_peg'

    @classmethod
    def compute(cls, price_item: str, df: pd.DataFrame, last_emissions: Dict):
        # logger.debug(f">> Computing metric: {cls.metric_name} item: {price_item}")
        # only calculate from the last 50 price points
        df = df[-50:]
        # if len(df) > 20 and len(df['price'].unique()) < 4:
        if len(df) > 20 and len(df['price'].unique()) < 4:
            topic = build_mqtt_topic(price_item, str(Metrics.DOUBLE_PEG))
            logger.warning(f">> Double Peg appears in {price_item}")
            # TODO: get all topics (with user specification) created from core and push to all of them
            publish(
                last_emissions,
                topic,
                f"{MetricsShortDescription.DOUBLE_PEG}",
                120
            )
