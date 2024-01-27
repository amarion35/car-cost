from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    username: str
    password: str
    cluster_name: str
