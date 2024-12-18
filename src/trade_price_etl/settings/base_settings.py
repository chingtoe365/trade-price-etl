import logging

from pydantic_settings import BaseSettings

from trade_price_etl.settings.extractor_settings import ExtractorSettings
from trade_price_etl.settings.log_settings import LoggingSettings
from trade_price_etl.settings.mqtt_settings import MqttSettings
from trade_price_etl.settings.redis_settings import RedisSettings
from trade_price_etl.settings.signal_settings import SignalSettings

logger = logging.getLogger(__name__)


class EtlSettings(BaseSettings, case_sensitive=True):

    MQTT: MqttSettings = MqttSettings()

    REDIS: RedisSettings = RedisSettings()

    LOGGING: LoggingSettings = LoggingSettings()

    EXTRACTOR: ExtractorSettings = ExtractorSettings()

    SIGNAL: SignalSettings = SignalSettings()

    DEBUG: bool = False
    DEBUG_WEEKEND: bool = False
    MP_CALCULATOR_WORKERS: int = 3


settings = EtlSettings()
logger.info(settings)