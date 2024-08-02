from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='REDIS_')

    DB: int = 0
    HOST: str = 'localhost'
    PORT: int = 6379
    USER: str = ''
    PASSWORD: str = ''
    
    RETENTION_TIME: int = 86400000 # 1 day in millisecs