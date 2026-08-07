from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = '.env',
        env_file_encoding='utf-8'
    )

    secret_key = SecretStr
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30

    urls_per_page: int = 15

    url_duration = 60
    url_rate_limit = 50

    mail_server: str = 'localhost'
    mail_port: int = 100
    mail_username: str = ''
    mail_password: SecretStr = SecretStr()
    mail_from: str = 'noreply@urlShortner.com'
    mail_use_tls: bool = True

    frontend_url: str = 'http://localhost:8000'


settings = Settings()


= Index(
    Filter(
        M:M,
        ISNUMBER(Search(B3,L:L)), 
        ISNUMBER(Sheet5!A3,Sheet5!L:Sheet5!G4), 
        "NA"
    )
)