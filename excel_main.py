"""
Main work for work with exce lfil
"""

from emp_mongodb import EmpInfo
from excel_module import ReadExcel, TimeCalculation
from mongodb import MongoDB


class EmpSalary:
    """这是最终到处所有计算后的数据"""
    def __init__(self, filename) -> None:
        self.data = {}
        self.filename = filename

        # 读取导入的文件
        self.read_excel = ReadExcel(self.filename)

        # 读取文件的日和月
        self._name = self.read_excel.get_name()
        self._day = self.read_excel.get_day()
        self._month = self.read_excel._date.month

        # 读取 EmpInfo 的数据
        self.EMPINFO = EmpInfo()

        # 执行 main 功能 / time 部分可以删除
        import time
        start_time = int(time.time())
        self.main()
        end_time = int(time.time())
        print(end_time - start_time)

    def make_emp_info(self, name: str) -> None:
        """执行所有的操作"""
        get_all_list = self.read_excel.generate_all()
        emp = self.EMPINFO.emp_one(name)

        emp_sum_salary = []
        daily_salary = emp["daily_salary"]
        hour_salary = daily_salary / 8

        send_to_mongodb = []
        for index, day in enumerate(self._day):
            time_cal = TimeCalculation(emp_time=get_all_list[name], emp_salary=hour_salary)
            pay_day_cost = time_cal.result(index)
            emp_sum_salary.append(pay_day_cost)

            send_to_mongodb.append(
                {
                    "day": day,
                    "pay_perday": pay_day_cost,
                    "work_time": time_cal.emp_time[index],
                }
            )

        # 存于 MongoDB 的格式
        store_data = {
            "daily_salary": daily_salary,
            "total_salary": sum(emp_sum_salary),
            "output": send_to_mongodb,
        }
        self.data[name.title()] = store_data

    def main(self):
        """导出至 MongoDB"""
        get_emp_name = self.EMPINFO.emp_info()
        emp_name = [x["_id"] for x in get_emp_name]

        # 最终输出，计算没人的基本工资
        for each_emp in emp_name:
            try:
                self.make_emp_info(each_emp)
            except KeyError:
                continue

        # 上传至 MongoDB
        # mongodb = MongoDB()
        # work_hour_collection = mongodb.work_hour_collection()
        # send_data = {
        #     "_id": f"{self._month}-{self._day[0]}",
        #     "emp_work_hours": self.data
        # }
        # work_hour_collection.insert_one(send_data)

        # 测试输出
        # print(self.data)

        # import pandas as pd
        # list_name = self.read_excel.get_name()
        # list_1 = pd.DataFrame(list_name)
        # list_1.to_excel("test.xlsx")
