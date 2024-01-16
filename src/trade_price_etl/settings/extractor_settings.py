from pydantic_settings import BaseSettings, SettingsConfigDict


class ExtractorSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix='EXTRACTOR_')

    POLL_FREQUENCY_SINGLE_TABLE: int = 1
    POLL_FREQUENCY_MULTIPLE_TABLES: int = 1
    POLL_FREQUENCY_SINGLE_TABLE_SLOW: int = 5
    POLL_FREQUENCY_MULTIPLE_TABLES_SLOW: int = 5
    BLOCKADE_STOPPAGE_WAIT: int = 20
