from pydantic import BaseSettings


class Settings(BaseSettings):
    source_url: str = 'https://habr.com/'
    host: str = '0.0.0.0:8000'
    word_len: int = 6

    class Config:
        env_file = 'config.env'


settings = Settings()
