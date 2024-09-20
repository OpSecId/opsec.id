from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "Open and Secure Identity Platform"
    PROJECT_VERSION: str = "v0"
    
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    MULTIKEY: str = os.environ["MULTIKEY"]

    DOMAIN: str = os.environ["DOMAIN"]
    ASKAR_DB: str = "sqlite://app.db"


settings = Settings()
