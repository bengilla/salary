"""
Project for TBROS employees salary calculator and employee person info
"""

from datetime import datetime as dt

import pandas as pd
import pendulum


class ReadExcel:
    """读取 excel 文件"""

    def __init__(self, filename):
        # 选择 excel 的第二页和 excel 文件名
        self._sheet_num = 2
        self._filename = filename

        # pandas 生成和生成日期
        self._df = pd.read_excel(self._filename, sheet_name=self._sheet_num)
        self._date = dt.strptime(self._df.loc[1][2].split(" ")[0], "%Y-%m-%d")

    def get_day(self):
        """读取 excel 文件的日期"""
        num_index = 0
        day_list = [int(x) for x in self._df.loc[2] if str(x) != "nan"]
        # 如果 31 生成 16 天，如果没有 31 生成 15 天
        if 1 in day_list:
            return day_list[num_index : num_index + 15]
        else:
            if 31 in day_list:
                return day_list[num_index : num_index + 16]
            else:
                return day_list[num_index : num_index + 15]

    def get_name(self):
        """把所有名字变为列表"""
        column_name = [i for i in self._df.columns]
        get_name_columns = self._df.loc[3::2][column_name[10]]  # col and row number
        name_list = [i.lower() for i in get_name_columns]
        return name_list

    def get_time(self, row_num: int):
        """获取时间"""
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

    def generate_all(self):
        """输出全部列表，如果列表全 0 就排除"""
        all_list = {}
        num = 4
        for emp_name in self.get_name():
            all_list[emp_name] = self.get_time(num)
            num += 2

        # 删除没上班的员工
        del_emp_no_working = []
        for key, value in all_list.items():
            if all(elem == 0 for elem in value):
                del_emp_no_working.append(key)
        for i in del_emp_no_working:
            del all_list[i]

        return all_list


class TimeCalculation:
    """TimeCalculation 是计算所有员工的上下班时间"""

    def __init__(self, emp_time, emp_salary) -> None:
        self.emp_time: list = emp_time
        self.emp_salary: float = emp_salary
        self.emp_work_hour: int = 0

    def result(self, num):
        """功能：计算时间，把时间换成工资计算"""
        if self.emp_time[num] == 0 or len(self.emp_time[num]) < 2:
            return 0

        elif isinstance(self.emp_time[num], list):
            emp_in = pendulum.parse(self.emp_time[num][0])
            emp_out = pendulum.parse(self.emp_time[num][-1])
            day_in = pendulum.parse("08:35")
            day_out = pendulum.parse("17:25")

            # 午餐
            lunch_time = 1  # Lunch Time
            # 祈祷
            sembahyang = 2

            # 计算白天的工作时间 -----------------------------------------
            # 正常
            if emp_in <= day_in and emp_out >= day_out:
                self.emp_work_hour += 8
            # 早到 早退
            elif emp_in <= day_in and emp_out <= day_out:
                total_times = pendulum.period(day_in, emp_out)
                if total_times.hours > 4:
                    self.emp_work_hour += total_times.hours - lunch_time
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1
                else:
                    self.emp_work_hour += total_times.hours
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1
            # 晚到 晚退
            elif emp_in >= day_in and emp_out >= day_out:
                total_times = pendulum.period(emp_in, day_out)
                if total_times.hours > 4:
                    self.emp_work_hour += total_times.hours - lunch_time
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1
                else:
                    self.emp_work_hour += total_times.hours
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1

            # 计算加班 -------------------------------------------------
            overtime = [
                "18:10",
                "18:55",
                "19:40",
                "20:25",
                "21:10",
                "21:55",
                "22:55",
                "23:55",
            ]
            for time in overtime:
                if emp_out >= pendulum.parse(time):
                    self.emp_work_hour += 1

            return self.emp_work_hour * self.emp_salary
