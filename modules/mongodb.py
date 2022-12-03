"""
MongoDB connect system
Create collection system
"""

import datetime as dt
import os

from dotenv import load_dotenv
from pymongo import MongoClient


class MongoDB:
    """链接 MongoDB"""

    def __init__(self) -> None:
        # Local Testing MongoDB-------------------------------
        self.conn = MongoClient(host="127.0.0.1", port=27017)

        # Real Server MongoDB --------------------------------
        # load_dotenv()
        # self.conn = MongoClient(
        #     host=[
        #         f"mongodb+srv://bengilla:{os.getenv('PASSWORD')}@cluster0.uhsmo.mongodb.net/?retryWrites=true&w=majority"
        #     ],
        #     serverSelectionTimeoutMS=5000,
        # )

        self.collection = self.conn[os.getenv("USER_CONFIRM")]

    def user_collection(self):
        """会员资料"""
        collection = self.conn["USER_DATA"]
        return collection["users"]

    def info_collection(self):
        """链接至 emp-info"""
        return self.collection["emp-info"]

    def work_hour_collection(self):
        """链接至 emp-<年份>"""
        return self.collection[f"emp-{dt.datetime.now().year}"]
