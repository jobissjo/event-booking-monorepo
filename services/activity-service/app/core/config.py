from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Activity Service"
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field("supersecretkey123", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    RABBITMQ_URL: str = Field(
        "amqp://guest:guest@rabbitmq:5672/",
        env="RABBITMQ_URL",
    )
    ACTIVITY_EXCHANGE: str = Field("activity.events", env="ACTIVITY_EXCHANGE")
    ACTIVITY_QUEUE: str = Field("activity-service", env="ACTIVITY_QUEUE")
    ACTIVITY_ROUTING_KEY: str = Field("activity.#", env="ACTIVITY_ROUTING_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
