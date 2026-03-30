"""
Excel reading service
"""

import json
import os
from datetime import datetime as dt
from typing import Any

import pandas as pd
import pendulum


class ExcelReader:
    """Read and parse Excel file from time clock"""

    def __init__(self, filename):
        self._filename = filename
        self._config = self._load_config()
        self._sheet_num = 2
        self._df = pd.read_excel(self._filename, sheet_name=self._sheet_num)
        self._date = self._parse_date()

    def _load_config(self) -> dict:
        """Load work hours configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        with open(config_path, "r") as f:
            return json.load(f)

    def _parse_date(self) -> dt:
        """Parse date from Excel file"""
        cell_value = self._df.iloc[1, 2]
        start_date_str = cell_value.split("~")[0].strip()
        return dt.strptime(start_date_str, "%Y-%m-%d")

    @property
    def date(self) -> dt:
        """Get parsed date"""
        return self._date

    @property
    def month(self) -> int:
        """Get month"""
        return self._date.month

    def get_day_list(self) -> list:
        """Get list of working days from Excel"""
        day_values = [int(x) for x in self._df.loc[2] if str(x) != "nan"]
        if not day_values:
            return []
        if 31 in day_values:
            return day_values[:16]
        return day_values[:15]

    def get_names(self) -> list:
        """Get all employee names from Excel"""
        column_name = [i for i in self._df.columns]
        name_column = self._df.loc[3::2][column_name[10]]
        return [i.lower() for i in name_column if pd.notna(i)]

    def get_time(self, row_num: int) -> list:
        """Get time records for a specific row"""
        time_records = []
        row_data = [0 if str(x) == "nan" else x for x in self._df.loc[row_num]]

        for each_time in row_data:
            if each_time == 0:
                time_records.append(0)
            else:
                if len(str(each_time)) <= 5:
                    time_records.append([str(each_time)])
                else:
                    time_records.append([str(each_time)[0:5], str(each_time)[-5:]])
        return time_records

    def generate_all_records(self) -> dict:
        """Generate all employee time records, excluding those with no work"""
        all_records = {}
        row_num = 4
        for emp_name in self.get_names():
            all_records[emp_name] = self.get_time(row_num)
            row_num += 2

        all_records = {
            k: v for k, v in all_records.items() if not all(elem == 0 for elem in v)
        }
        return all_records
