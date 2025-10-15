from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field
from pydantic.types import SecretStr


class JWTSettings(BaseModel):
    secret_key: SecretStr
    algorithm: str
    access_token_ttl: int


class GlobalSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_nested_delimiter='__'
    )
    DATABASE_URL: str
    jwt: JWTSettings = Field(default_factory=JWTSettings)


config = GlobalSettings()
