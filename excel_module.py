"""
Project for TBROS employees salary calculator and employee person info
"""

from datetime import datetime as dt
from datetime import timedelta

import pandas as pd


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
        day_list = [x for x in self._df.loc[2]]
        # 如果 31 生成 16 天，如果没有 31 生成 15 天
        if 31 not in day_list:
            num_index = day_list.index(1)
            return day_list[num_index : num_index + 15]
        else:
            num_index = day_list.index(16)
            return day_list[num_index : num_index + 16]

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
        self.emp_work_hours: int = 0

    def result(self, num):
        """功能：计算时间，把时间换成工资计算"""
        if self.emp_time[num] == 0:
            return 0

        elif len(self.emp_time[num]) < 2:
            return 0

        elif isinstance(self.emp_time[num], list):

            # 把文字转换成 time 格式
            def calculate_time(time_input):
                try:
                    time_output = dt.strptime(time_input, "%H:%M")
                    return time_output
                except Exception:
                    return dt.strptime("00:00", "%H:%M")

            # 上班时间，下班时间
            emp_in = calculate_time(self.emp_time[num][0])
            emp_out = calculate_time(self.emp_time[num][-1])

            # 规定上班时间，规定下班时间
            day_in = calculate_time("08:30")
            day_out = calculate_time("17:30")

            # 午饭时间
            lunch = timedelta(hours=1)
            # lunch = 1

            # 周五祈祷时间
            sembahyang = 2

            # 加班时间，1730 至 2200 每 45 分钟 + 1 小时给工人
            # lv1_overtime = timedelta(minutes=45)  # 17:30 - 22:00 +1 hour
            # lv2_overtime = timedelta(minutes=60)  # 22:00 - 00:00 +2 hours

            # 计算白天的工作时间
            # 做满 8 个小时
            if emp_in < day_in and emp_out > day_out:  # Full day
                self.emp_work_hours += 8

            # 测试 ----------------------------------------------------------
            elif emp_out > day_out:
                work_hour = day_out - emp_in
                if work_hour > timedelta(hours=4):
                    total_hour = str(work_hour - lunch)[0:4]
                    self.emp_work_hours += calculate_time(total_hour).hour
                    if calculate_time(total_hour).minute > 30:
                        self.emp_work_hours += 1

            else:
                work_hour = emp_out - emp_in
                if work_hour > timedelta(hours=4):
                    total_hour = str(work_hour - lunch)[0:4]
                    self.emp_work_hours += calculate_time(total_hour).hour
                    if calculate_time(total_hour).minute > 30:
                        self.emp_work_hours += 1
                elif work_hour < timedelta(hours=4):
                    pass

            # --------------------------------------------------------------
            # # 晚到 晚退
            # elif emp_in > day_in and emp_out > day_out:  # Late come until 17:30
            #     temp = str(day_out - emp_in)[0:4]
            #     # 如果工作4个小时
            #     if calculate_time(temp).hour > 5:
            #         self.emp_work_hours += calculate_time(temp).hour - lunch
            #         if calculate_time(temp).minute > 30:
            #             self.emp_work_hours += 1
            #     else:
            #         self.emp_work_hours += calculate_time(temp).hour
            #         if calculate_time(temp).minute > 30:
            #             self.emp_work_hours += 1

            # # 早到 早退 ***
            # elif emp_in < day_in and emp_out < day_out:  # Early Come Early Out
            #     temp = str(emp_out - day_in)[0:4]

            #     if calculate_time(temp).hour > 1 and calculate_time(temp).hour <= 5:
            #         self.emp_work_hours += calculate_time(temp).hour
            #     elif calculate_time(temp).hour > 5:
            #         self.emp_work_hours += calculate_time(temp).hour - lunch
            #         if calculate_time(temp).minute > 30:
            #             self.emp_work_hours += 1
            #     # else:
            #     #     self.emp_work_hours += calculate_time(temp).hour
            #     #     if calculate_time(temp).minute > 30:
            #     #         self.emp_work_hours += 1

            # # 晚到 早退
            # elif emp_in > day_in and emp_out < day_out:  # Early Come Early Out
            #     temp = str(emp_out - emp_in)[0:4]

            #     if calculate_time(temp).hour > 4:
            #         self.emp_work_hours += calculate_time(temp).hour - lunch
            #         if calculate_time(temp).minute > 30:
            #             self.emp_work_hours += 1
            #     else:
            #         self.emp_work_hours += calculate_time(temp).hour
            #         if calculate_time(temp).minute > 30:
            #             self.emp_work_hours += 1
            # --------------------------------------------------------------

            # 计算加班的工作时间
            if emp_out >= calculate_time("18:50"):  # 加班至 1900
                self.emp_work_hours += 2

            if emp_out >= calculate_time("21:50"):  # 加班至 2200
                self.emp_work_hours += 4

            if emp_out >= calculate_time("23:50"):  # 加班至 0000
                self.emp_work_hours += 3

            return self.emp_work_hours * self.emp_salary


# file = ReadExcel("data/10/test.xls")
# a = file._df
# day = file.get_day()
# name = file.get_name()
# time = file.get_time(10)
# all_emp = file.generate_all()
# print(time)
