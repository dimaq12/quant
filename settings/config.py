"""Application configuration via Pydantic BaseSettings."""
#@module:
#@  layer: config
#@  depends: [pydantic]
#@  exposes: [Settings, settings]
#@  restrictions: []
#@end

from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    SYMBOL: str = Field("BTCUSDT", env="SYMBOL")
    RAW_BUFFER_MINUTES: int = Field(5, env="RAW_BUFFER_MINUTES")
    TRADES_PER_SEC: int = Field(50, env="TRADES_PER_SEC")
    MU_EPS: float = Field(1e-5, env="MU_EPS")
    SIGMA_LOW: float = Field(0.001, env="SIGMA_LOW")
    SIGMA_MED: float = Field(0.01, env="SIGMA_MED")
    SIGMA_HIGH: float = Field(0.05, env="SIGMA_HIGH")
    KAPPA_CRIT: float = Field(1.0, env="KAPPA_CRIT")
    TELEGRAM_TOKEN: str = Field(..., env="TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID: str = Field(..., env="TELEGRAM_CHAT_ID")

settings = Settings()  # singleton
