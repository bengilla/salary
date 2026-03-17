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
        # Local Testing MongoDB
        # conn = MongoClient(host="127.0.0.1", port=27017)

        # Real Server MongoDB
        load_dotenv()
        conn = MongoClient(
            host=os.getenv("DB_URL"),
            serverSelectionTimeoutMS=5000,
        )

        # Collection
        self.collection = conn["TBROSVENTURESSDNBHD"]

    def info_collection(self):
        """
        链接至 emp-info
        """
        return self.collection["info"]

    def work_hour_collection(self):
        """
        链接至 emp-<年份>
        """
        return self.collection[f"{dt.datetime.now().year}"]

    def all_work_hour_collections(self):
        """
        获取所有年份的工作时间集合
        """
        all_collections = self.collection.list_collection_names()
        return [self.collection[name] for name in all_collections if name.isdigit()]

    def find_in_all_years(self, doc_id: str):
        """
        在所有年份集合中查找文档 (支持日期或ObjectId)
        """
        from bson.objectid import ObjectId

        # Try as ObjectId first
        try:
            oid = ObjectId(doc_id)
            for coll in self.all_work_hour_collections():
                doc = coll.find_one({"_id": oid})
                if doc:
                    return doc
        except Exception:
            pass
        # Try as date string
        for coll in self.all_work_hour_collections():
            doc = coll.find_one({"date": doc_id})
            if doc:
                return doc
        return None
