from pydantic_settings import BaseSettings, SettingsConfigDict


class SignalSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix='SIGNAL_')

    COMPUTE_FREQUENCY: int = 3
    DOUBLE_PEG_TIME_SPAN: int = 50
    DOUBLE_PEG_MIN_DATA_POINT_LENGTH: int = 20
    DOUBLE_PEG_MAX_NUM_UNIQUE_PRICE: int = 4
    VOLATILITY_CUTOFF: float = 0.01
    FROZEN_WINDOW_DOUBLE_PEG: int = 120
    FROZEN_WINDOW_VOLATILITY_ONE_MINUTE: int = 180
    FROZEN_WINDOW_VOLATILITY_FIVE_MINUTE: int = 1500
