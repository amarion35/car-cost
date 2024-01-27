from pydantic_settings import BaseSettings, SettingsConfigDict

from car_cost.settings.database_settings import DatabaseSettings


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    database_settings: DatabaseSettings
