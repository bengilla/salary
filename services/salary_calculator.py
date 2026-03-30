"""
Salary calculation service with new overtime rules
"""

import json
import math
import os

import pendulum


class SalaryCalculator:
    """Calculate employee salary based on work hours"""

    def __init__(self, emp_time: list, emp_salary: float, version: str = "v0800"):
        self.emp_time = emp_time
        self.emp_salary = emp_salary
        self.version = version
        self._config = self._load_config()
        self.work_hours = 0.0

    def _load_config(self) -> dict:
        """Load work hours configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        with open(config_path, "r") as f:
            return json.load(f)

    def _get_version_config(self) -> dict:
        """Get config for selected version"""
        return self._config["versions"][self.version]

    def _parse_time(self, time_str: str) -> pendulum.DateTime:
        """Parse time string to pendulum DateTime"""
        if time_str == "24:00":
            return pendulum.parse("23:59:59")
        return pendulum.parse(time_str)

    def _calculate_daily_hours(self, day_index: int) -> float:
        """Calculate work hours for a specific day"""
        if self.emp_time[day_index] == 0 or len(self.emp_time[day_index]) < 2:
            return 0.0

        emp_in = self._parse_time(self.emp_time[day_index][0])
        emp_out = self._parse_time(self.emp_time[day_index][-1])

        version_cfg = self._get_version_config()
        day_start = self._parse_time(version_cfg["start"])
        day_end = self._parse_time(version_cfg["end"])
        ot_start = self._parse_time(version_cfg["overtime_start"])
        max_time = self._parse_time(version_cfg["max_time"])

        if emp_out > max_time:
            emp_out = max_time

        if emp_in > emp_out:
            return 0.0

        lunch_start = self._parse_time("12:00")
        lunch_end = self._parse_time("13:00")

        standard_hours = self._calculate_standard_hours(emp_in, emp_out, day_start, day_end, lunch_start, lunch_end)

        ot_hours = 0.0
        if emp_out > ot_start:
            ot_hours = self._calculate_ot_hours(emp_in, emp_out, ot_start, lunch_start, lunch_end)

        total_hours = standard_hours + ot_hours
        self.work_hours = round(total_hours * 2) / 2
        return self.work_hours

    def _calculate_standard_hours(self, emp_in, emp_out, day_start, day_end, lunch_start, lunch_end):
        """Calculate standard work hours (08:00-17:00 or 08:30-17:30)"""
        standard_start = max(emp_in, day_start)
        standard_end = min(emp_out, day_end)

        if standard_start >= standard_end:
            return 0.0

        if emp_in > day_start and emp_in < self._parse_time("10:00"):
            standard_start = self._parse_time("10:00")

        if standard_start >= standard_end:
            return 0.0

        mins = standard_end.diff(standard_start).in_minutes()
        lunch_mins = self._calculate_lunch_deduction(standard_start, standard_end, lunch_start, lunch_end)
        mins -= lunch_mins

        return max(0, mins / 60.0)

    def _calculate_ot_hours(self, emp_in, emp_out, ot_start, lunch_start, lunch_end):
        """Calculate overtime hours based on user rules"""
        ot_start_adj = max(ot_start, lunch_end)

        if emp_out <= ot_start_adj:
            return 0.0

        ot_start_for_calc = max(emp_in, ot_start_adj)
        if emp_out <= ot_start_for_calc:
            return 0.0

        if emp_in <= ot_start_adj and emp_out <= self._parse_time("18:30"):
            ot_mins = emp_out.diff(ot_start_adj).in_minutes()
            ot_hours = ot_mins / 60.0
            if ot_hours >= 1.5:
                return 2.0
            return math.ceil(ot_hours)

        total_ot = 0.0

        if ot_start_adj < self._parse_time("18:30") and emp_out > ot_start_adj and emp_in <= ot_start_adj:
            first_ot_end = min(emp_out, self._parse_time("18:30"))
            ot_mins = first_ot_end.diff(ot_start_adj).in_minutes()
            first_ot = ot_mins / 60.0
            if first_ot >= 1.5:
                total_ot += 2.0
            else:
                total_ot += math.ceil(first_ot)

        if emp_out > self._parse_time("18:30"):
            second_start = max(self._parse_time("18:30"), ot_start_for_calc)

            if emp_out >= self._parse_time("20:30"):
                total_ot += 2.0
            elif emp_out >= self._parse_time("19:30"):
                total_ot += 1.0

            if emp_out >= self._parse_time("21:30"):
                total_ot += 2.0

            if emp_out >= self._parse_time("22:30"):
                total_ot += 1.0

            if emp_out >= self._parse_time("23:30"):
                total_ot += 1.0

        return total_ot

    def _calculate_lunch_deduction(self, period_start, period_end, lunch_start, lunch_end):
        """Calculate lunch time deduction within a period"""
        if period_end <= lunch_start or period_start >= lunch_end:
            return 0

        lunch_start_in_period = max(period_start, lunch_start)
        lunch_end_in_period = min(period_end, lunch_end)

        if lunch_end_in_period > lunch_start_in_period:
            return lunch_end_in_period.diff(lunch_start_in_period).in_minutes()
        return 0

    def calculate_day_salary(self, day_index: int) -> float:
        """Calculate salary for a specific day"""
        hours = self._calculate_daily_hours(day_index)
        return round(hours * self.emp_salary, 2)

    def round_salary(self, salary: float) -> float:
        """Round salary to nearest 10"""
        rounded = round(salary)
        balance = rounded % 10
        threshold = self._config.get("salary_round_threshold", 5)
        unit = self._config.get("salary_round_unit", 10)

        if balance > threshold:
            return rounded + (unit - balance)
        else:
            return rounded - balance
