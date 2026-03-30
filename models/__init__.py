"""
Employee data model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Employee:
    """Employee data model"""

    _id: str
    name: str
    ic: str
    pay_hour: float
    img_employee: str = ""
    dob: str = ""
    nationality: str = ""
    gender: str = ""
    contact: str = ""
    address: str = ""
    sign_date: str = ""

    @classmethod
    def from_db_doc(cls, doc: dict) -> "Employee":
        """Create Employee from MongoDB document"""
        return cls(
            _id=doc.get("_id", ""),
            name=doc.get("name", ""),
            ic=doc.get("ic", ""),
            pay_hour=doc.get("pay_hour", 0.0),
            img_employee=doc.get("img_employee", ""),
            dob=doc.get("dob", ""),
            nationality=doc.get("nationality", ""),
            gender=doc.get("gender", ""),
            contact=doc.get("contact", ""),
            address=doc.get("address", ""),
            sign_date=doc.get("sign_date", ""),
        )

    def to_db_doc(self) -> dict:
        """Convert to MongoDB document"""
        return {
            "_id": self._id,
            "name": self.name,
            "ic": self.ic,
            "pay_hour": self.pay_hour,
            "img_employee": self.img_employee,
            "dob": self.dob,
            "nationality": self.nationality,
            "gender": self.gender,
            "contact": self.contact,
            "address": self.address,
            "sign_date": self.sign_date,
        }


@dataclass
class DailyWorkRecord:
    """Daily work record for an employee"""

    day: int
    day_of_week: str
    pay_perday: float
    work_time: list
    daily_work_hours: float


@dataclass
class SalaryRecord:
    """Monthly salary record for an employee"""

    pay_hour: float
    total_salary: float
    total_work_hours: float
    daily_records: list = field(default_factory=list)

    def to_db_doc(self) -> dict:
        """Convert to MongoDB document format"""
        return {
            "pay_hour": self.pay_hour,
            "total_salary": self.total_salary,
            "total_work_hours": self.total_work_hours,
            "output": self.daily_records,
        }


@dataclass
class MonthlySalaryBatch:
    """Monthly salary batch document"""

    _id: str
    date: str
    total_amounts: float
    emp_work_hours: dict

    def to_db_doc(self) -> dict:
        """Convert to MongoDB document"""
        return {
            "_id": self._id,
            "date": self.date,
            "total_amounts": self.total_amounts,
            "emp_work_hours": self.emp_work_hours,
        }
