import os
import pendulum
from config.settings import settings
from pymongo import MongoClient


class MongoDB:
    def __init__(self) -> None:
        # Local Testing MongoDB-------------------------------
        # client = MongoClient(settings.DB_LOCAL)
        client = MongoClient(os.environ["DB_LOCAL"])

        self.user_info = client["USER_INFO"]
        self.user_data = client["USER_DATA"]

    # user data section
    def user_collection(self):
        """User Data"""
        return self.user_info["USER-data"]

    # After user login
    def emp_info_collection(self, db_title: str):
        """链接至 emp-info"""
        return self.user_data[db_title + "-info"]

    def emp_work_hour_collection(self, db_title: str, db_year: str):
        """链接至 emp-<年份>"""
        return self.user_data[f"{db_title}-{db_year}"]

    def collection_name(self, db_title: str):
        collection_detail: dict[str] = {}
        db_collection_name = self.user_data.list_collection_names()

        for name in db_collection_name:
            split_name = name.split("-")
            title = split_name[0]
            year = split_name[1]

            if db_title == title and year.isnumeric():
                collection = self.emp_work_hour_collection(title, year)

                # get date
                get_date = [col["date"] for col in collection.find({})]
                result_date = []
                for date in get_date:
                    result = pendulum.from_format(date, "DD-MMM-YYYY")
                    result_date.append(result)

                result_date.sort()

                # turn back to 01-Jan-1111
                re_arrange_date = [date.format("DD-MMM-YYYY") for date in result_date]

                # store to collection_detail
                collection_detail[year] = re_arrange_date

        return collection_detail
