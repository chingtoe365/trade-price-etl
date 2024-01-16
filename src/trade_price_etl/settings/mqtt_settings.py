from pydantic_settings import BaseSettings, SettingsConfigDict


class MqttSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix='MQTT_')

    HOST: str = ''
    PORT: int = 1
    USER: str = ''
    PASSWORD: str = ''
