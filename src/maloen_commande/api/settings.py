from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: PostgresDsn = Field(
        PostgresDsn(url="postgresql+psycopg2://commande:commande@localhost/commande")
    )

    model_config = SettingsConfigDict(env_prefix="maloen_commande_")


settings = Settings.model_validate({})
