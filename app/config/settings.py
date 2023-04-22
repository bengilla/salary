"""Settings Section"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Setting Class"""

    TITLE = "Employee System"
    VERSION = "0.1"
    DESCRIPTION = "Hello World"

    LOGIN_TITLE = "Employee work system - Login"
    REGISTER_TITLE = "Employee work system - Register"

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    TOKEN_TIMEOUT = os.getenv("TOKEN_TIMEOUT")

    DB_LOCAL = os.getenv("DB_LOCAL")
    DB_URL = os.getenv("DB_URL")

    CODE_URL = os.getenv("CODE_URL")


settings = Settings()
