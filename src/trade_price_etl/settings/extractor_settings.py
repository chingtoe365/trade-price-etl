from pydantic_settings import BaseSettings, SettingsConfigDict


class ExtractorSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix='EXTRACTOR_')

    POLL_FREQUENCY_SINGLE_TABLE: int = 5
    POLL_FREQUENCY_MULTIPLE_TABLES: int = 3
    BLOCKADE_STOPPAGE_WAIT: int = 20
