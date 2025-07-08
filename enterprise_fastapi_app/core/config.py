from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Enterprise Example"
    PROJECT_VERSION: str = "1.0.0"


settings = Settings() 