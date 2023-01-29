"""
MongoDB connect system
Create collection system
"""

import datetime as dt
import os

from dotenv import load_dotenv
import motor.motor_asyncio as motor

class MongoDB:
    """Connect MongoDB"""

    def __init__(self) -> None:
        load_dotenv()

        # Local Testing MongoDB-------------------------------
        client = motor.AsyncIOMotorClient(os.environ["DB_URL"])
        # client = motor.AsyncIOMotorClient(os.getenv("DB_LOCAL"))

        # Real Server MongoDB --------------------------------
        # client = motor.AsyncIOMotorClient(os.getenv("DB_URL"))

        self.user_info = client["USER_INFO"]
        self.user_data = client["USER_DATA"]

    # user data section
    def user_collection(self):
        """User Data"""
        return self.user_info["USER-data"]

    # After user login
    def info_collection(self, db_title: str):
        """链接至 emp-info"""
        return self.user_data[db_title + "-info"]

    def work_hour_collection(self, db_title: str):
        """链接至 emp-<年份>"""
        return self.user_data[f"{db_title}-{dt.datetime.now().year}"]
