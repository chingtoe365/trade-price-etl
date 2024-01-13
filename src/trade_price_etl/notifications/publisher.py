import datetime
import logging
from typing import Dict

import paho.mqtt.publish as mqtt_publish

from multiprocessing import Array, Manager
from trade_price_etl.settings.base_settings import settings


logger = logging.getLogger(__name__)

# mp_manager = Manager()
# _LAST_EMISSIONS = mp_manager.dict()
# _LAST_EMISSIONS = {}

# _LAST_EMISSIONS = Array('last_emission', )


def freeze_or_emit(last_emissions: Dict, topic: str, frozen_duration: int) -> bool:
    """ Return decision to freeze or emit signals, if True emit else freeze

    @param last_emissions: sharable dictionary recording last emissions for all signals
    @param topic: topic to be emitted to it is consisted of price item and signal name
    @param frozen_duration: emission even frozen duration since last, in seconds
    @return: True to emit Flase do nothing (freeze)
    """
    to_emit = False
    last_emit = last_emissions.get(topic, None)
    # logger.debug(_LAST_EMISSIONS)
    now = datetime.datetime.now()
    # logger.debug(now.strftime("%H:%M:s"))
    if last_emit:
        elapsed = now - last_emit
        # logger.debug(elapsed.seconds)
        if elapsed.seconds > frozen_duration:
            last_emissions[topic] = now
            to_emit = True
    else:
        last_emissions[topic] = now
        to_emit = True
    return to_emit


def publish(last_emits: Dict, topic: str, message: str, frozen_duration: int) -> None:
    """ Publish a message to MQTT

    @param last_emits:
    @param topic:
    @param message:
    @param frozen_duration: emission even frozen duration since last, in seconds
    @return:
    """
    if freeze_or_emit(last_emits, topic, frozen_duration):
        mqtt_publish.single(
            topic,
            message,
            hostname=settings.MQTT_HOST
        )
        logger.info("Published message '%s' to topic '%s'", message, topic)
        # logger.debug("Current last emission dict >>> ")
        # logger.debug(last_emits)
