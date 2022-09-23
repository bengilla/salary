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
        try:
            load_dotenv()
            conn = MongoClient(
                f"mongodb+srv://bengilla:{os.getenv('PASSWORD')}@cluster0.uhsmo.mongodb.net/?retryWrites=true&w=majority"
            )
            print(conn)
            # conn = MongoClient("127.0.0.1:27017")
            self.db = conn["TBROS"]
        except Exception as err:  # pylint: disable=broad-except
            print(err)

    def info_collection(self):
        """
        链接至 emp-info
        """
        return self.db["emp-info"]

    def work_hour_collection(self):
        """
        链接至 emp-<年份>
        """
        return self.db[f"emp-{dt.datetime.now().year}"]
