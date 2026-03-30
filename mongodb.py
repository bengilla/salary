"""
MongoDB connection system with local/remote switching
"""

import datetime as dt
import os

from dotenv import load_dotenv
from pymongo import MongoClient


class MongoDB:
    """MongoDB connection manager"""

    def __init__(self) -> None:
        load_dotenv()
        use_local = os.getenv("USE_LOCAL_DB", "false").lower() == "true"

        if use_local:
            self._client = MongoClient(host="127.0.0.1", port=27017)
        else:
            db_url = os.getenv("DB_URL")
            self._client = MongoClient(
                host=db_url,
                serverSelectionTimeoutMS=5000,
            )

        self._db = self._client["TBROSVENTURESSDNBHD"]

    @property
    def info_collection(self):
        """Employee info collection"""
        return self._db["info"]

    @property
    def work_hour_collection(self):
        """Current year work hours collection"""
        return self._db[f"{dt.datetime.now().year}"]

    def all_work_hour_collections(self):
        """Get all year-based work hour collections"""
        all_collections = self._db.list_collection_names()
        return [self._db[name] for name in all_collections if name.isdigit()]

    def find_in_all_years(self, doc_id: str):
        """Search document across all year collections by ObjectId or date"""
        from bson.objectid import ObjectId

        try:
            oid = ObjectId(doc_id)
            for coll in self.all_work_hour_collections():
                doc = coll.find_one({"_id": oid})
                if doc:
                    return doc
        except Exception:
            pass

        for coll in self.all_work_hour_collections():
            doc = coll.find_one({"date": doc_id})
            if doc:
                return doc
        return None


def get_mongodb():
    """Factory function for MongoDB instance"""
    return MongoDB()
