"""MongoDB Section"""
import pendulum
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from config.settings import settings


class CodeDB:
    def __init__(self) -> None:
        self.code = MongoClient(settings.CODE_URL)

    def verify_code(self) -> list:
        return self.code["temp_code"]


class MongoDB:
    """使用MongoDB的服务"""

    def __init__(self, name) -> None:
        # Local Testing MongoDB-------------------------------
        # self.client = MongoClient(settings.DB_LOCAL, serverSelectionTimeoutMS=3000)
        self.client = MongoClient(settings.DB_URL, serverSelectionTimeoutMS=3000)

        # member info
        self.user_info = self.client["SALARY_USER_INFO"]
        # company info
        self.user_data = self.client[name]
        # get code for 5 minutes
        self.code = self.client["CODE"]

    # db status
    def status(self) -> bool:
        """检查mongodb是否连线"""
        try:
            server_info = self.client.server_info()
            if server_info["ok"] == 1.0:
                return True
        except ServerSelectionTimeoutError:
            return False

    def collection_list(self):
        """生成collection里面的名单"""
        collection_name = self.client.list_database_names()
        result = [name.lower() for name in collection_name]
        return result

    # user data section
    def user_collection(self):
        """这是用户注册跟员工部分无关"""
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
        """???"""
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
