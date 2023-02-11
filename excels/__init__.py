import pendulum
from excels.excel_module import ReadExcel
from excels.timecalculation import TimeCalculation
from models.mongo import MongoDB


class EmpSalary:
    """这是最终到处所有计算后的数据"""

    def __init__(self, db_collection: str, excel_file):
        self.data = {}
        self.total_amounts = 0

        # send excel file to ReadExcel to calculation the data
        self.read_excel = ReadExcel(excel_file)

        # get name, day, month from ReadExcel data
        self._date = self.read_excel.get_date()
        print(self._date)

        # get data from mongodb
        _mongodb = MongoDB()
        self._empinfo = _mongodb.emp_info_collection(db_collection)
        self._work_hour = _mongodb.emp_work_hour_collection(
            db_collection, self._date.year
        )

        # get day list from excel top column
        self._day_list: list = self.read_excel.get_day_list()

        self._get_all_list = self.read_excel.generate_all()

        self._get_emp_total_in_excel = self.read_excel.get_emp_total_in_excel()

        self._day: int = self._date.day
        self._month: int = self._date.month
        self._year: int = self._date.year

        # run main section
        self.main()

    def emp_on_web(self) -> list:
        emp_name_on_web = self._empinfo.find({})
        emp_on_web = [emp["_id"] for emp in emp_name_on_web]
        return emp_on_web

    def emp_not_in_web(self) -> list:
        # get all employee on web
        emp_name_on_web = self._empinfo.find({})
        emp_on_web = [emp["_id"] for emp in emp_name_on_web]

        # get employee on excel
        emp_on_excel = [emp.lower() for emp in self._get_emp_total_in_excel["name"]]

        # check employee in excels is it on web
        result = [emp for emp in emp_on_excel if emp not in emp_on_web]
        print(result)
        return result

    def emp_final_calculation(self, id: str):
        # get single employee data
        single_emp_data = self._empinfo.find_one({"_id": id})

        pay_hour = single_emp_data["pay_hour"]

        emp_sum_salary = []
        total_work_hours = []
        send_to_mongodb = []

        for index, day in enumerate(self._day_list):
            time_cal = TimeCalculation(
                emp_time=self._get_all_list[id], emp_salary=pay_hour
            )

            pay_day_cost = time_cal.result(index)
            emp_sum_salary.append(pay_day_cost)
            total_work_hours.append(time_cal.emp_work_hour)

            # create day list
            day_of_week = pendulum.from_format(
                f"{self._month}-{self._day_list[index]}", "MM-DD"
            )

            # append full list to mongodb
            send_to_mongodb.append(
                {
                    "day": day,
                    "day_of_week": day_of_week.format("dd"),
                    "pay_perday": pay_day_cost,
                    "work_time": time_cal.emp_time[index],
                    "daily_work_hours": time_cal.emp_work_hour,
                }
            )

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

        self.total_amounts += output_emp_salary
        self.data[id.title()] = store_data


    def main(self):
        """导出至 MongoDB"""
        get_emp_name = self._empinfo.find({})
        emp_name = [x["_id"] for x in get_emp_name]

        # 最终输出，计算没人的基本工资
        for each_emp in emp_name:
            try:
                self.emp_final_calculation(each_emp)
            except KeyError:
                continue

        # 上传至 MongoDB
        send_data = {
            "date": self._date.format("DD-MMM-YYYY"),
            "total_amounts": self.total_amounts,
            "emp_work_hours": self.data,
        }
        self._work_hour.insert_one(send_data)
        # print(send_data)
