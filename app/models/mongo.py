import pendulum
from config.settings import settings
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


class MongoDB:
    def __init__(self, name) -> None:
        # Local Testing MongoDB-------------------------------
        # self.client = MongoClient(settings.DB_LOCAL, serverSelectionTimeoutMS=3000)
        self.client = MongoClient(settings.DB_URL, serverSelectionTimeoutMS=3000)

        # member info
        self.user_info = self.client["USER_INFO"]
        # company info
        self.user_data = self.client[name]

    # db status
    def status(self):
        """DB status"""
        try:
            server_info = self.client.server_info()
            if server_info["ok"] == 1.0:
                return True
        except ServerSelectionTimeoutError:
            return False

    def collection_list(self):
        collection_name = self.client.list_database_names()
        result = [name.lower() for name in collection_name]
        return result

    # user data section
    def user_collection(self):
        """User Data"""
        return self.user_info["USER-data"]

    # member register using company name as db collection
    # after user login
    def emp_info_collection(self):
        """链接至 emp-info"""
        return self.user_data["info"]

    def emp_work_hour_collection(self, db_year: str):
        """链接至 emp-<年份>"""
        return self.user_data[f"{db_year}"]

    def collection_name(self):
        collection_detail: dict[str] = {}
        db_collection_name = self.user_data.list_collection_names()

        for name in db_collection_name:
            if name.isnumeric():
                collection = self.emp_work_hour_collection(name)

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
                collection_detail[name] = re_arrange_date

        return collection_detail
