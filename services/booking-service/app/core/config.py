from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Booking Service"
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field("supersecretkey123", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    PAYMENT_SERVICE_URL: str = Field(
        "http://payment-service:8003",
        env="PAYMENT_SERVICE_URL",
    )
    PAYMENT_TIMEOUT_SECONDS: float = Field(10.0, env="PAYMENT_TIMEOUT_SECONDS")
    RABBITMQ_URL: str = Field(
        "amqp://guest:guest@rabbitmq:5672/",
        env="RABBITMQ_URL",
    )
    RABBITMQ_CONNECT_RETRIES: int = Field(30, env="RABBITMQ_CONNECT_RETRIES")
    RABBITMQ_CONNECT_DELAY_SECONDS: int = Field(
        3,
        env="RABBITMQ_CONNECT_DELAY_SECONDS",
    )
    ACTIVITY_EXCHANGE: str = Field("activity.events", env="ACTIVITY_EXCHANGE")
    ACTIVITY_ROUTING_KEY: str = Field("activity.booking", env="ACTIVITY_ROUTING_KEY")
    PAYMENT_EXCHANGE: str = Field("payment.events", env="PAYMENT_EXCHANGE")
    PAYMENT_QUEUE: str = Field("booking-service.payments", env="PAYMENT_QUEUE")
    PAYMENT_ROUTING_KEY: str = Field("payment.#", env="PAYMENT_ROUTING_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
