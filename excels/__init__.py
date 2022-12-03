"""
Main work for work with exce lfil
"""

import pendulum

from emp import EmpInfo
from excels.excel_module import ReadExcel, TimeCalculation
from modules.mongodb import MongoDB


class EmpSalary:
    """这是最终到处所有计算后的数据"""

    def __init__(self, filename) -> None:
        self.data = {}
        self.filename = filename

        # 读取导入的文件
        self.read_excel = ReadExcel(self.filename)

        # 读取文件的日和月
        self._name: list = self.read_excel.get_name()  # Get all name in excel (list)
        self._month: int = self.read_excel._date.month  # Get month in excel
        self._day: list = self.read_excel.get_day()  # Get day uin excel (list)

        self._date_from_readexcel: str = (
            self.read_excel._date.date()
        )  # Get full date in excel
        self._date = pendulum.datetime(
            self._date_from_readexcel.year,
            self._date_from_readexcel.month,
            self._date_from_readexcel.day,
        )  # Turn date to pendulum format

        # 读取全部列表
        self._get_all_list = (
            self.read_excel.generate_all()
        )  # Get name and work hours in dict

        # 执行 main 功能
        self.main()

    def find_no_emp(self) -> list:
        """Find who not in excel file"""
        # 列出没有名字在网站的，等于说没有这个人的工资/天
        _empinfo = EmpInfo()
        emp_on_web = [x["name"].lower() for x in _empinfo.emp_info()]
        emp_on_excel = [x for x in self._name]
        not_register = [x for x in emp_on_excel if x not in emp_on_web]
        return not_register

    def make_emp_info(self, name: str) -> None:
        """执行所有的操作"""
        _empinfo = EmpInfo()
        emp = _empinfo.emp_one(name)

        emp_sum_salary = []
        pay_hour = emp["pay_hour"]
        total_work_hours = []

        send_to_mongodb = []
        for index, day in enumerate(self._day):
            time_cal = TimeCalculation(
                emp_time=self._get_all_list[name], emp_salary=pay_hour
            )
            pay_day_cost = time_cal.result(index)
            emp_sum_salary.append(pay_day_cost)
            total_work_hours.append(time_cal.emp_work_hour)

            # 做星期几的列表
            day_of_week = pendulum.from_format(
                f"{self._month}-{self._day[index]}", "MM-DD"
            )

            send_to_mongodb.append(
                {
                    "day": day,
                    "day_of_week": day_of_week.format("dd"),
                    "pay_perday": pay_day_cost,
                    "work_time": time_cal.emp_time[index],
                    "daily_work_hours": time_cal.emp_work_hour,
                }
            )  # full list append to mongodb

            # round the salary amount
            sum_salary = round(sum(emp_sum_salary))
            balance = sum_salary % 10
            add_subtract = 10 - balance
            output_emp_salary = 0

            if balance > 5:
                output_emp_salary += sum_salary + add_subtract
            else:
                output_emp_salary += sum_salary - balance

        # 存于 MongoDB 的格式
        store_data = {
            "pay_hour": pay_hour,
            "total_salary": output_emp_salary,
            "total_work_hours": sum(total_work_hours),
            "output": send_to_mongodb,
        }
        self.data[name.title()] = store_data

    def main(self):
        """导出至 MongoDB"""
        _empinfo = EmpInfo()
        get_emp_name = _empinfo.emp_info()
        emp_name = [x["_id"] for x in get_emp_name]

        # 最终输出，计算没人的基本工资
        for each_emp in emp_name:
            try:
                self.make_emp_info(each_emp)
            except KeyError:
                continue

        # 上传至 MongoDB
        mongodb = MongoDB()
        work_hour_collection = mongodb.work_hour_collection()
        send_data = {
            "_id": self._date.format("MMM DD, YYYY"),
            "emp_work_hours": self.data,
        }
        work_hour_collection.insert_one(send_data)
