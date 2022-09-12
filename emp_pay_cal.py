"""
Project for TBROS employees salary calculator and employee person info
"""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

# 自身库
from emp_mongodb import EmpInfo
from mongodb import MongoDB


class ReadExcel:
    """读取Excel文件"""
    def __init__(self, filename) -> None:
        self._sheet_num = 2
        self._filename = filename

        self._df = pd.read_excel(self._filename, sheet_name=self._sheet_num)
        self._date = datetime.strptime(self._df.loc[1][2].split(" ")[0], "%Y-%m-%d")

    def get_day(self) -> list[int]:
        """抓取时间的数字"""
        day_list = [x for x in self._df.loc[2]]
        if 31 not in day_list:
            return day_list[:15]
        else:
            return day_list[:16]

    def get_name(self) -> list[str]:
        """把所有名字变为列表"""
        column_list_name = [i for i in self._df.columns]
        get_name_list = self._df.loc[3::2][column_list_name[10]]  # col and row number
        name_list = [i.lower() for i in get_name_list]
        return name_list

    def get_time(self, row_num: int) -> list[str, int]:
        """获取名字和时间"""
        store_time = []
        get_time_from_excel = [
            0 if str(x) == "nan" else x for x in self._df.loc[row_num]
        ]
        for each_time in get_time_from_excel:
            if each_time == 0:
                store_time.append(0)
            else:
                if len(each_time) <= 5:
                    store_time.append([each_time])
                else:
                    store_time.append([each_time[0:5], each_time[-5:]])
        return store_time

    def get_all_list(self) -> dict:
        """输出全部列表"""
        all_list = {}
        num = 4
        for show_name in self.get_name():
            all_list[show_name] = self.get_time(num)
            num += 2

        # Delete none working emp
        del_emp_no_working = []
        for key, value in all_list.items():
            if all(elem == 0 for elem in value):
                del_emp_no_working.append(key)
        for i in del_emp_no_working:
            del all_list[i]

        return all_list


class TimeCal:
    """Time Calculator"""
    def __init__(self, emp_time, emp_salary) -> None:
        self.emp_time: list = emp_time
        self.emp_salary: float = emp_salary
        self.emp_pay: int = 0

    def result(self, num):
        """功能：计算时间，把时间换成工资计算"""
        if self.emp_time[num] == 0:
            return 0

        elif len(self.emp_time[num]) < 2:
            return 0

        # elif type(self.emp_time[num]) == list:
        elif isinstance(self.emp_time[num], list):
            # c_time = lambda t: datetime.strptime(t, "%H:%M")
            def c_time(time_input):
                time_output = datetime.strptime(time_input, "%H:%M")
                return time_output

            emp_in = c_time(self.emp_time[num][0])
            emp_out = c_time(self.emp_time[num][-1])
            day_in = c_time("08:35")
            day_out = c_time("17:25")

            lunch_time = 1  # Lunch Time

            # lv1_overtime = timedelta(minutes=45)  # 17:30 - 22:00
            # lv2_overtime = timedelta(minutes=40)  # 22:00 - End

            # Day Time Work Hour
            if emp_in < day_in and emp_out > day_out:  # Full day
                self.emp_pay += 8
            elif emp_in > day_in and emp_out > day_out:  # Late come until 17:30
                temp = str(day_out - emp_in)[0:4]
                # print(temp)
                if c_time(temp).hour > 5:
                    self.emp_pay += c_time(temp).hour - lunch_time
                    if c_time(temp).minute > 30:
                        self.emp_pay += 1
                else:
                    self.emp_pay += c_time(temp).hour
                    if c_time(temp).minute > 30:
                        self.emp_pay += 1
            elif emp_in < day_in and emp_out < day_out:  # Early Come Early Out
                temp = str(emp_out - day_in)[0:4]
                # print(temp)
                if c_time(temp).hour > 5:
                    self.emp_pay += c_time(temp).hour - lunch_time
                    if c_time(temp).minute > 30:
                        self.emp_pay += 1
                else:
                    self.emp_pay += c_time(temp).hour
                    if c_time(temp).minute > 30:
                        self.emp_pay += 1
            elif emp_in > day_in and emp_out < day_out:  # Early Come Early Out
                temp = str(emp_out - emp_in)[0:4]
                # print(temp)
                if c_time(temp).hour > 5:
                    self.emp_pay += c_time(temp).hour - lunch_time
                    if c_time(temp).minute > 30:
                        self.emp_pay += 1
                else:
                    self.emp_pay += c_time(temp).hour
                    if c_time(temp).minute > 30:
                        self.emp_pay += 1

            # OverTime
            if emp_out >= c_time("18:55"):
                self.emp_pay += 2

            if emp_out >= c_time("21:55"):
                self.emp_pay += 4

            if emp_out >= c_time("23:55"):
                self.emp_pay += 3

            return self.emp_pay * self.emp_salary


class FileCal:
    """Final class to work"""
    def __init__(self, filename) -> None:
        self.data = {}
        self.filename = filename
        self.send_to_mongodb()

    def main(self, name: str) -> None:
        """执行所有的操作"""

        read_excel = ReadExcel(self.filename)
        _day = read_excel.get_day()

        get_all_list = read_excel.get_all_list()

        # check_name_list = [i for i in get_all_list]
        # print(check_name_list)

        emp = EmpInfo().emp_one(name)

        emp_sum_salary = []
        daily_salary = emp["daily_salary"]
        hour_salary = daily_salary / 8

        send_to_mongodb = []
        for index, day in enumerate(_day):
            time_cal = TimeCal(emp_time=get_all_list[name], emp_salary=hour_salary)
            pay_day_cost = time_cal.result(index)
            emp_sum_salary.append(pay_day_cost)

            send_to_mongodb.append(
                {
                    "day": day,
                    "pay_perday": pay_day_cost,
                    "work_time": time_cal.emp_time[index],
                }
            )

        # Store to data
        store_data = {
            "daily_salary": daily_salary,
            "total_salary": sum(emp_sum_salary),
            "output": send_to_mongodb,
        }
        self.data[name.title()] = store_data

    def send_to_mongodb(self):
        """main"""
        get_emp_name = EmpInfo().emp_info()
        emp_name = [x["_id"] for x in get_emp_name]

        # Final Output
        # Catch all emp info incluse salary
        for each_emp in emp_name:
            self.main(each_emp)

        # Send to mongoDB database
        read_excel = ReadExcel(self.filename)
        _day = read_excel.get_day()
        _month = read_excel._date.month  # pylint: disable=W0212
        
        mongodb = MongoDB()
        work_hour_collection = mongodb.work_hour_collection()
        send_data = {
            "_id": f"{_month}-{_day[0]}",
            "emp_work_hours": self.data
        }
        work_hour_collection.insert_one(send_data)

        # Test single person
        # main("alom")
        # print(self.data)

# Test------------------------------------------------------------------------
# e = ReadExcel()
# print(e.get_day())
# print(e.get_name())
# print(e.get_time(8))
# print(len(e.get_all_list()))

# Real Output ----------------------------------------------------------------
# a = FileCal("data/8/1_StandardReport.xls")
# a.send_to_mongodb()
