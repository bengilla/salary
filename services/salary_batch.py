"""
Salary batch processing service
"""

import pendulum

from mongodb import get_mongodb
from services.excel_reader import ExcelReader
from services.salary_calculator import SalaryCalculator


class SalaryBatchService:
    """Process salary batches from Excel files"""

    def __init__(self, filename, version: str = "v0800"):
        self.filename = filename
        self.version = version
        self._db = get_mongodb()
        self._excel_reader = ExcelReader(filename)
        self._emp_records = {}
        self._not_registered = []

    def _load_employees(self) -> dict:
        """Load employees from database, keyed by lowercase name"""
        employees = {}
        for emp in self._db.info_collection.find({}):
            name_key = emp["name"].lower()
            employees[name_key] = emp
        return employees

    def _get_day_of_week(self, month: int, day: int) -> str:
        """Get day of week string"""
        dt_str = f"{month}-{day}"
        return pendulum.from_format(dt_str, "MM-DD").format("dd")

    def _round_salary(self, salary: float) -> float:
        """Round salary to nearest 10"""
        rounded = round(salary)
        balance = rounded % 10
        if balance > 5:
            return rounded + (10 - balance)
        return rounded - balance

    def process(self) -> tuple[dict, list]:
        """Process Excel file and calculate salaries"""
        db_employees = self._load_employees()
        excel_names = self._excel_reader.get_names()
        day_list = self._excel_reader.get_day_list()
        all_records = self._excel_reader.generate_all_records()

        self._not_registered = [name for name in excel_names if name not in db_employees]

        for emp_name, emp_data in db_employees.items():
            if emp_name not in all_records:
                continue

            try:
                daily_salaries = []
                total_hours = []
                daily_records = []
                pay_hour = emp_data["pay_hour"]

                for idx, day in enumerate(day_list):
                    calc = SalaryCalculator(all_records[emp_name], pay_hour, self.version)
                    day_salary = calc.calculate_day_salary(idx)
                    daily_salaries.append(day_salary)
                    total_hours.append(calc.work_hours)

                    daily_records.append({
                        "day": day,
                        "day_of_week": self._get_day_of_week(
                            self._excel_reader.month, day
                        ),
                        "pay_perday": day_salary,
                        "work_time": all_records[emp_name][idx]
                        if idx < len(all_records[emp_name])
                        else [],
                        "daily_work_hours": calc.work_hours,
                    })

                total_salary = self._round_salary(sum(daily_salaries))

                self._emp_records[emp_name.title()] = {
                    "pay_hour": pay_hour,
                    "total_salary": total_salary,
                    "total_work_hours": sum(total_hours),
                    "output": daily_records,
                }
            except (KeyError, IndexError):
                continue

        return self._emp_records, self._not_registered

    def save_to_db(self) -> float:
        """Save processed records to MongoDB and return total amount"""
        total = sum(data["total_salary"] for data in self._emp_records.values())

        batch_date = pendulum.datetime(
            self._excel_reader.date.year,
            self._excel_reader.date.month,
            self._excel_reader.date.day,
        )

        doc = {
            "_id": batch_date.format("MMM DD, YYYY"),
            "date": batch_date.format("DD-MMM-YYYY"),
            "total_amounts": total,
            "emp_work_hours": self._emp_records,
        }

        self._db.work_hour_collection.insert_one(doc)
        return total
