import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from trade_price_etl.settings.log_settings import LoggingSettings


logger = logging.getLogger(__name__)


class EtlSettings(BaseSettings, case_sensitive=True):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        # env_prefix='',
        extra='ignore',
        env_nested_delimiter='_'
    )

    # MQTT broker
    MQTT_HOST: str = ""
    MQTT_PORT: int = 0
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""

    LOGGING: LoggingSettings = LoggingSettings()


settings = EtlSettings()