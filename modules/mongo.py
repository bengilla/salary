"""
MongoDB connect system
Create collection system
"""

import datetime as dt
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

class MongoDB:
    """链接 MongoDB"""

    def __init__(self) -> None:
        load_dotenv()

        try:
            # Local Testing MongoDB-------------------------------
            self.conn = MongoClient(host=[os.getenv('MONGODB_LOCAL')], serverSelectionTimeoutMS=2000)
        except ServerSelectionTimeoutError:
            # Real Server MongoDB --------------------------------
            # self.conn = MongoClient(host=[os.getenv('MONGODB_URL')])
            print("online host")

        self.user_info = self.conn["USER_INFO"]
        self.user_data = self.conn["USER_DATA"]

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
