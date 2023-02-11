import pandas as pd
import pendulum


class ReadExcel:
    """读取 excel 文件"""

    def __init__(self, excel_file):
        # 选择 excel 的第二页和 excel 文件名
        self._sheet_num = 2
        self._excel_file = excel_file

        # pandas 生成和生成日期
        self._df = pd.read_excel(self._excel_file, sheet_name=self._sheet_num)

    def get_date(self):
        return pendulum.from_format(self._df.loc[1][2].split(" ")[0], "YYYY-MM-DD")

    def get_day_list(self):
        day_list = [int(x) for x in self._df.loc[2] if str(x) != "nan"]
        return day_list

    def get_emp_total_in_excel(self):
        items = self._df.loc[3::2]["Unnamed: 10"]
        name = [name for name in items]
        return {"length": len(items), "name": name}

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