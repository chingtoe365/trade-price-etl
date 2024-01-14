from pydantic_settings import BaseSettings, SettingsConfigDict


class ExtractorSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix='EXTRACTOR_')
