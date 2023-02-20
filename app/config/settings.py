import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    TITLE = "Employee System"
    VERSION = "0.1"
    DESCRIPTION = "Hello World"

    LOGIN_TITLE = "Employee work system - Login"
    REGISTER_TITLE = "Employee work system - Register"

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    DB_LOCAL = os.getenv("DB_LOCAL")
    DB_URL = os.getenv("DB_URL")


settings = Settings()
