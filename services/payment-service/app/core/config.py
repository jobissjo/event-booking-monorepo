from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Payment Service"
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field("supersecretkey123", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    RABBITMQ_URL: str = Field(
        "amqp://guest:guest@rabbitmq:5672/",
        env="RABBITMQ_URL",
    )
    PAYMENT_EXCHANGE: str = Field("payment.events", env="PAYMENT_EXCHANGE")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
