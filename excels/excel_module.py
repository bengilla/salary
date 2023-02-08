import pandas as pd
import pendulum


class ReadExcel:
    """读取 excel 文件"""

    def __init__(self, file):
        # 选择 excel 的第二页和 excel 文件名
        self._sheet_num = 2
        self._file = file

        # pandas 生成和生成日期
        self._df = pd.read_excel(self._file, sheet_name=self._sheet_num)

    def get_date(self):
        return pendulum.from_format(self._df.loc[1][2].split(" ")[0], "YYYY-MM-DD")

    def get_day_list(self):
        day_list = [int(x) for x in self._df.loc[2] if str(x) != "nan"]
        return day_list

    def get_emp_total_in_excel(self):
        items = self._df.loc[3::2]["Unnamed: 10"]
        name = [name for name in items]
        return {"length": len(items), "name": name}

    def get_emp_info(self, columns: int):
        emp_name: str = self._df.loc[columns][10].lower()
        emp_time_list = [0 if str(x) == "nan" else x for x in self._df.loc[columns + 1]]

        store_time = []

        for each_time in emp_time_list:
            if each_time == 0:
                store_time.append(0)
            else:
                if len(each_time) <= 5:
                    store_time.append([each_time])
                else:
                    store_time.append([each_time[0:5], each_time[-5:]])

        emp_list = {"name": emp_name, "time_list": store_time}
        return emp_list
