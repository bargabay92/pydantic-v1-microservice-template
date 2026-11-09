from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "orders-service"
    database_url: str = "sqlite:///./orders.db"
    max_items_per_order: int = Field(50, gt=0)
    debug: bool = False
    model_config = SettingsConfigDict(env_prefix="ORDERS_", case_sensitive=False)


settings = Settings()
